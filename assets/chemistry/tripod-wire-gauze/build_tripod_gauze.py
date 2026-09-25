"""
build_tripod_gauze.py — NCERT Class 10 High-Fidelity Tripod Stand with Wire Gauze & China Dish
Dual collections:
  - Tripod_Gauze_Full: Assembled cast iron tripod, nichrome wire gauze with ceramic heat pad, china dish with oxidized copper powder
  - Tripod_Gauze_Section: 180° cutaway of china dish and ceramic pad showing the unoxidized copper core and surface CuO crust
"""

import sys
from pathlib import Path
import math
import shutil
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "tripod-wire-gauze"

COLOR_CAST_IRON   = (0.12, 0.13, 0.15)
COLOR_GAUZE_MESH  = (0.70, 0.72, 0.75)
COLOR_CERAMIC_PAD = (0.92, 0.90, 0.85)
COLOR_PORCELAIN   = (0.96, 0.96, 0.98)
COLOR_COPPER_RAW  = (0.75, 0.35, 0.18) # Elemental reddish copper
COLOR_COPPER_OX   = (0.10, 0.10, 0.11) # Black CuO crust
COLOR_PLINTH      = (0.16, 0.18, 0.22)
COLOR_GOLD        = (0.85, 0.68, 0.22)
COLOR_CYAN_DIM    = (0.20, 0.80, 0.95)


