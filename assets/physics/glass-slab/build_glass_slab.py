"""
build_glass_slab.py — Laboratory-Grade Glass Slab Refraction & Lateral Displacement
NCERT Class 10 Science Chapter 9 (Light - Reflection and Refraction), Activity 10.10 & Fig 9.10.

Dual Collections:
  1. Glass_Slab_Full:
     - Real-world laboratory tabletop experiment setup.
     - Softwood drawing board pinned with 4 brass thumb tacks on studio slate plinth.
     - White laboratory paper with pencil tracing of slab ABCD.
     - Rectangular borosilicate glass slab (130mm x 60mm x 22mm, n = 1.52) with optical clarity.
     - Mini optical diode laser emitter module aligned along incident ray.
     - Glowing emerald laser beam (incident -> refracted inside slab -> emergent parallel).
     - Four laboratory optical mapping pins: E, F (crimson) and G, H (amber yellow) on steel needles.

  2. Glass_Slab_Section (Ray Optics Diagram):
     - Comprehensive textbook geometric optics breakdown matching NCERT Fig 9.10.
     - Same datum plinth, board, and slab elevation for seamless viewer switching.
     - Glowing incident ray, refracted ray, and emergent ray.
     - Cyan normal lines NN' at interface AB and MM' at interface CD.
     - Circular angle arcs for Angle of Incidence (i), Angle of Refraction (r), and Angle of Emergence (e).
     - Extended undeviated incident ray path.
     - Lateral displacement caliper (d) with perpendicular dimension line.
     - Studio educational plaque mounted on brass stanchions:
       * "REFRACTION THROUGH GLASS SLAB"
       * "i = e  |  Emergent Ray || Incident Ray"
       * "Lateral Shift  d = t · sin(i - r) / cos(r)"
       * "Snell's Law: sin(i)/sin(r) = n = 1.52"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'glass-slab'

# Calibrated Laboratory Palette
COLOR_GLASS         = (0.98, 0.99, 1.00)     # High-clarity optical borosilicate glass
COLOR_RAY_INCIDENT  = (0.15, 0.95, 0.35)     # Glowing emerald laser ray
COLOR_RAY_EXTEND    = (0.85, 0.85, 0.85)     # Extended original ray (dashed/grey)
COLOR_NORMAL        = (0.20, 0.80, 1.00)     # Normal line NN' (luminescent cyan)
COLOR_LATERAL_DISP  = (1.00, 0.55, 0.15)     # Lateral displacement caliper d (bright amber)
COLOR_ANGLE_ARC     = (1.00, 0.85, 0.20)     # Angle measurement arcs (i, r, e)
COLOR_PIN_RED       = (0.92, 0.18, 0.18)     # Incident pins E, F
COLOR_PIN_YELLOW    = (0.98, 0.82, 0.18)     # Emergent pins G, H
COLOR_PIN_STEEL     = (0.88, 0.90, 0.94)     # Machined steel needle shaft
COLOR_BOARD_PIN     = (0.86, 0.70, 0.28)     # Brass drawing board thumb tacks
COLOR_WOOD_BOARD    = (0.76, 0.60, 0.40)     # Softwood drawing board
COLOR_PAPER         = (0.96, 0.96, 0.94)     # White laboratory paper sheet
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Educational badge gold accent
COLOR_PENCIL        = (0.28, 0.30, 0.32)     # Graphite pencil tracing line on paper
COLOR_LASER_CASE    = (0.15, 0.16, 0.18)     # Black anodized aluminium laser pointer

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=14.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_glass_mat(name="OpticalGlass"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*COLOR_GLASS, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.005
    bsdf.inputs["IOR"].default_value = 1.52
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 1.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
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
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=16,
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

def build_optical_pin(name, location, pin_mat, head_mat, collection, height=0.024, pin_rad=0.0009, head_rad=0.0035):
    objs = []
    shaft = kit.primitive_object(f"{name}_shaft", "cylinder", pin_mat,
                                 size=(pin_rad * 2, pin_rad * 2, height),
                                 location=(location[0], location[1], location[2] + height * 0.5))
    link_strictly(shaft, collection)
    objs.append(shaft)

    head = kit.primitive_object(f"{name}_head", "uv_sphere", head_mat,
                                size=(head_rad * 2, head_rad * 2, head_rad * 2),
                                location=(location[0], location[1], location[2] + height + head_rad * 0.7))
    link_strictly(head, collection)
    objs.append(head)
    return objs

def build_angle_arc(name, center, r, start_deg, end_deg, mat, collection, segments=16):
    diff = (end_deg - start_deg) % 360.0
    if diff > 180.0:
        diff -= 360.0
    pts = []
    for s in range(segments + 1):
        frac = s / segments
        deg = start_deg + frac * diff
        rad = math.radians(deg)
        pt = Vector((center.x + r * math.cos(rad), center.y + r * math.sin(rad), center.z))
        pts.append(pt)

    curve_data = bpy.data.curves.new(name=f"{name}_data", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = 0.0009
    curve_data.bevel_resolution = 6
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('POLY')
    spline.points.add(len(pts) - 1)
    for i, pt in enumerate(pts):
        spline.points[i].co = (pt.x, pt.y, pt.z, 1.0)

    obj = bpy.data.objects.new(name, curve_data)
    obj.data.materials.append(mat)
    link_strictly(obj, collection)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    return obj

def calculate_optics_geometry():
    """
    Computes exact Snell's law refraction vectors through the glass slab.
    Slab: width = 0.130m (X: -0.065 to +0.065), thickness = 0.060m (Y: -0.030 to +0.030), height = 0.022m (Z).
    Interface 1 (AB): Y = +0.030m.
    Interface 2 (CD): Y = -0.030m.
    n1 = 1.00 (air), n2 = 1.52 (borosilicate glass).
    """
    n1, n2 = 1.00, 1.52
    angle_i = math.radians(45.0)
    angle_r = math.asin((n1 / n2) * math.sin(angle_i))
    angle_e = angle_i

    # Mid-height of slab: z = 0.038m
    z_ray = 0.038
    O = Vector((-0.018, 0.030, z_ray))

    # Incident ray direction: coming from upper-left towards O (+X, -Y)
    dir_incident = Vector((math.sin(angle_i), -math.cos(angle_i), 0.0)).normalized()
    E = O - dir_incident * 0.064
    F = O - dir_incident * 0.030
    laser_pos = O - dir_incident * 0.088

    # Refracted ray direction inside glass: bending towards normal (Y-axis)
    dir_refracted = Vector((math.sin(angle_r), -math.cos(angle_r), 0.0)).normalized()
    dy = -0.060
    dist_inside = abs(dy) / math.cos(angle_r)
    O_prime = O + dir_refracted * dist_inside  # Point of emergence on CD (Y = -0.030)

    # Emergent ray direction: bends away from normal, strictly parallel to incident ray!
    dir_emergent = dir_incident
    G = O_prime + dir_emergent * 0.030
    H = O_prime + dir_emergent * 0.064
    target_pos = O_prime + dir_emergent * 0.088

    # Extended undeviated incident ray from O
    extended_end = O + dir_incident * (dist_inside * 1.6)

    # Lateral displacement vector d (perpendicular from extended line to O_prime)
    # d = t * sin(i - r) / cos(r)
    t_slab = 0.060
    d_magnitude = t_slab * math.sin(angle_i - angle_r) / math.cos(angle_r)
    # Direction perpendicular to dir_incident in XY plane towards +X/+Y
    dir_perp = Vector((-dir_incident.y, dir_incident.x, 0.0)).normalized()
    # Foot of perpendicular on extended line from O_prime
    foot_on_extended = O_prime + dir_perp * d_magnitude

    return {
        "O": O,
        "O_prime": O_prime,
        "E": E,
        "F": F,
        "G": G,
        "H": H,
        "laser_pos": laser_pos,
        "target_pos": target_pos,
        "extended_end": extended_end,
        "foot_on_extended": foot_on_extended,
        "dir_incident": dir_incident,
        "dir_refracted": dir_refracted,
        "dir_emergent": dir_emergent,
        "angle_i": angle_i,
        "angle_r": angle_r,
        "angle_e": angle_e,
        "d_magnitude": d_magnitude,
        "z_ray": z_ray
    }

def build_shared_datum(prefix, collection):
    """Builds the stable physical tabletop datum shared by both views."""
    objs = []
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_wood   = kit.add_material(f"{prefix}_wood", COLOR_WOOD_BOARD, metallic=0.04, roughness=0.50)
    mat_paper  = kit.add_material(f"{prefix}_paper", COLOR_PAPER, metallic=0.02, roughness=0.75)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BOARD_PIN, metallic=0.92, roughness=0.25)

    # 1. Slate Display Plinth
    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                 size=(0.280, 0.230, 0.016),
                                 location=(0.0, 0.0, 0.008))
    link_strictly(plinth, collection)
    objs.append(plinth)

    # Plinth Footing Rim
    rim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                               size=(0.286, 0.236, 0.003),
                               location=(0.0, 0.0, 0.0015))
    link_strictly(rim, collection)
    objs.append(rim)

    # 2. Wooden Drawing Board
    board = kit.primitive_object(f"{prefix}_board", "cube", mat_wood,
                                 size=(0.250, 0.190, 0.010),
                                 location=(0.0, 0.0, 0.021))
    link_strictly(board, collection)
    objs.append(board)

    # 3. White Laboratory Paper Sheet
    paper = kit.primitive_object(f"{prefix}_paper", "cube", mat_paper,
                                 size=(0.220, 0.160, 0.001),
                                 location=(0.0, 0.0, 0.0265))
    link_strictly(paper, collection)
    objs.append(paper)

    # 4. Corner Drawing Board Thumb Tacks
    for tx, ty in [(-0.098, -0.070), (0.098, -0.070), (-0.098, 0.070), (0.098, 0.070)]:
        tack = kit.primitive_object(f"{prefix}_tack_{tx}_{ty}", "cylinder", mat_brass,
                                   size=(0.007, 0.007, 0.002),
                                   location=(tx, ty, 0.0275))
        link_strictly(tack, collection)
        objs.append(tack)

    return objs

def build_glass_slab_full(collection):
    """Builds the authentic classroom laboratory experiment setup."""
    objs = []
    prefix = "gs_full"
    datum_objs = build_shared_datum(prefix, collection)
    objs.extend(datum_objs)

    mat_glass  = create_glass_mat(f"{prefix}_glass")
    mat_ray    = create_emissive_mat(f"{prefix}_laser_ray", COLOR_RAY_INCIDENT, strength=16.0)
    mat_pin_r  = kit.add_material(f"{prefix}_pin_red", COLOR_PIN_RED, metallic=0.1, roughness=0.35)
    mat_pin_y  = kit.add_material(f"{prefix}_pin_yellow", COLOR_PIN_YELLOW, metallic=0.1, roughness=0.35)
    mat_needle = kit.add_material(f"{prefix}_pin_steel", COLOR_PIN_STEEL, metallic=0.92, roughness=0.20)
    mat_pencil = kit.add_material(f"{prefix}_pencil", COLOR_PENCIL, metallic=0.0, roughness=0.60)
    mat_laser  = kit.add_material(f"{prefix}_laser_case", COLOR_LASER_CASE, metallic=0.8, roughness=0.30)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_laser_brass", COLOR_BOARD_PIN, metallic=0.92, roughness=0.25)

    opt = calculate_optics_geometry()

    # 1. Pencil Outline of Slab ABCD on paper
    # Rectangle of size 0.130m x 0.060m at z = 0.0272m
    w, d = 0.130, 0.060
    pencil_lines = [
        ((-w/2, -d/2, 0.0272), (w/2, -d/2, 0.0272)),
        ((w/2, -d/2, 0.0272), (w/2, d/2, 0.0272)),
        ((w/2, d/2, 0.0272), (-w/2, d/2, 0.0272)),
        ((-w/2, d/2, 0.0272), (-w/2, -d/2, 0.0272)),
    ]
    for idx, (p1, p2) in enumerate(pencil_lines):
        seg = create_cylinder_segment(f"{prefix}_pencil_edge_{idx}", p1, p2, 0.0005, mat_pencil, collection)
        objs.append(seg)

    # 2. Rectangular Borosilicate Glass Slab ABCD
    h_slab = 0.022
    slab = kit.primitive_object(f"{prefix}_slab", "cube", mat_glass,
                                size=(0.130, 0.060, h_slab),
                                location=(0.0, 0.0, 0.027 + h_slab * 0.5))
    link_strictly(slab, collection)
    objs.append(slab)

    # 3. Mini Diode Laser Module at Incident Origin
    # Anodized barrel with brass aperture collar
    laser_dir = opt["dir_incident"]
    laser_rot = Vector((0.0, 0.0, 1.0)).rotation_difference(laser_dir).to_euler()
    laser_barrel = kit.primitive_object(f"{prefix}_laser_barrel", "cylinder", mat_laser,
                                        size=(0.012, 0.012, 0.026),
                                        location=opt["laser_pos"] - laser_dir * 0.013,
                                        rotation_euler=laser_rot)
    link_strictly(laser_barrel, collection)
    laser_collar = kit.primitive_object(f"{prefix}_laser_collar", "cylinder", mat_brass,
                                        size=(0.013, 0.013, 0.004),
                                        location=opt["laser_pos"] - laser_dir * 0.002,
                                        rotation_euler=laser_rot)
    link_strictly(laser_collar, collection)
    objs.extend([laser_barrel, laser_collar])

    # 4. Glowing Emerald Laser Beam Segments
    # (a) Incident beam: laser -> O
    r_inc = create_cylinder_segment(f"{prefix}_beam_incident", opt["laser_pos"], opt["O"], 0.0014, mat_ray, collection)
    # (b) Refracted beam inside glass: O -> O'
    r_ref = create_cylinder_segment(f"{prefix}_beam_refracted", opt["O"], opt["O_prime"], 0.0014, mat_ray, collection)
    # (c) Emergent beam: O' -> target
    r_eme = create_cylinder_segment(f"{prefix}_beam_emergent", opt["O_prime"], opt["target_pos"], 0.0014, mat_ray, collection)
    objs.extend([r_inc, r_ref, r_eme])

    # 5. Four Laboratory Optical Mapping Pins
    # Incident pins E, F (Red)
    pin_e = build_optical_pin(f"{prefix}_pin_E", (opt["E"].x, opt["E"].y, 0.027), mat_needle, mat_pin_r, collection)
    pin_f = build_optical_pin(f"{prefix}_pin_F", (opt["F"].x, opt["F"].y, 0.027), mat_needle, mat_pin_r, collection)
    # Emergent pins G, H (Yellow)
    pin_g = build_optical_pin(f"{prefix}_pin_G", (opt["G"].x, opt["G"].y, 0.027), mat_needle, mat_pin_y, collection)
    pin_h = build_optical_pin(f"{prefix}_pin_H", (opt["H"].x, opt["H"].y, 0.027), mat_needle, mat_pin_y, collection)
    objs.extend(pin_e + pin_f + pin_g + pin_h)

    return objs

def build_glass_slab_section(collection):
    """Builds the comprehensive textbook ray optics diagram matching NCERT Fig 9.10."""
    objs = []
    prefix = "gs_sec"
    datum_objs = build_shared_datum(prefix, collection)
    objs.extend(datum_objs)

    mat_glass  = create_glass_mat(f"{prefix}_glass")
    mat_ray    = create_emissive_mat(f"{prefix}_ray_inc", COLOR_RAY_INCIDENT, strength=16.0)
    mat_ext    = create_emissive_mat(f"{prefix}_ray_ext", COLOR_RAY_EXTEND, strength=5.0)
    mat_norm   = create_emissive_mat(f"{prefix}_normal", COLOR_NORMAL, strength=10.0)
    mat_d      = create_emissive_mat(f"{prefix}_lat_disp", COLOR_LATERAL_DISP, strength=14.0)
    mat_arc    = create_emissive_mat(f"{prefix}_arc", COLOR_ANGLE_ARC, strength=12.0)
    mat_badge  = kit.add_material(f"{prefix}_badge_bg", COLOR_PLINTH, metallic=0.1, roughness=0.5)
    mat_text   = kit.add_material(f"{prefix}_badge_text", (0.95, 0.95, 0.95), metallic=0.0, roughness=0.4)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_plaque_brass", COLOR_BOARD_PIN, metallic=0.92, roughness=0.25)

    opt = calculate_optics_geometry()
    ray_z = opt["z_ray"]

    # 1. Optical Glass Slab ABCD
    h_slab = 0.022
    slab = kit.primitive_object(f"{prefix}_slab", "cube", mat_glass,
                                size=(0.130, 0.060, h_slab),
                                location=(0.0, 0.0, 0.027 + h_slab * 0.5))
    link_strictly(slab, collection)
    objs.append(slab)

    # 2. Ray Optics Paths
    # (a) Incident beam: E -> O
    r_inc = create_cylinder_segment(f"{prefix}_ray_inc", opt["laser_pos"] + opt["dir_incident"] * 0.015, opt["O"], 0.0014, mat_ray, collection)
    # (b) Refracted beam: O -> O'
    r_ref = create_cylinder_segment(f"{prefix}_ray_ref", opt["O"], opt["O_prime"], 0.0014, mat_ray, collection)
    # (c) Emergent beam: O' -> target
    r_eme = create_cylinder_segment(f"{prefix}_ray_eme", opt["O_prime"], opt["target_pos"], 0.0014, mat_ray, collection)
    objs.extend([r_inc, r_ref, r_eme])

    # (d) Extended undeviated original incident ray from O
    r_ext = create_cylinder_segment(f"{prefix}_ray_ext", opt["O"], opt["extended_end"], 0.0009, mat_ext, collection)
    objs.append(r_ext)

    # 3. Normal Lines NN' (at interface AB / point O) and MM' (at interface CD / point O')
    # Normals lie strictly along the Y axis perpendicular to interfaces
    n1_top = opt["O"] + Vector((0.0, 0.028, 0.0))
    n1_bot = opt["O"] - Vector((0.0, 0.024, 0.0))
    norm1 = create_cylinder_segment(f"{prefix}_norm_NN", n1_bot, n1_top, 0.0008, mat_norm, collection)

    n2_top = opt["O_prime"] + Vector((0.0, 0.024, 0.0))
    n2_bot = opt["O_prime"] - Vector((0.0, 0.028, 0.0))
    norm2 = create_cylinder_segment(f"{prefix}_norm_MM", n2_bot, n2_top, 0.0008, mat_norm, collection)
    objs.extend([norm1, norm2])

    # 4. Circular Angle Measurement Arcs
    # (a) Angle of Incidence (i) at O: between normal (+Y: 90 deg) and incoming incident ray (-dir_incident: 135 deg)
    arc_i = build_angle_arc(f"{prefix}_arc_i", opt["O"], 0.014, 90.0, 135.0, mat_arc, collection)
    # (b) Angle of Refraction (r) at O: between normal (-Y: 270 deg) and refracted ray (dir_refracted: ~297.7 deg)
    ref_deg = math.degrees(math.atan2(opt["dir_refracted"].y, opt["dir_refracted"].x))
    arc_r = build_angle_arc(f"{prefix}_arc_r", opt["O"], 0.014, 270.0, ref_deg, mat_arc, collection)
    # (c) Angle of Emergence (e) at O': between normal (-Y: 270 deg) and emergent ray (dir_emergent: 315 deg)
    arc_e = build_angle_arc(f"{prefix}_arc_e", opt["O_prime"], 0.014, 270.0, 315.0, mat_arc, collection)
    objs.extend([arc_i, arc_r, arc_e])

    # 5. Lateral Displacement Dimension Line & Caliper d
    # Perpendicular line from foot_on_extended to O_prime
    line_d = create_cylinder_segment(f"{prefix}_line_d", opt["foot_on_extended"], opt["O_prime"], 0.0012, mat_d, collection)
    # Dimension label badge 'd'
    d_mid = (opt["foot_on_extended"] + opt["O_prime"]) * 0.5 + Vector((0.004, -0.004, 0.0))
    badge_d = kit.primitive_object(f"{prefix}_badge_d", "cube", mat_d,
                                   size=(0.010, 0.004, 0.008),
                                   location=d_mid)
    link_strictly(badge_d, collection)
    objs.extend([line_d, badge_d])

    # 6. Educational Plaque Standing on Slate Plinth (Front Stanchions)
    plaque_w, plaque_h, plaque_th = 0.170, 0.038, 0.004
    plaque_y = -0.098
    plaque_z = 0.034
    leg_l = kit.primitive_object(f"{prefix}_plaque_leg_l", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(-0.060, plaque_y, 0.016 + 0.015))
    leg_r = kit.primitive_object(f"{prefix}_plaque_leg_r", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(0.060, plaque_y, 0.016 + 0.015))
    link_strictly(leg_l, collection)
    link_strictly(leg_r, collection)

    # Angled Plaque Face (tilted back 25 deg towards camera)
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

    # Gold rim along top of plaque
    trim_pos = local_plaque_pt(0.0, plaque_h * 0.5, front_offset=0.0)
    plaque_gold_trim = kit.primitive_object(f"{prefix}_plaque_trim", "cube", mat_brass,
                                           size=(plaque_w + 0.004, plaque_th + 0.001, 0.002),
                                           location=trim_pos,
                                           rotation_euler=tilt_rot)
    link_strictly(plaque_gold_trim, collection)

    # Silkscreen Title Bar: "REFRACTION THROUGH GLASS SLAB"
    bar_pos = local_plaque_pt(0.0, 0.010)
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_d,
                                     size=(plaque_w * 0.88, 0.001, 0.005),
                                     location=bar_pos,
                                     rotation_euler=tilt_rot)
    link_strictly(title_bar, collection)

    # Sub-bars representing Formula Blocks
    sub1_pos = local_plaque_pt(0.0, 0.002)
    sub_bar1 = kit.primitive_object(f"{prefix}_formula_bar1", "cube", mat_norm,
                                    size=(plaque_w * 0.72, 0.001, 0.0035),
                                    location=sub1_pos,
                                    rotation_euler=tilt_rot)
    sub2_pos = local_plaque_pt(0.0, -0.006)
    sub_bar2 = kit.primitive_object(f"{prefix}_formula_bar2", "cube", mat_ray,
                                    size=(plaque_w * 0.60, 0.001, 0.0035),
                                    location=sub2_pos,
                                    rotation_euler=tilt_rot)
    link_strictly(sub_bar1, collection)
    link_strictly(sub_bar2, collection)

    objs.extend([leg_l, leg_r, plaque_face, plaque_gold_trim, title_bar, sub_bar1, sub_bar2])
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
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 8
    scene.cycles.transmission_bounces = 12
    scene.cycles.transparent_max_bounces = 12
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    # Overhead soft area light for crystal clear glass highlights
    top_light_data = bpy.data.lights.new(name="Overhead_Glass_Light", type='AREA')
    top_light_data.energy = 18.0
    top_light_data.size = 0.45
    top_light_data.color = (0.95, 0.98, 1.0)
    top_light_obj = bpy.data.objects.new("Overhead_Glass_Light", top_light_data)
    top_light_obj.location = (0.0, -0.04, 0.35)
    bpy.context.scene.collection.objects.link(top_light_obj)

    col_full = bpy.data.collections.new("Glass_Slab_Full")
    col_sec  = bpy.data.collections.new("Glass_Slab_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_glass_slab_full(col_full)
    sec_objs  = build_glass_slab_section(col_sec)

    cam_data = bpy.data.cameras.new("Glass_Slab_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Glass_Slab_Camera", cam_data)
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

    # Render Preview 1: Full Laboratory Experiment Setup
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.035)), distance=0.46, elev_deg=34, azim_deg=-30)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section / Annotated Ray Optics Diagram
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.035)), distance=0.44, elev_deg=34, azim_deg=-26)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== GLASS SLAB BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
