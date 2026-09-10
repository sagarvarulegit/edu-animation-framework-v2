"""
build_glass_prism_refraction.py — Assembled Glass Prism Refraction & Dispersion Experiment
CBSE Class 10 Physics: Light — Refraction through a Glass Prism & White Light Dispersion
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "glass-prism-refraction"


def create_cylinder_between(name, p1, p2, radius, material):
    """Creates a smooth cylindrical segment between two 3D points p1 and p2."""
    v1 = Vector(p1)
    v2 = Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-6:
        return None
    center = (v1 + v2) / 2.0
    
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=24,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
        
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center
    
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(diff)
    obj.rotation_euler = rot_quat.to_euler()
    obj.data.materials.append(material)
    return obj


def build_optical_pin(name, location, pin_mat, head_mat, height=0.032, pin_rad=0.0009, head_rad=0.0028):
    """Creates a vertical laboratory optical pin with metallic shaft and red spherical head."""
    objects = []
    shaft = kit.primitive_object(f"{name}-shaft", "cylinder", pin_mat,
                                  size=(pin_rad * 2, pin_rad * 2, height),
                                  location=(location[0], location[1], location[2] + height / 2))
    objects.append(shaft)
    head = kit.primitive_object(f"{name}-head", "uv_sphere", head_mat,
                                 size=(head_rad * 2, head_rad * 2, head_rad * 2),
                                 location=(location[0], location[1], location[2] + height + head_rad * 0.7))
    objects.append(head)
    return objects


def build_setup():
    objects = []

    # =========================================================================
    # 1. SHADERS & MATERIALS (NATURAL GLASS & HIGH-VIBRANCY EMISSIVE RAYS)
    # =========================================================================
    wood_mat = kit.add_material(f"{ASSET_ID}-wood", (0.82, 0.68, 0.48), metallic=0.0, roughness=0.55)
    paper_mat = kit.add_material(f"{ASSET_ID}-paper", (0.98, 0.98, 0.97), metallic=0.0, roughness=0.92)
    thumb_metal = kit.add_machined_metal_material(f"{ASSET_ID}-thumb-metal", (0.92, 0.92, 0.95), metallic=0.95, roughness=0.2)
    thumb_cap = kit.add_material(f"{ASSET_ID}-thumb-cap", (0.2, 0.55, 0.95), metallic=0.1, roughness=0.3)

    # Crystal Clear Optical Crown Glass (IOR = 1.52)
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.94, 0.98, 1.0), ior=1.52, roughness=0.005)

    casing_mat = kit.add_material(f"{ASSET_ID}-casing", (0.15, 0.16, 0.18), metallic=0.7, roughness=0.4)
    pin_metal_mat = kit.add_machined_metal_material(f"{ASSET_ID}-pin-metal", (0.94, 0.94, 0.96), metallic=0.98, roughness=0.15)
    pin_head_mat = kit.add_material(f"{ASSET_ID}-pin-head", (0.92, 0.15, 0.15), metallic=0.1, roughness=0.3)
    screen_mat = kit.add_material(f"{ASSET_ID}-screen", (0.97, 0.97, 0.97), metallic=0.0, roughness=0.8)

    # White Light Incident Ray Material
    white_ray_mat = kit.add_material(f"{ASSET_ID}-incident-ray", (1.0, 1.0, 1.0), metallic=0.0, roughness=0.2)
    bsdf_w = white_ray_mat.node_tree.nodes["Principled BSDF"]
    bsdf_w.inputs["Emission Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    bsdf_w.inputs["Emission Strength"].default_value = 16.0

    # Normal & Extension lines
    normal_mat = kit.add_material(f"{ASSET_ID}-normal-line", (0.1, 0.85, 1.0), metallic=0.0, roughness=0.3)
    bsdf_n = normal_mat.node_tree.nodes["Principled BSDF"]
    bsdf_n.inputs["Emission Color"].default_value = (0.1, 0.85, 1.0, 1.0)
    bsdf_n.inputs["Emission Strength"].default_value = 8.0

    dashed_ext_mat = kit.add_material(f"{ASSET_ID}-dashed-extension", (1.0, 0.85, 0.2), metallic=0.0, roughness=0.3)
    bsdf_d = dashed_ext_mat.node_tree.nodes["Principled BSDF"]
    bsdf_d.inputs["Emission Color"].default_value = (1.0, 0.85, 0.2, 1.0)
    bsdf_d.inputs["Emission Strength"].default_value = 9.0

    # 7 Spectral VIBGYOR Materials
    spectrum_defs = [
        ("red",    (0.98, 0.12, 0.12), 1.513, 37.8, "Red (700nm - Min deviation)"),
        ("orange", (0.98, 0.50, 0.05), 1.515, 38.3, "Orange (620nm)"),
        ("yellow", (0.98, 0.90, 0.10), 1.517, 38.7, "Yellow (580nm - Mean ray)"),
        ("green",  (0.12, 0.88, 0.25), 1.520, 39.4, "Green (530nm)"),
        ("blue",   (0.12, 0.50, 0.98), 1.525, 40.5, "Blue (480nm)"),
        ("indigo", (0.35, 0.15, 0.75), 1.529, 41.4, "Indigo (440nm)"),
        ("violet", (0.65, 0.12, 0.88), 1.534, 42.6, "Violet (400nm - Max deviation)")
    ]

    spec_mats = {}
    for cname, rgb, n_val, dev_deg, label in spectrum_defs:
        mat = kit.add_material(f"{ASSET_ID}-spec-{cname}", rgb, metallic=0.0, roughness=0.2)
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 14.0
        spec_mats[cname] = mat

    # =========================================================================
    # 2. DRAWING BOARD & PAPER WITH THUMB PINS
    # =========================================================================
    board_w = 0.340
    board_l = 0.260
    board_h = 0.016
    board = kit.primitive_object(f"{ASSET_ID}-drawing-board", "cube", wood_mat,
                                 size=(board_w, board_l, board_h),
                                 location=(0.0, 0.0, -board_h / 2))
    objects.append(board)

    paper_w = 0.290
    paper_l = 0.210
    paper_thick = 0.0006
    paper = kit.primitive_object(f"{ASSET_ID}-paper-sheet", "cube", paper_mat,
                                 size=(paper_w, paper_l, paper_thick),
                                 location=(0.0, 0.0, paper_thick / 2))
    objects.append(paper)

    corner_offsets = [
        (-paper_w / 2 + 0.014, -paper_l / 2 + 0.014),
        ( paper_w / 2 - 0.014, -paper_l / 2 + 0.014),
        (-paper_w / 2 + 0.014,  paper_l / 2 - 0.014),
        ( paper_w / 2 - 0.014,  paper_l / 2 - 0.014),
    ]
    for idx, (px, py) in enumerate(corner_offsets):
        pin_obj = kit.primitive_object(f"{ASSET_ID}-thumb-pin-{idx}", "cylinder", thumb_cap,
                                       size=(0.009, 0.009, 0.004),
                                       location=(px, py, 0.002))
        objects.append(pin_obj)

    # =========================================================================
    # 3. EQUILATERAL GLASS PRISM (60 deg apex)
    # =========================================================================
    prism_side = 0.075
    prism_h = 0.055
    tri_h = prism_side * math.sqrt(3) / 2
    
    y_apex = 2 * tri_h / 3 - 0.010
    y_base = -tri_h / 3 - 0.010
    x_half = prism_side / 2

    A_xy = (0.0, y_apex)
    B_xy = (-x_half, y_base)
    C_xy = (x_half, y_base)

    bm_prism = bmesh.new()
    v_b0 = bm_prism.verts.new((B_xy[0], B_xy[1], 0.0002))
    v_b1 = bm_prism.verts.new((C_xy[0], C_xy[1], 0.0002))
    v_b2 = bm_prism.verts.new((A_xy[0], A_xy[1], 0.0002))
    v_t0 = bm_prism.verts.new((B_xy[0], B_xy[1], prism_h))
    v_t1 = bm_prism.verts.new((C_xy[0], C_xy[1], prism_h))
    v_t2 = bm_prism.verts.new((A_xy[0], A_xy[1], prism_h))

    bm_prism.faces.new([v_b0, v_b1, v_b2])
    bm_prism.faces.new([v_t2, v_t1, v_t0])
    bm_prism.faces.new([v_b0, v_b2, v_t2, v_t0])
    bm_prism.faces.new([v_b2, v_b1, v_t1, v_t2])
    bm_prism.faces.new([v_b1, v_b0, v_t0, v_t1])

    bmesh.ops.recalc_face_normals(bm_prism, faces=bm_prism.faces)
    prism_mesh = bpy.data.meshes.new(f"{ASSET_ID}-glass-prism")
    bm_prism.to_mesh(prism_mesh)
    bm_prism.free()

    for poly in prism_mesh.polygons:
        poly.use_smooth = False

    prism_obj = bpy.data.objects.new(f"{ASSET_ID}-glass-prism", prism_mesh)
    bpy.context.collection.objects.link(prism_obj)
    prism_obj.data.materials.append(glass_mat)
    objects.append(prism_obj)

    # Outline pencil trace
    line_mat = kit.add_material(f"{ASSET_ID}-pencil-trace", (0.3, 0.3, 0.32), metallic=0.0, roughness=0.8)
    trace_r = 0.0004
    z_paper = 0.0008
    create_cylinder_between(f"{ASSET_ID}-trace-AB", (B_xy[0], B_xy[1], z_paper), (A_xy[0], A_xy[1], z_paper), trace_r, line_mat)
    create_cylinder_between(f"{ASSET_ID}-trace-AC", (A_xy[0], A_xy[1], z_paper), (C_xy[0], C_xy[1], z_paper), trace_r, line_mat)
    create_cylinder_between(f"{ASSET_ID}-trace-BC", (C_xy[0], C_xy[1], z_paper), (B_xy[0], B_xy[1], z_paper), trace_r, line_mat)

    # =========================================================================
    # 4. SNELL'S LAW & SPECTRAL DISPERSION OPTICS
    # =========================================================================
    ray_z = prism_h * 0.45
    t_hit = 0.46
    E_pos = Vector((B_xy[0] + t_hit * (A_xy[0] - B_xy[0]),
                    B_xy[1] + t_hit * (A_xy[1] - B_xy[1]),
                    ray_z))

    i_deg = 48.0
    i_rad = math.radians(i_deg)
    inc_angle = math.radians(150.0 - 180.0 + i_deg) # 18 deg
    d_inc = Vector((math.cos(inc_angle), math.sin(inc_angle), 0.0)).normalized()

    # Ray Source / Collimator
    P_pos = E_pos - d_inc * 0.095

    # Surface Normal 1
    n1_dir = Vector((-math.cos(math.radians(30)), math.sin(math.radians(30)), 0.0)).normalized()
    N1_out = E_pos + n1_dir * 0.035
    N1_in  = E_pos - n1_dir * 0.025
    obj_n1 = create_cylinder_between(f"{ASSET_ID}-normal-1", N1_in, N1_out, 0.0007, normal_mat)
    if obj_n1: objects.append(obj_n1)

    # Incident White Light Ray
    beam_r = 0.0013
    obj_inc = create_cylinder_between(f"{ASSET_ID}-ray-incident", P_pos, E_pos, beam_r * 1.2, white_ray_mat)
    if obj_inc: objects.append(obj_inc)

    # Observation Screen Position
    scr_w = 0.006
    scr_l = 0.080
    scr_h = 0.065
    scr_center_pos = Vector((0.115, -0.040, ray_z))
    screen = kit.primitive_object(f"{ASSET_ID}-screen", "cube", screen_mat,
                                  size=(scr_w, scr_l, scr_h),
                                  location=(scr_center_pos.x, scr_center_pos.y, scr_h / 2))
    screen.rotation_euler = (0.0, 0.0, math.radians(70.0))
    objects.append(screen)

    # Optical Pins on Incident Ray
    P1_pos = P_pos + (E_pos - P_pos) * 0.28
    P2_pos = P_pos + (E_pos - P_pos) * 0.72
    pins_data = [
        (f"{ASSET_ID}-pin-P1", (P1_pos.x, P1_pos.y, 0.0)),
        (f"{ASSET_ID}-pin-P2", (P2_pos.x, P2_pos.y, 0.0)),
    ]
    for pin_name, pos in pins_data:
        pin_objs = build_optical_pin(pin_name, pos, pin_metal_mat, pin_head_mat, height=0.030)
        objects.extend(pin_objs)

    # Calculate and build 7 distinct spectral rays (ROYGBIV)
    A_deg = 60.0
    for cname, rgb, n_glass, dev_deg, label in spectrum_defs:
        # Refraction at Face AB
        sin_r1 = math.sin(i_rad) / n_glass
        r1_deg = math.degrees(math.asin(sin_r1))
        
        # Internal angle at Face AC
        r2_deg = A_deg - r1_deg
        sin_e = n_glass * math.sin(math.radians(r2_deg))
        e_deg = math.degrees(math.asin(sin_e))
        
        # Refracted ray direction inside prism
        ref_angle = math.radians(150.0 - 180.0 + r1_deg)
        d_ref = Vector((math.cos(ref_angle), math.sin(ref_angle), 0.0)).normalized()
        
        # Intersection with Face AC
        p1 = Vector((E_pos.x, E_pos.y))
        p2 = p1 + Vector((d_ref.x, d_ref.y))
        p3 = Vector((A_xy[0], A_xy[1]))
        p4 = Vector((C_xy[0], C_xy[1]))
        denom = (p1.x - p2.x) * (p3.y - p4.y) - (p1.y - p2.y) * (p3.x - p4.x)
        t_inter = ((p1.x - p3.x) * (p3.y - p4.y) - (p1.y - p3.y) * (p3.x - p4.x)) / denom
        F_xy = p1 + t_inter * Vector((d_ref.x, d_ref.y))
        F_pos = Vector((F_xy.x, F_xy.y, ray_z))

        # Emergent ray direction
        em_angle = math.radians(30.0 - e_deg)
        d_em = Vector((math.cos(em_angle), math.sin(em_angle), 0.0)).normalized()
        
        # Ray endpoint on screen
        S_pos = F_pos + d_em * 0.098
        
        cmat = spec_mats[cname]

        # Refracted internal ray
        obj_ref = create_cylinder_between(f"{ASSET_ID}-ray-refracted-{cname}", E_pos, F_pos, 0.0009, cmat)
        if obj_ref: objects.append(obj_ref)

        # Emergent dispersed ray
        obj_em = create_cylinder_between(f"{ASSET_ID}-ray-emergent-{cname}", F_pos, S_pos, 0.0011, cmat)
        if obj_em: objects.append(obj_em)

        # Projected spectral band on screen
        band = kit.primitive_object(f"{ASSET_ID}-band-{cname}", "cube", cmat,
                                     size=(0.002, 0.005, 0.004),
                                     location=(S_pos.x - 0.002, S_pos.y, ray_z))
        objects.append(band)

        # Emergent Optical Pins P3, P4 on the mean Yellow ray
        if cname == "yellow":
            # Surface Normal 2
            n2_dir = Vector((math.cos(math.radians(30)), math.sin(math.radians(30)), 0.0)).normalized()
            N2_out = F_pos + n2_dir * 0.035
            N2_in  = F_pos - n2_dir * 0.025
            obj_n2 = create_cylinder_between(f"{ASSET_ID}-normal-2", N2_in, N2_out, 0.0007, normal_mat)
            if obj_n2: objects.append(obj_n2)

            # Extended straight line paths
            H_pos = E_pos + d_inc * 0.090
            obj_ext_inc = create_cylinder_between(f"{ASSET_ID}-ext-incident", E_pos, H_pos, 0.0007, dashed_ext_mat)
            if obj_ext_inc: objects.append(obj_ext_inc)

            P3_pos = F_pos + (S_pos - F_pos) * 0.30
            P4_pos = F_pos + (S_pos - F_pos) * 0.75
            p3_objs = build_optical_pin(f"{ASSET_ID}-pin-P3", (P3_pos.x, P3_pos.y, 0.0), pin_metal_mat, pin_head_mat, height=0.030)
            p4_objs = build_optical_pin(f"{ASSET_ID}-pin-P4", (P4_pos.x, P4_pos.y, 0.0), pin_metal_mat, pin_head_mat, height=0.030)
            objects.extend(p3_objs)
            objects.extend(p4_objs)

    # Ray Box Collimator
    box_w = 0.038
    box_l = 0.055
    box_h = 0.028
    collimator_pos = P_pos - d_inc * (box_l / 2 + 0.004)
    collimator = kit.primitive_object(f"{ASSET_ID}-raybox", "cube", casing_mat,
                                      size=(box_w, box_l, box_h),
                                      location=(collimator_pos.x, collimator_pos.y, ray_z))
    collimator.rotation_euler = (0.0, 0.0, inc_angle - math.pi / 2)
    objects.append(collimator)

    emitter = kit.primitive_object(f"{ASSET_ID}-aperture", "cylinder", white_ray_mat,
                                   size=(0.008, 0.008, 0.004),
                                   location=(P_pos.x, P_pos.y, ray_z),
                                   rotation_euler=(0.0, math.pi / 2, inc_angle))
    objects.append(emitter)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_setup()
    
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    
    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 48.0
    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (0.24, -0.32, 0.26)
    direction = Vector((-0.24, 0.32, -0.24)).normalized()
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam

    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity daylight {ASSET_ID} built and rendered.")


if __name__ == "__main__":
    main()
