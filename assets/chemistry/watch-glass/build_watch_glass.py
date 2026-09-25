"""
build_watch_glass.py — NCERT Class 9-12 High-Fidelity 80mm Borosilicate Watch Glass
Dual collections:
  - Watch_Glass_Full: Borosilicate concave spherical dish with beveled rim, holding fine chemical crystal sample, resting on studio pedestal
  - Watch_Glass_Section: 180° lathe cross-section revealing uniform 1.6mm glass thickness, spherical curvature arch, crystal layer profile, and plaque
"""

import sys
import math
import shutil
from pathlib import Path
from mathutils import Vector, Euler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy
import bmesh

ASSET_ID = "watch-glass"

# Calibrated Laboratory Palette
COLOR_GLASS         = (0.95, 0.98, 1.00)     # Borosilicate glass (IOR 1.52)
COLOR_CRYSTALS      = (0.80, 0.88, 0.95)     # Fine analytical sample powder / crystals
COLOR_STAND_BASE    = (0.12, 0.13, 0.16)     # Dark slate laboratory pedestal
COLOR_GOLD          = (0.90, 0.75, 0.22)     # Plaque frame
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)     # Dimension caliper
COLOR_PROFILE_ARC   = (0.25, 0.75, 0.95)     # Curvature arc


def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_emissive_mat(name, color, strength=8.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    diff = p2 - p1
    length = diff.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = diff.to_track_quat("Z", "Y").to_euler()

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = mid
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# WATCH GLASS SPHERICAL PROFILE GENERATOR
# -----------------------------------------------------------------------------
def get_watch_glass_profile():
    # Spherical curvature radius R = 0.088m, thickness t = 0.0016m, diameter = 0.080m (radius = 0.040m)
    # Origin (0,0) at bottom-most convex point of outer glass surface
    r_max = 0.040
    t_glass = 0.0016
    R_sphere = 0.088
    # Center of sphere for outer surface is at (0, R_sphere)
    # z_outer(r) = R_sphere - sqrt(R_sphere^2 - r^2)
    prof = []
    num_pts = 24
    for i in range(num_pts + 1):
        r = r_max * (i / num_pts)
        z = R_sphere - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    # Rim bevel & top edge
    z_outer_rim = prof[-1][1]
    prof.append((r_max + 0.0006, z_outer_rim + 0.0008))
    prof.append((r_max + 0.0004, z_outer_rim + t_glass + 0.0004))
    prof.append((r_max, z_outer_rim + t_glass))

    # Inner spherical surface returning to center r = 0
    # Center of sphere for inner surface is at (0, R_sphere + t_glass)
    # z_inner(r) = (R_sphere + t_glass) - sqrt(R_sphere^2 - r^2)
    for i in range(num_pts, -1, -1):
        r = r_max * (i / num_pts)
        z = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    return prof


def get_crystal_powder_profile():
    # Shallow layer of solid crystals collected in the center bowl
    # r from 0 to 0.022, z follows inner surface with a convex powder heap
    t_glass = 0.0016
    R_sphere = 0.088
    r_powder = 0.022
    prof = []
    num_pts = 16
    # Inner surface contact
    for i in range(num_pts + 1):
        r = r_powder * (i / num_pts)
        z = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    # Upper surface of powder heap tapering smoothly from center (thickness 2.2mm at center)
    for i in range(num_pts, -1, -1):
        r = r_powder * (i / num_pts)
        z_base = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        h_heap = 0.0022 * (1.0 - (r / r_powder)**2)
        prof.append((r, z_base + h_heap))

    return prof


# -----------------------------------------------------------------------------
# LATHE HELPERS
# -----------------------------------------------------------------------------
def build_lathe_full(name, profile_points, segments=64, mat=None, collection=None):
    bm = bmesh.new()
    rings = []
    for r_pt, z_pt in profile_points:
        ring = []
        for s in range(segments):
            theta = 2.0 * math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm.verts.new((x, y, z_pt)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new([rings[i][s], rings[i+1][s], rings[i+1][next_s], rings[i][next_s]])

    if profile_points[0][0] == 0.0:
        center_v = bm.verts.new((0.0, 0.0, profile_points[0][1]))
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new([center_v, rings[0][next_s], rings[0][s]])

    if profile_points[-1][0] == 0.0:
        center_v = bm.verts.new((0.0, 0.0, profile_points[-1][1]))
        for s in range(segments):
            next_s = (s + 1) % segments
            bm.faces.new([center_v, rings[-1][s], rings[-1][next_s]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if collection:
        link_strictly(obj, collection)
    return obj


def build_lathe_half(name, profile_points, segments=36, mat=None, collection=None):
    # Revolve from -pi/2 to pi/2
    bm = bmesh.new()
    rings = []
    for r_pt, z_pt in profile_points:
        ring = []
        for s in range(segments + 1):
            theta = -math.pi / 2.0 + math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm.verts.new((x, y, z_pt)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for s in range(segments):
            bm.faces.new([rings[i][s], rings[i+1][s], rings[i+1][s+1], rings[i][s+1]])

    bm.faces.new([rings[i][0] for i in range(len(rings))])
    bm.faces.new([rings[i][segments] for i in range(len(rings))][::-1])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if mat:
        obj.data.materials.append(mat)
    if collection:
        link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# BUILD WATCH GLASS FULL
# -----------------------------------------------------------------------------
def build_watch_glass_full(collection):
    glass_mat    = kit.add_glass_material("wg-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    powder_mat   = kit.add_material("wg-powder", COLOR_CRYSTALS, metallic=0.05, roughness=0.88)
    plinth_mat   = kit.add_material("wg-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)

    # 1. Studio Base
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.180, 0.160, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Main Watch Glass Body
    glass_obj = build_lathe_full(f"{ASSET_ID}_Body", get_watch_glass_profile(), segments=64, mat=glass_mat, collection=collection)
    
    # 3. Collected Crystal Powder Heap
    powder_obj = build_lathe_full(f"{ASSET_ID}_Powder_Bed", get_crystal_powder_profile(), segments=48, mat=powder_mat, collection=collection)

    # Scatter a few micro-crystal facets on top for authentic crystalline appearance
    for i in range(18):
        ang = i * 2.39996
        rad = 0.004 + (i % 6) * 0.0025
        px = math.cos(ang) * rad
        py = math.sin(ang) * rad
        pz = 0.0025 + 0.0012 * (1.0 - (rad / 0.020)**2)
        grain = kit.primitive_object(
            f"{ASSET_ID}_Crystal_{i:02d}", "uv_sphere", powder_mat,
            size=(0.0016, 0.0016, 0.0012),
            location=(px, py, pz)
        )
        link_strictly(grain, collection)


# -----------------------------------------------------------------------------
# BUILD WATCH GLASS SECTION (180° Cutaway & Profile Geometry)
# -----------------------------------------------------------------------------
def build_watch_glass_section(collection):
    glass_mat  = kit.add_glass_material("wg-sec-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    powder_mat = kit.add_material("wg-sec-powder", COLOR_CRYSTALS, metallic=0.05, roughness=0.88)
    plinth_mat = kit.add_material("wg-sec-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("wg-sec-gold", COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat    = create_emissive_mat("wg-sec-dim", COLOR_CYAN_DIM, strength=10.0)
    arc_mat    = create_emissive_mat("wg-sec-arc", COLOR_PROFILE_ARC, strength=12.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Sec_Plinth", "cube", plinth_mat,
        size=(0.240, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. 180° Lathe Cutaway Models
    glass_half = build_lathe_half(f"{ASSET_ID}_Sec_Body", get_watch_glass_profile(), segments=48, mat=glass_mat, collection=collection)
    powder_half = build_lathe_half(f"{ASSET_ID}_Sec_Powder", get_crystal_powder_profile(), segments=36, mat=powder_mat, collection=collection)

    # Elevate slightly for clean pedestal clearance
    z_elev = 0.004
    for obj in [glass_half, powder_half]:
        obj.location = (0.0, 0.015, z_elev)

    # 3. Dimension Calipers & Curvature Arc
    # Diameter Caliper Line (80 mm diameter across rim)
    y_line = 0.015
    create_cylinder_segment(f"{ASSET_ID}_Dim_Diam", (-0.040, y_line, z_elev + 0.012), (0.040, y_line, z_elev + 0.012), 0.0003, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Diam_L", (-0.040, y_line, z_elev + 0.008), (-0.040, y_line, z_elev + 0.016), 0.0004, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Diam_R", (0.040, y_line, z_elev + 0.008), (0.040, y_line, z_elev + 0.016), 0.0004, dim_mat, collection)

    # Thickness Caliper Line (1.6 mm wall thickness)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Thick", (0.0, y_line, z_elev), (0.0, y_line, z_elev + 0.0016), 0.00025, arc_mat, collection)

    # 4. Educational Plaque (Placed to the left side and angled cleanly towards the camera)
    plq_x = -0.055
    plq_y = -0.010
    plq_rot = (math.radians(12.0), 0.0, math.radians(40.0))

    plaque_base = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Base", "cube", plinth_mat,
        size=(0.095, 0.010, 0.046),
        location=(plq_x, plq_y, 0.022),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_base, collection)

    plq_norm_x = 0.005 * math.sin(math.radians(40.0))
    plq_norm_y = -0.005 * math.cos(math.radians(40.0))

    plaque_border = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Border", "cube", gold_mat,
        size=(0.091, 0.002, 0.042),
        location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.022),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat("wg-sec-txt", (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(
        f"{ASSET_ID}_Plaque_TitleBar", "cube", txt_mat,
        size=(0.075, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.032),
        rotation_euler=plq_rot
    )
    link_strictly(title_bar, collection)

    line_1 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line1", "cube", dim_mat,
        size=(0.065, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.022),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line2", "cube", arc_mat,
        size=(0.055, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.014),
        rotation_euler=plq_rot
    )
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING SETUP
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 45.0
    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Framed slightly elevated to look down into the concave watch glass bowl
    cam.location = (0.16, -0.22, 0.14)
    cam_target = Vector((0.0, 0.0, 0.010))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new("Key_Light", type="AREA")
    key_light_data.energy = 35.0
    key_light_data.size = 0.35
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.20, -0.18, 0.25)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new("Fill_Light", type="AREA")
    fill_light_data.energy = 16.0
    fill_light_data.size = 0.40
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.20, -0.16, 0.20)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new("Rim_Light", type="POINT")
    rim_light_data.energy = 25.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (0.0, 0.22, 0.20)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Watch_Glass_Full")
    sec_col  = bpy.data.collections.new("Watch_Glass_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_watch_glass_full(full_col)
    build_watch_glass_section(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB only
    bpy.ops.object.select_all(action='DESELECT')
    for obj in full_col.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = full_col.objects[0]

    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / f"{ASSET_ID}.glb"),
        use_selection=True,
        export_format='GLB'
    )

    viewer_dest = Path("/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets") / f"{ASSET_ID}.glb"
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f"{ASSET_ID}.glb", viewer_dest)
        print(f"Synced GLB to: {viewer_dest}")

    # Render Preview 1: Watch_Glass_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Watch_Glass_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.14, -0.20, 0.12)
    cam_target = Vector((0.0, 0.0, 0.010))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
