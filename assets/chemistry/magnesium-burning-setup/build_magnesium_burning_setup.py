"""
build_magnesium_burning_setup.py — Complete Assembled Chemistry Lab Bench Setup
CBSE Class 10 Chemistry, Chapter 1: Chemical Reactions and Equations (Activity 1.1)
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "magnesium-burning-setup"


def build_setup():
    objects = []

    # =========================================================================
    # 1. SHADERS & MATERIALS
    # =========================================================================
    bench_mat = kit.add_material(f"{ASSET_ID}-bench", (0.16, 0.18, 0.22), metallic=0.1, roughness=0.7)
    tile_mat = kit.add_material(f"{ASSET_ID}-ceramic-tile", (0.92, 0.93, 0.94), metallic=0.0, roughness=0.3)
    
    cast_iron_mat = kit.add_material(f"{ASSET_ID}-cast-iron", (0.12, 0.12, 0.14), metallic=0.75, roughness=0.55)
    brass_mat = kit.add_machined_metal_material(f"{ASSET_ID}-brass", (0.85, 0.65, 0.22), metallic=0.92, roughness=0.25)
    nickel_mat = kit.add_machined_metal_material(f"{ASSET_ID}-nickel-stem", (0.82, 0.84, 0.86), metallic=0.95, roughness=0.22)
    hose_rubber_mat = kit.add_material(f"{ASSET_ID}-rubber-hose", (0.88, 0.42, 0.12), metallic=0.0, roughness=0.6)
    
    tongs_steel_mat = kit.add_machined_metal_material(f"{ASSET_ID}-tongs-steel", (0.88, 0.90, 0.92), metallic=0.98, roughness=0.20)
    mg_metal_mat = kit.add_material(f"{ASSET_ID}-magnesium-metal", (0.84, 0.86, 0.89), metallic=1.0, roughness=0.32)
    mgo_powder_mat = kit.add_material(f"{ASSET_ID}-mgo-powder", (0.96, 0.96, 0.95), metallic=0.0, roughness=0.95)
    
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-watch-glass", tint=(0.95, 0.98, 1.0), ior=1.517, roughness=0.01)
    sandpaper_mat = kit.add_material(f"{ASSET_ID}-sandpaper", (0.32, 0.30, 0.28), metallic=0.0, roughness=0.92)

    # =========================================================================
    # 2. LABORATORY BENCH & HEAT-RESISTANT CERAMIC SAFETY TILE
    # =========================================================================
    bench_w = 0.400
    bench_l = 0.320
    bench_h = 0.016
    bench = kit.primitive_object(f"{ASSET_ID}-bench", "cube", bench_mat,
                                 size=(bench_w, bench_l, bench_h),
                                 location=(0.05, 0.0, -bench_h / 2))
    objects.append(bench)

    tile_w = 0.240
    tile_l = 0.220
    tile_h = 0.005
    tile = kit.primitive_object(f"{ASSET_ID}-tile", "cube", tile_mat,
                                size=(tile_w, tile_l, tile_h),
                                location=(0.0, 0.0, tile_h / 2))
    objects.append(tile)

    # =========================================================================
    # 3. HIGH-FIDELITY BUNSEN BURNER (Positioned at Origin)
    # =========================================================================
    # Heavy Cast-Iron Base
    base_profile = [
        (0.000, 0.005),
        (0.042, 0.005),
        (0.042, 0.008),
        (0.038, 0.012),
        (0.016, 0.016),
        (0.014, 0.022),
        (0.000, 0.022)
    ]
    burner_base = kit.lathe_object(f"{ASSET_ID}-burner-base", base_profile, segments=48, material=cast_iron_mat)
    objects.append(burner_base)

    # Gas Inlet Barb
    barb_bm = bmesh.new()
    bmesh.ops.create_cone(barb_bm, cap_ends=True, cap_tris=True, segments=24,
                          radius1=0.004, radius2=0.0035, depth=0.026)
    barb_mesh = bpy.data.meshes.new(f"{ASSET_ID}-gas-barb")
    barb_bm.to_mesh(barb_mesh)
    barb_bm.free()
    for poly in barb_mesh.polygons:
        poly.use_smooth = True
    barb_obj = bpy.data.objects.new(f"{ASSET_ID}-gas-barb", barb_mesh)
    barb_obj.location = (-0.022, 0.0, 0.014)
    barb_obj.rotation_euler = (0.0, 1.5708, 0.0)
    bpy.context.collection.objects.link(barb_obj)
    barb_obj.data.materials.append(brass_mat)
    objects.append(barb_obj)

    # Orange Flexible Gas Supply Hose (Curved path exiting off-bench)
    hose_points = [
        Vector((-0.032, 0.0, 0.014)),
        Vector((-0.060, 0.005, 0.012)),
        Vector((-0.100, 0.020, 0.008)),
        Vector((-0.145, 0.050, 0.005)),
        Vector((-0.190, 0.090, 0.005))
    ]
    for i in range(len(hose_points) - 1):
        p1 = hose_points[i]
        p2 = hose_points[i+1]
        diff = p2 - p1
        seg = kit.primitive_object(f"{ASSET_ID}-hose-seg-{i}", "cylinder", hose_rubber_mat,
                                   size=(0.009, 0.009, diff.length),
                                   location=(p1 + p2) / 2)
        rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(diff)
        seg.rotation_euler = rot_quat.to_euler()
        objects.append(seg)

    # Brass Air Collar
    collar_profile = [
        (0.0080, 0.022),
        (0.0112, 0.022),
        (0.0118, 0.024),
        (0.0118, 0.040),
        (0.0112, 0.042),
        (0.0080, 0.042),
        (0.0080, 0.022)  # Closes inner cylindrical wall
    ]
    collar_obj = kit.lathe_object(f"{ASSET_ID}-air-collar", collar_profile, segments=36, material=brass_mat)
    objects.append(collar_obj)

    # Nickel Mixing Chimney / Stem
    stem_h = 0.125
    stem_profile = [
        (0.0065, 0.042),
        (0.0070, 0.048),
        (0.0068, stem_h - 0.005),
        (0.0078, stem_h - 0.001),
        (0.0080, stem_h),
        (0.0060, stem_h),
        (0.0055, 0.042),
        (0.0065, 0.042)  # Closes bottom annular face
    ]
    stem_obj = kit.lathe_object(f"{ASSET_ID}-stem", stem_profile, segments=48, material=nickel_mat)
    objects.append(stem_obj)

    # Dual Bunsen Flame (Outer blue mantle + Inner intense pale-blue core)
    outer_flame_mat = bpy.data.materials.new(f"{ASSET_ID}-flame-outer")
    outer_flame_mat.use_nodes = True
    bsdf_fo = outer_flame_mat.node_tree.nodes["Principled BSDF"]
    bsdf_fo.inputs["Base Color"].default_value = (0.08, 0.25, 0.85, 1.0)
    bsdf_fo.inputs["Emission Color"].default_value = (0.15, 0.45, 1.0, 1.0)
    bsdf_fo.inputs["Emission Strength"].default_value = 8.0

    inner_flame_mat = bpy.data.materials.new(f"{ASSET_ID}-flame-inner")
    inner_flame_mat.use_nodes = True
    bsdf_fi = inner_flame_mat.node_tree.nodes["Principled BSDF"]
    bsdf_fi.inputs["Base Color"].default_value = (0.70, 0.85, 1.0, 1.0)
    bsdf_fi.inputs["Emission Color"].default_value = (0.80, 0.92, 1.0, 1.0)
    bsdf_fi.inputs["Emission Strength"].default_value = 24.0

    outer_flame = kit.primitive_object(f"{ASSET_ID}-flame-outer", "cone", outer_flame_mat,
                                        size=(0.015, 0.004, 0.045),
                                        location=(0.0, 0.0, stem_h + 0.0225))
    objects.append(outer_flame)

    inner_flame = kit.primitive_object(f"{ASSET_ID}-flame-inner", "cone", inner_flame_mat,
                                        size=(0.007, 0.002, 0.025),
                                        location=(0.0, 0.0, stem_h + 0.0125))
    objects.append(inner_flame)

    # Flame Illumination Light
    flame_light_data = bpy.data.lights.new(f"{ASSET_ID}-flame-light", type="POINT")
    flame_light_data.energy = 5.0
    flame_light_data.color = (0.6, 0.75, 1.0)
    flame_light_data.shadow_soft_size = 0.02
    flame_light = bpy.data.objects.new(f"{ASSET_ID}-flame-light", flame_light_data)
    bpy.context.collection.objects.link(flame_light)
    flame_light.location = (0.0, 0.0, stem_h + 0.020)
    objects.append(flame_light)

    # =========================================================================
    # 4. BOROSILICATE WATCH GLASS WITH COLLECTED MgO WHITE POWDER
    # Positioned directly beneath ribbon burning zone to collect falling ash
    # =========================================================================
    wg_x = 0.035
    wg_y = 0.000
    wg_z = tile_h
    wg_rad = 0.040  # 80mm diameter watch glass
    
    wg_profile = []
    for deg in range(0, 36, 3):
        rad = math.radians(deg)
        r = wg_rad * math.sin(rad)
        z = wg_z + 0.008 * (1.0 - math.cos(rad))
        wg_profile.append((r, z))
    # Add rim & thickness
    wg_profile.append((wg_rad * math.sin(math.radians(35)), wg_z + 0.008 * (1.0 - math.cos(math.radians(35))) + 0.0012))
    for r, z in reversed(wg_profile[:-1]):
        wg_profile.append((max(0.0, r - 0.0008), z + 0.0012))

    watch_glass = kit.lathe_object(f"{ASSET_ID}-watch-glass", wg_profile, segments=48, material=glass_mat,
                                   location=(wg_x, wg_y, 0.0))
    objects.append(watch_glass)

    # Heap of White Magnesium Oxide Powder in Watch Glass
    mgo_heap = kit.primitive_object(f"{ASSET_ID}-mgo-powder-heap", "cone", mgo_powder_mat,
                                    size=(0.028, 0.002, 0.006),
                                    location=(wg_x, wg_y, wg_z + 0.004))
    objects.append(mgo_heap)

    # =========================================================================
    # 5. RETORT STAND WITH BOSSHEAD & EXTENSION UTILITY CLAMP
    # Provides physical ground support for the crucible tongs holding the ribbon
    # =========================================================================
    stand_base_x = 0.160
    stand_base_y = 0.075
    stand_base_z = tile_h + 0.006
    stand_h = 0.280

    # Cast Iron Heavy Rectangular Retort Base
    stand_base = kit.primitive_object(
        f"{ASSET_ID}-retort-base", "cube", cast_iron_mat,
        size=(0.140, 0.090, 0.012),
        location=(stand_base_x, stand_base_y, stand_base_z)
    )
    objects.append(stand_base)

    # Vertical Steel Retort Rod
    rod_x = stand_base_x + 0.040
    rod_y = stand_base_y
    rod_z = stand_base_z + stand_h / 2
    stand_rod = kit.primitive_object(
        f"{ASSET_ID}-retort-rod", "cylinder", nickel_mat,
        size=(0.010, 0.010, stand_h),
        location=(rod_x, rod_y, rod_z)
    )
    objects.append(stand_rod)

    tongs_z_hold = stem_h + 0.024  # Positioned right in the flame combustion zone

    # Cast Alloy Bosshead Clamp (Right-angle connector)
    bosshead = kit.primitive_object(
        f"{ASSET_ID}-bosshead", "cube", cast_iron_mat,
        size=(0.022, 0.022, 0.026),
        location=(rod_x, rod_y, tongs_z_hold)
    )
    bosshead_screw_1 = kit.primitive_object(
        f"{ASSET_ID}-bosshead-screw-1", "cylinder", brass_mat,
        size=(0.006, 0.006, 0.018),
        location=(rod_x + 0.014, rod_y, tongs_z_hold)
    )
    bosshead_screw_1.rotation_euler = (0, 1.5708, 0)
    bosshead_screw_2 = kit.primitive_object(
        f"{ASSET_ID}-bosshead-screw-2", "cylinder", brass_mat,
        size=(0.006, 0.006, 0.018),
        location=(rod_x, rod_y + 0.014, tongs_z_hold)
    )
    bosshead_screw_2.rotation_euler = (1.5708, 0, 0)
    objects.extend([bosshead, bosshead_screw_1, bosshead_screw_2])

    # Extension Utility Clamp Rod & Jaws
    clamp_ext_len = 0.075
    clamp_rod = kit.primitive_object(
        f"{ASSET_ID}-clamp-extension-rod", "cylinder", nickel_mat,
        size=(0.008, 0.008, clamp_ext_len),
        location=(rod_x, rod_y - clamp_ext_len / 2, tongs_z_hold)
    )
    clamp_rod.rotation_euler = (1.5708, 0, 0)
    objects.append(clamp_rod)

    # Clamp Jaws Holding Tongs Handles
    clamp_jaw_upper = kit.primitive_object(
        f"{ASSET_ID}-clamp-jaw-upper", "cube", tongs_steel_mat,
        size=(0.012, 0.024, 0.006),
        location=(rod_x - 0.015, rod_y - clamp_ext_len, tongs_z_hold + 0.006)
    )
    clamp_jaw_lower = kit.primitive_object(
        f"{ASSET_ID}-clamp-jaw-lower", "cube", tongs_steel_mat,
        size=(0.012, 0.024, 0.006),
        location=(rod_x - 0.015, rod_y - clamp_ext_len, tongs_z_hold - 0.006)
    )
    objects.extend([clamp_jaw_upper, clamp_jaw_lower])

    # =========================================================================
    # 6. AUTHENTIC CRUCIBLE TONGS (Scissor pivot with bowed gripping tips)
    # =========================================================================
    tongs_pivot_x = 0.125
    tongs_pivot_y = 0.000

    # Pivot Rivet Pin
    tongs_pin = kit.primitive_object(
        f"{ASSET_ID}-tongs-pin", "cylinder", tongs_steel_mat,
        size=(0.006, 0.006, 0.014),
        location=(tongs_pivot_x, tongs_pivot_y, tongs_z_hold)
    )
    objects.append(tongs_pin)

    # Left & Right Handles (Rear shanks clamped by utility clamp)
    handle_len = 0.080
    handle_left = kit.primitive_object(
        f"{ASSET_ID}-tongs-handle-left", "cube", tongs_steel_mat,
        size=(handle_len, 0.005, 0.004),
        location=(tongs_pivot_x + handle_len / 2, 0.008, tongs_z_hold)
    )
    handle_left.rotation_euler = (0, 0, math.radians(6.0))
    handle_right = kit.primitive_object(
        f"{ASSET_ID}-tongs-handle-right", "cube", tongs_steel_mat,
        size=(handle_len, 0.005, 0.004),
        location=(tongs_pivot_x + handle_len / 2, -0.008, tongs_z_hold)
    )
    handle_right.rotation_euler = (0, 0, math.radians(-6.0))
    objects.extend([handle_left, handle_right])

    # Finger loop rings at end of handles (closed profile)
    loop_profile = [(0.010, 0.0), (0.012, 0.0), (0.012, 0.003), (0.010, 0.003), (0.010, 0.0)]
    loop_left = kit.lathe_object(
        f"{ASSET_ID}-loop-left",
        loop_profile,
        segments=24, material=tongs_steel_mat,
        location=(tongs_pivot_x + handle_len, 0.016, tongs_z_hold)
    )
    loop_right = kit.lathe_object(
        f"{ASSET_ID}-loop-right",
        loop_profile,
        segments=24, material=tongs_steel_mat,
        location=(tongs_pivot_x + handle_len, -0.016, tongs_z_hold)
    )
    objects.extend([loop_left, loop_right])

    # Front Bowed Gripping Jaws (Curved outwards then inward to pinch ribbon)
    jaw_pts_left = [
        Vector((tongs_pivot_x, 0.002, tongs_z_hold)),
        Vector((tongs_pivot_x - 0.035, 0.014, tongs_z_hold)),
        Vector((tongs_pivot_x - 0.065, 0.006, tongs_z_hold)),
        Vector((tongs_pivot_x - 0.080, 0.0015, tongs_z_hold)),
    ]
    jaw_left = kit.primitive_object(
        f"{ASSET_ID}-tongs-jaw-left", "cube", tongs_steel_mat,
        size=(0.080, 0.005, 0.004),
        location=(tongs_pivot_x - 0.040, 0.008, tongs_z_hold)
    )
    jaw_left.rotation_euler = (0, 0, math.radians(-5.0))

    jaw_right = kit.primitive_object(
        f"{ASSET_ID}-tongs-jaw-right", "cube", tongs_steel_mat,
        size=(0.080, 0.005, 0.004),
        location=(tongs_pivot_x - 0.040, -0.008, tongs_z_hold)
    )
    jaw_right.rotation_euler = (0, 0, math.radians(5.0))
    objects.extend([jaw_left, jaw_right])

    # Wavy Elemental Magnesium Ribbon Strip (Held firmly at flame position)
    ribbon_len = 0.085
    ribbon_w = 0.008
    ribbon_thick = 0.0012
    ribbon_stations = 60
    
    verts = []
    half_w = ribbon_w / 2
    half_th = ribbon_thick / 2
    
    for s in range(ribbon_stations):
        t = s / (ribbon_stations - 1)
        # Tip extends from flame center (x=0) to tongs tips (x=0.045)
        rx = -0.005 + t * ribbon_len
        rz = tongs_z_hold + 0.0025 * math.sin(2.0 * math.pi * 2.5 * t)
        for sign_y in (+1, -1):
            for sign_z in (+1, -1):
                verts.append((rx, sign_y * half_w, rz + sign_z * half_th))
                
    faces = []
    for s in range(ribbon_stations - 1):
        a = s * 4
        b = a + 4
        faces.append((a, a + 1, b + 1, b))
        faces.append((a + 1, a + 2, b + 2, b + 1))
        faces.append((a + 2, a + 3, b + 3, b + 2))
        faces.append((a + 3, a, b, b + 3))
    first = 0
    last = (ribbon_stations - 1) * 4
    faces.append((first, first + 1, first + 2, first + 3))
    faces.append((last + 3, last + 2, last + 1, last))

    ribbon_obj = kit.mesh_object(f"{ASSET_ID}-ribbon", verts, faces, mg_metal_mat)
    objects.append(ribbon_obj)

    # =========================================================================
    # 7. SANDPAPER STRIP (Pre-experiment cleaning step)
    # =========================================================================
    sp_x = -0.060
    sp_y = -0.065
    sandpaper = kit.primitive_object(f"{ASSET_ID}-sandpaper-strip", "cube", sandpaper_mat,
                                     size=(0.045, 0.035, 0.001),
                                     location=(sp_x, sp_y, tile_h + 0.0005))
    sandpaper.rotation_euler = (0.0, 0.0, math.radians(18.0))
    objects.append(sandpaper)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_setup()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    
    # Angled studio camera showcasing burner, glowing flame, tongs, ribbon, and watch glass
    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 45.0
    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.28, -0.36, 0.28)
    direction = Vector((-0.23, 0.36, -0.18)).normalized()
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam

    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] Assembled {ASSET_ID} experiment template built and rendered successfully.")


if __name__ == "__main__":
    main()
