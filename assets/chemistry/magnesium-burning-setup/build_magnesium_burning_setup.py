"""
build_magnesium_burning_setup.py — NCERT Class 10 Chemistry Activity 1.1
Dual collections:
  - Magnesium_Burning_Setup_Full: Complete assembled experiment with Bunsen burner, retort stand, tongs holding ribbon undergoing dazzling white combustion, falling ash flakes, and watch glass collecting white MgO powder
  - Magnesium_Burning_Setup_Reaction: Close-up reaction zone detail showing ribbon tip vapor phase combustion, isothermal temperature isotherms, O2 diffusion vectors, and balanced equation plaque
"""

import sys
import math
import shutil
from pathlib import Path
from mathutils import Vector, Euler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy
import bmesh

ASSET_ID = 'magnesium-burning-setup'

COLOR_BENCH         = (0.16, 0.18, 0.22)
COLOR_TILE          = (0.92, 0.93, 0.94)
COLOR_CAST_IRON     = (0.12, 0.12, 0.14)
COLOR_BRASS         = (0.85, 0.65, 0.22)
COLOR_NICKEL        = (0.82, 0.84, 0.86)
COLOR_HOSE          = (0.88, 0.42, 0.12)
COLOR_STEEL         = (0.88, 0.90, 0.92)
COLOR_MG_METAL      = (0.88, 0.90, 0.93)
COLOR_MGO_ASH       = (0.96, 0.96, 0.95)
COLOR_GLASS         = (0.95, 0.98, 1.00)
COLOR_SANDPAPER     = (0.32, 0.30, 0.28)
COLOR_GOLD          = (0.90, 0.75, 0.22)
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)
COLOR_O2_ARR        = (0.15, 0.75, 0.95)
COLOR_ISOTHERM_HOT  = (1.00, 0.95, 0.80)
COLOR_ISOTHERM_MID  = (1.00, 0.60, 0.15)


