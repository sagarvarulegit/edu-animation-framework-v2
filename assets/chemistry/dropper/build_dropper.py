"""
build_dropper.py — NCERT Class 9-12 High-Fidelity Pasteur Dropper / Pipette
Dual collections:
  - Dropper_Full: Assembled borosilicate glass pipette with graduation marks, liquid column, forming capillary droplet, ribbed silicone squeeze bulb, suspended in lab pipette stand
  - Dropper_Section: 180° longitudinal cutaway section exposing glass wall thickness, capillary bore, bulb hollow suction chamber, fluid meniscus, and annotated plaque
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

ASSET_ID = "dropper"

# Calibrated Laboratory Palette
COLOR_GLASS         = (0.95, 0.98, 1.00)     # Borosilicate glass (IOR 1.52)
COLOR_RUBBER_BLUE   = (0.05, 0.18, 0.62)     # Vivid molded silicone rubber bulb
COLOR_LIQUID_REAGENT= (0.88, 0.06, 0.18)     # Crimson reagent solution (IOR 1.333)
COLOR_GRADUATION    = (0.96, 0.96, 0.98)     # White ceramic graduation enamel
COLOR_STAND_BASE    = (0.12, 0.13, 0.16)     # Dark slate laboratory pedestal
COLOR_CHROME        = (0.85, 0.88, 0.92)     # Polished laboratory stand rod
COLOR_ACRYLIC       = (0.92, 0.96, 0.98)     # Clear support fork ring
COLOR_GOLD          = (0.90, 0.75, 0.22)     # Plaque frame
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)     # Dimension caliper
COLOR_PRESSURE_ARR  = (0.15, 0.75, 0.95)     # Pressure vector arrows


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
# LATHE HELPERS FOR FULL & 180° SECTION
# -----------------------------------------------------------------------------
def build_lathe_full(name, profile_points, segments=48, mat=None, collection=None):
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
    # Revolve from -pi/2 to +pi/2
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
            bm.faces.new([rings[i][s], rings[i+1][s], rings[i+1][next_s], rings[i][next_s]]) if False else None
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
# GEOMETRY PROFILES
# -----------------------------------------------------------------------------
def get_glass_profile():
    prof = [
        (0.0025, 0.150),
        (0.0042, 0.150),
        (0.0044, 0.148),
        (0.0036, 0.145),
        (0.0036, 0.065),
        (0.0014, 0.045),
        (0.0014, 0.003),
        (0.0011, 0.000),
        (0.0006, 0.000),
        (0.0006, 0.045),
        (0.0025, 0.065),
        (0.0025, 0.148),
        (0.0025, 0.150)
    ]
    return prof


def get_rubber_bulb_profile():
    prof = []
    prof.append((0.0038, 0.138))
    prof.append((0.0052, 0.139))
    prof.append((0.0052, 0.148))
    prof.append((0.0070, 0.152))
    prof.append((0.0085, 0.154))
    prof.append((0.0080, 0.156))
    prof.append((0.0110, 0.160))
    prof.append((0.0125, 0.163))
    prof.append((0.0120, 0.165))
    prof.append((0.0140, 0.170))
    prof.append((0.0135, 0.178))
    prof.append((0.0090, 0.185))
    prof.append((0.0000, 0.188))
    
    # Inner wall
    prof.append((0.0000, 0.186))
    prof.append((0.0072, 0.183))
    prof.append((0.0118, 0.176))
    prof.append((0.0122, 0.170))
    prof.append((0.0095, 0.162))
    prof.append((0.0065, 0.154))
    prof.append((0.0044, 0.150))
    prof.append((0.0035, 0.148))
    prof.append((0.0035, 0.138))
    prof.append((0.0038, 0.138))
    return prof


def get_liquid_profile():
    prof = []
    num_m = 12
    r_men = 0.0024
    for i in range(num_m + 1):
        frac = i / num_m
        r = r_men * (1.0 - frac)
        z = 0.098 - 0.0018 * math.cos(math.pi / 2 * frac)
        prof.append((r, z))
    prof.extend([
        (0.0024, 0.065),
        (0.00058, 0.045),
        (0.00058, 0.000),
        (0.0000, 0.000)
    ])
    return prof


def get_droplet_profile():
    prof = [
        (0.00058, 0.000),
        (0.00075, -0.0008),
        (0.00060, -0.0018),
        (0.00120, -0.0032),
        (0.00140, -0.0045),
        (0.00110, -0.0055),
        (0.0000,  -0.0060)
    ]
    return prof


# -----------------------------------------------------------------------------
# BUILD DROPPER FULL
# -----------------------------------------------------------------------------
def build_dropper_full(collection):
    glass_mat  = kit.add_glass_material("dp-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    rubber_mat = kit.add_material("dp-rubber", COLOR_RUBBER_BLUE, metallic=0.0, roughness=0.38)
    liquid_mat = kit.add_glass_material("dp-liquid", COLOR_LIQUID_REAGENT, ior=1.333, roughness=0.010)
    grad_mat   = kit.add_material("dp-grad", COLOR_GRADUATION, metallic=0.1, roughness=0.30)
    plinth_mat = kit.add_material("dp-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    chrome_mat = kit.add_machined_metal_material("dp-chrome", COLOR_CHROME, metallic=0.96, roughness=0.18)
    acrylic_mat= kit.add_glass_material("dp-acrylic", COLOR_ACRYLIC, ior=1.49, roughness=0.04)

    # 1. Studio Plinth & Laboratory Stand
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.220, 0.160, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    stand_post = kit.primitive_object(
        f"{ASSET_ID}_Stand_Post", "cylinder", chrome_mat,
        size=(0.008, 0.008, 0.190),
        location=(0.0, 0.045, 0.095)
    )
    link_strictly(stand_post, collection)

    support_arm = kit.primitive_object(
        f"{ASSET_ID}_Support_Arm", "cylinder", chrome_mat,
        size=(0.006, 0.006, 0.045),
        location=(0.0, 0.0225, 0.145),
        rotation_euler=(math.radians(90.0), 0.0, 0.0)
    )
    link_strictly(support_arm, collection)

    cradle_fork = kit.primitive_object(
        f"{ASSET_ID}_Cradle_Fork", "cylinder", acrylic_mat,
        size=(0.020, 0.020, 0.006),
        location=(0.0, 0.0, 0.145)
    )
    link_strictly(cradle_fork, collection)

    # 2. Dropper Assembly
    z_elev = 0.018
    pipette = build_lathe_full(f"{ASSET_ID}_Glass_Pipette", get_glass_profile(), segments=48, mat=glass_mat, collection=collection)
    bulb = build_lathe_full(f"{ASSET_ID}_Rubber_Bulb", get_rubber_bulb_profile(), segments=48, mat=rubber_mat, collection=collection)
    liquid = build_lathe_full(f"{ASSET_ID}_Liquid_Column", get_liquid_profile(), segments=48, mat=liquid_mat, collection=collection)
    droplet = build_lathe_full(f"{ASSET_ID}_Pendant_Droplet", get_droplet_profile(), segments=36, mat=liquid_mat, collection=collection)

    for obj in [pipette, bulb, liquid, droplet]:
        obj.location = (0.0, 0.0, z_elev)

    # Graduation Markings
    grad_levels = [0.075, 0.098, 0.120, 0.140]
    for gz in grad_levels:
        ring = kit.primitive_object(
            f"{ASSET_ID}_Grad_Ring_{gz:.3f}", "cylinder", grad_mat,
            size=(0.0073, 0.0073, 0.0006),
            location=(0.0, 0.0, gz + z_elev)
        )
        link_strictly(ring, collection)


# -----------------------------------------------------------------------------
# BUILD DROPPER SECTION (180° Longitudinal Cutaway & Engineering Mechanics)
# -----------------------------------------------------------------------------
def build_dropper_section(collection):
    glass_mat  = kit.add_glass_material("dp-sec-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    rubber_mat = kit.add_material("dp-sec-rubber", COLOR_RUBBER_BLUE, metallic=0.0, roughness=0.38)
    liquid_mat = kit.add_glass_material("dp-sec-liquid", COLOR_LIQUID_REAGENT, ior=1.333, roughness=0.010)
    plinth_mat = kit.add_material("dp-sec-plinth", COLOR_STAND_BASE, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("dp-sec-gold", COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat    = create_emissive_mat("dp-sec-dim", COLOR_CYAN_DIM, strength=10.0)
    arr_mat    = create_emissive_mat("dp-sec-arr", COLOR_PRESSURE_ARR, strength=12.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Sec_Plinth", "cube", plinth_mat,
        size=(0.280, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. 180° Cutaway Models (Revolved from -pi/2 to pi/2, angled by -25° for clear internal 3D depth)
    z_elev = 0.018
    pipette_half = build_lathe_half(f"{ASSET_ID}_Sec_Pipette", get_glass_profile(), segments=36, mat=glass_mat, collection=collection)
    bulb_half = build_lathe_half(f"{ASSET_ID}_Sec_Bulb", get_rubber_bulb_profile(), segments=36, mat=rubber_mat, collection=collection)
    liquid_half = build_lathe_half(f"{ASSET_ID}_Sec_Liquid", get_liquid_profile(), segments=36, mat=liquid_mat, collection=collection)
    droplet_half = build_lathe_half(f"{ASSET_ID}_Sec_Droplet", get_droplet_profile(), segments=24, mat=liquid_mat, collection=collection)

    rot_angle = math.radians(-25.0)
    cos_r = math.cos(rot_angle)
    sin_r = math.sin(rot_angle)
    x_center = 0.030

    for obj in [pipette_half, bulb_half, liquid_half, droplet_half]:
        obj.location = (x_center, 0.0, z_elev)
        obj.rotation_euler = (0.0, 0.0, rot_angle)

    def rot_pt(x_rel, y_rel, z):
        return (x_center + x_rel * cos_r - y_rel * sin_r,
                x_rel * sin_r + y_rel * cos_r,
                z)

    # 3. Dimension Calipers & Mechanics Visualization
    # Capillary bore caliper line (Ø 1.2 mm)
    p_cap_1 = rot_pt(-0.007, 0.0, z_elev + 0.020)
    p_cap_2 = rot_pt(0.007, 0.0, z_elev + 0.020)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Cap_1", p_cap_1, p_cap_2, 0.00025, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Cap_L", rot_pt(-0.007, 0.0, z_elev + 0.016), rot_pt(-0.007, 0.0, z_elev + 0.024), 0.0003, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Cap_R", rot_pt(0.007, 0.0, z_elev + 0.016), rot_pt(0.007, 0.0, z_elev + 0.024), 0.0003, dim_mat, collection)

    # Barrel bore caliper line (Ø 7.2 mm outer, 4.8 mm inner)
    p_bar_1 = rot_pt(-0.013, 0.0, z_elev + 0.110)
    p_bar_2 = rot_pt(0.013, 0.0, z_elev + 0.110)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Bar_1", p_bar_1, p_bar_2, 0.00025, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Bar_L", rot_pt(-0.013, 0.0, z_elev + 0.106), rot_pt(-0.013, 0.0, z_elev + 0.114), 0.0003, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_Bar_R", rot_pt(0.013, 0.0, z_elev + 0.106), rot_pt(0.013, 0.0, z_elev + 0.114), 0.0003, dim_mat, collection)

    # Atmospheric pressure pushing upward at capillary tip
    create_cylinder_segment(f"{ASSET_ID}_Arr_Atm_1", rot_pt(0.0, 0.0, z_elev - 0.014), rot_pt(0.0, 0.0, z_elev - 0.007), 0.0005, arr_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Arr_Atm_L", rot_pt(-0.004, 0.0, z_elev - 0.014), rot_pt(-0.004, 0.0, z_elev - 0.007), 0.0004, arr_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Arr_Atm_R", rot_pt(0.004, 0.0, z_elev - 0.014), rot_pt(0.004, 0.0, z_elev - 0.007), 0.0004, arr_mat, collection)

    # Suction vacuum arrows inside rubber bulb chamber
    create_cylinder_segment(f"{ASSET_ID}_Arr_Vac_1", rot_pt(0.005, 0.0, z_elev + 0.165), rot_pt(0.005, 0.0, z_elev + 0.175), 0.0004, arr_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Arr_Vac_2", rot_pt(-0.005, 0.0, z_elev + 0.165), rot_pt(-0.005, 0.0, z_elev + 0.175), 0.0004, arr_mat, collection)

    # 4. Educational Plaque
    plaque_base = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Base", "cube", plinth_mat,
        size=(0.095, 0.010, 0.060),
        location=(-0.065, -0.010, 0.075),
        rotation_euler=(0.0, 0.0, math.radians(-10.0))
    )
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Border", "cube", gold_mat,
        size=(0.091, 0.002, 0.056),
        location=(-0.065, -0.016, 0.075),
        rotation_euler=(0.0, 0.0, math.radians(-10.0))
    )
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat("dp-sec-txt", (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(
        f"{ASSET_ID}_Plaque_TitleBar", "cube", txt_mat,
        size=(0.078, 0.002, 0.005),
        location=(-0.065, -0.018, 0.092),
        rotation_euler=(0.0, 0.0, math.radians(-10.0))
    )
    link_strictly(title_bar, collection)

    line_1 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line1", "cube", dim_mat,
        size=(0.065, 0.002, 0.003),
        location=(-0.065, -0.018, 0.078),
        rotation_euler=(0.0, 0.0, math.radians(-10.0))
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line2", "cube", arr_mat,
        size=(0.055, 0.002, 0.003),
        location=(-0.065, -0.018, 0.064),
        rotation_euler=(0.0, 0.0, math.radians(-10.0))
    )
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING SETUP
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 38.0
    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Framed to capture the entire vertical pipette, bulb, and stand
    cam.location = (0.28, -0.38, 0.13)
    cam_target = Vector((0.0, 0.0, 0.105))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new("Key_Light", type="AREA")
    key_light_data.energy = 45.0
    key_light_data.size = 0.40
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.28, -0.26, 0.32)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new("Fill_Light", type="AREA")
    fill_light_data.energy = 18.0
    fill_light_data.size = 0.45
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.28, -0.22, 0.24)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new("Rim_Light", type="POINT")
    rim_light_data.energy = 30.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (0.0, 0.30, 0.28)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Dropper_Full")
    sec_col  = bpy.data.collections.new("Dropper_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_dropper_full(full_col)
    build_dropper_section(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB only (select objects in full_col)
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

    # Render Preview 1: Dropper_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Dropper_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.20, -0.38, 0.12)
    cam_target = Vector((0.0, 0.0, 0.105))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