def link_strictly(obj, target_collection):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target_collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_cylinder_segment(name, p1, p2, radius, material, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    disp = p2 - p1
    length = disp.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = Vector((0, 0, 1)).rotation_difference(disp).to_euler()
    obj = kit.primitive_object(
        name, "cylinder", material,
        size=(radius * 2, radius * 2, length),
        location=mid, rotation_euler=rot
    )
    link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# BUILD TRIPOD FULL
# -----------------------------------------------------------------------------
def build_tripod_full(collection):
    iron_mat    = kit.add_material("tf-iron", COLOR_CAST_IRON, metallic=0.72, roughness=0.52)
    gauze_mat   = kit.add_material("tf-gauze", COLOR_GAUZE_MESH, metallic=0.75, roughness=0.35)
    ceramic_mat = kit.add_material("tf-ceramic", COLOR_CERAMIC_PAD, metallic=0.04, roughness=0.85)
    dish_mat    = kit.add_material("tf-porcelain", COLOR_PORCELAIN, metallic=0.05, roughness=0.15)
    cu_raw_mat  = kit.add_machined_metal_material("tf-cu-raw", COLOR_COPPER_RAW, metallic=0.85, roughness=0.45)
    cu_ox_mat   = kit.add_material("tf-cu-ox", COLOR_COPPER_OX, metallic=0.15, roughness=0.85)
    plinth_mat  = kit.add_material("tf-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.280, 0.280, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Triangular/Circular Cast-Iron Tripod Ring (z = 0.160m)
    ring_z = 0.160
    ring_r_outer = 0.056
    ring_r_inner = 0.042
    ring_h = 0.012
    ring_profile = [
        (ring_r_inner, ring_z - ring_h / 2),
        (ring_r_outer, ring_z - ring_h / 2),
        (ring_r_outer, ring_z + ring_h / 2),
        (ring_r_inner, ring_z + ring_h / 2),
        (ring_r_inner, ring_z - ring_h / 2)
    ]
    ring = kit.lathe_object(f"{ASSET_ID}_Ring", ring_profile, segments=64, material=iron_mat)
    link_strictly(ring, collection)

    # 3. Three Splayed Steel Legs (at 0°, 120°, 240°)
    # Top leg attachment at r = 0.050, z = 0.155; foot at r = 0.082, z = 0.000
    for i in range(3):
        theta = 2.0 * math.pi * i / 3.0
        top_pos = Vector((0.050 * math.cos(theta), 0.050 * math.sin(theta), ring_z - 0.005))
        btm_pos = Vector((0.084 * math.cos(theta), 0.084 * math.sin(theta), 0.003))

        leg = create_cylinder_segment(f"{ASSET_ID}_Leg_{i}", top_pos, btm_pos, 0.0045, iron_mat, collection)

        # Anti-slip rubber foot at bottom
        foot = kit.primitive_object(
            f"{ASSET_ID}_Foot_{i}", "cylinder", iron_mat,
            size=(0.012, 0.012, 0.006),
            location=btm_pos
        )
        link_strictly(foot, collection)

    # 4. Nichrome Wire Gauze Sheet (125mm x 125mm x 2mm at z = ring_z + ring_h / 2 + 0.001)
    gauze_z = ring_z + ring_h / 2 + 0.001
    gauze = kit.primitive_object(
        f"{ASSET_ID}_Wire_Gauze", "cube", gauze_mat,
        size=(0.125, 0.125, 0.002),
        location=(0.0, 0.0, gauze_z)
    )
    link_strictly(gauze, collection)

    # Ceramic Center Heat-Distribution Disc (diameter 76mm, height 3mm)
    pad_z = gauze_z + 0.002
    pad = kit.primitive_object(
        f"{ASSET_ID}_Ceramic_Pad", "cylinder", ceramic_mat,
        size=(0.076, 0.076, 0.003),
        location=(0.0, 0.0, pad_z)
    )
    link_strictly(pad, collection)

    # 5. Porcelain Evaporating Dish (China Dish) resting on ceramic pad
    dish_base_z = pad_z + 0.0015
    dish_profile = [
        (0.000, dish_base_z),
        (0.024, dish_base_z),
        (0.040, dish_base_z + 0.012),
        (0.046, dish_base_z + 0.025),
        (0.048, dish_base_z + 0.028), # Rim apex
        (0.045, dish_base_z + 0.028), # Rim inner bevel
        (0.038, dish_base_z + 0.014),
        (0.022, dish_base_z + 0.003),
        (0.000, dish_base_z + 0.003)  # Inner floor
    ]
    dish = kit.lathe_object(f"{ASSET_ID}_China_Dish", dish_profile, segments=64, material=dish_mat)
    link_strictly(dish, collection)

    # 6. Copper Powder Mound (Mound of Cu in china dish)
    # Reddish base layer + thin black surface crust (CuO)
    powder_base_z = dish_base_z + 0.003
    powder_core = kit.primitive_object(
        f"{ASSET_ID}_Copper_Core", "uv_sphere", cu_raw_mat,
        size=(0.038, 0.038, 0.010),
        location=(0.0, 0.0, powder_base_z + 0.004)
    )
    link_strictly(powder_core, collection)

    powder_crust = kit.primitive_object(
        f"{ASSET_ID}_Copper_Oxide_Crust", "uv_sphere", cu_ox_mat,
        size=(0.039, 0.039, 0.011),
        location=(0.0, 0.0, powder_base_z + 0.005)
    )
    link_strictly(powder_crust, collection)

    print("Built Tripod_Gauze_Full successfully.")


# -----------------------------------------------------------------------------
# BUILD TRIPOD SECTION (Thermal Dispersion & Reaction Layer Cutaway)
# -----------------------------------------------------------------------------
def build_tripod_section(collection):
    iron_mat    = kit.add_material("sec-tg-iron", COLOR_CAST_IRON, metallic=0.72, roughness=0.52)
    gauze_mat   = kit.add_material("sec-tg-gauze", COLOR_GAUZE_MESH, metallic=0.75, roughness=0.35)
    ceramic_mat = kit.add_material("sec-tg-ceramic", COLOR_CERAMIC_PAD, metallic=0.04, roughness=0.85)
    dish_mat    = kit.add_material("sec-tg-porcelain", COLOR_PORCELAIN, metallic=0.05, roughness=0.15)
    cu_raw_mat  = kit.add_machined_metal_material("sec-tg-cu-raw", COLOR_COPPER_RAW, metallic=0.85, roughness=0.45)
    cu_ox_mat   = kit.add_material("sec-tg-cu-ox", COLOR_COPPER_OX, metallic=0.15, roughness=0.85)
    plinth_mat  = kit.add_material("sec-tg-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat    = kit.add_machined_metal_material("sec-tg-gold", COLOR_GOLD, metallic=0.92, roughness=0.20)
    dim_mat     = kit.add_material("sec-tg-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)
    plaque_bg   = kit.add_material("sec-tg-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Macro Plinth
    plinth = kit.primitive_object(
        "Sec_Plinth", "cube", plinth_mat,
        size=(0.280, 0.280, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    ring_z = 0.160
    ring_h = 0.012
    gauze_z = ring_z + ring_h / 2 + 0.001
    pad_z = gauze_z + 0.002
    dish_base_z = pad_z + 0.0015

    # 2. Half Wire Gauze & Ceramic Pad
    half_gauze = kit.primitive_object(
        "Sec_Gauze_Half", "cube", gauze_mat,
        size=(0.125, 0.0625, 0.002),
        location=(0.0, 0.03125, gauze_z)
    )
    link_strictly(half_gauze, collection)

    half_pad = kit.primitive_object(
        "Sec_Ceramic_Pad_Half", "cylinder", ceramic_mat,
        size=(0.076, 0.076, 0.003),
        location=(0.0, 0.0, pad_z)
    )
    # Clip half pad in Y
    link_strictly(half_pad, collection)

    # 3. 180° Cutaway Porcelain China Dish
    dish_profile = [
        (0.000, dish_base_z),
        (0.024, dish_base_z),
        (0.040, dish_base_z + 0.012),
        (0.046, dish_base_z + 0.025),
        (0.048, dish_base_z + 0.028),
        (0.045, dish_base_z + 0.028),
        (0.038, dish_base_z + 0.014),
        (0.022, dish_base_z + 0.003),
        (0.000, dish_base_z + 0.003)
    ]
    bm_dish = bmesh.new()
    segments = 32
    rings = []
    for r_pt, z_pt in dish_profile:
        ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm_dish.verts.new((x, y, z_pt)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for s in range(segments):
            bm_dish.faces.new([rings[i][s], rings[i+1][s], rings[i+1][s+1], rings[i][s+1]])

    bm_dish.faces.new([rings[i][0] for i in range(len(rings))])
    bm_dish.faces.new([rings[i][segments] for i in range(len(rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_dish, faces=bm_dish.faces)
    mesh_dish = bpy.data.meshes.new("Sec_Dish_Mesh")
    bm_dish.to_mesh(mesh_dish)
    bm_dish.free()

    obj_dish = bpy.data.objects.new("Sec_Dish_Cutaway", mesh_dish)
    bpy.context.collection.objects.link(obj_dish)
    obj_dish.data.materials.append(dish_mat)
    link_strictly(obj_dish, collection)

    # 4. Cross-Section Reaction Layers: Unoxidized Cu core underneath CuO crust
    powder_base_z = dish_base_z + 0.003
    core_cut = kit.primitive_object(
        "Sec_Cu_Core_Cut", "uv_sphere", cu_raw_mat,
        size=(0.036, 0.018, 0.010),
        location=(0.0, 0.009, powder_base_z + 0.004)
    )
    link_strictly(core_cut, collection)

    crust_cut = kit.primitive_object(
        "Sec_CuO_Crust_Cut", "uv_sphere", cu_ox_mat,
        size=(0.038, 0.019, 0.012),
        location=(0.0, 0.0095, powder_base_z + 0.005)
    )
    link_strictly(crust_cut, collection)

    # 5. Dimension Calipers
    create_cylinder_segment("Sec_Caliper_Dish_Dia", (-0.048, 0.0, dish_base_z + 0.035), (0.048, 0.0, dish_base_z + 0.035), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_Gauze_W", (-0.0625, 0.0, gauze_z - 0.010), (0.0625, 0.0, gauze_z - 0.010), 0.0006, dim_mat, collection)

    # 6. Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.200, 0.006, 0.054),
        location=(0.0, -0.068, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.204, 0.004, 0.058),
        location=(0.0, -0.068, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    for dx in [-0.075, 0.075]:
        leg = kit.primitive_object(
            f"Sec_Plaque_Leg_{dx}", "cylinder", gold_mat,
            size=(0.003, 0.003, 0.024),
            location=(dx, -0.060, 0.012)
        )
        link_strictly(leg, collection)

    title_strip = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.170, 0.001, 0.008),
        location=(0.0, -0.070, 0.038),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(title_strip, collection)

    sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.140, 0.001, 0.004),
        location=(0.0, -0.069, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub1, collection)

    sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", gold_mat,
        size=(0.155, 0.001, 0.004),
        location=(0.0, -0.068, 0.014),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub2, collection)

    print("Built Tripod_Gauze_Section successfully.")


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING RIG
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("Tripod_Camera")
    cam_data.lens = 45.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("Tripod_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Studio elevated angle capturing tripod stand, china dish and powder
    cam_obj.location = (0.28, -0.34, 0.30)
    cam_target = Vector((0.0, 0.0, 0.150))
    cam_dir = cam_target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting Rig
    key_light_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_light_data.energy = 5.0
    key_light_data.size = 0.40
    key_light_data.color = (1.0, 0.96, 0.92)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.30, -0.30, 0.38)
    key_dir = cam_target - key_light.location
    key_light.rotation_euler = key_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_light_data.energy = 2.0
    fill_light_data.size = 0.50
    fill_light_data.color = (0.85, 0.92, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.30, -0.22, 0.22)
    fill_dir = cam_target - fill_light.location
    fill_light.rotation_euler = fill_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_light_data.energy = 3.5
    rim_light_data.size = 0.35
    rim_light_data.color = (0.80, 0.90, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (-0.18, 0.32, 0.32)
    rim_dir = cam_target - rim_light.location
    rim_light.rotation_euler = rim_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Tripod_Gauze_Full")
    sec_col  = bpy.data.collections.new("Tripod_Gauze_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_tripod_full(full_col)
    build_tripod_section(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False
    kit.export_glb(out_dir / f"{ASSET_ID}.glb")

    viewer_dest = Path("/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets") / f"{ASSET_ID}.glb"
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f"{ASSET_ID}.glb", viewer_dest)
        print(f"Synced GLB to: {viewer_dest}")

    # Render Preview 1: Tripod_Gauze_Full
    kit.configure_render(width=1280, height=720, samples=14)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Tripod_Gauze_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.24, -0.30, 0.22)
    cam_target = Vector((0.0, 0.0, 0.150))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
