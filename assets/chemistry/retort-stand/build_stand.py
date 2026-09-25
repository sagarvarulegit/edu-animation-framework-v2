"""
build_stand.py — NCERT Class 9-12 High-Fidelity Retort Stand with Bosshead & 3-Prong Clamp
Dual collections:
  - Retort_Stand_Full: Assembled heavy stand with support rod, bosshead, articulated 3-prong clamp with silicone sleeves gripping a test tube
  - Retort_Stand_Detail: Engineering macro view of the dual V-groove bosshead and clamp articulation mechanics with plaque
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

ASSET_ID = "retort-stand"

COLOR_CAST_IRON   = (0.10, 0.11, 0.13)
COLOR_CHROME      = (0.86, 0.88, 0.90)
COLOR_BOSSHEAD    = (0.42, 0.45, 0.48)
COLOR_BRASS       = (0.86, 0.68, 0.22)
COLOR_RUBBER_RED  = (0.82, 0.18, 0.14)
COLOR_GLASS       = (0.92, 0.96, 0.98)
COLOR_CUSO4       = (0.12, 0.45, 0.95)
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
# BUILD RETORT STAND FULL
# -----------------------------------------------------------------------------
def build_stand_full(collection):
    iron_mat   = kit.add_material("sf-iron", COLOR_CAST_IRON, metallic=0.72, roughness=0.48)
    chrome_mat = kit.add_machined_metal_material("sf-chrome", COLOR_CHROME, metallic=0.95, roughness=0.14)
    boss_mat   = kit.add_machined_metal_material("sf-boss", COLOR_BOSSHEAD, metallic=0.88, roughness=0.28)
    brass_mat  = kit.add_machined_metal_material("sf-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    rubber_mat = kit.add_material("sf-rubber", COLOR_RUBBER_RED, metallic=0.0, roughness=0.55)
    glass_mat  = kit.add_glass_material("sf-glass", COLOR_GLASS, ior=1.52, roughness=0.012)
    liq_mat    = kit.add_glass_material("sf-liquid", COLOR_CUSO4, ior=1.333, roughness=0.008)
    plinth_mat = kit.add_material("sf-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.320, 0.240, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Heavy Cast-Iron Base Plate (200mm x 125mm x 14mm, offset rod mount)
    # Rod mounted at (0.055, 0.0, 0.0)
    base_plate = kit.primitive_object(
        f"{ASSET_ID}_Base_Plate", "cube", iron_mat,
        size=(0.200, 0.125, 0.014),
        location=(0.0, 0.0, 0.007)
    )
    link_strictly(base_plate, collection)

    # Rubber feet under base plate
    for dx in [-0.088, 0.088]:
        for dy in [-0.052, 0.052]:
            foot = kit.primitive_object(
                f"{ASSET_ID}_Foot_{dx}_{dy}", "cylinder", iron_mat,
                size=(0.012, 0.012, 0.004),
                location=(dx, dy, -0.002)
            )
            link_strictly(foot, collection)

    # Tapped Rod Socket Boss Collar (at x = 0.065, y = 0.0)
    boss_collar = kit.primitive_object(
        f"{ASSET_ID}_Rod_Boss", "cylinder", iron_mat,
        size=(0.024, 0.024, 0.018),
        location=(0.065, 0.0, 0.018)
    )
    link_strictly(boss_collar, collection)

    # 3. Precision Chrome Steel Vertical Support Rod (diameter 10mm, height 480mm)
    rod_h = 0.480
    rod_x = 0.065
    support_rod = kit.primitive_object(
        f"{ASSET_ID}_Support_Rod", "cylinder", chrome_mat,
        size=(0.010, 0.010, rod_h),
        location=(rod_x, 0.0, rod_h / 2)
    )
    link_strictly(support_rod, collection)

    # Top rounded cap of support rod
    rod_cap = kit.primitive_object(
        f"{ASSET_ID}_Rod_Cap", "uv_sphere", chrome_mat,
        size=(0.010, 0.010, 0.010),
        location=(rod_x, 0.0, rod_h)
    )
    link_strictly(rod_cap, collection)

    # 4. Die-Cast Bosshead Clamp (Right-Angle clamp located at z = 0.280m)
    clamp_z = 0.280
    boss_body = kit.primitive_object(
        f"{ASSET_ID}_Bosshead_Body", "cube", boss_mat,
        size=(0.034, 0.030, 0.034),
        location=(rod_x, 0.0, clamp_z)
    )
    link_strictly(boss_body, collection)

    # Bosshead T-Screw 1 (Vertical rod clamp screw pointing +X)
    create_cylinder_segment(f"{ASSET_ID}_TScrew1_Stem", (rod_x + 0.017, 0.0, clamp_z), (rod_x + 0.032, 0.0, clamp_z), 0.0035, brass_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_TScrew1_Bar", (rod_x + 0.032, -0.016, clamp_z), (rod_x + 0.032, 0.016, clamp_z), 0.0030, brass_mat, collection)

    # Bosshead T-Screw 2 (Horizontal clamp rod screw pointing +Y)
    create_cylinder_segment(f"{ASSET_ID}_TScrew2_Stem", (rod_x, 0.015, clamp_z), (rod_x, 0.030, clamp_z), 0.0035, brass_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_TScrew2_Bar", (rod_x - 0.016, 0.030, clamp_z), (rod_x + 0.016, 0.030, clamp_z), 0.0030, brass_mat, collection)

    # 5. Articulated 3-Prong Utility Clamp
    # Clamp shaft extending horizontally along -X towards center of base
    clamp_shaft_len = 0.135
    clamp_shaft_start_x = rod_x - 0.017
    clamp_shaft_end_x = clamp_shaft_start_x - clamp_shaft_len
    create_cylinder_segment(
        f"{ASSET_ID}_Clamp_Shaft",
        (clamp_shaft_start_x, 0.0, clamp_z),
        (clamp_shaft_end_x, 0.0, clamp_z),
        0.0040, boss_mat, collection
    )

    # Swivel knuckle joint
    knuckle = kit.primitive_object(
        f"{ASSET_ID}_Knuckle", "uv_sphere", boss_mat,
        size=(0.014, 0.014, 0.014),
        location=(clamp_shaft_end_x, 0.0, clamp_z)
    )
    link_strictly(knuckle, collection)

    # Scissor clamp hub & brass adjustment nut
    hub = kit.primitive_object(
        f"{ASSET_ID}_Clamp_Hub", "cube", boss_mat,
        size=(0.018, 0.022, 0.016),
        location=(clamp_shaft_end_x - 0.014, 0.0, clamp_z)
    )
    link_strictly(hub, collection)

    nut = kit.primitive_object(
        f"{ASSET_ID}_Clamp_Nut", "cylinder", brass_mat,
        size=(0.011, 0.011, 0.008),
        location=(clamp_shaft_end_x - 0.014, 0.0, clamp_z + 0.012),
        rotation_euler=(0.0, 0.0, 0.0)
    )
    link_strictly(nut, collection)

    # 3 Curved Fingers: 1 upper, 2 lower
    # Jaws center at x = clamp_shaft_end_x - 0.045
    jaw_root_x = clamp_shaft_end_x - 0.023
    jaw_tip_x = jaw_root_x - 0.048
    test_tube_x = (jaw_root_x + jaw_tip_x) / 2.0

    # Upper finger (centered in Y, above test tube)
    create_cylinder_segment(f"{ASSET_ID}_Jaw_Upper_Arm", (jaw_root_x, 0.0, clamp_z + 0.006), (jaw_tip_x, 0.0, clamp_z + 0.012), 0.003, boss_mat, collection)
    # Upper finger silicone rubber sleeve
    create_cylinder_segment(f"{ASSET_ID}_Sleeve_Upper", (test_tube_x + 0.016, 0.0, clamp_z + 0.010), (test_tube_x - 0.016, 0.0, clamp_z + 0.012), 0.0045, rubber_mat, collection)

    # Lower finger Left
    create_cylinder_segment(f"{ASSET_ID}_Jaw_Lower_L_Arm", (jaw_root_x, -0.008, clamp_z - 0.006), (jaw_tip_x, -0.012, clamp_z - 0.010), 0.003, boss_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Sleeve_Lower_L", (test_tube_x + 0.016, -0.009, clamp_z - 0.008), (test_tube_x - 0.016, -0.012, clamp_z - 0.010), 0.0045, rubber_mat, collection)

    # Lower finger Right
    create_cylinder_segment(f"{ASSET_ID}_Jaw_Lower_R_Arm", (jaw_root_x, 0.008, clamp_z - 0.006), (jaw_tip_x, 0.012, clamp_z - 0.010), 0.003, boss_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Sleeve_Lower_R", (test_tube_x + 0.016, 0.009, clamp_z - 0.008), (test_tube_x - 0.016, 0.012, clamp_z - 0.010), 0.0045, rubber_mat, collection)

    # 6. Clamped Laboratory Test Tube & CuSO4 Solution
    # Test tube: outer diameter 18mm, height 140mm, positioned vertically at (test_tube_x, 0.0)
    tt_r = 0.009
    tt_h = 0.140
    tt_bottom_z = clamp_z - 0.070
    tt_top_z = tt_bottom_z + tt_h

    # Hemispherical bottom + cylinder body
    tt_profile = []
    num_pts = 12
    for i in range(num_pts + 1):
        ang = (math.pi / 2) * (i / num_pts)
        r = tt_r * math.sin(ang)
        z = tt_bottom_z + tt_r * (1.0 - math.cos(ang))
        tt_profile.append((r, z))
    tt_profile.extend([
        (tt_r, tt_top_z - 0.005),
        (tt_r + 0.0015, tt_top_z - 0.001), # Flared rim
        (tt_r + 0.0015, tt_top_z),
        (tt_r - 0.0010, tt_top_z + 0.0006),
        (tt_r - 0.0012, tt_top_z - 0.005),
        (tt_r - 0.0012, tt_bottom_z + tt_r)
    ])
    for i in range(num_pts, -1, -1):
        ang = (math.pi / 2) * (i / num_pts)
        r = (tt_r - 0.0012) * math.sin(ang)
        z = tt_bottom_z + 0.0015 + (tt_r - 0.0012) * (1.0 - math.cos(ang))
        tt_profile.append((r, z))

    tt_obj = kit.lathe_object(f"{ASSET_ID}_Test_Tube", tt_profile, segments=48, material=glass_mat)
    tt_obj.location.x = test_tube_x
    link_strictly(tt_obj, collection)

    # Aqueous solution inside test tube (height 60mm)
    liq_h = 0.060
    liq_profile = []
    for i in range(num_pts + 1):
        ang = (math.pi / 2) * (i / num_pts)
        r = (tt_r - 0.0014) * math.sin(ang)
        z = tt_bottom_z + 0.0018 + (tt_r - 0.0014) * (1.0 - math.cos(ang))
        liq_profile.append((r, z))
    liq_profile.extend([
        (tt_r - 0.0014, tt_bottom_z + liq_h - 0.001),
        (tt_r - 0.0022, tt_bottom_z + liq_h + 0.0006),
        (0.0, tt_bottom_z + liq_h)
    ])
    liq_obj = kit.lathe_object(f"{ASSET_ID}_Liquid", liq_profile, segments=48, material=liq_mat)
    liq_obj.location.x = test_tube_x
    link_strictly(liq_obj, collection)

    print("Built Retort_Stand_Full successfully.")


# -----------------------------------------------------------------------------
# BUILD RETORT STAND DETAIL (Bosshead & Clamp Articulation Mechanics)
# -----------------------------------------------------------------------------
def build_stand_detail(collection):
    iron_mat   = kit.add_material("sec-s-iron", COLOR_CAST_IRON, metallic=0.72, roughness=0.48)
    chrome_mat = kit.add_machined_metal_material("sec-s-chrome", COLOR_CHROME, metallic=0.95, roughness=0.14)
    boss_mat   = kit.add_machined_metal_material("sec-s-boss", COLOR_BOSSHEAD, metallic=0.88, roughness=0.28)
    brass_mat  = kit.add_machined_metal_material("sec-s-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    rubber_mat = kit.add_material("sec-s-rubber", COLOR_RUBBER_RED, metallic=0.0, roughness=0.55)
    plinth_mat = kit.add_material("sec-s-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("sec-s-gold", COLOR_GOLD, metallic=0.92, roughness=0.20)
    dim_mat    = kit.add_material("sec-s-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)
    plaque_bg  = kit.add_material("sec-s-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Macro Plinth
    plinth = kit.primitive_object(
        "Sec_Plinth", "cube", plinth_mat,
        size=(0.280, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Section of Vertical Chrome Rod with etched graduation rings
    rod_sec = kit.primitive_object(
        "Sec_Rod_Section", "cylinder", chrome_mat,
        size=(0.010, 0.010, 0.160),
        location=(0.065, 0.0, 0.080)
    )
    link_strictly(rod_sec, collection)

    # Graduation marks along rod (rings every 20mm)
    for gz in [0.030, 0.050, 0.070, 0.090, 0.110, 0.130]:
        ring = kit.primitive_object(
            f"Sec_Grad_{gz}", "cylinder", dim_mat,
            size=(0.0104, 0.0104, 0.0008),
            location=(0.065, 0.0, gz)
        )
        link_strictly(ring, collection)

    # 3. Cutaway Bosshead Body revealing internal 90° V-Grooves
    # Half-cut bosshead (split along Y=0)
    boss_cut = kit.primitive_object(
        "Sec_Bosshead_Cutaway", "cube", boss_mat,
        size=(0.034, 0.015, 0.034),
        location=(0.065, 0.0075, 0.080)
    )
    link_strictly(boss_cut, collection)

    # Dual brass clamping T-screws
    create_cylinder_segment("Sec_TScrew_V_Stem", (0.065 + 0.017, 0.0, 0.080), (0.065 + 0.034, 0.0, 0.080), 0.0035, brass_mat, collection)
    create_cylinder_segment("Sec_TScrew_V_Bar", (0.065 + 0.034, -0.016, 0.080), (0.065 + 0.034, 0.016, 0.080), 0.0030, brass_mat, collection)

    # 4. Clamp Extension Shaft & Swivel Joint Detail
    create_cylinder_segment("Sec_Shaft", (0.065 - 0.017, 0.0, 0.080), (-0.035, 0.0, 0.080), 0.0040, boss_mat, collection)

    knuckle = kit.primitive_object(
        "Sec_Knuckle", "uv_sphere", boss_mat,
        size=(0.016, 0.016, 0.016),
        location=(-0.035, 0.0, 0.080)
    )
    link_strictly(knuckle, collection)

    swivel_screw = kit.primitive_object(
        "Sec_Swivel_Nut", "cylinder", brass_mat,
        size=(0.012, 0.012, 0.008),
        location=(-0.035, 0.0, 0.092)
    )
    link_strictly(swivel_screw, collection)

    # 5. Articulated Clamp Jaws with Cutaway Rubber Sleeves
    create_cylinder_segment("Sec_Jaw_Top", (-0.045, 0.0, 0.086), (-0.088, 0.0, 0.092), 0.003, boss_mat, collection)
    create_cylinder_segment("Sec_Jaw_Btm", (-0.045, 0.0, 0.074), (-0.088, 0.0, 0.068), 0.003, boss_mat, collection)

    # Silicone rubber sleeves
    create_cylinder_segment("Sec_Sleeve_T", (-0.060, 0.0, 0.088), (-0.086, 0.0, 0.092), 0.0048, rubber_mat, collection)
    create_cylinder_segment("Sec_Sleeve_B", (-0.060, 0.0, 0.072), (-0.086, 0.0, 0.068), 0.0048, rubber_mat, collection)

    # 6. Dimension Calipers
    create_cylinder_segment("Sec_Caliper_Rod", (0.085, 0.0, 0.020), (0.085, 0.0, 0.140), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_Clamp", (-0.035, 0.0, 0.105), (0.065, 0.0, 0.105), 0.0006, dim_mat, collection)

    # 7. Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.200, 0.006, 0.054),
        location=(0.0, -0.065, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.204, 0.004, 0.058),
        location=(0.0, -0.065, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    for dx in [-0.075, 0.075]:
        leg = kit.primitive_object(
            f"Sec_Plaque_Leg_{dx}", "cylinder", gold_mat,
            size=(0.003, 0.003, 0.024),
            location=(dx, -0.058, 0.012)
        )
        link_strictly(leg, collection)

    title_strip = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.170, 0.001, 0.008),
        location=(0.0, -0.067, 0.038),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(title_strip, collection)

    sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.140, 0.001, 0.004),
        location=(0.0, -0.066, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub1, collection)

    sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", gold_mat,
        size=(0.155, 0.001, 0.004),
        location=(0.0, -0.065, 0.014),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub2, collection)

    print("Built Retort_Stand_Detail successfully.")


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING RIG
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("Stand_Camera")
    cam_data.lens = 38.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("Stand_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Studio 3/4 elevated angle capturing full stand and clamped vessel
    cam_obj.location = (0.58, -0.68, 0.38)
    cam_target = Vector((0.0, 0.0, 0.220))
    cam_dir = cam_target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting Rig
    key_light_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_light_data.energy = 6.0
    key_light_data.size = 0.50
    key_light_data.color = (1.0, 0.96, 0.92)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.35, -0.35, 0.45)
    key_dir = cam_target - key_light.location
    key_light.rotation_euler = key_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_light_data.energy = 2.5
    fill_light_data.size = 0.60
    fill_light_data.color = (0.88, 0.94, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.35, -0.25, 0.30)
    fill_dir = cam_target - fill_light.location
    fill_light.rotation_euler = fill_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_light_data.energy = 4.0
    rim_light_data.size = 0.45
    rim_light_data.color = (0.82, 0.90, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (-0.20, 0.38, 0.40)
    rim_dir = cam_target - rim_light.location
    rim_light.rotation_euler = rim_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Retort_Stand_Full")
    sec_col  = bpy.data.collections.new("Retort_Stand_Detail")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_stand_full(full_col)
    build_stand_detail(sec_col)
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

    # Render Preview 1: Retort_Stand_Full
    kit.configure_render(width=1280, height=720, samples=14)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Retort_Stand_Detail
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    # Focus camera on detail collection
    cam = bpy.context.scene.camera
    cam.location = (0.22, -0.26, 0.16)
    cam_target = Vector((0.0, 0.0, 0.080))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
