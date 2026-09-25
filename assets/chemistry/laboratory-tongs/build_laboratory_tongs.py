"""
build_laboratory_tongs.py — NCERT Class 9-12 High-Fidelity Laboratory Tongs
Dual collections:
  - Laboratory_Tongs_Full: Assembled forged stainless steel tongs with ergonomic finger loops, cross-lap pivot rivet, bowed jaws gripping a silvery magnesium ribbon
  - Laboratory_Tongs_Detail: Engineering macro view of the scissor cross-lap pivot and serrated jaw profile with plaque
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

ASSET_ID = "laboratory-tongs"

COLOR_STEEL_SATIN = (0.86, 0.88, 0.90)
COLOR_STEEL_RIVET = (0.75, 0.77, 0.80)
COLOR_MG_RIBBON   = (0.92, 0.94, 0.96)
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
# BUILD TONGS FULL
# -----------------------------------------------------------------------------
def build_tongs_full(collection):
    steel_mat  = kit.add_machined_metal_material("lt-steel", COLOR_STEEL_SATIN, metallic=0.95, roughness=0.20)
    rivet_mat  = kit.add_machined_metal_material("lt-rivet", COLOR_STEEL_RIVET, metallic=0.92, roughness=0.25)
    mg_mat     = kit.add_machined_metal_material("lt-mg-ribbon", COLOR_MG_RIBBON, metallic=0.90, roughness=0.28)
    plinth_mat = kit.add_material("lt-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.300, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    z_work = 0.012 # Resting slightly above plinth

    # 2. Central Pivot Rivet Pin
    rivet = kit.primitive_object(
        f"{ASSET_ID}_Rivet_Pin", "cylinder", rivet_mat,
        size=(0.0065, 0.0065, 0.009),
        location=(0.0, 0.0, z_work)
    )
    link_strictly(rivet, collection)

    rivet_cap_t = kit.primitive_object(
        f"{ASSET_ID}_Rivet_Cap_Top", "uv_sphere", rivet_mat,
        size=(0.008, 0.008, 0.004),
        location=(0.0, 0.0, z_work + 0.0045)
    )
    link_strictly(rivet_cap_t, collection)

    rivet_cap_b = kit.primitive_object(
        f"{ASSET_ID}_Rivet_Cap_Btm", "uv_sphere", rivet_mat,
        size=(0.008, 0.008, 0.004),
        location=(0.0, 0.0, z_work - 0.0045)
    )
    link_strictly(rivet_cap_b, collection)

    # 3. Two Forged Tongs Arms
    # Loop centers at X = -0.100, Y = ±0.025
    for sign in [-1, 1]:
        # Finger loop (torus/annulus)
        loop_r = 0.014
        loop_cx = -0.100
        loop_cy = sign * 0.024
        loop = kit.primitive_object(
            f"{ASSET_ID}_Loop_{sign}", "cylinder", steel_mat,
            size=(loop_r * 2, loop_r * 2, 0.004),
            location=(loop_cx, loop_cy, z_work + sign * 0.0015)
        )
        link_strictly(loop, collection)

        # Inner hole cutout visually represented by dark insert
        inner_hole = kit.primitive_object(
            f"{ASSET_ID}_Loop_Hole_{sign}", "cylinder", plinth_mat,
            size=((loop_r - 0.0035) * 2, (loop_r - 0.0035) * 2, 0.0045),
            location=(loop_cx, loop_cy, z_work + sign * 0.0015)
        )
        link_strictly(inner_hole, collection)

        # Proximal Shank: loop to pivot
        create_cylinder_segment(
            f"{ASSET_ID}_Prox_Shank_{sign}",
            (loop_cx + loop_r * 0.7, loop_cy - sign * 0.004, z_work + sign * 0.0015),
            (0.0, 0.0, z_work + sign * 0.0015),
            0.0024, steel_mat, collection
        )

        # Distal Shank: pivot to bow start (X = 0.035)
        bow_start_x = 0.035
        bow_start_y = sign * 0.005
        create_cylinder_segment(
            f"{ASSET_ID}_Dist_Shank_{sign}",
            (0.0, 0.0, z_work + sign * 0.0015),
            (bow_start_x, bow_start_y, z_work),
            0.0024, steel_mat, collection
        )

        # Bowed Jaw Section: bows outwards to Y = ±0.018 at X = 0.065, returns to Y = ±0.002 at X = 0.095
        bow_mid_x = 0.065
        bow_mid_y = sign * 0.018
        bow_end_x = 0.095
        bow_end_y = sign * 0.0025

        create_cylinder_segment(
            f"{ASSET_ID}_Bow_1_{sign}",
            (bow_start_x, bow_start_y, z_work),
            (bow_mid_x, bow_mid_y, z_work),
            0.0024, steel_mat, collection
        )
        create_cylinder_segment(
            f"{ASSET_ID}_Bow_2_{sign}",
            (bow_mid_x, bow_mid_y, z_work),
            (bow_end_x, bow_end_y, z_work),
            0.0024, steel_mat, collection
        )

        # Gripping Tip: straight parallel jaw tip from X = 0.095 to 0.125
        tip_end_x = 0.125
        tip_end_y = sign * 0.0015
        create_cylinder_segment(
            f"{ASSET_ID}_Jaw_Tip_{sign}",
            (bow_end_x, bow_end_y, z_work),
            (tip_end_x, tip_end_y, z_work),
            0.0022, steel_mat, collection
        )

        # Serration teeth along inner jaw tip
        for tx in [0.100, 0.107, 0.114, 0.121]:
            tooth = kit.primitive_object(
                f"{ASSET_ID}_Tooth_{sign}_{tx}", "cube", steel_mat,
                size=(0.0015, 0.0008, 0.003),
                location=(tx, sign * 0.0008, z_work)
            )
            link_strictly(tooth, collection)

    # 4. Silvery Magnesium Ribbon Strip clamped in jaws
    # Ribbon extends from X = 0.105 (clamped) to X = 0.165, curved upwards
    mg_ribbon = kit.primitive_object(
        f"{ASSET_ID}_Mg_Ribbon", "cube", mg_mat,
        size=(0.060, 0.0035, 0.0006),
        location=(0.140, 0.0, z_work + 0.002),
        rotation_euler=(0.0, math.radians(-10), 0.0)
    )
    link_strictly(mg_ribbon, collection)

    print("Built Laboratory_Tongs_Full successfully.")


# -----------------------------------------------------------------------------
# BUILD TONGS DETAIL (Pivot Joint & Serrated Jaw Profile)
# -----------------------------------------------------------------------------
def build_tongs_detail(collection):
    steel_mat  = kit.add_machined_metal_material("sec-lt-steel", COLOR_STEEL_SATIN, metallic=0.95, roughness=0.20)
    rivet_mat  = kit.add_machined_metal_material("sec-lt-rivet", COLOR_STEEL_RIVET, metallic=0.92, roughness=0.25)
    plinth_mat = kit.add_material("sec-lt-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("sec-lt-gold", COLOR_GOLD, metallic=0.92, roughness=0.20)
    dim_mat    = kit.add_material("sec-lt-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)
    plaque_bg  = kit.add_material("sec-lt-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)

    # 1. Macro Plinth
    plinth = kit.primitive_object(
        "Sec_Plinth", "cube", plinth_mat,
        size=(0.280, 0.200, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    z_work = 0.020

    # 2. Enlarged Cross-Lap Pivot Hinge Detail (Scale 1.5x for clarity)
    scale = 1.4
    rivet = kit.primitive_object(
        "Sec_Rivet_Pin", "cylinder", rivet_mat,
        size=(0.008 * scale, 0.008 * scale, 0.012 * scale),
        location=(-0.040, 0.0, z_work)
    )
    link_strictly(rivet, collection)

    cap_t = kit.primitive_object(
        "Sec_Rivet_Cap_T", "uv_sphere", rivet_mat,
        size=(0.010 * scale, 0.010 * scale, 0.006 * scale),
        location=(-0.040, 0.0, z_work + 0.006 * scale)
    )
    link_strictly(cap_t, collection)

    # Scissor Lap Arm Section
    for sign in [-1, 1]:
        arm = kit.primitive_object(
            f"Sec_Hinge_Arm_{sign}", "cube", steel_mat,
            size=(0.050 * scale, 0.006 * scale, 0.0035 * scale),
            location=(-0.040, sign * 0.004 * scale, z_work + sign * 0.002 * scale),
            rotation_euler=(0.0, 0.0, sign * math.radians(15))
        )
        link_strictly(arm, collection)

    # 3. Macro Serrated Gripping Jaw Detail
    jaw_x = 0.050
    for sign in [-1, 1]:
        jaw_bar = kit.primitive_object(
            f"Sec_Macro_Jaw_{sign}", "cube", steel_mat,
            size=(0.060, 0.005, 0.006),
            location=(jaw_x, sign * 0.005, z_work)
        )
        link_strictly(jaw_bar, collection)

        # Visible sharp gripping teeth
        for tx in [-0.020, -0.010, 0.000, 0.010, 0.020]:
            tooth = kit.primitive_object(
                f"Sec_Macro_Tooth_{sign}_{tx}", "cube", gold_mat,
                size=(0.002, 0.0015, 0.005),
                location=(jaw_x + tx, sign * 0.002, z_work)
            )
            link_strictly(tooth, collection)

    # 4. Dimension Calipers
    create_cylinder_segment("Sec_Caliper_Jaw_Gap", (jaw_x, -0.005, z_work + 0.010), (jaw_x, 0.005, z_work + 0.010), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_Hinge_Dia", (-0.040 - 0.006, 0.0, z_work + 0.015), (-0.040 + 0.006, 0.0, z_work + 0.015), 0.0006, dim_mat, collection)

    # 5. Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.200, 0.006, 0.054),
        location=(0.0, -0.062, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.204, 0.004, 0.058),
        location=(0.0, -0.062, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    for dx in [-0.075, 0.075]:
        leg = kit.primitive_object(
            f"Sec_Plaque_Leg_{dx}", "cylinder", gold_mat,
            size=(0.003, 0.003, 0.024),
            location=(dx, -0.055, 0.012)
        )
        link_strictly(leg, collection)

    title_strip = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.170, 0.001, 0.008),
        location=(0.0, -0.064, 0.038),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(title_strip, collection)

    sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.140, 0.001, 0.004),
        location=(0.0, -0.063, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub1, collection)

    sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", gold_mat,
        size=(0.155, 0.001, 0.004),
        location=(0.0, -0.062, 0.014),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub2, collection)

    print("Built Laboratory_Tongs_Detail successfully.")


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING RIG
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("Tongs_Camera")
    cam_data.lens = 45.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("Tongs_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Studio elevated angle capturing full tongs and magnesium ribbon
    cam_obj.location = (0.24, -0.28, 0.20)
    cam_target = Vector((0.020, 0.0, 0.015))
    cam_dir = cam_target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting Rig
    key_light_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_light_data.energy = 4.5
    key_light_data.size = 0.35
    key_light_data.color = (1.0, 0.96, 0.92)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.22, -0.22, 0.26)
    key_dir = cam_target - key_light.location
    key_light.rotation_euler = key_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_light_data.energy = 1.8
    fill_light_data.size = 0.45
    fill_light_data.color = (0.85, 0.92, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.22, -0.18, 0.18)
    fill_dir = cam_target - fill_light.location
    fill_light.rotation_euler = fill_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_light_data.energy = 3.2
    rim_light_data.size = 0.30
    rim_light_data.color = (0.80, 0.90, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (-0.12, 0.25, 0.22)
    rim_dir = cam_target - rim_light.location
    rim_light.rotation_euler = rim_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Laboratory_Tongs_Full")
    sec_col  = bpy.data.collections.new("Laboratory_Tongs_Detail")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_tongs_full(full_col)
    build_tongs_detail(sec_col)
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

    # Render Preview 1: Laboratory_Tongs_Full
    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Laboratory_Tongs_Detail
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.20, -0.22, 0.16)
    cam_target = Vector((0.0, 0.0, 0.020))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
