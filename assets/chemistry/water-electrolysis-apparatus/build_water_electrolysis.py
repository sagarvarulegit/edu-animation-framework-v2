"""
build_water_electrolysis.py — NCERT Class 10 Chemistry Activity 1.7 (Fig 1.6)
Electrolysis of Water Laboratory Apparatus

Dual Collections:
1. Electrolysis_Apparatus_Full:
   - Translucent polypropylene laboratory mug with handle, rim, and graduations.
   - Rubber stoppers sealing base perforations.
   - Two cylindrical carbon/graphite electrodes.
   - Two inverted graduated borosilicate glass test tubes with 2:1 stoichiometric gas displacement:
     * Cathode (Right, -ve terminal): 2 Volumes H2 gas headspace, vigorous bubble effervescence.
     * Anode (Left, +ve terminal): 1 Volume O2 gas headspace, stoichiometric bubble effervescence.
   - Acidified water liquid bulk with distinct gas-liquid menisci.
   - Heavy 6V DC laboratory battery with red/black terminal posts.
   - Brass plug key / knife switch on insulating base.
   - Flexible insulated copper wires (red & black) connecting battery to electrodes.
   - Heavy exhibition bench plinth.

2. Electrolysis_Apparatus_Section:
   - Longitudinal cutaway through mug and electrode interface revealing:
     * Rubber stopper internal bore and hermetic seal with mug base.
     * Graphite electrode seating and copper contact wire junction.
     * Cutaway water column and gas bubbles nucleating from graphite surface.
     * Pedagogical 2:1 volumetric comparison calipers (2x H2 vs 1x O2).
     * Stoichiometric chemical reaction plaque: 2H2O(l) -> 2H2(g) + O2(g).
     * Gas identification test badges: Cathode (Burning splinter with 'POP!' flame flash) and Anode (Glowing splinter rekindling).
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'water-electrolysis-apparatus'

# Color Palette & Material Constants
COLOR_PLASTIC_MUG = (0.78, 0.90, 0.96)     # Translucent polypropylene lab plastic (clear tint)
COLOR_WATER       = (0.65, 0.85, 0.95)     # Acidified water with faint aqua refraction
COLOR_GLASS_TUBE  = (0.94, 0.98, 1.00)     # Borosilicate glass
COLOR_GRAPHITE    = (0.12, 0.12, 0.14)     # Matte charcoal carbon rod
COLOR_RUBBER      = (0.04, 0.04, 0.05)     # Dense vulcanized black rubber stopper
COLOR_BATTERY     = (0.08, 0.18, 0.35)     # Navy industrial battery casing
COLOR_TERM_RED    = (0.85, 0.10, 0.12)     # Anode (+) positive red terminal
COLOR_TERM_BLACK  = (0.05, 0.05, 0.06)     # Cathode (-) negative black terminal
COLOR_BRASS       = (0.85, 0.70, 0.22)     # Machined brass terminals & switch
COLOR_WIRE_RED    = (0.82, 0.12, 0.14)     # Red insulated wire
COLOR_WIRE_BLACK  = (0.10, 0.10, 0.12)     # Black insulated wire
COLOR_ENAMEL      = (0.96, 0.96, 0.96)     # White graduation marks
COLOR_PLINTH      = (0.14, 0.16, 0.19)     # Laboratory bench base
COLOR_GAS_H2      = (0.25, 0.80, 1.00)     # Luminescent hydrogen gas headspace
COLOR_GAS_O2      = (1.00, 0.75, 0.25)     # Luminescent oxygen gas headspace
COLOR_FLAME       = (1.00, 0.45, 0.05)     # Splint flame emission

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=4.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_plastic_mug_mesh(name, cutaway=False):
    """
    Creates a laboratory polypropylene mug with tapered wall, lip, and flat bottom.
    If cutaway=True, removes the front quadrant facing the camera (-X, -Y quadrant: pi to 1.5*pi).
    """
    bm = bmesh.new()
    segments = 48
    r_bot = 0.046
    r_top = 0.052
    h_mug = 0.108
    t_wall = 0.0028
    z_bot = 0.016

    # Cutaway: remove quadrant from theta = -pi (-180 deg) to -pi/2 (-90 deg)
    # Remaining range: -pi/2 to pi (270 degrees)
    start_angle = -0.5 * math.pi if cutaway else 0.0
    end_angle   = math.pi if cutaway else 2.0 * math.pi
    actual_segs = int(segments * 0.75) if cutaway else segments

    steps_z = 6
    outer_rings = []
    inner_rings = []

    for i in range(steps_z + 1):
        frac = i / steps_z
        z = z_bot + frac * h_mug
        r_out = r_bot + frac * (r_top - r_bot)
        r_in = r_out - t_wall
        if frac == 1.0:
            r_out += 0.0025

        o_ring = []
        i_ring = []
        for s in range(actual_segs + (1 if cutaway else 0)):
            if cutaway:
                theta = start_angle + (end_angle - start_angle) * (s / actual_segs)
            else:
                theta = 2.0 * math.pi * (s / actual_segs)
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            vo = bm.verts.new((r_out * cos_t, r_out * sin_t, z))
            vi = bm.verts.new((r_in * cos_t, r_in * sin_t, z))
            o_ring.append(vo)
            i_ring.append(vi)
        outer_rings.append(o_ring)
        inner_rings.append(i_ring)

    # Faces for outer & inner walls
    for i in range(steps_z):
        for s in range(actual_segs):
            next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
            bm.faces.new([outer_rings[i][s], outer_rings[i][next_s], outer_rings[i+1][next_s], outer_rings[i+1][s]])
            bm.faces.new([inner_rings[i][next_s], inner_rings[i][s], inner_rings[i+1][s], inner_rings[i+1][next_s]])

    # Top rim face
    for s in range(actual_segs):
        next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
        bm.faces.new([outer_rings[-1][s], inner_rings[-1][s], inner_rings[-1][next_s], outer_rings[-1][next_s]])

    # Bottom inner floor
    floor_verts = []
    r_floor = r_bot - t_wall
    for s in range(actual_segs + (1 if cutaway else 0)):
        if cutaway:
            theta = start_angle + (end_angle - start_angle) * (s / actual_segs)
        else:
            theta = 2.0 * math.pi * (s / actual_segs)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        vf = bm.verts.new((r_floor * 0.4 * cos_t, r_floor * 0.4 * sin_t, z_bot + t_wall))
        floor_verts.append(vf)

    for s in range(actual_segs):
        next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
        bm.faces.new([inner_rings[0][s], inner_rings[0][next_s], floor_verts[next_s], floor_verts[s]])

    center_v = bm.verts.new((0.0, 0.0, z_bot + t_wall))
    for s in range(actual_segs):
        next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
        bm.faces.new([floor_verts[s], floor_verts[next_s], center_v])

    # Bottom outer base
    base_center = bm.verts.new((0.0, 0.0, z_bot))
    for s in range(actual_segs):
        next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
        bm.faces.new([base_center, outer_rings[0][next_s], outer_rings[0][s]])

    # Cut slice caps
    if cutaway:
        for i in range(steps_z):
            bm.faces.new([outer_rings[i][0], outer_rings[i+1][0], inner_rings[i+1][0], inner_rings[i][0]])
            bm.faces.new([outer_rings[i][-1], inner_rings[i][-1], inner_rings[i+1][-1], outer_rings[i+1][-1]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return mesh

def create_handle_mesh(name):
    """Creates a smooth curved lab mug handle positioned on the +X side (away from cutaway)."""
    bm = bmesh.new()
    handle_pts = [
        Vector((0.048, 0.0, 0.096)),
        Vector((0.076, 0.0, 0.092)),
        Vector((0.082, 0.0, 0.065)),
        Vector((0.076, 0.0, 0.038)),
        Vector((0.046, 0.0, 0.034))
    ]
    w, t = 0.006, 0.003
    cross_profile = [Vector((0, -w/2, -t/2)), Vector((0, w/2, -t/2)),
                     Vector((0, w/2, t/2)), Vector((0, -w/2, t/2))]

    rings = []
    samples = 16
    for step in range(samples + 1):
        u = step / samples
        p = (1-u)**4 * handle_pts[0] + 4*(1-u)**3*u * handle_pts[1] + 6*(1-u)**2*u**2 * handle_pts[2] + 4*(1-u)*u**3 * handle_pts[3] + u**4 * handle_pts[4]
        if step < samples:
            u_next = (step + 0.01) / samples
            p_next = (1-u_next)**4 * handle_pts[0] + 4*(1-u_next)**3*u_next * handle_pts[1] + 6*(1-u_next)**2*u_next**2 * handle_pts[2] + 4*(1-u_next)*u_next**3 * handle_pts[3] + u_next**4 * handle_pts[4]
            tangent = (p_next - p).normalized()
        else:
            tangent = Vector((-1.0, 0.0, -0.2)).normalized()

        normal = Vector((0.0, 1.0, 0.0))
        binormal = tangent.cross(normal).normalized()

        ring = []
        for cp in cross_profile:
            pos = p + cp.y * normal + cp.z * binormal
            ring.append(bm.verts.new(pos))
        rings.append(ring)

    for i in range(samples):
        for j in range(4):
            nj = (j + 1) % 4
            bm.faces.new([rings[i][j], rings[i][nj], rings[i+1][nj], rings[i+1][j]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return mesh

def build_inverted_tube(prefix, x_pos, gas_type, gas_headspace, num_bubbles, col, mat_glass, mat_water, mat_meniscus, mat_gas, mat_grad):
    """
    Constructs an inverted borosilicate test tube over the electrode.
    Stoichiometrically accurate:
    - O2 (Anode, x=-0.024): 1 volume unit gas headspace (gas_headspace = 0.022 m)
    - H2 (Cathode, x=+0.024): 2 volume units gas headspace (gas_headspace = 0.044 m)
    """
    objs = []
    r_tube = 0.0095
    t_tube = 0.0012
    h_tube = 0.135
    z_lip = 0.024
    z_dome = z_lip + h_tube

    # 1. Glass tube body
    tube_profile = [
        (0.000, z_dome),
        (r_tube * 0.85, z_dome - 0.002),
        (r_tube, z_dome - 0.006),
        (r_tube, z_lip + 0.003),
        (r_tube + 0.0012, z_lip),
        (r_tube - t_tube, z_lip),
        (r_tube - t_tube, z_dome - 0.006),
        (0.000, z_dome - t_tube - 0.004)
    ]
    tube_glass = kit.lathe_object(f"{prefix}-glass", tube_profile, segments=36, material=mat_glass, location=(x_pos, 0.0, 0.0))
    link_strictly(tube_glass, col)
    objs.append(tube_glass)

    # 2. Water column inside inverted tube
    z_meniscus = z_dome - gas_headspace
    water_col_h = max(0.01, z_meniscus - z_lip)
    water_col_z = z_lip + water_col_h * 0.5
    w_inner = kit.primitive_object(
        f"{prefix}-water-col", "cylinder", mat_water,
        size=( (r_tube - t_tube)*2, (r_tube - t_tube)*2, water_col_h ),
        location=(x_pos, 0.0, water_col_z)
    )
    link_strictly(w_inner, col)
    objs.append(w_inner)

    # 3. Gas-liquid meniscus disc
    meniscus = kit.primitive_object(
        f"{prefix}-meniscus", "cylinder", mat_meniscus,
        size=( (r_tube - t_tube)*1.98, (r_tube - t_tube)*1.98, 0.0018 ),
        location=(x_pos, 0.0, z_meniscus)
    )
    link_strictly(meniscus, col)
    objs.append(meniscus)

    # 4. Luminescent gaseous headspace volume
    gas_vol_h = gas_headspace
    gas_vol_z = z_dome - gas_vol_h * 0.5
    gas_vol = kit.primitive_object(
        f"{prefix}-gas-headspace", "cylinder", mat_gas,
        size=( (r_tube - t_tube)*1.9, (r_tube - t_tube)*1.9, gas_vol_h ),
        location=(x_pos, 0.0, gas_vol_z)
    )
    link_strictly(gas_vol, col)
    objs.append(gas_vol)

    # 5. Graduation lines
    for g in range(6):
        gz = z_lip + 0.020 + g * 0.018
        if gz < z_dome - 0.008:
            tick = kit.primitive_object(
                f"{prefix}-grad-{g}", "cylinder", mat_grad,
                size=(r_tube * 2.05, r_tube * 2.05, 0.0009),
                location=(x_pos, 0.0, gz)
            )
            link_strictly(tick, col)
            objs.append(tick)

    # 6. Stream of rising gas bubbles
    mat_bub = kit.add_material(f"mat-bub-{gas_type}", (0.95, 0.98, 1.0), roughness=0.04, transmission=0.88)
    for b in range(num_bubbles):
        b_frac = (b + 0.5) / num_bubbles
        bz = z_lip + 0.015 + b_frac * (water_col_h - 0.018)
        rad_offset = 0.0035 * math.sin(b * 2.5)
        bx = x_pos + rad_offset
        by = 0.0035 * math.cos(b * 2.5)
        bub_r = 0.0015 + 0.0008 * (b / num_bubbles)
        bub = kit.primitive_object(
            f"{prefix}-bubble-{b}", "uv_sphere", mat_bub,
            size=(bub_r*2, bub_r*2, bub_r*2),
            location=(bx, by, bz)
        )
        link_strictly(bub, col)
        objs.append(bub)

    return objs

def build_battery_and_circuit(prefix, col, mat_battery, mat_term_red, mat_term_black, mat_brass, mat_wire_red, mat_wire_black):
    """
    Constructs a 6V DC Laboratory Battery pack, knife switch, and connecting wires.
    """
    objs = []
    bat_loc = Vector((0.0, -0.078, 0.022))
    bat_box = kit.primitive_object(
        f"{prefix}-battery-body", "cube", mat_battery,
        size=(0.068, 0.042, 0.036),
        location=bat_loc
    )
    link_strictly(bat_box, col)
    objs.append(bat_box)

    bat_lid = kit.primitive_object(
        f"{prefix}-battery-lid", "cube", mat_term_black,
        size=(0.070, 0.044, 0.005),
        location=bat_loc + Vector((0, 0, 0.020))
    )
    link_strictly(bat_lid, col)
    objs.append(bat_lid)

    # Battery Terminal Posts
    term_p = kit.primitive_object(
        f"{prefix}-bat-term-pos", "cylinder", mat_term_red,
        size=(0.007, 0.007, 0.012),
        location=bat_loc + Vector((-0.022, 0.0, 0.026))
    )
    term_n = kit.primitive_object(
        f"{prefix}-bat-term-neg", "cylinder", mat_term_black,
        size=(0.007, 0.007, 0.012),
        location=bat_loc + Vector((0.022, 0.0, 0.026))
    )
    link_strictly(term_p, col)
    link_strictly(term_n, col)
    objs.extend([term_p, term_n])

    for t_obj in [term_p, term_n]:
        nut = kit.primitive_object(
            f"{t_obj.name}-nut", "cylinder", mat_brass,
            size=(0.009, 0.009, 0.0035),
            location=t_obj.location + Vector((0, 0, 0.003))
        )
        link_strictly(nut, col)
        objs.append(nut)

    # Plug Key Switch
    sw_loc = Vector((0.068, -0.040, 0.010))
    sw_base = kit.primitive_object(
        f"{prefix}-switch-base", "cube", mat_term_black,
        size=(0.034, 0.020, 0.007),
        location=sw_loc
    )
    link_strictly(sw_base, col)
    objs.append(sw_base)

    sw_c1 = kit.primitive_object(f"{prefix}-sw-c1", "cube", mat_brass, size=(0.008, 0.012, 0.007), location=sw_loc + Vector((-0.009, 0, 0.005)))
    sw_c2 = kit.primitive_object(f"{prefix}-sw-c2", "cube", mat_brass, size=(0.008, 0.012, 0.007), location=sw_loc + Vector((0.009, 0, 0.005)))
    sw_plug = kit.primitive_object(f"{prefix}-sw-plug", "cylinder", mat_brass, size=(0.005, 0.005, 0.014), location=sw_loc + Vector((0, 0, 0.009)))
    link_strictly(sw_c1, col)
    link_strictly(sw_c2, col)
    link_strictly(sw_plug, col)
    objs.extend([sw_c1, sw_c2, sw_plug])

    # Connecting Wires
    w1_pts = [
        Vector((-0.024, 0.0, 0.006)),
        Vector((-0.042, -0.025, 0.006)),
        Vector((-0.045, -0.060, 0.008)),
        Vector((-0.022, -0.078, 0.042))
    ]
    w1 = kit.create_smooth_tube(f"{prefix}-wire-anode", w1_pts, radius=0.0015, material=mat_wire_red)
    link_strictly(w1, col)
    objs.append(w1)

    w2_pts = [
        Vector((0.024, 0.0, 0.006)),
        Vector((0.046, -0.015, 0.006)),
        Vector((0.059, -0.040, 0.014))
    ]
    w2 = kit.create_smooth_tube(f"{prefix}-wire-cathode-sw", w2_pts, radius=0.0015, material=mat_wire_black)
    link_strictly(w2, col)
    objs.append(w2)

    w3_pts = [
        Vector((0.077, -0.040, 0.014)),
        Vector((0.068, -0.065, 0.008)),
        Vector((0.045, -0.080, 0.010)),
        Vector((0.022, -0.078, 0.042))
    ]
    w3 = kit.create_smooth_tube(f"{prefix}-wire-sw-bat", w3_pts, radius=0.0015, material=mat_wire_black)
    link_strictly(w3, col)
    objs.append(w3)

    return objs

def build_electrolysis_full(col):
    """Constructs the complete 3D apparatus for Electrolysis_Apparatus_Full collection."""
    objs = []
    # Materials
    mat_plinth    = kit.add_material("elec-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_mug       = kit.add_glass_material("elec-mug", tint=COLOR_PLASTIC_MUG, ior=1.45, roughness=0.08, transmission=0.88)
    mat_water     = kit.add_material("elec-water", COLOR_WATER, roughness=0.03, transmission=0.92, ior=1.333)
    mat_glass     = kit.add_glass_material("elec-tube-glass", tint=COLOR_GLASS_TUBE, ior=1.517, roughness=0.02, transmission=0.95)
    mat_meniscus  = kit.add_material("elec-meniscus", (0.85, 0.95, 1.0), roughness=0.08, transmission=0.75)
    mat_graphite  = kit.add_material("elec-graphite", COLOR_GRAPHITE, metallic=0.15, roughness=0.75)
    mat_rubber    = kit.add_material("elec-rubber", COLOR_RUBBER, metallic=0.02, roughness=0.88)
    mat_battery   = kit.add_material("elec-battery", COLOR_BATTERY, metallic=0.10, roughness=0.40)
    mat_term_red  = kit.add_material("elec-term-red", COLOR_TERM_RED, metallic=0.20, roughness=0.30)
    mat_term_black= kit.add_material("elec-term-black", COLOR_TERM_BLACK, metallic=0.20, roughness=0.30)
    mat_brass     = kit.add_material("elec-brass", COLOR_BRASS, metallic=0.85, roughness=0.25)
    mat_wire_red  = kit.add_material("elec-wire-red", COLOR_WIRE_RED, metallic=0.05, roughness=0.35)
    mat_wire_black= kit.add_material("elec-wire-black", COLOR_WIRE_BLACK, metallic=0.05, roughness=0.35)
    mat_enamel    = kit.add_material("elec-enamel", COLOR_ENAMEL, metallic=0.0, roughness=0.30)
    mat_gas_h2    = create_emissive_mat("elec-gas-h2", COLOR_GAS_H2, strength=3.0)
    mat_gas_o2    = create_emissive_mat("elec-gas-o2", COLOR_GAS_O2, strength=2.8)

    # 1. Exhibition Lab Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-plinth", "cube", mat_plinth,
        size=(0.240, 0.210, 0.016),
        location=(0.0, -0.015, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    # 2. Translucent Polypropylene Mug Body & Handle
    mug_mesh = create_plastic_mug_mesh(f"{ASSET_ID}-mug-mesh", cutaway=False)
    mug_obj = bpy.data.objects.new(f"{ASSET_ID}-mug", mug_mesh)
    mug_obj.data.materials.append(mat_mug)
    col.objects.link(mug_obj)
    objs.append(mug_obj)

    handle_mesh = create_handle_mesh(f"{ASSET_ID}-handle-mesh")
    handle_obj = bpy.data.objects.new(f"{ASSET_ID}-handle", handle_mesh)
    handle_obj.data.materials.append(mat_mug)
    col.objects.link(handle_obj)
    objs.append(handle_obj)

    # Measurement graduations
    for m in range(1, 5):
        mz = 0.024 + m * 0.018
        mr = 0.046 + (mz - 0.016) / 0.108 * 0.006
        mark = kit.primitive_object(
            f"{ASSET_ID}-mug-grad-{m}", "cylinder", mat_enamel,
            size=(mr * 2.015, mr * 2.015, 0.0006),
            location=(0.0, 0.0, mz)
        )
        link_strictly(mark, col)
        objs.append(mark)

    # 3. Acidified Water Liquid Bulk in Mug
    water_bulk = kit.primitive_object(
        f"{ASSET_ID}-water-bulk", "cylinder", mat_water,
        size=(0.088, 0.088, 0.068),
        location=(0.0, 0.0, 0.054)
    )
    link_strictly(water_bulk, col)
    objs.append(water_bulk)

    # 4. Rubber Stoppers sealing base holes
    for x_pos, name in [(-0.024, "anode"), (0.024, "cathode")]:
        stopper = kit.primitive_object(
            f"{ASSET_ID}-stopper-{name}", "cylinder", mat_rubber,
            size=(0.017, 0.017, 0.018),
            location=(x_pos, 0.0, 0.016)
        )
        link_strictly(stopper, col)
        objs.append(stopper)

        t_screw = kit.primitive_object(
            f"{ASSET_ID}-screw-{name}", "cylinder", mat_brass,
            size=(0.006, 0.006, 0.010),
            location=(x_pos, 0.0, 0.005)
        )
        link_strictly(t_screw, col)
        objs.append(t_screw)

    # 5. Graphite Carbon Rod Electrodes
    for x_pos, name in [(-0.024, "anode"), (0.024, "cathode")]:
        rod = kit.primitive_object(
            f"{ASSET_ID}-electrode-{name}", "cylinder", mat_graphite,
            size=(0.007, 0.007, 0.066),
            location=(x_pos, 0.0, 0.052)
        )
        link_strictly(rod, col)
        objs.append(rod)

    # 6. Inverted Graduated Test Tubes (2:1 Stoichiometric Ratio)
    # Anode: Oxygen (1x Vol = 0.022m)
    t_anode_objs = build_inverted_tube(
        f"{ASSET_ID}-anode", -0.024, "O2", 0.022, 5, col,
        mat_glass, mat_water, mat_meniscus, mat_gas_o2, mat_enamel
    )
    objs.extend(t_anode_objs)

    # Cathode: Hydrogen (2x Vol = 0.044m)
    t_cathode_objs = build_inverted_tube(
        f"{ASSET_ID}-cathode", 0.024, "H2", 0.044, 11, col,
        mat_glass, mat_water, mat_meniscus, mat_gas_h2, mat_enamel
    )
    objs.extend(t_cathode_objs)

    # 7. Battery & Circuit
    circuit_objs = build_battery_and_circuit(
        ASSET_ID, col, mat_battery, mat_term_red, mat_term_black, mat_brass, mat_wire_red, mat_wire_black
    )
    objs.extend(circuit_objs)

    return objs

def build_electrolysis_section(col):
    """
    Constructs the longitudinal cutaway collection revealing:
    - Internal rubber stopper cross-section and drilled bore.
    - Seated graphite electrode.
    - Water column cutaway showing bubble nucleation on the rod.
    - 2:1 Volumetric Gas Displacement calipers.
    - Chemical reaction plaque: 2H2O -> 2H2 + O2.
    - Gas test badges: Cathode (Pop sound) & Anode (Glowing splint).
    """
    objs = []
    # Materials
    mat_plinth    = kit.add_material("sec-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_mug       = kit.add_glass_material("sec-mug", tint=COLOR_PLASTIC_MUG, ior=1.45, roughness=0.08, transmission=0.88)
    mat_water     = kit.add_material("sec-water", COLOR_WATER, roughness=0.03, transmission=0.92, ior=1.333)
    mat_glass     = kit.add_glass_material("sec-tube-glass", tint=COLOR_GLASS_TUBE, ior=1.517, roughness=0.02, transmission=0.95)
    mat_meniscus  = kit.add_material("sec-meniscus", (0.85, 0.95, 1.0), roughness=0.08, transmission=0.75)
    mat_graphite  = kit.add_material("sec-graphite", COLOR_GRAPHITE, metallic=0.15, roughness=0.75)
    mat_rubber    = kit.add_material("sec-rubber", COLOR_RUBBER, metallic=0.02, roughness=0.88)
    mat_battery   = kit.add_material("sec-battery", COLOR_BATTERY, metallic=0.10, roughness=0.40)
    mat_term_red  = kit.add_material("sec-term-red", COLOR_TERM_RED, metallic=0.20, roughness=0.30)
    mat_term_black= kit.add_material("sec-term-black", COLOR_TERM_BLACK, metallic=0.20, roughness=0.30)
    mat_brass     = kit.add_material("sec-brass", COLOR_BRASS, metallic=0.85, roughness=0.25)
    mat_wire_red  = kit.add_material("sec-wire-red", COLOR_WIRE_RED, metallic=0.05, roughness=0.35)
    mat_wire_black= kit.add_material("sec-wire-black", COLOR_WIRE_BLACK, metallic=0.05, roughness=0.35)
    mat_enamel    = kit.add_material("sec-enamel", COLOR_ENAMEL, metallic=0.0, roughness=0.30)
    mat_gas_h2    = create_emissive_mat("sec-gas-h2", COLOR_GAS_H2, strength=3.5)
    mat_gas_o2    = create_emissive_mat("sec-gas-o2", COLOR_GAS_O2, strength=3.2)
    mat_flame     = create_emissive_mat("sec-flame", COLOR_FLAME, strength=7.0)
    mat_cut_edge  = kit.add_material("sec-cutedge", (0.95, 0.65, 0.15), metallic=0.1, roughness=0.3)

    # 1. Base Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-sec-plinth", "cube", mat_plinth,
        size=(0.240, 0.210, 0.016),
        location=(0.0, -0.015, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    # 2. Cutaway Mug Body (front quadrant removed)
    mug_mesh = create_plastic_mug_mesh(f"{ASSET_ID}-sec-mug-mesh", cutaway=True)
    mug_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-mug", mug_mesh)
    mug_obj.data.materials.append(mat_mug)
    col.objects.link(mug_obj)
    objs.append(mug_obj)

    handle_mesh = create_handle_mesh(f"{ASSET_ID}-sec-handle-mesh")
    handle_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-handle", handle_mesh)
    handle_obj.data.materials.append(mat_mug)
    col.objects.link(handle_obj)
    objs.append(handle_obj)

    # 3. Water Bulk (Cutaway matching mug)
    wb_mesh = bmesh.new()
    wb_segs = 36
    r_wb = 0.043
    h_wb = 0.068
    z_wb_bot = 0.019
    for s in range(wb_segs + 1):
        theta = -0.5 * math.pi + (1.5 * math.pi) * (s / wb_segs)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        wb_mesh.verts.new((r_wb * cos_t, r_wb * sin_t, z_wb_bot))
        wb_mesh.verts.new((r_wb * cos_t, r_wb * sin_t, z_wb_bot + h_wb))
    center_bot = wb_mesh.verts.new((0.0, 0.0, z_wb_bot))
    center_top = wb_mesh.verts.new((0.0, 0.0, z_wb_bot + h_wb))
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
    wb_m = bpy.data.meshes.new(f"{ASSET_ID}-sec-water-mesh")
    wb_mesh.to_mesh(wb_m)
    wb_mesh.free()
    for poly in wb_m.polygons:
        poly.use_smooth = True
    wb_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-water-bulk", wb_m)
    wb_obj.data.materials.append(mat_water)
    col.objects.link(wb_obj)
    objs.append(wb_obj)

    # 4. Rubber Stoppers & Electrodes
    for x_pos, name in [(-0.024, "anode"), (0.024, "cathode")]:
        stopper = kit.primitive_object(
            f"{ASSET_ID}-sec-stopper-{name}", "cylinder", mat_rubber,
            size=(0.017, 0.017, 0.018),
            location=(x_pos, 0.0, 0.016)
        )
        link_strictly(stopper, col)
        objs.append(stopper)

        rod = kit.primitive_object(
            f"{ASSET_ID}-sec-electrode-{name}", "cylinder", mat_graphite,
            size=(0.007, 0.007, 0.066),
            location=(x_pos, 0.0, 0.052)
        )
        link_strictly(rod, col)
        objs.append(rod)

        screw = kit.primitive_object(
            f"{ASSET_ID}-sec-screw-{name}", "cylinder", mat_brass,
            size=(0.006, 0.006, 0.010),
            location=(x_pos, 0.0, 0.005)
        )
        link_strictly(screw, col)
        objs.append(screw)

    # 5. Inverted Test Tubes
    t_anode_objs = build_inverted_tube(
        f"{ASSET_ID}-sec-anode", -0.024, "O2", 0.022, 6, col,
        mat_glass, mat_water, mat_meniscus, mat_gas_o2, mat_enamel
    )
    objs.extend(t_anode_objs)

    t_cathode_objs = build_inverted_tube(
        f"{ASSET_ID}-sec-cathode", 0.024, "H2", 0.044, 12, col,
        mat_glass, mat_water, mat_meniscus, mat_gas_h2, mat_enamel
    )
    objs.extend(t_cathode_objs)

    # 6. Battery & Circuit
    circuit_objs = build_battery_and_circuit(
        f"{ASSET_ID}-sec", col, mat_battery, mat_term_red, mat_term_black, mat_brass, mat_wire_red, mat_wire_black
    )
    objs.extend(circuit_objs)

    # 7. Pedagogical Caliper Brackets
    z_dome = 0.024 + 0.135
    caliper_o2 = kit.create_smooth_tube(
        f"{ASSET_ID}-sec-caliper-o2",
        [Vector((-0.038, 0.0, z_dome)), Vector((-0.042, 0.0, z_dome)),
         Vector((-0.042, 0.0, z_dome - 0.022)), Vector((-0.038, 0.0, z_dome - 0.022))],
        radius=0.0012, material=mat_gas_o2
    )
    link_strictly(caliper_o2, col)
    objs.append(caliper_o2)

    caliper_h2 = kit.create_smooth_tube(
        f"{ASSET_ID}-sec-caliper-h2",
        [Vector((0.038, 0.0, z_dome)), Vector((0.042, 0.0, z_dome)),
         Vector((0.042, 0.0, z_dome - 0.044)), Vector((0.038, 0.0, z_dome - 0.044))],
        radius=0.0012, material=mat_gas_h2
    )
    link_strictly(caliper_h2, col)
    objs.append(caliper_h2)

    # 8. Chemical Equation Plaque Banner
    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-bg", "cube", mat_term_black,
        size=(0.140, 0.004, 0.024),
        location=(0.0, 0.055, 0.150)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-trim", "cube", mat_cut_edge,
        size=(0.144, 0.005, 0.002),
        location=(0.0, 0.055, 0.163)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    # 9. Gas Identification Test Icons
    splint_h2 = kit.primitive_object(
        f"{ASSET_ID}-sec-splint-h2", "cylinder", mat_brass,
        size=(0.002, 0.002, 0.036),
        location=(0.038, 0.0, 0.170),
        rotation_euler=(0.0, 0.5, 0.0)
    )
    link_strictly(splint_h2, col)
    objs.append(splint_h2)

    flame_h2 = kit.primitive_object(
        f"{ASSET_ID}-sec-flame-h2", "uv_sphere", mat_flame,
        size=(0.008, 0.008, 0.014),
        location=(0.028, 0.0, 0.182)
    )
    link_strictly(flame_h2, col)
    objs.append(flame_h2)

    pop_ring = kit.lathe_object(
        f"{ASSET_ID}-sec-pop-ring",
        [(0.008, 0.0), (0.014, 0.001), (0.016, 0.0), (0.014, -0.001)],
        segments=24, material=mat_flame,
        location=(0.028, 0.0, 0.182),
        rotation_euler=(0.3, 0.0, 0.0)
    )
    link_strictly(pop_ring, col)
    objs.append(pop_ring)

    splint_o2 = kit.primitive_object(
        f"{ASSET_ID}-sec-splint-o2", "cylinder", mat_brass,
        size=(0.002, 0.002, 0.036),
        location=(-0.038, 0.0, 0.170),
        rotation_euler=(0.0, -0.5, 0.0)
    )
    link_strictly(splint_o2, col)
    objs.append(splint_o2)

    ember_o2 = kit.primitive_object(
        f"{ASSET_ID}-sec-ember-o2", "uv_sphere", mat_gas_o2,
        size=(0.005, 0.005, 0.008),
        location=(-0.028, 0.0, 0.182)
    )
    link_strictly(ember_o2, col)
    objs.append(ember_o2)

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

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    col_full = bpy.data.collections.new("Electrolysis_Apparatus_Full")
    col_sec  = bpy.data.collections.new("Electrolysis_Apparatus_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_electrolysis_full(col_full)
    sec_objs  = build_electrolysis_section(col_sec)

    # Set up Camera
    cam_data = bpy.data.cameras.new("Electrolysis_Camera")
    cam_data.lens = 50.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Electrolysis_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Save Blend file
    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    # Export GLB with both collections active
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    # Sync GLB to interactive viewer
    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    # Render Preview 1: Full Apparatus
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.015, 0.088)), distance=0.52, elev_deg=22, azim_deg=-28)
    kit.configure_render(width=1280, height=720, samples=24)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section View
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.095)), distance=0.52, elev_deg=20, azim_deg=-25)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== WATER ELECTROLYSIS APPARATUS BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