def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_emissive_mat(name, color, strength=8.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Emission Color'].default_value = (*color[:3], 1.0)
        bsdf.inputs['Emission Strength'].default_value = strength
    return mat


def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    diff = p2 - p1
    length = diff.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = diff.to_track_quat('Z', 'Y').to_euler()

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(f'{name}_Mesh')
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
# BUILD FULL ASSEMBLED EXPERIMENT
# -----------------------------------------------------------------------------
def build_setup_full(collection):
    bench_mat = kit.add_material(f'{ASSET_ID}-bench', COLOR_BENCH, metallic=0.1, roughness=0.7)
    tile_mat = kit.add_material(f'{ASSET_ID}-ceramic-tile', COLOR_TILE, metallic=0.0, roughness=0.3)
    cast_iron_mat = kit.add_material(f'{ASSET_ID}-cast-iron', COLOR_CAST_IRON, metallic=0.75, roughness=0.55)
    brass_mat = kit.add_machined_metal_material(f'{ASSET_ID}-brass', COLOR_BRASS, metallic=0.92, roughness=0.25)
    nickel_mat = kit.add_machined_metal_material(f'{ASSET_ID}-nickel', COLOR_NICKEL, metallic=0.95, roughness=0.22)
    hose_rubber_mat = kit.add_material(f'{ASSET_ID}-hose', COLOR_HOSE, metallic=0.0, roughness=0.6)
    tongs_steel_mat = kit.add_machined_metal_material(f'{ASSET_ID}-tongs', COLOR_STEEL, metallic=0.98, roughness=0.20)
    mg_metal_mat = kit.add_machined_metal_material(f'{ASSET_ID}-mg-ribbon', COLOR_MG_METAL, metallic=0.95, roughness=0.25)
    mgo_powder_mat = kit.add_material(f'{ASSET_ID}-mgo-powder', COLOR_MGO_ASH, metallic=0.0, roughness=0.95)
    glass_mat = kit.add_glass_material(f'{ASSET_ID}-glass', tint=COLOR_GLASS, ior=1.52, roughness=0.012)
    sandpaper_mat = kit.add_material(f'{ASSET_ID}-sandpaper', COLOR_SANDPAPER, metallic=0.0, roughness=0.92)

    # 1. Laboratory Bench & Ceramic Safety Tile
    bench_h = 0.016
    bench = kit.primitive_object(f'{ASSET_ID}_Bench', 'cube', bench_mat,
                                 size=(0.400, 0.320, bench_h),
                                 location=(0.05, 0.0, -bench_h / 2.0))
    link_strictly(bench, collection)

    tile_h = 0.005
    tile = kit.primitive_object(f'{ASSET_ID}_Tile', 'cube', tile_mat,
                                size=(0.240, 0.220, tile_h),
                                location=(0.0, 0.0, tile_h / 2.0))
    link_strictly(tile, collection)

    # 2. Bunsen Burner
    base_profile = [(0.000, 0.005), (0.042, 0.005), (0.042, 0.008), (0.038, 0.012),
                    (0.016, 0.016), (0.014, 0.022), (0.000, 0.022)]
    burner_base = kit.lathe_object(f'{ASSET_ID}_Burner_Base', base_profile, segments=48, material=cast_iron_mat)
    link_strictly(burner_base, collection)

    # Gas Barb & Hose
    barb = kit.primitive_object(f'{ASSET_ID}_Gas_Barb', 'cylinder', brass_mat,
                                size=(0.007, 0.007, 0.026),
                                location=(-0.022, 0.0, 0.014),
                                rotation_euler=(0.0, 1.5708, 0.0))
    link_strictly(barb, collection)

    hose_points = [Vector((-0.032, 0.0, 0.014)), Vector((-0.060, 0.005, 0.012)),
                   Vector((-0.100, 0.020, 0.008)), Vector((-0.145, 0.050, 0.005)),
                   Vector((-0.190, 0.090, 0.005))]
    for i in range(len(hose_points) - 1):
        p1, p2 = hose_points[i], hose_points[i+1]
        diff = p2 - p1
        seg = kit.primitive_object(f'{ASSET_ID}_Hose_{i}', 'cylinder', hose_rubber_mat,
                                   size=(0.009, 0.009, diff.length),
                                   location=(p1 + p2) / 2.0)
        seg.rotation_euler = Vector((0.0, 0.0, 1.0)).rotation_difference(diff).to_euler()
        link_strictly(seg, collection)

    # Air Collar & Stem
    collar_profile = [(0.0080, 0.022), (0.0118, 0.022), (0.0118, 0.042), (0.0080, 0.042), (0.0080, 0.022)]
    collar = kit.lathe_object(f'{ASSET_ID}_Air_Collar', collar_profile, segments=36, material=brass_mat)
    link_strictly(collar, collection)

    stem_h = 0.125
    stem_profile = [(0.0065, 0.042), (0.0070, 0.048), (0.0068, stem_h - 0.005),
                    (0.0080, stem_h), (0.0060, stem_h), (0.0055, 0.042), (0.0065, 0.042)]
    stem = kit.lathe_object(f'{ASSET_ID}_Stem', stem_profile, segments=48, material=nickel_mat)
    link_strictly(stem, collection)

    # Blue Heating Flame
    outer_flame_mat = create_emissive_mat(f'{ASSET_ID}_Flame_Outer', (0.12, 0.40, 0.95), strength=1.4)
    inner_flame_mat = create_emissive_mat(f'{ASSET_ID}_Flame_Inner', (0.75, 0.90, 1.00), strength=2.2)

    outer_flame = kit.primitive_object(f'{ASSET_ID}_Flame_Outer', 'cone', outer_flame_mat,
                                       size=(0.015, 0.004, 0.045),
                                       location=(0.0, 0.0, stem_h + 0.0225))
    inner_flame = kit.primitive_object(f'{ASSET_ID}_Flame_Inner', 'cone', inner_flame_mat,
                                       size=(0.007, 0.002, 0.025),
                                       location=(0.0, 0.0, stem_h + 0.0125))
    link_strictly(outer_flame, collection)
    link_strictly(inner_flame, collection)

    # 3. Watch Glass & Collected White MgO Powder
    wg_x = 0.038
    wg_y = 0.000
    wg_z = tile_h
    wg_profile = []
    for deg in range(0, 36, 3):
        rad = math.radians(deg)
        r = 0.040 * math.sin(rad)
        z = wg_z + 0.008 * (1.0 - math.cos(rad))
        wg_profile.append((r, z))
    wg_profile.append((0.040 * math.sin(math.radians(35)), wg_z + 0.008 * (1.0 - math.cos(math.radians(35))) + 0.0015))
    for r, z in reversed(wg_profile[:-1]):
        wg_profile.append((max(0.0, r - 0.0010), z + 0.0015))

    watch_glass = kit.lathe_object(f'{ASSET_ID}_Watch_Glass', wg_profile, segments=48, material=glass_mat,
                                   location=(wg_x, wg_y, 0.0))
    link_strictly(watch_glass, collection)

    mgo_heap = kit.primitive_object(f'{ASSET_ID}_MgO_Heap', 'cone', mgo_powder_mat,
                                    size=(0.030, 0.003, 0.007),
                                    location=(wg_x, wg_y, wg_z + 0.0045))
    link_strictly(mgo_heap, collection)

    # 4. Retort Stand & Extension Clamp
    stand_base_x = 0.160
    stand_base_y = 0.075
    stand_base_z = tile_h + 0.006
    stand_h = 0.280

    stand_base = kit.primitive_object(f'{ASSET_ID}_Retort_Base', 'cube', cast_iron_mat,
                                      size=(0.140, 0.090, 0.012),
                                      location=(stand_base_x, stand_base_y, stand_base_z))
    link_strictly(stand_base, collection)

    rod_x = stand_base_x + 0.040
    rod_y = stand_base_y
    rod_z = stand_base_z + stand_h / 2.0
    stand_rod = kit.primitive_object(f'{ASSET_ID}_Retort_Rod', 'cylinder', nickel_mat,
                                     size=(0.010, 0.010, stand_h),
                                     location=(rod_x, rod_y, rod_z))
    link_strictly(stand_rod, collection)

    tongs_z_hold = stem_h + 0.024

    bosshead = kit.primitive_object(f'{ASSET_ID}_Bosshead', 'cube', cast_iron_mat,
                                    size=(0.022, 0.022, 0.026),
                                    location=(rod_x, rod_y, tongs_z_hold))
    boss_s1 = kit.primitive_object(f'{ASSET_ID}_Boss_S1', 'cylinder', brass_mat,
                                   size=(0.006, 0.006, 0.018),
                                   location=(rod_x + 0.014, rod_y, tongs_z_hold),
                                   rotation_euler=(0, 1.5708, 0))
    boss_s2 = kit.primitive_object(f'{ASSET_ID}_Boss_S2', 'cylinder', brass_mat,
                                   size=(0.006, 0.006, 0.018),
                                   location=(rod_x, rod_y + 0.014, tongs_z_hold),
                                   rotation_euler=(1.5708, 0, 0))
    link_strictly(bosshead, collection)
    link_strictly(boss_s1, collection)
    link_strictly(boss_s2, collection)

    clamp_ext_len = 0.075
    clamp_rod = kit.primitive_object(f'{ASSET_ID}_Clamp_Rod', 'cylinder', nickel_mat,
                                     size=(0.008, 0.008, clamp_ext_len),
                                     location=(rod_x, rod_y - clamp_ext_len / 2.0, tongs_z_hold),
                                     rotation_euler=(1.5708, 0, 0))
    clamp_jaw_u = kit.primitive_object(f'{ASSET_ID}_Clamp_Jaw_U', 'cube', tongs_steel_mat,
                                       size=(0.012, 0.024, 0.006),
                                       location=(rod_x - 0.015, rod_y - clamp_ext_len, tongs_z_hold + 0.006))
    clamp_jaw_l = kit.primitive_object(f'{ASSET_ID}_Clamp_Jaw_L', 'cube', tongs_steel_mat,
                                       size=(0.012, 0.024, 0.006),
                                       location=(rod_x - 0.015, rod_y - clamp_ext_len, tongs_z_hold - 0.006))
    link_strictly(clamp_rod, collection)
    link_strictly(clamp_jaw_u, collection)
    link_strictly(clamp_jaw_l, collection)

    # 5. Laboratory Tongs
    tongs_pivot_x = 0.125
    tongs_pivot_y = 0.000
    tongs_pin = kit.primitive_object(f'{ASSET_ID}_Tongs_Pin', 'cylinder', tongs_steel_mat,
                                     size=(0.006, 0.006, 0.014),
                                     location=(tongs_pivot_x, tongs_pivot_y, tongs_z_hold))
    link_strictly(tongs_pin, collection)

    handle_len = 0.080
    h_l = kit.primitive_object(f'{ASSET_ID}_Tongs_H_L', 'cube', tongs_steel_mat,
                              size=(handle_len, 0.005, 0.004),
                              location=(tongs_pivot_x + handle_len / 2.0, 0.008, tongs_z_hold),
                              rotation_euler=(0, 0, math.radians(6.0)))
    h_r = kit.primitive_object(f'{ASSET_ID}_Tongs_H_R', 'cube', tongs_steel_mat,
                              size=(handle_len, 0.005, 0.004),
                              location=(tongs_pivot_x + handle_len / 2.0, -0.008, tongs_z_hold),
                              rotation_euler=(0, 0, math.radians(-6.0)))
    link_strictly(h_l, collection)
    link_strictly(h_r, collection)

    loop_prof = [(0.010, 0.0), (0.012, 0.0), (0.012, 0.003), (0.010, 0.003), (0.010, 0.0)]
    l_l = kit.lathe_object(f'{ASSET_ID}_Loop_L', loop_prof, segments=24, material=tongs_steel_mat,
                           location=(tongs_pivot_x + handle_len, 0.016, tongs_z_hold))
    l_r = kit.lathe_object(f'{ASSET_ID}_Loop_R', loop_prof, segments=24, material=tongs_steel_mat,
                           location=(tongs_pivot_x + handle_len, -0.016, tongs_z_hold))
    link_strictly(l_l, collection)
    link_strictly(l_r, collection)

    jaw_l = kit.primitive_object(f'{ASSET_ID}_Jaw_L', 'cube', tongs_steel_mat,
                                size=(0.080, 0.005, 0.004),
                                location=(tongs_pivot_x - 0.040, 0.008, tongs_z_hold),
                                rotation_euler=(0, 0, math.radians(-5.0)))
    jaw_r = kit.primitive_object(f'{ASSET_ID}_Jaw_R', 'cube', tongs_steel_mat,
                                size=(0.080, 0.005, 0.004),
                                location=(tongs_pivot_x - 0.040, -0.008, tongs_z_hold),
                                rotation_euler=(0, 0, math.radians(5.0)))
    link_strictly(jaw_l, collection)
    link_strictly(jaw_r, collection)

    # 6. Magnesium Ribbon Held by Tongs
    ribbon_len = 0.085
    ribbon_w = 0.008
    ribbon_th = 0.0010
    ribbon_stations = 48
    verts = []
    for s in range(ribbon_stations):
        t = s / (ribbon_stations - 1)
        rx = -0.005 + t * ribbon_len
        rz = tongs_z_hold + 0.0020 * math.sin(2.0 * math.pi * 2.5 * t)
        for sign_y in (+1, -1):
            for sign_z in (+1, -1):
                verts.append((rx, sign_y * ribbon_w / 2.0, rz + sign_z * ribbon_th / 2.0))
    faces = []
    for s in range(ribbon_stations - 1):
        a = s * 4
        b = a + 4
        faces.extend([(a, a+1, b+1, b), (a+1, a+2, b+2, b+1), (a+2, a+3, b+3, b+2), (a+3, a, b, b+3)])
    faces.append((0, 1, 2, 3))
    last = (ribbon_stations - 1) * 4
    faces.append((last+3, last+2, last+1, last))

    ribbon = kit.mesh_object(f'{ASSET_ID}_Ribbon', verts, faces, mg_metal_mat)
    link_strictly(ribbon, collection)

    # 7. DAZZLING WHITE FLAME COMBUSTION FLARE (Active combustion at ribbon tip)
    flare_core_mat = create_emissive_mat(f'{ASSET_ID}_Flare_Core', (1.0, 1.0, 1.0), strength=18.0)
    flare_corona_mat = create_emissive_mat(f'{ASSET_ID}_Flare_Corona', (0.90, 0.95, 1.00), strength=8.0)

    # Inner intense radiant flare
    flare_core = kit.primitive_object(f'{ASSET_ID}_Combustion_Core', 'uv_sphere', flare_core_mat,
                                      size=(0.016, 0.016, 0.022),
                                      location=(-0.005, 0.0, tongs_z_hold))
    link_strictly(flare_core, collection)

    # Outer incandescent corona
    flare_corona = kit.primitive_object(f'{ASSET_ID}_Combustion_Corona', 'uv_sphere', flare_corona_mat,
                                        size=(0.028, 0.026, 0.036),
                                        location=(-0.005, 0.0, tongs_z_hold))
    link_strictly(flare_corona, collection)

    # Thermal Illumination Light
    flame_light_data = bpy.data.lights.new(f'{ASSET_ID}_Combustion_Light', type='POINT')
    flame_light_data.energy = 25.0
    flame_light_data.color = (0.95, 0.98, 1.0)
    flame_light_data.shadow_soft_size = 0.015
    flame_light = bpy.data.objects.new(f'{ASSET_ID}_Combustion_Light', flame_light_data)
    flame_light.location = (-0.005, 0.0, tongs_z_hold + 0.005)
    bpy.context.collection.objects.link(flame_light)
    link_strictly(flame_light, collection)

    # 8. Descending Glowing White Ash Flakes (Dropping into watch glass)
    flake_mat = create_emissive_mat(f'{ASSET_ID}_Falling_Ash', (0.98, 0.98, 0.96), strength=4.0)
    for i in range(8):
        frac = i / 7.0
        fx = -0.004 + 0.025 * frac + 0.003 * math.sin(i * 1.5)
        fy = 0.002 * math.cos(i * 2.0)
        fz = tongs_z_hold - 0.015 - frac * (tongs_z_hold - wg_z - 0.018)
        ash_f = kit.primitive_object(f'{ASSET_ID}_Falling_Flake_{i}', 'cube', flake_mat,
                                     size=(0.0020, 0.0016, 0.0006),
                                     location=(fx, fy, fz),
                                     rotation_euler=(math.radians(20 * i), math.radians(15 * i), 0))
        link_strictly(ash_f, collection)

    # 9. Sandpaper Strip on Tile
    sandpaper = kit.primitive_object(f'{ASSET_ID}_Sandpaper', 'cube', sandpaper_mat,
                                     size=(0.045, 0.035, 0.001),
                                     location=(-0.060, -0.065, tile_h + 0.0005),
                                     rotation_euler=(0.0, 0.0, math.radians(18.0)))
    link_strictly(sandpaper, collection)


# -----------------------------------------------------------------------------
# BUILD REACTION BREAKDOWN / DETAIL
# -----------------------------------------------------------------------------
def build_setup_reaction_detail(collection):
    plinth_mat   = kit.add_material(f'{ASSET_ID}_Sec_Plinth', COLOR_BENCH, metallic=0.15, roughness=0.70)
    mg_metal_mat = kit.add_machined_metal_material(f'{ASSET_ID}_Sec_Mg', COLOR_MG_METAL, metallic=0.98, roughness=0.18)
    tarnish_mat  = kit.add_material(f'{ASSET_ID}_Sec_Tarnish', (0.35, 0.38, 0.40), metallic=0.2, roughness=0.85)
    gold_mat     = kit.add_machined_metal_material(f'{ASSET_ID}_Sec_Gold', COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat      = create_emissive_mat(f'{ASSET_ID}_Sec_Dim', COLOR_CYAN_DIM, strength=10.0)
    o2_arr_mat   = create_emissive_mat(f'{ASSET_ID}_Sec_O2', COLOR_O2_ARR, strength=12.0)
    hot_mat      = create_emissive_mat(f'{ASSET_ID}_Sec_Hot', COLOR_ISOTHERM_HOT, strength=15.0)
    mid_mat      = create_emissive_mat(f'{ASSET_ID}_Sec_Mid', COLOR_ISOTHERM_MID, strength=6.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(f'{ASSET_ID}_Sec_Plinth', 'cube', plinth_mat,
                                 size=(0.320, 0.220, 0.012),
                                 location=(0.0, 0.0, -0.006))
    link_strictly(plinth, collection)

    # 2. Magnified Ribbon Combustion Tip (Center at x = 0.040, y = 0.0, z = 0.045)
    rx = 0.040
    ry = -0.005
    rz = 0.045

    # Solid Mg Ribbon Core
    mg_core = kit.primitive_object(f'{ASSET_ID}_Sec_Ribbon_Core', 'cube', mg_metal_mat,
                                   size=(0.065, 0.016, 0.006),
                                   location=(rx + 0.035, ry, rz))
    link_strictly(mg_core, collection)

    # Melting / Vaporizing Transition Zone
    trans_zone = kit.primitive_object(f'{ASSET_ID}_Sec_Trans_Zone', 'cylinder', mid_mat,
                                      size=(0.016, 0.016, 0.012),
                                      location=(rx, ry, rz),
                                      rotation_euler=(0.0, 1.5708, 0.0))
    link_strictly(trans_zone, collection)

    # Intense Vapor-Phase Combustion Flare
    comb_core = kit.primitive_object(f'{ASSET_ID}_Sec_Flame_Core', 'uv_sphere', hot_mat,
                                     size=(0.032, 0.032, 0.042),
                                     location=(rx - 0.020, ry, rz))
    link_strictly(comb_core, collection)

    # Atmospheric O2 Diffusion Inflow Arrows
    for angle_deg in [45, 135, -45, -135]:
        rad = math.radians(angle_deg)
        p_start = (rx - 0.020 + 0.042 * math.cos(rad), ry + 0.042 * math.sin(rad), rz)
        p_end   = (rx - 0.020 + 0.022 * math.cos(rad), ry + 0.022 * math.sin(rad), rz)
        create_cylinder_segment(f'{ASSET_ID}_O2_Arr_{angle_deg}', p_start, p_end, 0.0006, o2_arr_mat, collection)

    # Isothermal Temperature Contour Rings (3100 K & 2800 K)
    create_cylinder_segment(f'{ASSET_ID}_Iso_Top', (rx - 0.020, ry - 0.025, rz + 0.026),
                            (rx - 0.020, ry + 0.025, rz + 0.026), 0.0003, hot_mat, collection)
    create_cylinder_segment(f'{ASSET_ID}_Iso_Bot', (rx - 0.020, ry - 0.025, rz - 0.026),
                            (rx - 0.020, ry + 0.025, rz - 0.026), 0.0003, hot_mat, collection)

    # 3. Chemical Equation & Educational Plaque
    plq_x = -0.075
    plq_y = 0.010
    plq_rot = (math.radians(12.0), 0.0, math.radians(35.0))
    plq_norm_x = 0.005 * math.sin(math.radians(35.0))
    plq_norm_y = -0.005 * math.cos(math.radians(35.0))

    plaque_base = kit.primitive_object(f'{ASSET_ID}_Plaque_Base', 'cube', plinth_mat,
                                       size=(0.105, 0.010, 0.065),
                                       location=(plq_x, plq_y, 0.035),
                                       rotation_euler=plq_rot)
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(f'{ASSET_ID}_Plaque_Border', 'cube', gold_mat,
                                         size=(0.101, 0.002, 0.061),
                                         location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.035),
                                         rotation_euler=plq_rot)
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat(f'{ASSET_ID}_Sec_Txt', (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(f'{ASSET_ID}_Plaque_TitleBar', 'cube', txt_mat,
                                     size=(0.085, 0.002, 0.005),
                                     location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.052),
                                     rotation_euler=plq_rot)
    link_strictly(title_bar, collection)

    # Reaction Equation Line: 2Mg + O2 -> 2MgO
    eq_bar = kit.primitive_object(f'{ASSET_ID}_Plaque_EqBar', 'cube', hot_mat,
                                  size=(0.078, 0.002, 0.004),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.040),
                                  rotation_euler=plq_rot)
    link_strictly(eq_bar, collection)

    line_1 = kit.primitive_object(f'{ASSET_ID}_Plaque_Line1', 'cube', dim_mat,
                                  size=(0.070, 0.002, 0.003),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.028),
                                  rotation_euler=plq_rot)
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(f'{ASSET_ID}_Plaque_Line2', 'cube', o2_arr_mat,
                                  size=(0.060, 0.002, 0.003),
                                  location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.018),
                                  rotation_euler=plq_rot)
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING SETUP
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new('edu_camera')
    cam_data.lens = 42.0
    cam = bpy.data.objects.new('edu_camera', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Framed angled laboratory view showcasing burner, flare, tongs, ribbon, and watch glass
    cam.location = (0.28, -0.36, 0.26)
    cam_target = Vector((0.02, 0.0, 0.090))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new('Key_Light', type='AREA')
    key_light_data.energy = 45.0
    key_light_data.size = 0.40
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new('Key_Light', key_light_data)
    key_light.location = (0.30, -0.25, 0.35)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new('Fill_Light', type='AREA')
    fill_light_data.energy = 20.0
    fill_light_data.size = 0.45
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new('Fill_Light', fill_light_data)
    fill_light.location = (-0.28, -0.22, 0.28)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new('Rim_Light', type='POINT')
    rim_light_data.energy = 30.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new('Rim_Light', rim_light_data)
    rim_light.location = (0.0, 0.30, 0.30)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    full_col = bpy.data.collections.new('Magnesium_Burning_Setup_Full')
    sec_col  = bpy.data.collections.new('Magnesium_Burning_Setup_Reaction')
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_setup_full(full_col)
    build_setup_reaction_detail(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f'{ASSET_ID}.blend')

    # Export Full GLB only
    bpy.ops.object.select_all(action='DESELECT')
    for obj in full_col.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = full_col.objects[0]

    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / f'{ASSET_ID}.glb'),
        use_selection=True,
        export_format='GLB'
    )

    viewer_dest = Path('/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets') / f'{ASSET_ID}.glb'
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f'{ASSET_ID}.glb', viewer_dest)
        print(f'Synced GLB to: {viewer_dest}')

    # Render Preview 1: Magnesium_Burning_Setup_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / 'preview.png')

    # Render Preview 2: Magnesium_Burning_Setup_Reaction
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.18, -0.26, 0.16)
    cam_target = Vector((0.0, 0.0, 0.040))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat('-Z', 'Y').to_euler()

    kit.render_preview(out_dir / 'preview_section.png')

    print(f'=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===')


if __name__ == '__main__':
    main()
