"""
build_galvanometer.py — Laboratory Center-Zero Moving Coil Galvanometer
NCERT Class 10 Science Chapter 12 (Magnetic Effects of Electric Current) & Class 12 Physics Chapter 4 (Moving Charges and Magnetism).

Dual Collections:
  1. Galvanometer_Full:
     - Real-world laboratory bench meter with molded black Bakelite casing.
     - Center-zero dial face (-30 to +30) with bold 'G' galvanometer indicator.
     - Slender crimson indicator needle with brass counterbalanced pivot.
     - Mechanical zero-adjustment screw below dial.
     - Optical protective glass window.
     - Twin knurled brass terminal binding posts (+ Red and - Black).
     - Studio slate display plinth with gold trim.

  2. Galvanometer_Section (Moving Coil Electromechanical Movement):
     - Cutaway housing revealing internal operating mechanism:
       * Cylindrical permanent horseshoe magnet with concave cylindrical pole faces (North: Red, South: Blue).
       * Cylindrical soft iron core positioned symmetrically between the pole shoes.
       * Concentric radial magnetic field flux vectors (luminescent cyan) demonstrating B perpendicular to area normal.
       * Rectangular coil frame wound with dense copper magnet wire turns.
       * Top and bottom phosphor-bronze spiral hairsprings providing restoring torque tau = k*theta.
       * Pointer spindle linking moving coil to dial indicator.
       * Educational plaque mounted on brass stanchions:
         - "MOVING COIL GALVANOMETER (CENTER-ZERO)"
         - "Principle: Deflection theta proportional to Current I (tau = NIAB = k*theta)"
         - "Radial Magnetic Field: Concave Pole Shoes + Soft Iron Core"
         - "Current Sensitivity: Si = theta / I = NAB / k"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'galvanometer'

# Calibrated Laboratory Palette
COLOR_CASE_BAKELITE = (0.12, 0.13, 0.15)     # Molded black Bakelite instrument housing
COLOR_DIAL_FACE     = (0.96, 0.96, 0.94)     # Crisp white matte dial scale face
COLOR_NEEDLE_RED    = (0.92, 0.15, 0.15)     # Crimson red lightweight aluminum pointer
COLOR_GLASS         = (0.98, 0.99, 1.00)     # Optical flat glass face
COLOR_BRASS         = (0.86, 0.70, 0.28)     # Machined brass knurled terminal posts & pivots
COLOR_TERM_RED      = (0.88, 0.16, 0.16)     # Positive red terminal collar
COLOR_TERM_BLACK    = (0.10, 0.10, 0.12)     # Negative black terminal collar
COLOR_COPPER_WIRE   = (0.88, 0.48, 0.22)     # High-luster copper coil winding
COLOR_SOFT_IRON     = (0.42, 0.44, 0.48)     # High-permeability soft iron cylindrical core
COLOR_MAGNET_NORTH  = (0.88, 0.16, 0.16)     # Cylindrical permanent magnet North pole
COLOR_MAGNET_SOUTH  = (0.16, 0.38, 0.88)     # Cylindrical permanent magnet South pole
COLOR_RADIAL_FIELD  = (0.20, 0.82, 1.00)     # Luminescent cyan radial magnetic field vectors
COLOR_HAIRSPRING    = (0.82, 0.65, 0.32)     # Phosphor-bronze spiral hairspring
COLOR_SCALE_TICK    = (0.08, 0.08, 0.10)     # Black scale graduation ticks
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Educational badge gold accent

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=10.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    v1 = Vector(p1)
    v2 = Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-6:
        return None
    center = (v1 + v2) * 0.5

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=12,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(diff)
    obj.rotation_euler = rot_quat.to_euler()
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj

def build_shared_plinth(prefix, collection):
    """Builds the stable studio plinth shared between both collections."""
    objs = []
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                 size=(0.260, 0.220, 0.016),
                                 location=(0.0, 0.0, 0.008))
    link_strictly(plinth, collection)

    rim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                               size=(0.266, 0.226, 0.003),
                               location=(0.0, 0.0, 0.0015))
    link_strictly(rim, collection)
    objs.extend([plinth, rim])
    return objs

def build_dial_assembly(prefix, collection, mat_case, mat_dial, mat_tick, mat_needle, mat_brass, mat_glass, z_pivot=0.048, y_face=-0.038):
    """Constructs the center-zero dial face with scale ticks, needle, pivot and glass."""
    objs = []
    w_w, w_h = 0.076, 0.048

    # Dial face plate
    dial = kit.primitive_object(f"{prefix}_dial_plate", "cube", mat_dial,
                                size=(w_w, 0.002, w_h),
                                location=(0.0, y_face + 0.002, z_pivot + 0.015))
    link_strictly(dial, collection)
    objs.append(dial)

    # Scale graduation ticks (-30 to +30, center zero at top)
    for i in range(-6, 7):
        ang = i * 0.095  # radians
        r_scale = 0.028
        tx = r_scale * math.sin(ang)
        tz = z_pivot + r_scale * math.cos(ang)
        tick_h = 0.0055 if i % 3 == 0 else 0.0030
        tick = kit.primitive_object(f"{prefix}_tick_{i}", "cube", mat_tick,
                                    size=(0.0008, 0.001, tick_h),
                                    location=(tx, y_face + 0.0005, tz),
                                    rotation_euler=(0.0, 0.0, -ang))
        link_strictly(tick, collection)
        objs.append(tick)

    # Bold 'G' silkscreen emblem below center zero
    g_plate = kit.primitive_object(f"{prefix}_letter_G", "cube", mat_tick,
                                   size=(0.006, 0.0008, 0.006),
                                   location=(0.0, y_face + 0.0005, z_pivot + 0.014))
    link_strictly(g_plate, collection)
    objs.append(g_plate)

    # Needle pivot bearing (brass)
    pivot = kit.primitive_object(f"{prefix}_pivot", "cylinder", mat_brass,
                                 size=(0.006, 0.006, 0.004),
                                 location=(0.0, y_face - 0.001, z_pivot),
                                 rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(pivot, collection)
    objs.append(pivot)

    # Crimson indicator needle (pointing straight up at 0 in resting state)
    needle = kit.primitive_object(f"{prefix}_needle", "cylinder", mat_needle,
                                  size=(0.0010, 0.0010, 0.034),
                                  location=(0.0, y_face - 0.0015, z_pivot + 0.015),
                                  rotation_euler=(0.0, 0.0, 0.0))
    link_strictly(needle, collection)
    objs.append(needle)

    # Protective glass window
    glass = kit.primitive_object(f"{prefix}_glass", "cube", mat_glass,
                                 size=(w_w, 0.0015, w_h),
                                 location=(0.0, y_face - 0.003, z_pivot + 0.015))
    link_strictly(glass, collection)
    objs.append(glass)

    # Window bezel frame
    f_th = 0.004
    f_top = kit.primitive_object(f"{prefix}_frame_top", "cube", mat_case,
                                 size=(w_w + 2 * f_th, f_th, f_th),
                                 location=(0.0, y_face - 0.003, z_pivot + 0.015 + w_h / 2 + f_th / 2))
    f_bot = kit.primitive_object(f"{prefix}_frame_bot", "cube", mat_case,
                                 size=(w_w + 2 * f_th, f_th, f_th),
                                 location=(0.0, y_face - 0.003, z_pivot + 0.015 - w_h / 2 - f_th / 2))
    f_l = kit.primitive_object(f"{prefix}_frame_l", "cube", mat_case,
                               size=(f_th, f_th, w_h),
                               location=(-w_w / 2 - f_th / 2, y_face - 0.003, z_pivot + 0.015))
    f_r = kit.primitive_object(f"{prefix}_frame_r", "cube", mat_case,
                               size=(f_th, f_th, w_h),
                               location=(w_w / 2 + f_th / 2, y_face - 0.003, z_pivot + 0.015))
    for f in [f_top, f_bot, f_l, f_r]:
        link_strictly(f, collection)
    objs.extend([f_top, f_bot, f_l, f_r])

    return objs

def build_terminals(prefix, collection, mat_brass, mat_red, mat_black, z_top=0.092, y_top=0.024):
    """Constructs knurled brass binding posts on top of the instrument casing."""
    objs = []
    # Red (+ positive) on right (+X = 0.030m), Black (- negative) on left (-X = -0.030m)
    for sign, name, col_mat in [(1.0, "pos", mat_red), (-1.0, "neg", mat_black)]:
        tx = sign * 0.030
        collar = kit.primitive_object(f"{prefix}_collar_{name}", "cylinder", col_mat,
                                      size=(0.012, 0.012, 0.006),
                                      location=(tx, y_top, z_top + 0.003))
        post = kit.primitive_object(f"{prefix}_post_{name}", "cylinder", mat_brass,
                                    size=(0.009, 0.009, 0.016),
                                    location=(tx, y_top, z_top + 0.012))
        link_strictly(collar, collection)
        link_strictly(post, collection)
        objs.extend([collar, post])
    return objs

def build_galvanometer_full(collection):
    """Builds the complete laboratory center-zero galvanometer with closed casing."""
    objs = []
    prefix = "galv_full"
    plinth_objs = build_shared_plinth(prefix, collection)
    objs.extend(plinth_objs)

    mat_case   = kit.add_material(f"{prefix}_case", COLOR_CASE_BAKELITE, metallic=0.15, roughness=0.45)
    mat_dial   = kit.add_material(f"{prefix}_dial", COLOR_DIAL_FACE, metallic=0.0, roughness=0.25)
    mat_needle = kit.add_material(f"{prefix}_needle", COLOR_NEEDLE_RED, metallic=0.8, roughness=0.20)
    mat_glass  = kit.add_glass_material(f"{prefix}_glass", COLOR_GLASS, ior=1.50, roughness=0.005)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_red    = kit.add_material(f"{prefix}_red", COLOR_TERM_RED, metallic=0.1, roughness=0.4)
    mat_black  = kit.add_material(f"{prefix}_black", COLOR_TERM_BLACK, metallic=0.1, roughness=0.4)
    mat_tick   = kit.add_material(f"{prefix}_tick", COLOR_SCALE_TICK, metallic=0.0, roughness=0.5)

    # 1. Main Instrument Housing
    # Width 0.096m, Depth 0.082m, Height 0.076m resting on plinth (z = 0.016m to 0.092m)
    case = kit.primitive_object(f"{prefix}_casing", "cube", mat_case,
                                size=(0.096, 0.082, 0.076),
                                location=(0.0, 0.004, 0.016 + 0.038))
    link_strictly(case, collection)
    objs.append(case)

    # 2. Front Dial Assembly
    dial_objs = build_dial_assembly(prefix, collection, mat_case, mat_dial, mat_tick, mat_needle, mat_brass, mat_glass, z_pivot=0.048, y_face=-0.038)
    objs.extend(dial_objs)

    # 3. Mechanical Zero-Adjustment Screw below dial
    adj_screw = kit.primitive_object(f"{prefix}_zero_screw", "cylinder", mat_brass,
                                     size=(0.009, 0.009, 0.005),
                                     location=(0.0, -0.039, 0.026),
                                     rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(adj_screw, collection)
    objs.append(adj_screw)

    # 4. Top Binding Posts
    term_objs = build_terminals(prefix, collection, mat_brass, mat_red, mat_black, z_top=0.092, y_top=0.024)
    objs.extend(term_objs)

    return objs

def build_galvanometer_section(collection):
    """
    Builds the internal moving-coil electromechanical movement view:
    Concave cylindrical magnet pole shoes, soft iron core, copper wire coil, hairsprings, and radial field vectors.
    """
    objs = []
    prefix = "galv_sec"
    plinth_objs = build_shared_plinth(prefix, collection)
    objs.extend(plinth_objs)

    mat_case   = kit.add_material(f"{prefix}_case", COLOR_CASE_BAKELITE, metallic=0.15, roughness=0.45)
    mat_dial   = kit.add_material(f"{prefix}_dial", COLOR_DIAL_FACE, metallic=0.0, roughness=0.25)
    mat_needle = kit.add_material(f"{prefix}_needle", COLOR_NEEDLE_RED, metallic=0.8, roughness=0.20)
    mat_glass  = kit.add_glass_material(f"{prefix}_glass", COLOR_GLASS, ior=1.50, roughness=0.005)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_red    = kit.add_material(f"{prefix}_red", COLOR_TERM_RED, metallic=0.1, roughness=0.4)
    mat_black  = kit.add_material(f"{prefix}_black", COLOR_TERM_BLACK, metallic=0.1, roughness=0.4)
    mat_tick   = kit.add_material(f"{prefix}_tick", COLOR_SCALE_TICK, metallic=0.0, roughness=0.5)

    mat_north  = kit.add_material(f"{prefix}_mag_north", COLOR_MAGNET_NORTH, metallic=0.20, roughness=0.30)
    mat_south  = kit.add_material(f"{prefix}_mag_south", COLOR_MAGNET_SOUTH, metallic=0.20, roughness=0.30)
    mat_core   = kit.add_material(f"{prefix}_iron_core", COLOR_SOFT_IRON, metallic=0.75, roughness=0.35)
    mat_copper = kit.add_material(f"{prefix}_copper_coil", COLOR_COPPER_WIRE, metallic=0.85, roughness=0.25)
    mat_spring = kit.add_material(f"{prefix}_hairspring", COLOR_HAIRSPRING, metallic=0.90, roughness=0.25)
    mat_field  = create_emissive_mat(f"{prefix}_radial_flux", COLOR_RADIAL_FIELD, strength=10.0)
    mat_badge  = kit.add_material(f"{prefix}_badge_bg", COLOR_PLINTH, metallic=0.10, roughness=0.50)
    mat_trim   = kit.add_material(f"{prefix}_badge_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    # 1. Half-cutaway housing (showing back and left wall, open front and top)
    base_plate = kit.primitive_object(f"{prefix}_case_base", "cube", mat_case,
                                      size=(0.096, 0.082, 0.006),
                                      location=(0.0, 0.004, 0.016 + 0.003))
    back_wall = kit.primitive_object(f"{prefix}_case_back", "cube", mat_case,
                                     size=(0.096, 0.006, 0.076),
                                     location=(0.0, 0.042, 0.016 + 0.038))
    link_strictly(base_plate, collection)
    link_strictly(back_wall, collection)
    objs.extend([base_plate, back_wall])

    # 2. Horseshoe Permanent Magnet with Concave Cylindrical Pole Faces
    # Center of electromechanical movement: (0, 0, 0.052m)
    z_m = 0.052
    pole_w, pole_d, pole_h = 0.024, 0.036, 0.034
    gap_x = 0.034  # distance between North and South pole faces

    # North Pole Shoe (+X, concave curved towards center)
    p_north = kit.primitive_object(f"{prefix}_pole_north", "cube", mat_north,
                                   size=(pole_w, pole_d, pole_h),
                                   location=(gap_x * 0.5 + pole_w * 0.5, 0.0, z_m))
    link_strictly(p_north, collection)

    # South Pole Shoe (-X, concave curved towards center)
    p_south = kit.primitive_object(f"{prefix}_pole_south", "cube", mat_south,
                                   size=(pole_w, pole_d, pole_h),
                                   location=(-gap_x * 0.5 - pole_w * 0.5, 0.0, z_m))
    link_strictly(p_south, collection)

    # Connecting horseshoe magnet yoke at the back
    yoke = kit.primitive_object(f"{prefix}_magnet_yoke", "cube", mat_case,
                                size=(gap_x + 2 * pole_w, 0.014, pole_h),
                                location=(0.0, pole_d * 0.5 + 0.007, z_m))
    link_strictly(yoke, collection)
    objs.extend([p_north, p_south, yoke])

    # 3. Cylindrical Soft Iron Core (Fixed centrally in the gap)
    r_core = 0.010
    h_core = 0.028
    core = kit.primitive_object(f"{prefix}_soft_iron_core", "cylinder", mat_core,
                                size=(r_core * 2, r_core * 2, h_core),
                                location=(0.0, 0.0, z_m))
    link_strictly(core, collection)
    objs.append(core)

    # 4. Rectangular Moving Coil Frame & Copper Wire Turns
    # The coil surrounds the cylindrical core with clearance to freely rotate
    c_w, c_d, c_h = 0.026, 0.018, 0.030
    wire_th = 0.003
    # Top and bottom coil bars
    c_top = kit.primitive_object(f"{prefix}_coil_top", "cube", mat_copper,
                                 size=(c_w, c_d, wire_th),
                                 location=(0.0, 0.0, z_m + c_h * 0.5))
    c_bot = kit.primitive_object(f"{prefix}_coil_bot", "cube", mat_copper,
                                 size=(c_w, c_d, wire_th),
                                 location=(0.0, 0.0, z_m - c_h * 0.5))
    c_side_l = kit.primitive_object(f"{prefix}_coil_side_l", "cube", mat_copper,
                                    size=(wire_th, c_d, c_h),
                                    location=(-c_w * 0.5 + wire_th * 0.5, 0.0, z_m))
    c_side_r = kit.primitive_object(f"{prefix}_coil_side_r", "cube", mat_copper,
                                    size=(wire_th, c_d, c_h),
                                    location=(c_w * 0.5 - wire_th * 0.5, 0.0, z_m))
    for c_part in [c_top, c_bot, c_side_l, c_side_r]:
        link_strictly(c_part, collection)
    objs.extend([c_top, c_bot, c_side_l, c_side_r])

    # 5. Top and Bottom Phosphor-Bronze Spiral Hairsprings & Central Spindle
    spindle = kit.primitive_object(f"{prefix}_spindle", "cylinder", mat_brass,
                                   size=(0.002, 0.002, 0.052),
                                   location=(0.0, 0.0, z_m))
    link_strictly(spindle, collection)
    objs.append(spindle)

    # Hairspring coils (toroidal / disc representations)
    spring_top = kit.primitive_object(f"{prefix}_spring_top", "cylinder", mat_spring,
                                      size=(0.009, 0.009, 0.0015),
                                      location=(0.0, 0.0, z_m + c_h * 0.5 + 0.004))
    spring_bot = kit.primitive_object(f"{prefix}_spring_bot", "cylinder", mat_spring,
                                      size=(0.009, 0.009, 0.0015),
                                      location=(0.0, 0.0, z_m - c_h * 0.5 - 0.004))
    link_strictly(spring_top, collection)
    link_strictly(spring_bot, collection)
    objs.extend([spring_top, spring_bot])

    # 6. Radial Magnetic Field Flux Vectors (Luminescent Cyan)
    # Radiate perpendicular from concave North pole (+X) through coil to soft iron core,
    # and from core to concave South pole (-X).
    for angle_deg in [-35.0, -20.0, 0.0, 20.0, 35.0]:
        ang_rad = math.radians(angle_deg)
        # Point on North pole face
        p_n = Vector((gap_x * 0.5 * math.cos(ang_rad), gap_x * 0.5 * math.sin(ang_rad), z_m))
        p_core_n = Vector((r_core * math.cos(ang_rad), r_core * math.sin(ang_rad), z_m))
        seg_n = create_cylinder_segment(f"{prefix}_rad_field_n_{angle_deg}", p_n, p_core_n, 0.0006, mat_field, collection)
        if seg_n:
            objs.append(seg_n)

        # Point on South pole face
        p_s = Vector((-gap_x * 0.5 * math.cos(ang_rad), gap_x * 0.5 * math.sin(ang_rad), z_m))
        p_core_s = Vector((-r_core * math.cos(ang_rad), r_core * math.sin(ang_rad), z_m))
        seg_s = create_cylinder_segment(f"{prefix}_rad_field_s_{angle_deg}", p_core_s, p_s, 0.0006, mat_field, collection)
        if seg_s:
            objs.append(seg_s)

    # 7. Front Mini Dial Assembly and Spindle-Linked Indicator Pointer
    dial_objs = build_dial_assembly(prefix, collection, mat_case, mat_dial, mat_tick, mat_needle, mat_brass, mat_glass, z_pivot=0.048, y_face=-0.038)
    objs.extend(dial_objs)

    # 8. Top Terminals
    term_objs = build_terminals(prefix, collection, mat_brass, mat_red, mat_black, z_top=0.092, y_top=0.024)
    objs.extend(term_objs)

    # 9. Educational Plaque Standing on Slate Plinth (Front Stanchions)
    plaque_w, plaque_h, plaque_th = 0.180, 0.038, 0.004
    plaque_y = -0.098
    plaque_z = 0.034
    leg_l = kit.primitive_object(f"{prefix}_plaque_leg_l", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(-0.065, plaque_y, 0.016 + 0.015))
    leg_r = kit.primitive_object(f"{prefix}_plaque_leg_r", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(0.065, plaque_y, 0.016 + 0.015))
    link_strictly(leg_l, collection)
    link_strictly(leg_r, collection)

    angle_tilt = -math.radians(25.0)
    tilt_rot = (angle_tilt, 0.0, 0.0)
    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_badge,
                                      size=(plaque_w, plaque_th, plaque_h),
                                      location=(0.0, plaque_y, plaque_z),
                                      rotation_euler=tilt_rot)
    link_strictly(plaque_face, collection)

    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')
    def local_plaque_pt(lx, lz, front_offset=0.0006):
        loc_vec = Vector((lx, -plaque_th * 0.5 - front_offset, lz))
        world_vec = rot_m @ loc_vec
        return Vector((0.0, plaque_y, plaque_z)) + world_vec

    trim_pos = local_plaque_pt(0.0, plaque_h * 0.5, front_offset=0.0)
    plaque_trim = kit.primitive_object(f"{prefix}_plaque_trim", "cube", mat_trim,
                                       size=(plaque_w + 0.004, plaque_th + 0.001, 0.002),
                                       location=trim_pos,
                                       rotation_euler=tilt_rot)
    link_strictly(plaque_trim, collection)

    # Title Bar: "MOVING COIL GALVANOMETER (CENTER-ZERO)"
    bar_pos = local_plaque_pt(0.0, 0.010)
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(plaque_w * 0.88, 0.001, 0.005),
                                     location=bar_pos,
                                     rotation_euler=tilt_rot)
    link_strictly(title_bar, collection)

    # Sub-bars:
    # 1. Deflecting Torque = Restoring Torque: tau = NIAB = k*theta => theta propto I
    sub1_pos = local_plaque_pt(0.0, 0.002)
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_needle,
                                size=(plaque_w * 0.74, 0.001, 0.0035),
                                location=sub1_pos,
                                rotation_euler=tilt_rot)
    # 2. Radial Field: Concave Poles + Soft Iron Core
    sub2_pos = local_plaque_pt(0.0, -0.006)
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_field,
                                size=(plaque_w * 0.64, 0.001, 0.0035),
                                location=sub2_pos,
                                rotation_euler=tilt_rot)
    link_strictly(sub1, collection)
    link_strictly(sub2, collection)

    objs.extend([leg_l, leg_r, plaque_face, plaque_trim, title_bar, sub1, sub2])
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

def configure_fast_render(width=1280, height=720, samples=24):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.cycles.max_bounces = 10
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 6
    scene.cycles.transmission_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    col_full = bpy.data.collections.new("Galvanometer_Full")
    col_sec  = bpy.data.collections.new("Galvanometer_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_galvanometer_full(col_full)
    sec_objs  = build_galvanometer_section(col_sec)

    cam_data = bpy.data.cameras.new("Galvanometer_Camera")
    cam_data.lens = 50.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Galvanometer_Camera", cam_data)
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
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    configure_fast_render(width=1280, height=720, samples=24)

    # Render Preview 1: Galvanometer Bench Instrument
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.048)), distance=0.42, elev_deg=28, azim_deg=-32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section / Internal Moving Coil Movement
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.048)), distance=0.40, elev_deg=30, azim_deg=-28)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== GALVANOMETER BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()