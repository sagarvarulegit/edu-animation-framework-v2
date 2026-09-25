"""
build_magnesium_oxide.py — NCERT Class 10 Chemistry Activity 1.1 High-Fidelity Magnesium Oxide Ash
Dual collections:
  - Magnesium_Oxide_Full: Fluffy brilliant-white MgO ash powder heap with micro-granules and flakes in an 80mm watch glass
  - Magnesium_Oxide_Detail: Longitudinal cross-section of ash heap with ionic crystal unit cell inset, dimensions, and chemical reaction plaque
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

ASSET_ID = "magnesium-oxide"

# Calibrated Laboratory Palette
COLOR_GLASS         = (0.95, 0.98, 1.00)     # Borosilicate watch glass (IOR 1.52)
COLOR_MGO_ASH       = (0.96, 0.96, 0.95)     # Brilliant white MgO powder ash
COLOR_MGO_FLAKE     = (0.92, 0.92, 0.90)     # Crumbling combustion flakes
COLOR_ION_MG        = (0.85, 0.65, 0.95)     # Mg2+ cation (ionic crystal callout)
COLOR_ION_O         = (0.95, 0.35, 0.35)     # O2- anion (ionic crystal callout)
COLOR_STAND_BASE    = (0.12, 0.13, 0.16)     # Dark slate pedestal
COLOR_GOLD          = (0.90, 0.75, 0.22)     # Plaque frame
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)     # Dimension caliper
COLOR_BOND          = (0.80, 0.82, 0.86)     # Ionic lattice bond sticks


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
# WATCH GLASS & ASH PROFILE HELPERS
# -----------------------------------------------------------------------------
def get_watch_glass_profile():
    r_max = 0.040
    t_glass = 0.0016
    R_sphere = 0.088
    prof = []
    num_pts = 24
    for i in range(num_pts + 1):
        r = r_max * (i / num_pts)
        z = R_sphere - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    z_outer_rim = prof[-1][1]
    prof.append((r_max + 0.0006, z_outer_rim + 0.0008))
    prof.append((r_max + 0.0004, z_outer_rim + t_glass + 0.0004))
    prof.append((r_max, z_outer_rim + t_glass))

    for i in range(num_pts, -1, -1):
        r = r_max * (i / num_pts)
        z = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    return prof


def get_mgo_heap_profile():
    # Volumetric heap of combustion ash in the center of the watch glass
    t_glass = 0.0016
    R_sphere = 0.088
    r_heap = 0.025
    prof = []
    num_pts = 20
    # Bottom contact with glass
    for i in range(num_pts + 1):
        r = r_heap * (i / num_pts)
        z = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        prof.append((r, z))

    # Upper dome profile of ash heap (h = 7.5mm at center, organic shape)
    for i in range(num_pts, -1, -1):
        r = r_heap * (i / num_pts)
        z_base = (R_sphere + t_glass) - math.sqrt(max(0.0, R_sphere**2 - r**2))
        frac = r / r_heap
        h_dome = 0.0075 * (1.0 - frac**1.8)
        prof.append((r, z_base + h_dome))

    return prof


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
# BUILD MAGNESIUM OXIDE FULL
# -----------------------------------------------------------------------------
def build_mgo_full(collection):
    glass_mat  = kit.add_glass_material("mgo-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    ash_mat    = kit.add_material("mgo-ash", COLOR_MGO_ASH, metallic=0.0, roughness=0.96)
    flake_mat  = kit.add_material("mgo-flake", COLOR_MGO_FLAKE, metallic=0.0, roughness=0.92)
    plinth_mat = kit.add_material("mgo-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.200, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Watch Glass
    watch_glass = build_lathe_full(f"{ASSET_ID}_Watch_Glass", get_watch_glass_profile(), segments=64, mat=glass_mat, collection=collection)

    # 3. Main Magnesium Oxide Ash Heap
    ash_heap = build_lathe_full(f"{ASSET_ID}_Ash_Heap", get_mgo_heap_profile(), segments=48, mat=ash_mat, collection=collection)

    # 4. Realistic Combustion Powder Granules and Ash Flakes
    for i in range(28):
        ang = i * 2.39996
        rad = 0.006 + (i % 7) * 0.0028
        frac = rad / 0.025
        h_dome = 0.0075 * max(0.0, 1.0 - frac**1.8)
        px = math.cos(ang) * rad
        py = math.sin(ang) * rad
        pz = 0.0020 + h_dome + 0.0004 * ((i % 3) - 1)
        
        # Alternate between spherical micro-grains and flat crumbling flakes
        if i % 3 == 0:
            grain = kit.primitive_object(
                f"{ASSET_ID}_Flake_{i:02d}", "cube", flake_mat,
                size=(0.0024, 0.0020, 0.0005),
                location=(px, py, pz),
                rotation_euler=(math.radians(15 * (i % 4)), math.radians(20 * (i % 3)), ang)
            )
        else:
            grain = kit.primitive_object(
                f"{ASSET_ID}_Grain_{i:02d}", "uv_sphere", ash_mat,
                size=(0.0018, 0.0018, 0.0014),
                location=(px, py, pz)
            )
        link_strictly(grain, collection)


# -----------------------------------------------------------------------------
# BUILD MAGNESIUM OXIDE DETAIL / SECTION
# -----------------------------------------------------------------------------
def build_mgo_detail(collection):
    glass_mat  = kit.add_glass_material("mgo-sec-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    ash_mat    = kit.add_material("mgo-sec-ash", COLOR_MGO_ASH, metallic=0.0, roughness=0.96)
    mg_ion_mat = kit.add_material("mgo-sec-mg-ion", COLOR_ION_MG, metallic=0.2, roughness=0.25)
    o_ion_mat  = kit.add_material("mgo-sec-o-ion", COLOR_ION_O, metallic=0.1, roughness=0.30)
    bond_mat   = kit.add_machined_metal_material("mgo-sec-bond", COLOR_BOND, metallic=0.85, roughness=0.30)
    plinth_mat = kit.add_material("mgo-sec-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("mgo-sec-gold", COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat    = create_emissive_mat("mgo-sec-dim", COLOR_CYAN_DIM, strength=10.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Sec_Plinth", "cube", plinth_mat,
        size=(0.280, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. 180° Cutaway Models (Revolved from -pi/2 to pi/2, cut face facing front camera)
    dish_x = 0.035
    dish_y = -0.010
    z_elev = 0.004

    glass_half = build_lathe_half(f"{ASSET_ID}_Sec_Watch_Glass", get_watch_glass_profile(), segments=48, mat=glass_mat, collection=collection)
    ash_half = build_lathe_half(f"{ASSET_ID}_Sec_Ash_Heap", get_mgo_heap_profile(), segments=36, mat=ash_mat, collection=collection)

    for obj in [glass_half, ash_half]:
        obj.location = (dish_x, dish_y, z_elev)

    # Dimension Calipers (Heap diameter 50mm, height 7.5mm)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Heap_Diam", (dish_x - 0.025, dish_y, z_elev + 0.004),
                            (dish_x + 0.025, dish_y, z_elev + 0.004), 0.00025, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Heap_H", (dish_x, dish_y, z_elev + 0.002),
                            (dish_x, dish_y, z_elev + 0.009), 0.00025, dim_mat, collection)

    # 3. Micro-Crystalline Ionic Lattice Callout (Rock-Salt NaCl-type unit cell inset)
    # Positioned above right side of dish as a floating atomic inset
    lat_x = dish_x + 0.025
    lat_y = dish_y + 0.030
    lat_z = 0.045
    spacing = 0.012
    r_mg = 0.0024  # Mg2+ ionic radius ~ 72 pm
    r_o  = 0.0034  # O2- ionic radius ~ 140 pm

    # 2x2x2 unit cell corners with alternating Mg2+ and O2- ions
    for ix in range(2):
        for iy in range(2):
            for iz in range(2):
                pos = (lat_x + (ix - 0.5) * spacing,
                       lat_y + (iy - 0.5) * spacing,
                       lat_z + (iz - 0.5) * spacing)
                is_mg = ((ix + iy + iz) % 2 == 0)
                ion_mat = mg_ion_mat if is_mg else o_ion_mat
                ion_r = r_mg if is_mg else r_o
                ion_name = f"{ASSET_ID}_Ion_{'Mg' if is_mg else 'O'}_{ix}{iy}{iz}"
                ion_obj = kit.primitive_object(ion_name, "uv_sphere", ion_mat,
                                               size=(ion_r * 2, ion_r * 2, ion_r * 2),
                                               location=pos)
                link_strictly(ion_obj, collection)

    # Bond rods along edges
    for ix in range(2):
        for iy in range(2):
            p1 = (lat_x + (ix - 0.5) * spacing, lat_y + (iy - 0.5) * spacing, lat_z - 0.5 * spacing)
            p2 = (lat_x + (ix - 0.5) * spacing, lat_y + (iy - 0.5) * spacing, lat_z + 0.5 * spacing)
            create_cylinder_segment(f"{ASSET_ID}_Bond_Z_{ix}_{iy}", p1, p2, 0.0004, bond_mat, collection)

    for ix in range(2):
        for iz in range(2):
            p1 = (lat_x + (ix - 0.5) * spacing, lat_y - 0.5 * spacing, lat_z + (iz - 0.5) * spacing)
            p2 = (lat_x + (ix - 0.5) * spacing, lat_y + 0.5 * spacing, lat_z + (iz - 0.5) * spacing)
            create_cylinder_segment(f"{ASSET_ID}_Bond_Y_{ix}_{iz}", p1, p2, 0.0004, bond_mat, collection)

    for iy in range(2):
        for iz in range(2):
            p1 = (lat_x - 0.5 * spacing, lat_y + (iy - 0.5) * spacing, lat_z + (iz - 0.5) * spacing)
            p2 = (lat_x + 0.5 * spacing, lat_y + (iy - 0.5) * spacing, lat_z + (iz - 0.5) * spacing)
            create_cylinder_segment(f"{ASSET_ID}_Bond_X_{iy}_{iz}", p1, p2, 0.0004, bond_mat, collection)

    # 4. Educational Plaque
    plq_x = -0.060
    plq_y = -0.005
    plq_rot = (math.radians(12.0), 0.0, math.radians(40.0))
    plq_norm_x = 0.005 * math.sin(math.radians(40.0))
    plq_norm_y = -0.005 * math.cos(math.radians(40.0))

    plaque_base = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Base", "cube", plinth_mat,
        size=(0.095, 0.010, 0.052),
        location=(plq_x, plq_y, 0.026),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Border", "cube", gold_mat,
        size=(0.091, 0.002, 0.048),
        location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.026),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat("mgo-sec-txt", (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(
        f"{ASSET_ID}_Plaque_TitleBar", "cube", txt_mat,
        size=(0.078, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.038),
        rotation_euler=plq_rot
    )
    link_strictly(title_bar, collection)

    line_1 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line1", "cube", dim_mat,
        size=(0.065, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.028),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line2", "cube", mg_ion_mat,
        size=(0.055, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.018),
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

    cam.location = (0.16, -0.22, 0.14)
    cam_target = Vector((0.0, 0.0, 0.012))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new("Key_Light", type="AREA")
    key_light_data.energy = 40.0
    key_light_data.size = 0.35
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.22, -0.18, 0.28)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new("Fill_Light", type="AREA")
    fill_light_data.energy = 18.0
    fill_light_data.size = 0.40
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.22, -0.16, 0.22)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new("Rim_Light", type="POINT")
    rim_light_data.energy = 28.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (0.0, 0.25, 0.22)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Magnesium_Oxide_Full")
    sec_col  = bpy.data.collections.new("Magnesium_Oxide_Detail")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_mgo_full(full_col)
    build_mgo_detail(sec_col)
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

    # Render Preview 1: Magnesium_Oxide_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Magnesium_Oxide_Detail
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.16, -0.22, 0.15)
    cam_target = Vector((0.0, 0.0, 0.020))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
