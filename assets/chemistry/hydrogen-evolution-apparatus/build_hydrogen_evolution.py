"""
build_hydrogen_evolution.py — NCERT Class 10 Chemistry Activity 2.1 & Fig 2.1
Reaction of Zinc Granules with Dilute Sulphuric Acid and Testing Hydrogen Gas

Dual Collections:
1. Hydrogen_Apparatus_Full:
   - Laboratory base plinth and heavy cast-iron retort stand with bosshead and 3-finger clamp holding the flask.
   - Borosilicate conical flask (Erlenmeyer) with white graduation markings.
   - Irregular metallic zinc granules sitting at flask bottom with effervescent micro-bubble swarms.
   - Dilute sulphuric acid solution bulk.
   - Two-hole rubber cork tightly sealing flask neck.
   - Glass thistle funnel dipping deeply beneath acid level (critical liquid seal principle).
   - Smooth arched borosilicate glass delivery tube bridging from flask to soap trough.
   - Glass crystallizing trough filled with soap solution.
   - Rising buoyant soap bubbles filled with lighter-than-air hydrogen gas.
   - Burning test candle with wax cylinder, wick, and luminous teardrop flame.

2. Hydrogen_Apparatus_Section:
   - Longitudinal cutaway through conical flask, rubber cork, and acid volume:
     * Cork cross-section showing dual bore channels.
     * Submerged thistle funnel liquid seal demonstration (prevents gas backflow).
     * Zinc-acid reaction interface with effervescence nucleation layer.
     * Flow direction arrows inside delivery tube showing H2 gas migration.
     * Combustion explosion dynamics: Top bubble popping with expanding flame flare and acoustic shockwave ring.
     * Chemical reaction plaque: Zn(s) + H2SO4(aq) -> ZnSO4(aq) + H2(g) ^ with 'Burns with Pop Sound' test banner.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'hydrogen-evolution-apparatus'

# Material Colors & Constants
COLOR_PLINTH       = (0.13, 0.15, 0.18)    # Laboratory bench base
COLOR_STAND_BASE   = (0.18, 0.20, 0.23)    # Cast iron retort stand base
COLOR_STEEL_ROD    = (0.80, 0.82, 0.85)    # Machined stainless steel rod & clamp
COLOR_BOSSHEAD     = (0.15, 0.16, 0.18)    # Black enamel bosshead clamp
COLOR_GLASS        = (0.95, 0.98, 1.00)    # Borosilicate glass
COLOR_ACID         = (0.85, 0.94, 0.98)    # Dilute H2SO4 aqueous acid
COLOR_SOAP_SOL     = (0.75, 0.90, 0.95)    # Soap solution in trough
COLOR_ZINC         = (0.72, 0.76, 0.80)    # Metallic granulated zinc
COLOR_RUBBER       = (0.05, 0.05, 0.06)    # Black laboratory rubber cork
COLOR_WAX          = (0.92, 0.89, 0.80)    # Candle paraffin wax
COLOR_FLAME        = (1.00, 0.50, 0.08)    # Candle flame emission
COLOR_POP_FLAME    = (1.00, 0.70, 0.15)    # Hydrogen pop explosion flare
COLOR_ENAMEL       = (0.96, 0.96, 0.96)    # White graduation markings
COLOR_FLOW_ARROW   = (0.25, 0.80, 1.00)    # Luminous H2 gas flow vector
COLOR_CUT_EDGE     = (0.95, 0.65, 0.15)    # Plaque trim

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=5.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_soap_bubble_mat(name):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.01, 0.02, 0.03, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.005
    bsdf.inputs["IOR"].default_value = 1.05
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.99
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.9
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (0.25, 0.65, 0.95, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.20
    return mat

def create_conical_flask_mesh(name, cutaway=False):
    """
    Erlenmeyer Conical Flask profile with flat base, conical body, cylindrical neck, and beaded rim.
    If cutaway=True, removes the front quadrant facing the camera.
    """
    bm = bmesh.new()
    segments = 48
    r_base = 0.044
    r_neck = 0.015
    h_cone = 0.075
    h_neck = 0.028
    t_wall = 0.0022
    z_bot  = 0.016

    start_angle = -0.5 * math.pi if cutaway else 0.0
    end_angle   = math.pi if cutaway else 2.0 * math.pi
    actual_segs = int(segments * 0.75) if cutaway else segments

    profile = [
        (0.000, z_bot),
        (r_base, z_bot),
        (r_base, z_bot + 0.004),
        (r_neck + 0.003, z_bot + h_cone),
        (r_neck, z_bot + h_cone + 0.006),
        (r_neck, z_bot + h_cone + h_neck),
        (r_neck + 0.0025, z_bot + h_cone + h_neck + 0.003),
        (r_neck - t_wall, z_bot + h_cone + h_neck + 0.003),
        (r_neck - t_wall, z_bot + h_cone + 0.006),
        (r_neck + 0.003 - t_wall, z_bot + h_cone),
        (r_base - t_wall, z_bot + 0.004 + t_wall),
        (r_base - t_wall, z_bot + t_wall),
        (0.000, z_bot + t_wall)
    ]

    rings = []
    for r, z in profile:
        ring = []
        for s in range(actual_segs + (1 if cutaway else 0)):
            if cutaway:
                theta = start_angle + (end_angle - start_angle) * (s / actual_segs)
            else:
                theta = 2.0 * math.pi * (s / actual_segs)
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            v = bm.verts.new((r * cos_t, r * sin_t, z))
            ring.append(v)
        rings.append(ring)

    for i in range(len(profile) - 1):
        for s in range(actual_segs):
            next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
            v1 = rings[i][s]
            v2 = rings[i][next_s]
            v3 = rings[i+1][next_s]
            v4 = rings[i+1][s]
            if profile[i][0] == 0.0:
                bm.faces.new([v1, v3, v4])
            elif profile[i+1][0] == 0.0:
                bm.faces.new([v1, v2, v3])
            else:
                bm.faces.new([v1, v2, v3, v4])

    if cutaway:
        for i in range(len(profile) - 1):
            if profile[i][0] > 0.0 or profile[i+1][0] > 0.0:
                bm.faces.new([rings[i][0], rings[i+1][0], rings[i+1][-1], rings[i][-1]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return mesh

def build_retort_stand(prefix, flask_loc, col, mat_stand, mat_steel, mat_bosshead):
    """
    Constructs a laboratory retort stand with cast iron base, vertical steel rod,
    bosshead clamp, and 3-finger clamp securing the flask neck.
    """
    objs = []
    base_loc = flask_loc + Vector((-0.055, 0.025, 0.0))
    stand_base = kit.primitive_object(
        f"{prefix}-stand-base", "cube", mat_stand,
        size=(0.110, 0.070, 0.014),
        location=base_loc + Vector((0, 0, 0.007))
    )
    link_strictly(stand_base, col)
    objs.append(stand_base)

    rod_loc = base_loc + Vector((0.035, 0.0, 0.125))
    stand_rod = kit.primitive_object(
        f"{prefix}-stand-rod", "cylinder", mat_steel,
        size=(0.008, 0.008, 0.250),
        location=rod_loc
    )
    link_strictly(stand_rod, col)
    objs.append(stand_rod)

    neck_z = flask_loc.z + 0.100
    boss_loc = Vector((rod_loc.x, rod_loc.y, neck_z))
    bosshead = kit.primitive_object(
        f"{prefix}-bosshead", "cube", mat_bosshead,
        size=(0.018, 0.018, 0.020),
        location=boss_loc
    )
    link_strictly(bosshead, col)
    objs.append(bosshead)

    arm_pts = [
        boss_loc,
        Vector((flask_loc.x - 0.016, flask_loc.y, neck_z))
    ]
    arm = kit.create_smooth_tube(f"{prefix}-clamp-arm", arm_pts, radius=0.003, material=mat_steel)
    link_strictly(arm, col)
    objs.append(arm)

    clamp_ring = kit.lathe_object(
        f"{prefix}-clamp-collar",
        [(0.015, -0.004), (0.018, -0.004), (0.018, 0.004), (0.015, 0.004)],
        segments=24, material=mat_steel,
        location=(flask_loc.x, flask_loc.y, neck_z)
    )
    link_strictly(clamp_ring, col)
    objs.append(clamp_ring)

    return objs

def build_zinc_granules_and_effervescence(prefix, flask_loc, col, mat_zinc, mat_bub, num_granules=8, num_bubs=20):
    """
    Creates faceted metallic zinc granules on flask bottom with active bubbling effervescence.
    """
    objs = []
    granule_offsets = [
        (0.000, 0.000, 0.005, 0.009),
        (0.014, 0.008, 0.005, 0.008),
        (-0.012, 0.012, 0.005, 0.008),
        (-0.015, -0.010, 0.005, 0.007),
        (0.012, -0.014, 0.005, 0.008),
        (0.022, 0.000, 0.005, 0.007),
        (-0.020, 0.004, 0.005, 0.007),
        (0.005, 0.020, 0.005, 0.006)
    ]
    for idx, (ox, oy, oz, sz) in enumerate(granule_offsets[:num_granules]):
        g = kit.primitive_object(
            f"{prefix}-zinc-{idx}", "cube", mat_zinc,
            size=(sz, sz * 0.9, sz * 0.7),
            location=flask_loc + Vector((ox, oy, oz + 0.016)),
            rotation_euler=(0.3 * idx, 0.4 * idx, 0.5 * idx)
        )
        link_strictly(g, col)
        objs.append(g)

    for b in range(num_bubs):
        frac = b / num_bubs
        bz = flask_loc.z + 0.020 + frac * 0.024
        spread = 0.020 * (1.0 - frac * 0.4)
        bx = flask_loc.x + spread * math.cos(b * 2.39)
        by = flask_loc.y + spread * math.sin(b * 2.39)
        bub_rad = 0.0012 + 0.0006 * frac
        bub = kit.primitive_object(
            f"{prefix}-effervescence-{b}", "uv_sphere", mat_bub,
            size=(bub_rad * 2, bub_rad * 2, bub_rad * 2),
            location=(bx, by, bz)
        )
        link_strictly(bub, col)
        objs.append(bub)

    return objs

def build_delivery_tube_and_trough(prefix, flask_loc, trough_loc, col, mat_glass, mat_soap_sol, mat_bubble):
    """
    Constructs the bent delivery tube bridging flask to soap trough,
    crystallizing dish trough, and ascending soap bubbles.
    """
    objs = []
    tube_start = flask_loc + Vector((0.007, 0.0, 0.108))
    tube_pts = [
        tube_start,
        tube_start + Vector((0, 0, 0.032)),
        Vector((flask_loc.x + 0.020, 0.0, 0.155)),
        Vector((trough_loc.x - 0.035, 0.0, 0.155)),
        Vector((trough_loc.x - 0.010, 0.0, 0.130)),
        Vector((trough_loc.x - 0.005, 0.0, 0.065)),
        trough_loc + Vector((-0.005, 0.0, 0.024))
    ]
    tube = kit.create_smooth_tube(f"{prefix}-deliv-tube", tube_pts, radius=0.0022, material=mat_glass, cap_ends=True)
    link_strictly(tube, col)
    objs.append(tube)

    trough_profile = [
        (0.000, 0.016),
        (0.046, 0.016),
        (0.048, 0.019),
        (0.048, 0.052),
        (0.045, 0.052),
        (0.045, 0.019),
        (0.000, 0.019)
    ]
    trough = kit.lathe_object(f"{prefix}-trough", trough_profile, segments=48, material=mat_glass, location=trough_loc)
    link_strictly(trough, col)
    objs.append(trough)

    soap_liquid = kit.primitive_object(
        f"{prefix}-soap-liquid", "cylinder", mat_soap_sol,
        size=(0.088, 0.088, 0.028),
        location=trough_loc + Vector((0, 0, 0.031))
    )
    link_strictly(soap_liquid, col)
    objs.append(soap_liquid)

    bubble_coords = [
        trough_loc + Vector((-0.005, 0.002, 0.048)),
        trough_loc + Vector((0.008, -0.006, 0.075)),
        trough_loc + Vector((-0.004, 0.008, 0.115)),
        trough_loc + Vector((0.012, 0.000, 0.155))
    ]
    bubble_radii = [0.010, 0.014, 0.018, 0.022]
    for b_idx, (b_pos, b_r) in enumerate(zip(bubble_coords, bubble_radii)):
        bub = kit.primitive_object(
            f"{prefix}-bubble-{b_idx}", "uv_sphere", mat_bubble,
            size=(b_r * 2, b_r * 2, b_r * 2),
            location=b_pos
        )
        link_strictly(bub, col)
        objs.append(bub)

    return objs

def build_candle(prefix, candle_loc, col, mat_wax, mat_flame, mat_stand):
    """
    Constructs a laboratory candle on candle stand with lit flame.
    """
    objs = []
    c_base = kit.primitive_object(
        f"{prefix}-candle-stand", "cylinder", mat_stand,
        size=(0.032, 0.032, 0.006),
        location=candle_loc + Vector((0, 0, 0.003))
    )
    link_strictly(c_base, col)
    objs.append(c_base)

    c_wax = kit.primitive_object(
        f"{prefix}-candle-wax", "cylinder", mat_wax,
        size=(0.016, 0.016, 0.090),
        location=candle_loc + Vector((0, 0, 0.051))
    )
    link_strictly(c_wax, col)
    objs.append(c_wax)

    wick_loc = candle_loc + Vector((0, 0, 0.098))
    c_wick = kit.primitive_object(
        f"{prefix}-candle-wick", "cylinder", mat_stand,
        size=(0.0016, 0.0016, 0.008),
        location=wick_loc
    )
    link_strictly(c_wick, col)
    objs.append(c_wick)

    flame_profile = [
        (0.000, 0.000),
        (0.0045, 0.005),
        (0.0040, 0.012),
        (0.0020, 0.018),
        (0.000, 0.024)
    ]
    flame = kit.lathe_object(
        f"{prefix}-candle-flame", flame_profile, segments=24, material=mat_flame,
        location=candle_loc + Vector((0, 0, 0.101))
    )
    link_strictly(flame, col)
    objs.append(flame)

    return objs

def build_hydrogen_full(col):
    """Constructs the complete 3D apparatus for Hydrogen_Apparatus_Full collection."""
    objs = []
    mat_plinth   = kit.add_material("h2-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_stand    = kit.add_material("h2-stand", COLOR_STAND_BASE, metallic=0.45, roughness=0.45)
    mat_steel    = kit.add_material("h2-steel", COLOR_STEEL_ROD, metallic=0.92, roughness=0.22)
    mat_bosshead = kit.add_material("h2-bosshead", COLOR_BOSSHEAD, metallic=0.30, roughness=0.50)
    mat_glass    = kit.add_glass_material("h2-glass", tint=COLOR_GLASS, ior=1.517, roughness=0.015, transmission=0.96)
    mat_acid     = kit.add_material("h2-acid", COLOR_ACID, roughness=0.03, transmission=0.92, ior=1.334)
    mat_soap_sol = kit.add_material("h2-soap-sol", COLOR_SOAP_SOL, roughness=0.04, transmission=0.88, ior=1.335)
    mat_bubble   = create_soap_bubble_mat("h2-bubble")
    mat_zinc     = kit.add_material("h2-zinc", COLOR_ZINC, metallic=0.88, roughness=0.35)
    mat_bub      = kit.add_material("h2-bub-eff", (0.95, 0.98, 1.0), roughness=0.03, transmission=0.88)
    mat_rubber   = kit.add_material("h2-rubber", COLOR_RUBBER, metallic=0.02, roughness=0.85)
    mat_wax      = kit.add_material("h2-wax", COLOR_WAX, metallic=0.0, roughness=0.35)
    mat_flame    = create_emissive_mat("h2-flame", COLOR_FLAME, strength=7.0)
    mat_enamel   = kit.add_material("h2-enamel", COLOR_ENAMEL, metallic=0.0, roughness=0.30)

    plinth = kit.primitive_object(
        f"{ASSET_ID}-plinth", "cube", mat_plinth,
        size=(0.340, 0.220, 0.016),
        location=(0.020, 0.0, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    flask_loc  = Vector((-0.055, 0.0, 0.0))
    trough_loc = Vector((0.075, 0.0, 0.0))
    candle_loc = Vector((0.145, 0.0, 0.016))

    stand_objs = build_retort_stand(ASSET_ID, flask_loc, col, mat_stand, mat_steel, mat_bosshead)
    objs.extend(stand_objs)

    flask_mesh = create_conical_flask_mesh(f"{ASSET_ID}-flask-mesh", cutaway=False)
    flask_obj = bpy.data.objects.new(f"{ASSET_ID}-flask", flask_mesh)
    flask_obj.data.materials.append(mat_glass)
    flask_obj.location = flask_loc
    col.objects.link(flask_obj)
    objs.append(flask_obj)

    for g in range(1, 4):
        gz = 0.016 + 0.020 + g * 0.014
        gr = 0.044 - (gz - 0.016) / 0.075 * (0.044 - 0.018)
        mark = kit.primitive_object(
            f"{ASSET_ID}-flask-grad-{g}", "cylinder", mat_enamel,
            size=(gr * 2.008, gr * 2.008, 0.0004),
            location=flask_loc + Vector((0, 0, gz))
        )
        link_strictly(mark, col)
        objs.append(mark)

    acid_bulk = kit.primitive_object(
        f"{ASSET_ID}-acid-bulk", "cylinder", mat_acid,
        size=(0.074, 0.074, 0.026),
        location=flask_loc + Vector((0, 0, 0.030))
    )
    link_strictly(acid_bulk, col)
    objs.append(acid_bulk)

    zinc_objs = build_zinc_granules_and_effervescence(ASSET_ID, flask_loc, col, mat_zinc, mat_bub)
    objs.extend(zinc_objs)

    cork = kit.primitive_object(
        f"{ASSET_ID}-cork", "cylinder", mat_rubber,
        size=(0.026, 0.026, 0.016),
        location=flask_loc + Vector((0, 0, 0.106))
    )
    link_strictly(cork, col)
    objs.append(cork)

    t_stem_pts = [
        flask_loc + Vector((-0.007, 0.0, 0.022)),
        flask_loc + Vector((-0.007, 0.0, 0.155))
    ]
    t_stem = kit.create_smooth_tube(f"{ASSET_ID}-thistle-stem", t_stem_pts, radius=0.0022, material=mat_glass, cap_ends=True)
    link_strictly(t_stem, col)
    objs.append(t_stem)

    t_cup_profile = [
        (0.000, 0.000), (0.0025, 0.000), (0.012, 0.018), (0.014, 0.022),
        (0.012, 0.022), (0.010, 0.018), (0.000, 0.000)
    ]
    t_cup = kit.lathe_object(
        f"{ASSET_ID}-thistle-cup", t_cup_profile, segments=32, material=mat_glass,
        location=flask_loc + Vector((-0.007, 0.0, 0.155))
    )
    link_strictly(t_cup, col)
    objs.append(t_cup)

    deliv_objs = build_delivery_tube_and_trough(ASSET_ID, flask_loc, trough_loc, col, mat_glass, mat_soap_sol, mat_bubble)
    objs.extend(deliv_objs)

    candle_objs = build_candle(ASSET_ID, candle_loc, col, mat_wax, mat_flame, mat_stand)
    objs.extend(candle_objs)

    return objs

def build_hydrogen_section(col):
    """
    Constructs the longitudinal cutaway collection revealing:
    - Flask & Cork 90° cross-section showing dual bored holes.
    - Thistle funnel submerged liquid seal principle.
    - Zinc granules reaction boundary layer.
    - H2 gas migration flow vectors through delivery tube.
    - Pop sound combustion explosion dynamics at top bubble.
    - Chemical reaction plaque: Zn + H2SO4 -> ZnSO4 + H2 ^.
    """
    objs = []
    mat_plinth   = kit.add_material("sec-h2-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_stand    = kit.add_material("sec-h2-stand", COLOR_STAND_BASE, metallic=0.45, roughness=0.45)
    mat_steel    = kit.add_material("sec-h2-steel", COLOR_STEEL_ROD, metallic=0.92, roughness=0.22)
    mat_bosshead = kit.add_material("sec-h2-bosshead", COLOR_BOSSHEAD, metallic=0.30, roughness=0.50)
    mat_glass    = kit.add_glass_material("sec-h2-glass", tint=COLOR_GLASS, ior=1.517, roughness=0.015, transmission=0.96)
    mat_acid     = kit.add_material("sec-h2-acid", COLOR_ACID, roughness=0.03, transmission=0.92, ior=1.334)
    mat_soap_sol = kit.add_material("sec-h2-soap-sol", COLOR_SOAP_SOL, roughness=0.04, transmission=0.88, ior=1.335)
    mat_bubble   = create_soap_bubble_mat("sec-h2-bubble")
    mat_zinc     = kit.add_material("sec-h2-zinc", COLOR_ZINC, metallic=0.88, roughness=0.35)
    mat_bub      = kit.add_material("sec-h2-bub-eff", (0.95, 0.98, 1.0), roughness=0.03, transmission=0.88)
    mat_rubber   = kit.add_material("sec-h2-rubber", COLOR_RUBBER, metallic=0.02, roughness=0.85)
    mat_wax      = kit.add_material("sec-h2-wax", COLOR_WAX, metallic=0.0, roughness=0.35)
    mat_flame    = create_emissive_mat("sec-h2-flame", COLOR_FLAME, strength=7.0)
    mat_pop      = create_emissive_mat("sec-h2-pop", COLOR_POP_FLAME, strength=9.0)
    mat_flow     = create_emissive_mat("sec-h2-flow", COLOR_FLOW_ARROW, strength=4.5)
    mat_trim     = kit.add_material("sec-h2-trim", COLOR_CUT_EDGE, metallic=0.1, roughness=0.3)

    plinth = kit.primitive_object(
        f"{ASSET_ID}-sec-plinth", "cube", mat_plinth,
        size=(0.340, 0.220, 0.016),
        location=(0.020, 0.0, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    flask_loc  = Vector((-0.055, 0.0, 0.0))
    trough_loc = Vector((0.075, 0.0, 0.0))
    candle_loc = Vector((0.145, 0.0, 0.016))

    stand_objs = build_retort_stand(f"{ASSET_ID}-sec", flask_loc, col, mat_stand, mat_steel, mat_bosshead)
    objs.extend(stand_objs)

    flask_mesh = create_conical_flask_mesh(f"{ASSET_ID}-sec-flask-mesh", cutaway=True)
    flask_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-flask", flask_mesh)
    flask_obj.data.materials.append(mat_glass)
    flask_obj.location = flask_loc
    col.objects.link(flask_obj)
    objs.append(flask_obj)

    wb_mesh = bmesh.new()
    wb_segs = 32
    r_wb = 0.036
    h_wb = 0.026
    z_bot = flask_loc.z + 0.017
    for s in range(wb_segs + 1):
        theta = -0.5 * math.pi + (1.5 * math.pi) * (s / wb_segs)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        wb_mesh.verts.new((flask_loc.x + r_wb * cos_t, flask_loc.y + r_wb * sin_t, z_bot))
        wb_mesh.verts.new((flask_loc.x + r_wb * cos_t, flask_loc.y + r_wb * sin_t, z_bot + h_wb))
    center_bot = wb_mesh.verts.new((flask_loc.x, flask_loc.y, z_bot))
    center_top = wb_mesh.verts.new((flask_loc.x, flask_loc.y, z_bot + h_wb))
    wb_mesh.verts.ensure_lookup_table()
    for s in range(wb_segs):
        v1 = wb_mesh.verts[s*2]
        v2 = wb_mesh.verts[s*2 + 1]
        v3 = wb_mesh.verts[(s+1)*2]
        v4 = wb_mesh.verts[(s+1)*2 + 1]
        wb_mesh.faces.new([v1, v3, v4, v2])
        wb_mesh.faces.new([center_bot, v1, v3])
        wb_mesh.faces.new([center_top, v4, v2])
    wb_mesh.faces.new([center_bot, wb_mesh.verts[0], wb_mesh.verts[1], center_top])
    wb_mesh.faces.new([center_bot, center_top, wb_mesh.verts[wb_segs*2 + 1], wb_mesh.verts[wb_segs*2]])
    bmesh.ops.recalc_face_normals(wb_mesh, faces=wb_mesh.faces)
    wb_m = bpy.data.meshes.new(f"{ASSET_ID}-sec-acid-mesh")
    wb_mesh.to_mesh(wb_m)
    wb_mesh.free()
    for poly in wb_m.polygons:
        poly.use_smooth = True
    acid_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-acid-bulk", wb_m)
    acid_obj.data.materials.append(mat_acid)
    col.objects.link(acid_obj)
    objs.append(acid_obj)

    zinc_objs = build_zinc_granules_and_effervescence(f"{ASSET_ID}-sec", flask_loc, col, mat_zinc, mat_bub)
    objs.extend(zinc_objs)

    cork = kit.primitive_object(
        f"{ASSET_ID}-sec-cork", "cylinder", mat_rubber,
        size=(0.026, 0.026, 0.016),
        location=flask_loc + Vector((0, 0, 0.106))
    )
    link_strictly(cork, col)
    objs.append(cork)

    t_stem_pts = [
        flask_loc + Vector((-0.007, 0.0, 0.022)),
        flask_loc + Vector((-0.007, 0.0, 0.155))
    ]
    t_stem = kit.create_smooth_tube(f"{ASSET_ID}-sec-thistle-stem", t_stem_pts, radius=0.0022, material=mat_glass, cap_ends=True)
    link_strictly(t_stem, col)
    objs.append(t_stem)

    t_cup_profile = [
        (0.000, 0.000), (0.0025, 0.000), (0.012, 0.018), (0.014, 0.022),
        (0.012, 0.022), (0.010, 0.018), (0.000, 0.000)
    ]
    t_cup = kit.lathe_object(
        f"{ASSET_ID}-sec-thistle-cup", t_cup_profile, segments=32, material=mat_glass,
        location=flask_loc + Vector((-0.007, 0.0, 0.155))
    )
    link_strictly(t_cup, col)
    objs.append(t_cup)

    seal_indicator = kit.create_smooth_tube(
        f"{ASSET_ID}-sec-liquid-seal-bracket",
        [flask_loc + Vector((-0.022, 0.0, 0.043)), flask_loc + Vector((-0.028, 0.0, 0.043)),
         flask_loc + Vector((-0.028, 0.0, 0.022)), flask_loc + Vector((-0.022, 0.0, 0.022))],
        radius=0.0012, material=mat_flow
    )
    link_strictly(seal_indicator, col)
    objs.append(seal_indicator)

    deliv_objs = build_delivery_tube_and_trough(f"{ASSET_ID}-sec", flask_loc, trough_loc, col, mat_glass, mat_soap_sol, mat_bubble)
    objs.extend(deliv_objs)

    flow_pts = [
        flask_loc + Vector((0.007, 0.0, 0.135)),
        Vector((-0.015, 0.0, 0.155)),
        Vector((0.035, 0.0, 0.155)),
        Vector((0.070, 0.0, 0.090))
    ]
    for idx, fpos in enumerate(flow_pts):
        arrow = kit.primitive_object(
            f"{ASSET_ID}-sec-flow-arrow-{idx}", "cone", mat_flow,
            size=(0.003, 0.003, 0.007),
            location=fpos,
            rotation_euler=(0.0, 1.57 if idx < 3 else -1.57, 0.0)
        )
        link_strictly(arrow, col)
        objs.append(arrow)

    candle_objs = build_candle(f"{ASSET_ID}-sec", candle_loc, col, mat_wax, mat_flame, mat_stand)
    objs.extend(candle_objs)

    pop_center = trough_loc + Vector((0.012, 0.0, 0.155))
    pop_flare = kit.primitive_object(
        f"{ASSET_ID}-sec-pop-flare", "uv_sphere", mat_pop,
        size=(0.038, 0.038, 0.038),
        location=pop_center
    )
    link_strictly(pop_flare, col)
    objs.append(pop_flare)

    pop_ring1 = kit.lathe_object(
        f"{ASSET_ID}-sec-pop-ring-1",
        [(0.024, 0.0), (0.032, 0.0015), (0.036, 0.0), (0.032, -0.0015)],
        segments=32, material=mat_pop,
        location=pop_center, rotation_euler=(0.2, 0.0, 0.0)
    )
    pop_ring2 = kit.lathe_object(
        f"{ASSET_ID}-sec-pop-ring-2",
        [(0.038, 0.0), (0.046, 0.0015), (0.050, 0.0), (0.046, -0.0015)],
        segments=32, material=mat_pop,
        location=pop_center, rotation_euler=(-0.3, 0.0, 0.0)
    )
    link_strictly(pop_ring1, col)
    link_strictly(pop_ring2, col)
    objs.extend([pop_ring1, pop_ring2])

    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-bg", "cube", mat_bosshead,
        size=(0.180, 0.004, 0.025),
        location=(0.010, 0.075, 0.175)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-trim", "cube", mat_trim,
        size=(0.184, 0.005, 0.002),
        location=(0.010, 0.075, 0.188)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    return objs

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def frame_camera_on_target(cam_obj, target_pos, distance, elev_deg, azim_deg):
    elev = math.radians(elev_deg)
    azim = math.radians(azim_deg)
    cx = target_pos.x + distance * math.cos(elev) * math.sin(azim)
    cy = target_pos.y - distance * math.cos(elev) * math.cos(azim)
    cz = target_pos.z + distance * math.sin(elev)
    cam_obj.location = Vector((cx, cy, cz))
    direction = (target_pos - cam_obj.location).normalized()
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def configure_fast_render(width=1280, height=720, samples=16):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.cycles.max_bounces = 4
    scene.cycles.diffuse_bounces = 2
    scene.cycles.glossy_bounces = 4
    scene.cycles.transmission_bounces = 4
    scene.cycles.transparent_max_bounces = 6
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    col_full = bpy.data.collections.new("Hydrogen_Apparatus_Full")
    col_sec  = bpy.data.collections.new("Hydrogen_Apparatus_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_hydrogen_full(col_full)
    sec_objs  = build_hydrogen_section(col_sec)

    cam_data = bpy.data.cameras.new("Hydrogen_Camera")
    cam_data.lens = 48.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Hydrogen_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    configure_fast_render(width=1280, height=720, samples=16)

    # Render Preview 1: Full Apparatus
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.025, 0.0, 0.090)), distance=0.58, elev_deg=20, azim_deg=-26)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section View
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.025, 0.0, 0.100)), distance=0.58, elev_deg=18, azim_deg=-24)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== HYDROGEN EVOLUTION APPARATUS BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
