"""
build_glass_prism_refraction.py — Refraction & Dispersion of Light Through a Glass Prism
NCERT Class 10 Physics:
- Chapter 11, Figure 11.4: Refraction of light through a triangular glass prism (Ray Diagram, Angle of Deviation D)
- Chapter 11, Figure 11.5: Dispersion of white light into 7 spectral colors (VIBGYOR)

Dual Collections:
- Prism_Full: Complete laboratory experiment setup (wooden board, paper, pins P1-P4, ray box,
  equilateral crown glass prism, and rainbow spectrum VIBGYOR projected on screen).
- Prism_Section: Clear textbook ray diagram view (Fig 11.4) showing incident ray PE, refracted ray EF,
  emergent ray FS, normals NN' & MM', ray extensions, and Angle of Deviation D arc.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'glass-prism-refraction'

# PBR Materials Palette
COLOR_WOOD = (0.78, 0.62, 0.42)
COLOR_PAPER = (0.97, 0.97, 0.96)
COLOR_PIN_CAP = (0.18, 0.52, 0.92)
COLOR_PIN_HEAD = (0.92, 0.15, 0.15)
COLOR_PIN_METAL = (0.94, 0.94, 0.96)
COLOR_CASING = (0.16, 0.17, 0.20)
COLOR_SCREEN = (0.98, 0.98, 0.98)
COLOR_NORMAL = (0.12, 0.85, 0.98)       # Cyan surface normals
COLOR_EXT = (1.00, 0.82, 0.15)          # Golden dashed ray extensions
COLOR_ARC_D = (0.98, 0.45, 0.10)        # Orange angle of deviation arc

# 7 VIBGYOR Spectrum Colors
SPECTRUM = [
    ("red",    (0.98, 0.12, 0.12), 1.513, "Red (700nm)"),
    ("orange", (0.98, 0.52, 0.08), 1.515, "Orange (620nm)"),
    ("yellow", (0.98, 0.90, 0.12), 1.517, "Yellow (580nm)"),
    ("green",  (0.12, 0.88, 0.25), 1.520, "Green (530nm)"),
    ("blue",   (0.12, 0.52, 0.98), 1.525, "Blue (480nm)"),
    ("indigo", (0.35, 0.16, 0.78), 1.529, "Indigo (440nm)"),
    ("violet", (0.68, 0.12, 0.90), 1.534, "Violet (400nm)"),
]

def link_strictly(obj, target_col):
    if obj.name not in target_col.objects:
        target_col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=14.0):
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

def build_optical_pin(name, location, pin_mat, head_mat, collection, height=0.030, pin_rad=0.0009, head_rad=0.0028):
    objs = []
    shaft = kit.primitive_object(f"{name}_shaft", "cylinder", pin_mat,
                                size=(pin_rad * 2, pin_rad * 2, height),
                                location=(location[0], location[1], location[2] + height * 0.5))
    link_strictly(shaft, collection)
    objs.append(shaft)

    head = kit.primitive_object(f"{name}_head", "uv_sphere", head_mat,
                               size=(head_rad * 2, head_rad * 2, head_rad * 2),
                               location=(location[0], location[1], location[2] + height + head_rad * 0.6))
    link_strictly(head, collection)
    objs.append(head)
    return objs

def build_prism_mesh(name, prism_side, prism_h, glass_mat, collection):
    tri_h = prism_side * math.sqrt(3) / 2
    y_apex = 2 * tri_h / 3 - 0.008
    y_base = -tri_h / 3 - 0.008
    x_half = prism_side / 2

    A_xy = (0.0, y_apex)
    B_xy = (-x_half, y_base)
    C_xy = (x_half, y_base)

    bm = bmesh.new()
    v_b0 = bm.verts.new((B_xy[0], B_xy[1], 0.0005))
    v_b1 = bm.verts.new((C_xy[0], C_xy[1], 0.0005))
    v_b2 = bm.verts.new((A_xy[0], A_xy[1], 0.0005))
    v_t0 = bm.verts.new((B_xy[0], B_xy[1], prism_h))
    v_t1 = bm.verts.new((C_xy[0], C_xy[1], prism_h))
    v_t2 = bm.verts.new((A_xy[0], A_xy[1], prism_h))

    bm.faces.new([v_b0, v_b1, v_b2])
    bm.faces.new([v_t2, v_t1, v_t0])
    bm.faces.new([v_b0, v_b2, v_t2, v_t0])
    bm.faces.new([v_b2, v_b1, v_t1, v_t2])
    bm.faces.new([v_b1, v_b0, v_t0, v_t1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = False

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(glass_mat)
    link_strictly(obj, collection)
    return obj, A_xy, B_xy, C_xy

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
    curve_data.bevel_depth = 0.0008
    curve_data.bevel_resolution = 8
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

def build_glass_prism_model(prefix, is_section, collection):
    objs = []

    mat_wood = kit.add_material(f"{prefix}_wood", COLOR_WOOD, metallic=0.0, roughness=0.6)
    mat_paper = kit.add_material(f"{prefix}_paper", COLOR_PAPER, metallic=0.0, roughness=0.95)
    mat_pin_cap = kit.add_material(f"{prefix}_pin_cap", COLOR_PIN_CAP, metallic=0.1, roughness=0.3)
    mat_pin_metal = kit.add_machined_metal_material(f"{prefix}_pin_metal", COLOR_PIN_METAL, metallic=0.98, roughness=0.15)
    mat_pin_head = kit.add_material(f"{prefix}_pin_head", COLOR_PIN_HEAD, metallic=0.1, roughness=0.3)
    mat_casing = kit.add_material(f"{prefix}_casing", COLOR_CASING, metallic=0.6, roughness=0.4)
    mat_screen = kit.add_material(f"{prefix}_screen", COLOR_SCREEN, metallic=0.0, roughness=0.85)
    
    # In Section view: IOR ~ 1.002 prevents double-vision refraction distortion of the diagram geometry
    glass_ior = 1.002 if is_section else 1.517
    glass_roughness = 0.001 if is_section else 0.008
    mat_glass = kit.add_glass_material(f"{prefix}_glass", tint=(0.96, 0.98, 1.0), ior=glass_ior, roughness=glass_roughness)

    mat_white_ray = create_emissive_mat(f"{prefix}_ray_white", (1.0, 1.0, 1.0), strength=18.0)
    mat_normal = create_emissive_mat(f"{prefix}_ray_normal", COLOR_NORMAL, strength=10.0)
    mat_ext = create_emissive_mat(f"{prefix}_ray_ext", COLOR_EXT, strength=10.0)
    mat_arc = create_emissive_mat(f"{prefix}_arc_d", COLOR_ARC_D, strength=12.0)

    # 1. Laboratory Board & Paper
    board_w, board_l, board_h = 0.320, 0.250, 0.014
    board = kit.primitive_object(f"{prefix}_Drawing_Board", "cube", mat_wood,
                                 size=(board_w, board_l, board_h),
                                 location=(0.0, 0.0, -board_h * 0.5))
    link_strictly(board, collection)
    objs.append(board)

    paper_w, paper_l, paper_thick = 0.280, 0.210, 0.0006
    paper = kit.primitive_object(f"{prefix}_Paper_Sheet", "cube", mat_paper,
                                 size=(paper_w, paper_l, paper_thick),
                                 location=(0.0, 0.0, paper_thick * 0.5))
    link_strictly(paper, collection)
    objs.append(paper)

    for idx, (px, py) in enumerate([
        (-paper_w*0.5 + 0.014, -paper_l*0.5 + 0.014),
        ( paper_w*0.5 - 0.014, -paper_l*0.5 + 0.014),
        (-paper_w*0.5 + 0.014,  paper_l*0.5 - 0.014),
        ( paper_w*0.5 - 0.014,  paper_l*0.5 - 0.014),
    ]):
        tack = kit.primitive_object(f"{prefix}_Thumb_Tack_{idx}", "cylinder", mat_pin_cap,
                                   size=(0.008, 0.008, 0.004),
                                   location=(px, py, 0.002))
        link_strictly(tack, collection)
        objs.append(tack)

    # 2. Equilateral Glass Prism
    prism_side = 0.075
    prism_h = 0.055
    prism_obj, A_xy, B_xy, C_xy = build_prism_mesh(f"{prefix}_Glass_Prism", prism_side, prism_h, mat_glass, collection)
    objs.append(prism_obj)

    # Pencil outline trace
    mat_pencil = kit.add_material(f"{prefix}_pencil", (0.35, 0.35, 0.38), metallic=0.0, roughness=0.8)
    trace_r = 0.0004
    z_paper = 0.0008
    t_ab = create_cylinder_segment(f"{prefix}_Trace_AB", (B_xy[0], B_xy[1], z_paper), (A_xy[0], A_xy[1], z_paper), trace_r, mat_pencil, collection)
    t_ac = create_cylinder_segment(f"{prefix}_Trace_AC", (A_xy[0], A_xy[1], z_paper), (C_xy[0], C_xy[1], z_paper), trace_r, mat_pencil, collection)
    t_bc = create_cylinder_segment(f"{prefix}_Trace_BC", (C_xy[0], C_xy[1], z_paper), (B_xy[0], B_xy[1], z_paper), trace_r, mat_pencil, collection)
    objs.extend([t_ab, t_ac, t_bc])

    # 3. Geometric Optics
    ray_z = prism_h * 0.45
    t_hit = 0.46
    E_pos = Vector((B_xy[0] + t_hit * (A_xy[0] - B_xy[0]),
                    B_xy[1] + t_hit * (A_xy[1] - B_xy[1]),
                    ray_z))

    i_deg = 48.0
    i_rad = math.radians(i_deg)
    inc_angle = math.radians(150.0 - 180.0 + i_deg)
    d_inc = Vector((math.cos(inc_angle), math.sin(inc_angle), 0.0)).normalized()

    P_pos = E_pos - d_inc * 0.095

    ray_inc = create_cylinder_segment(f"{prefix}_Ray_Incident", P_pos, E_pos, 0.0014, mat_white_ray, collection)
    objs.append(ray_inc)

    P1_pos = P_pos + (E_pos - P_pos) * 0.28
    P2_pos = P_pos + (E_pos - P_pos) * 0.72
    objs.extend(build_optical_pin(f"{prefix}_Pin_P1", (P1_pos.x, P1_pos.y, 0.0), mat_pin_metal, mat_pin_head, collection))
    objs.extend(build_optical_pin(f"{prefix}_Pin_P2", (P2_pos.x, P2_pos.y, 0.0), mat_pin_metal, mat_pin_head, collection))

    box_w, box_l, box_h = 0.036, 0.052, 0.026
    collimator_pos = P_pos - d_inc * (box_l * 0.5 + 0.004)
    collimator = kit.primitive_object(f"{prefix}_Ray_Box", "cube", mat_casing,
                                      size=(box_w, box_l, box_h),
                                      location=(collimator_pos.x, collimator_pos.y, ray_z))
    collimator.rotation_euler = (0.0, 0.0, inc_angle - math.pi * 0.5)
    link_strictly(collimator, collection)
    objs.append(collimator)

    # Normal 1 (NN')
    n1_dir = Vector((-math.cos(math.radians(30)), math.sin(math.radians(30)), 0.0)).normalized()
    N1_out = E_pos + n1_dir * 0.032
    N1_in  = E_pos - n1_dir * 0.022
    norm1 = create_cylinder_segment(f"{prefix}_Normal_NN", N1_in, N1_out, 0.0006, mat_normal, collection)
    objs.append(norm1)

    A_deg = 60.0

    if not is_section:
        # Full view: Pedagogically clear dispersion with visible VIBGYOR rainbow on observation screen
        # Pedagogical dispersion refractive indices (exaggerated slightly so 7 colors clearly separate)
        PEDAGOGICAL_SPECTRUM = [
            ("Red",    (1.00, 0.15, 0.10), 1.485, "R"),
            ("Orange", (1.00, 0.50, 0.05), 1.498, "O"),
            ("Yellow", (1.00, 0.90, 0.10), 1.512, "Y"),
            ("Green",  (0.10, 0.85, 0.25), 1.526, "G"),
            ("Blue",   (0.15, 0.45, 1.00), 1.542, "B"),
            ("Indigo", (0.30, 0.10, 0.70), 1.558, "I"),
            ("Violet", (0.60, 0.15, 0.90), 1.575, "V"),
        ]

        scr_w, scr_l, scr_h = 0.005, 0.090, 0.065
        scr_center_pos = Vector((0.096, -0.046, scr_h * 0.5))
        scr_angle = math.radians(195.0)

        # Screen base stand
        mat_stand = kit.add_material(f"{prefix}_screen_stand", (0.2, 0.22, 0.25), metallic=0.7, roughness=0.3)
        stand = kit.primitive_object(f"{prefix}_Screen_Stand", "cube", mat_stand,
                                    size=(0.020, 0.040, 0.006),
                                    location=(scr_center_pos.x, scr_center_pos.y, 0.003))
        stand.rotation_euler = (0.0, 0.0, scr_angle)
        link_strictly(stand, collection)
        objs.append(stand)

        screen = kit.primitive_object(f"{prefix}_Observation_Screen", "cube", mat_screen,
                                      size=(scr_w, scr_l, scr_h),
                                      location=(scr_center_pos.x, scr_center_pos.y, scr_center_pos.z))
        screen.rotation_euler = (0.0, 0.0, scr_angle)
        link_strictly(screen, collection)
        objs.append(screen)

        # Screen face normal pointing out from the receiving surface
        scr_n = Vector((math.cos(scr_angle), math.sin(scr_angle), 0.0))

        for cname, rgb, n_glass, label in PEDAGOGICAL_SPECTRUM:
            cmat = create_emissive_mat(f"{prefix}_mat_{cname}", rgb, strength=16.0)

            sin_r1 = math.sin(i_rad) / n_glass
            r1_deg = math.degrees(math.asin(sin_r1))

            r2_deg = A_deg - r1_deg
            sin_e = n_glass * math.sin(math.radians(r2_deg))
            e_deg = math.degrees(math.asin(sin_e))

            ref_angle = math.radians(150.0 - 180.0 + r1_deg)
            d_ref = Vector((math.cos(ref_angle), math.sin(ref_angle), 0.0)).normalized()

            p1 = Vector((E_pos.x, E_pos.y))
            p2 = p1 + Vector((d_ref.x, d_ref.y))
            p3 = Vector((A_xy[0], A_xy[1]))
            p4 = Vector((C_xy[0], C_xy[1]))
            denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
            t_inter = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denom
            F_xy = p1 + t_inter * Vector((d_ref.x, d_ref.y))
            F_pos = Vector((F_xy.x, F_xy.y, ray_z))

            em_angle = math.radians(30.0 - e_deg)
            d_em = Vector((math.cos(em_angle), math.sin(em_angle), 0.0)).normalized()

            # Plane intersection with screen face (offset by half-thickness towards normal)
            screen_plane_pt = scr_center_pos + scr_n * (scr_w * 0.5)
            denom_scr = d_em.dot(scr_n)
            if abs(denom_scr) > 1e-5:
                t_scr = (screen_plane_pt - F_pos).dot(scr_n) / denom_scr
            else:
                t_scr = 0.080
            S_pos = F_pos + d_em * t_scr

            r_ref = create_cylinder_segment(f"{prefix}_Ray_Ref_{cname}", E_pos, F_pos, 0.0008, cmat, collection)
            r_em = create_cylinder_segment(f"{prefix}_Ray_Em_{cname}", F_pos, S_pos, 0.0010, cmat, collection)
            objs.extend([r_ref, r_em])

            # Projected spectral band on screen surface
            band = kit.primitive_object(f"{prefix}_Band_{cname}", "cube", cmat,
                                         size=(0.0018, 0.0038, 0.016),
                                         location=(S_pos.x + scr_n.x * 0.0010, S_pos.y + scr_n.y * 0.0010, ray_z))
            band.rotation_euler = (0.0, 0.0, scr_angle)
            link_strictly(band, collection)
            objs.append(band)

    else:
        # Section view: Pure textbook ray diagram (NCERT Fig 11.4)
        n_glass = 1.517
        sin_r1 = math.sin(i_rad) / n_glass
        r1_deg = math.degrees(math.asin(sin_r1))

        r2_deg = A_deg - r1_deg
        sin_e = n_glass * math.sin(math.radians(r2_deg))
        e_deg = math.degrees(math.asin(sin_e))

        ref_angle = math.radians(150.0 - 180.0 + r1_deg)
        d_ref = Vector((math.cos(ref_angle), math.sin(ref_angle), 0.0)).normalized()

        p1 = Vector((E_pos.x, E_pos.y))
        p2 = p1 + Vector((d_ref.x, d_ref.y))
        p3 = Vector((A_xy[0], A_xy[1]))
        p4 = Vector((C_xy[0], C_xy[1]))
        denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        t_inter = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denom
        F_xy = p1 + t_inter * Vector((d_ref.x, d_ref.y))
        F_pos = Vector((F_xy.x, F_xy.y, ray_z))

        em_angle = math.radians(30.0 - e_deg)
        d_em = Vector((math.cos(em_angle), math.sin(em_angle), 0.0)).normalized()
        S_pos = F_pos + d_em * 0.090

        mat_mono = create_emissive_mat(f"{prefix}_mono_ray", (0.98, 0.88, 0.15), strength=18.0)
        r_ef = create_cylinder_segment(f"{prefix}_Ray_EF", E_pos, F_pos, 0.0013, mat_mono, collection)
        r_fs = create_cylinder_segment(f"{prefix}_Ray_FS", F_pos, S_pos, 0.0014, mat_mono, collection)
        objs.extend([r_ef, r_fs])

        P3_pos = F_pos + (S_pos - F_pos) * 0.35
        P4_pos = F_pos + (S_pos - F_pos) * 0.78
        objs.extend(build_optical_pin(f"{prefix}_Pin_P3", (P3_pos.x, P3_pos.y, 0.0), mat_pin_metal, mat_pin_head, collection))
        objs.extend(build_optical_pin(f"{prefix}_Pin_P4", (P4_pos.x, P4_pos.y, 0.0), mat_pin_metal, mat_pin_head, collection))

        n2_dir = Vector((math.cos(math.radians(30)), math.sin(math.radians(30)), 0.0)).normalized()
        N2_out = F_pos + n2_dir * 0.035
        N2_in  = F_pos - n2_dir * 0.022
        norm2 = create_cylinder_segment(f"{prefix}_Normal_MM", N2_in, N2_out, 0.0007, mat_normal, collection)
        objs.append(norm2)

        denom_g = d_inc.x * d_em.y - d_inc.y * d_em.x
        t_g = ((F_pos.x - E_pos.x) * d_em.y - (F_pos.y - E_pos.y) * d_em.x) / denom_g
        G_pos = E_pos + d_inc * t_g
        G_pos.z = ray_z

        H_pos = G_pos + d_inc * 0.040
        ext_inc = create_cylinder_segment(f"{prefix}_Ext_Incident", E_pos, H_pos, 0.0007, mat_ext, collection)
        ext_em = create_cylinder_segment(f"{prefix}_Ext_Emergent", F_pos, G_pos, 0.0007, mat_ext, collection)
        objs.extend([ext_inc, ext_em])

        ang_start = math.degrees(em_angle)
        ang_end = math.degrees(inc_angle)
        arc_d = build_angle_arc(f"{prefix}_Arc_Deviation_D", G_pos, 0.016, ang_start, ang_end, mat_arc, collection)
        objs.append(arc_d)

        # Angle of prism A arc at apex A (inside vertex A between AC and AB)
        apex_pos = Vector((A_xy[0], A_xy[1], ray_z))
        mat_apex_arc = create_emissive_mat(f"{prefix}_arc_a", (0.3, 0.8, 1.0), strength=12.0)
        arc_a = build_angle_arc(f"{prefix}_Arc_Prism_A", apex_pos, 0.014, 240.0, 300.0, mat_apex_arc, collection)
        objs.append(arc_a)

        # Angle of incidence i arc at point E (between normal NN' and incident ray)
        norm1_deg = math.degrees(math.atan2(n1_dir.y, n1_dir.x))
        inc_ray_rev_deg = math.degrees(math.atan2(-d_inc.y, -d_inc.x))
        arc_i = build_angle_arc(f"{prefix}_Arc_Incidence_i", E_pos, 0.012, norm1_deg, inc_ray_rev_deg, mat_arc, collection)
        objs.append(arc_i)

        # Angle of emergence e arc at point F (between normal MM' and emergent ray)
        norm2_deg = math.degrees(math.atan2(n2_dir.y, n2_dir.x))
        em_ray_deg = math.degrees(math.atan2(d_em.y, d_em.x))
        arc_e = build_angle_arc(f"{prefix}_Arc_Emergence_e", F_pos, 0.012, em_ray_deg, norm2_deg, mat_arc, collection)
        objs.append(arc_e)

    return objs

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.35, -0.45, 0.35), (9.0, 9.0, 8.8), 9.0, 0.45),
        ("Fill_Light", 'AREA', (-0.45, -0.40, 0.25), (5.5, 5.5, 6.0), 5.5, 0.50),
        ("Rim_Light", 'SPOT', (0.0, 0.45, 0.35), (8.0, 8.0, 8.0), 8.0, 0.35),
        ("Bottom_Bounce", 'POINT', (0.0, -0.20, 0.02), (2.8, 2.8, 3.0), 2.8, 0.15),
    ]

    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.15
            light_data.spot_blend = 0.30

        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance, elev_deg=35, azim_deg=-25):
    elev_rad = math.radians(elev_deg)
    azim_rad = math.radians(azim_deg)

    cam_x = target_center.x + distance * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_center.y - distance * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_center.z + distance * math.sin(elev_rad)

    cam_obj.location = (cam_x, cam_y, cam_z)

    direction = target_center - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

    world = bpy.data.worlds.new("Prism_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Prism_Full (Laboratory Experiment with VIBGYOR Rainbow on screen)
    col_full = bpy.data.collections.new("Prism_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_glass_prism_model("Full", is_section=False, collection=col_full)

    # 2. Collection: Prism_Section (Textbook Fig 11.4 Ray Diagram with Angle of Deviation D)
    col_section = bpy.data.collections.new("Prism_Section")
    bpy.context.scene.collection.children.link(col_section)
    sec_objs = build_glass_prism_model("Sec", is_section=True, collection=col_section)

    cam_data = bpy.data.cameras.new("Macro_Camera")
    cam_data.lens = 50.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Macro_Camera", cam_data)
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

    # Render Preview 1: Prism_Full (Lab experiment with visible rainbow fan on screen)
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.020, -0.010, 0.025)), distance=0.40, elev_deg=32, azim_deg=-35)
    kit.configure_render(width=1280, height=720, samples=32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Prism_Section (Textbook Fig 11.4 Ray Diagram showing D arc, normals & extensions)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.028)), distance=0.34, elev_deg=58, azim_deg=-20)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== GLASS PRISM REFRACTION BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
