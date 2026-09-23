"""
build_solenoid.py — Helical Solenoid with Magnetic Field Lines (NCERT Class 10 Fig 13.10)
CBSE Class 10 Science Chapter 13: Magnetic Effects of Electric Current
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'solenoid'

# Design System Colors
COLOR_COPPER = (0.92, 0.48, 0.18)
COLOR_BASE = (0.12, 0.13, 0.15)
COLOR_CRADLE = (0.18, 0.20, 0.23)
COLOR_CORE_TUBE = (0.85, 0.88, 0.92)
COLOR_CORE_SECTION = (0.75, 0.78, 0.82)
COLOR_BRASS = (0.88, 0.72, 0.26)
COLOR_NORTH = (0.88, 0.15, 0.12)
COLOR_SOUTH = (0.12, 0.35, 0.88)
COLOR_FLUX = (0.05, 0.72, 1.00)
COLOR_CURRENT = (1.00, 0.65, 0.08)

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=8.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_cylinder_segment(name, p1, p2, radius, mat, collection, segments=12):
    v1 = Vector(p1)
    v2 = Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-6:
        return None
    center = (v1 + v2) * 0.5

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=segments,
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

def build_curved_tube(name, points, radius, mat, collection, ring_res=8, radial_center_fn=None):
    if len(points) < 2:
        return None
    bm = bmesh.new()
    n_pts = len(points)
    rings = []

    p0 = Vector(points[0])
    p1 = Vector(points[1])
    t0 = (p1 - p0).normalized()
    if radial_center_fn:
        norm = (p0 - radial_center_fn(p0)).normalized()
    else:
        norm = Vector((0, 0, 1)).cross(t0)
        if norm.length < 1e-4:
            norm = Vector((0, 1, 0)).cross(t0)
        norm.normalize()
    binorm = t0.cross(norm).normalized()

    prev_t = t0
    prev_norm = norm
    prev_binorm = binorm

    for i, p in enumerate(points):
        p_vec = Vector(p)
        if i < n_pts - 1:
            t = (Vector(points[i + 1]) - p_vec).normalized()
        else:
            t = (p_vec - Vector(points[i - 1])).normalized()

        if radial_center_fn:
            center_axis_pt = radial_center_fn(p_vec)
            norm = (p_vec - center_axis_pt).normalized()
            binorm = t.cross(norm).normalized()
        else:
            rot_axis = prev_t.cross(t)
            if rot_axis.length > 1e-5:
                rot_ang = prev_t.angle(t)
                rot_mat = Matrix.Rotation(rot_ang, 4, rot_axis.normalized())
                norm = (rot_mat @ prev_norm.to_4d()).to_3d().normalized()
                binorm = (rot_mat @ prev_binorm.to_4d()).to_3d().normalized()
            else:
                norm = prev_norm
                binorm = prev_binorm

        prev_t = t
        prev_norm = norm
        prev_binorm = binorm

        ring = []
        for r_idx in range(ring_res):
            ang = 2.0 * math.pi * r_idx / ring_res
            v_co = p_vec + (norm * math.cos(ang) + binorm * math.sin(ang)) * radius
            ring.append(bm.verts.new(v_co))
        rings.append(ring)

    for i in range(n_pts - 1):
        for r_idx in range(ring_res):
            next_r = (r_idx + 1) % ring_res
            bm.faces.new([rings[i][r_idx], rings[i+1][r_idx],
                          rings[i+1][next_r], rings[i][next_r]])

    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj

def build_vector_arrow(name, loc, direction, mat, collection, length=0.009, radius=0.0032):
    dir_v = Vector(direction).normalized()
    rot_quat = Vector((0, 0, 1)).rotation_difference(dir_v)

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=12,
                          radius1=radius, radius2=0.0, depth=length)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(loc)
    obj.rotation_euler = rot_quat.to_euler()
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj

def build_solenoid_model(prefix, is_section, collection):
    objs = []

    # Materials
    mat_copper = kit.add_machined_metal_material(f"{prefix}_copper", COLOR_COPPER, metallic=0.96, roughness=0.20)
    mat_base = kit.add_material(f"{prefix}_base", COLOR_BASE, metallic=0.2, roughness=0.55)
    mat_cradle = kit.add_material(f"{prefix}_cradle", COLOR_CRADLE, metallic=0.5, roughness=0.4)
    mat_brass = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.95, roughness=0.22)
    mat_red = kit.add_material(f"{prefix}_term_pos", COLOR_NORTH, metallic=0.2, roughness=0.35)
    mat_black = kit.add_material(f"{prefix}_term_neg", (0.05, 0.05, 0.06), metallic=0.2, roughness=0.35)
    mat_flux = create_emissive_mat(f"{prefix}_magnetic_flux", COLOR_FLUX, strength=14.0)
    mat_current = create_emissive_mat(f"{prefix}_current_vector", COLOR_CURRENT, strength=16.0)

    # Core Tube Material
    if is_section:
        mat_core = kit.add_material(f"{prefix}_core_cut", COLOR_CORE_SECTION, metallic=0.1, roughness=0.45)
    else:
        mat_core = kit.add_material(f"{prefix}_core_acrylic", COLOR_CORE_TUBE, metallic=0.15, roughness=0.3)

    # 1. Apparatus Bench Base & Stand Saddles
    base_w, base_l, base_h = 0.250, 0.120, 0.014
    base_z = 0.007
    base = kit.primitive_object(f"{prefix}_Base_Bench", "cube", mat_base,
                                size=(base_w, base_l, base_h),
                                location=(0.0, 0.0, base_z))
    link_strictly(base, collection)
    objs.append(base)

    # Feet
    mat_rubber = kit.add_material(f"{prefix}_rubber_feet", (0.04, 0.04, 0.04), metallic=0.0, roughness=0.9)
    for fx in [-base_w * 0.44, base_w * 0.44]:
        for fy in [-base_l * 0.42, base_l * 0.42]:
            foot = kit.primitive_object(f"{prefix}_Foot_{fx}_{fy}", "cylinder", mat_rubber,
                                       size=(0.014, 0.014, 0.004),
                                       location=(fx, fy, 0.002))
            link_strictly(foot, collection)
            objs.append(foot)

    # Two upright support cradles holding solenoid tube at center (z = 0.062)
    solenoid_z = 0.062
    cradle_h = solenoid_z - base_h
    cradle_x_pos = 0.065
    for cx in [-cradle_x_pos, cradle_x_pos]:
        post = kit.primitive_object(f"{prefix}_Cradle_Post_{cx}", "cube", mat_cradle,
                                    size=(0.012, 0.048, cradle_h),
                                    location=(cx, 0.0, base_h + cradle_h * 0.5))
        saddle = kit.primitive_object(f"{prefix}_Cradle_Saddle_{cx}", "cylinder", mat_cradle,
                                      size=(0.048, 0.048, 0.012),
                                      location=(cx, 0.0, solenoid_z),
                                      rotation_euler=(0.0, math.pi * 0.5, 0.0))
        link_strictly(post, collection)
        link_strictly(saddle, collection)
        objs.extend([post, saddle])

    # 2. Central Former Tube (length = 0.160m, outer radius = 0.022m, inner radius = 0.019m)
    tube_len = 0.160
    r_core_out = 0.022

    if not is_section:
        # Full Tube: Cylinder
        core_obj = kit.primitive_object(f"{prefix}_Core_Tube", "cylinder", mat_core,
                                        size=(r_core_out * 2, r_core_out * 2, tube_len),
                                        location=(0.0, 0.0, solenoid_z),
                                        rotation_euler=(0.0, math.pi * 0.5, 0.0))
        link_strictly(core_obj, collection)
        objs.append(core_obj)
    else:
        # Section View: Longitudinal Half-Cylinder (rear half y >= 0 kept)
        bm_core_sec = bmesh.new()
        steps_phi = 20
        verts_wall = []
        for s in range(steps_phi + 1):
            phi = math.pi * s / steps_phi  # 0 to pi (y >= 0 half)
            y_co = r_core_out * math.sin(phi)
            z_co = r_core_out * math.cos(phi)
            v0 = bm_core_sec.verts.new((-tube_len * 0.5, y_co, solenoid_z + z_co))
            v1 = bm_core_sec.verts.new(( tube_len * 0.5, y_co, solenoid_z + z_co))
            verts_wall.append((v0, v1))

        for s in range(steps_phi):
            v0_a, v1_a = verts_wall[s]
            v0_b, v1_b = verts_wall[s + 1]
            bm_core_sec.faces.new([v0_a, v1_a, v1_b, v0_b])

        bmesh.ops.recalc_face_normals(bm_core_sec, faces=bm_core_sec.faces)
        mesh_core_sec = bpy.data.meshes.new(f"{prefix}_Core_Half_Tube")
        bm_core_sec.to_mesh(mesh_core_sec)
        bm_core_sec.free()
        for p in mesh_core_sec.polygons:
            p.use_smooth = True
        core_sec = bpy.data.objects.new(f"{prefix}_Core_Half_Tube", mesh_core_sec)
        core_sec.data.materials.append(mat_core)
        link_strictly(core_sec, collection)
        objs.append(core_sec)

    # 3. Helical Copper Coil (16 continuous uniform turns)
    turns = 16
    wire_r = 0.0022
    coil_r = r_core_out + wire_r * 0.95
    steps_per_turn = 24
    total_steps = turns * steps_per_turn

    x_start = -tube_len * 0.5 + 0.010
    x_end = tube_len * 0.5 - 0.010
    x_span = x_end - x_start
    radial_fn = lambda pt: Vector((pt.x, 0.0, solenoid_z))

    if not is_section:
        # Full smooth helix with analytical radial normals (zero twist)
        helix_pts = []
        for i in range(total_steps + 1):
            frac = i / total_steps
            x = x_start + frac * x_span
            theta = 2.0 * math.pi * turns * frac
            y = coil_r * math.cos(theta)
            z = solenoid_z + coil_r * math.sin(theta)
            helix_pts.append((x, y, z))

        coil_obj = build_curved_tube(f"{prefix}_Copper_Coil", helix_pts, wire_r, mat_copper, collection, ring_res=12, radial_center_fn=radial_fn)
        if coil_obj:
            objs.append(coil_obj)
    else:
        # Section view: Individual rear half-turns wound behind the core (y >= 0)
        steps_half = 16
        for t in range(turns):
            turn_pts = []
            for s in range(steps_half + 1):
                frac_s = s / steps_half
                phi = math.pi * frac_s
                x = x_start + (t + frac_s * 0.5) * (x_span / turns)
                y = coil_r * math.sin(phi)
                z = solenoid_z + coil_r * math.cos(phi)
                turn_pts.append((x, y, z))
            arc_obj = build_curved_tube(f"{prefix}_Rear_Arc_{t}", turn_pts, wire_r, mat_copper, collection, ring_res=8, radial_center_fn=radial_fn)
            if arc_obj:
                objs.append(arc_obj)

        # Wire cut cross-sections at y = 0
        mat_wire_cut = kit.add_material(f"{prefix}_wire_cut", (0.95, 0.60, 0.35), metallic=0.8, roughness=0.3)
        for t in range(turns):
            xt_top = x_start + t * (x_span / turns)
            xt_bot = x_start + (t + 0.5) * (x_span / turns)
            # Top cut (current emerging OUT toward viewer, symbolized by dot)
            cut_top = kit.primitive_object(f"{prefix}_WireCut_Top_{t}", "cylinder", mat_wire_cut,
                                           size=(wire_r * 2, wire_r * 2, 0.001),
                                           location=(xt_top, 0.0, solenoid_z + coil_r),
                                           rotation_euler=(math.pi * 0.5, 0.0, 0.0))
            dot = kit.primitive_object(f"{prefix}_Dot_{t}", "uv_sphere", mat_current,
                                       size=(0.0016, 0.0016, 0.0016),
                                       location=(xt_top, -0.001, solenoid_z + coil_r))
            # Bottom cut (current entering IN away from viewer, symbolized by cross)
            cut_bot = kit.primitive_object(f"{prefix}_WireCut_Bot_{t}", "cylinder", mat_wire_cut,
                                           size=(wire_r * 2, wire_r * 2, 0.001),
                                           location=(xt_bot, 0.0, solenoid_z - coil_r),
                                           rotation_euler=(math.pi * 0.5, 0.0, 0.0))
            cross1 = create_cylinder_segment(f"{prefix}_CrossA_{t}",
                                            (xt_bot - 0.0012, -0.001, solenoid_z - coil_r - 0.0012),
                                            (xt_bot + 0.0012, -0.001, solenoid_z - coil_r + 0.0012),
                                            0.0003, mat_current, collection)
            cross2 = create_cylinder_segment(f"{prefix}_CrossB_{t}",
                                            (xt_bot - 0.0012, -0.001, solenoid_z - coil_r + 0.0012),
                                            (xt_bot + 0.0012, -0.001, solenoid_z - coil_r - 0.0012),
                                            0.0003, mat_current, collection)
            link_strictly(cut_top, collection)
            link_strictly(dot, collection)
            link_strictly(cut_bot, collection)
            objs.extend([cut_top, dot, cut_bot, cross1, cross2])

    # 4. Terminal Posts (+ Red, - Black) & Leads
    term_y = -base_l * 0.35
    for side, tx, col_mat in [("Pos", -0.080, mat_red), ("Neg", 0.080, mat_black)]:
        post = kit.primitive_object(f"{prefix}_Term_Post_{side}", "cylinder", mat_brass,
                                    size=(0.012, 0.012, 0.024),
                                    location=(tx, term_y, base_h + 0.012))
        collar = kit.primitive_object(f"{prefix}_Term_Collar_{side}", "cylinder", col_mat,
                                      size=(0.016, 0.016, 0.006),
                                      location=(tx, term_y, base_h + 0.003))
        nut = kit.primitive_object(f"{prefix}_Term_Nut_{side}", "cylinder", mat_brass,
                                   size=(0.014, 0.014, 0.006),
                                   location=(tx, term_y, base_h + 0.020))
        link_strictly(post, collection)
        link_strictly(collar, collection)
        link_strictly(nut, collection)
        objs.extend([post, collar, nut])

    # Lead wires connecting terminals to coil endpoints
    lead_pos_pts = [
        (-0.080, term_y, base_h + 0.015),
        (-0.080, term_y * 0.4, base_h + 0.008),
        (x_start, -coil_r * 0.8, solenoid_z - coil_r * 0.5),
        (x_start, 0.0, solenoid_z - coil_r),
    ]
    lead_neg_pts = [
        (0.080, term_y, base_h + 0.015),
        (0.080, term_y * 0.4, base_h + 0.008),
        (x_end, -coil_r * 0.8, solenoid_z - coil_r * 0.5),
        (x_end, 0.0, solenoid_z - coil_r),
    ]
    lead_pos = build_curved_tube(f"{prefix}_Lead_Pos", lead_pos_pts, 0.0016, mat_red, collection)
    lead_neg = build_curved_tube(f"{prefix}_Lead_Neg", lead_neg_pts, 0.0016, mat_black, collection)
    if lead_pos: objs.append(lead_pos)
    if lead_neg: objs.append(lead_neg)

    # 5. Polarity Badges (South = -X Left, North = +X Right)
    mat_n_badge = kit.add_material(f"{prefix}_mat_n_badge", COLOR_NORTH, metallic=0.3, roughness=0.3)
    mat_s_badge = kit.add_material(f"{prefix}_mat_s_badge", COLOR_SOUTH, metallic=0.3, roughness=0.3)
    mat_letter = kit.add_material(f"{prefix}_mat_letter", (1.0, 1.0, 1.0), metallic=0.0, roughness=0.2)

    # South Pole Badge (-X end)
    s_plate = kit.primitive_object(f"{prefix}_Badge_South", "cylinder", mat_s_badge,
                                   size=(0.026, 0.026, 0.004),
                                   location=(-tube_len * 0.5 - 0.004, 0.0, solenoid_z),
                                   rotation_euler=(0.0, math.pi * 0.5, 0.0))
    s_label = kit.primitive_object(f"{prefix}_Label_S", "cube", mat_letter,
                                   size=(0.002, 0.010, 0.014),
                                   location=(-tube_len * 0.5 - 0.007, 0.0, solenoid_z))
    link_strictly(s_plate, collection)
    link_strictly(s_label, collection)
    objs.extend([s_plate, s_label])

    # North Pole Badge (+X end)
    n_plate = kit.primitive_object(f"{prefix}_Badge_North", "cylinder", mat_n_badge,
                                   size=(0.026, 0.026, 0.004),
                                   location=(tube_len * 0.5 + 0.004, 0.0, solenoid_z),
                                   rotation_euler=(0.0, math.pi * 0.5, 0.0))
    n_label = kit.primitive_object(f"{prefix}_Label_N", "cube", mat_letter,
                                   size=(0.002, 0.010, 0.014),
                                   location=(tube_len * 0.5 + 0.007, 0.0, solenoid_z))
    link_strictly(n_plate, collection)
    link_strictly(n_label, collection)
    objs.extend([n_plate, n_label])

    # 6. Magnetic Field Lines (CBSE Fig 13.10)
    # A. Uniform Internal Field Lines (Parallel straight lines inside core traveling South -> North, i.e. -X to +X)
    int_len = tube_len + 0.020
    internal_offsets = [
        (0.0, 0.0),
        (-0.008, 0.0), (0.008, 0.0),
        (0.0, -0.008), (0.0, 0.008),
        (-0.006, -0.006), (0.006, -0.006),
        (-0.006, 0.006), (0.006, 0.006),
    ]

    for idx, (oy, oz) in enumerate(internal_offsets):
        p1 = (-int_len * 0.5, oy, solenoid_z + oz)
        p2 = ( int_len * 0.5, oy, solenoid_z + oz)
        line = create_cylinder_segment(f"{prefix}_Int_Flux_{idx}", p1, p2, 0.0009, mat_flux, collection)
        objs.append(line)

        # Directional arrows inside pointing from South (-X) to North (+X)
        if idx in [0, 1, 2, 3, 4]:
            arrow = build_vector_arrow(f"{prefix}_Int_Arrow_{idx}", (0.0, oy, solenoid_z + oz),
                                       (1.0, 0.0, 0.0), mat_flux, collection, length=0.007, radius=0.0025)
            objs.append(arrow)

    # B. External Dipolar Return Loops (North (+X) -> South (-X))
    loop_configs = [
        (0.125, 0.045, 0.0),
        (0.145, 0.065, 0.0),
        (0.168, 0.090, 0.0),
        (0.135, 0.052, math.radians(35.0)),
        (0.135, 0.052, math.radians(-35.0)),
        (0.155, 0.075, math.radians(55.0)),
        (0.155, 0.075, math.radians(-55.0)),
    ]

    for loop_idx, (a_rad, b_rad, tilt_ang) in enumerate(loop_configs):
        for side in [-1, 1]:
            steps = 40
            loop_pts = []
            cos_tilt = math.cos(tilt_ang)
            sin_tilt = math.sin(tilt_ang)

            for s in range(steps + 1):
                t = math.pi * s / steps
                px = a_rad * math.cos(t)
                py_local = side * b_rad * math.sin(t)
                pz_local = 0.0

                py = py_local * cos_tilt - pz_local * sin_tilt
                pz = solenoid_z + py_local * sin_tilt + pz_local * cos_tilt
                loop_pts.append((px, py, pz))

            loop_obj = build_curved_tube(f"{prefix}_Ext_Loop_{loop_idx}_{side}", loop_pts, 0.0009, mat_flux, collection, ring_res=8)
            if loop_obj:
                objs.append(loop_obj)

            # Directional arrow on return loop (pointing towards South: -X)
            mid_idx = steps // 2
            mid_pt = loop_pts[mid_idx]
            next_pt = loop_pts[mid_idx + 1]
            dir_v = (Vector(next_pt) - Vector(mid_pt)).normalized()
            arrow = build_vector_arrow(f"{prefix}_Ext_Arrow_{loop_idx}_{side}", mid_pt, dir_v, mat_flux, collection, length=0.008, radius=0.0028)
            objs.append(arrow)

    return objs

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.35, -0.40, 0.40), (9.0, 9.0, 8.8), 10.0, 0.50),
        ("Fill_Light", 'AREA', (-0.45, -0.35, 0.25), (6.0, 6.0, 6.2), 6.5, 0.55),
        ("Rim_Light", 'SPOT', (0.0, 0.45, 0.35), (8.5, 8.5, 8.5), 9.0, 0.40),
        ("Bottom_Bounce", 'POINT', (0.0, -0.15, 0.03), (3.0, 3.0, 3.2), 3.0, 0.15),
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

def frame_camera_on_target(cam_obj, target_center, distance, elev_deg=30, azim_deg=-28):
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

    world = bpy.data.worlds.new("Solenoid_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Solenoid_Full (Complete Laboratory Apparatus)
    col_full = bpy.data.collections.new("Solenoid_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_solenoid_model("Full", is_section=False, collection=col_full)

    # 2. Collection: Solenoid_Section (Longitudinal Cutaway Showing Uniform Internal Field & Polarity)
    col_section = bpy.data.collections.new("Solenoid_Section")
    bpy.context.scene.collection.children.link(col_section)
    sec_objs = build_solenoid_model("Sec", is_section=True, collection=col_section)

    cam_data = bpy.data.cameras.new("Macro_Camera")
    cam_data.lens = 52.0
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

    # Render Preview 1: Solenoid_Full
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.055)), distance=0.44, elev_deg=26, azim_deg=-32)
    kit.configure_render(width=1280, height=720, samples=32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Solenoid_Section
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.055)), distance=0.40, elev_deg=34, azim_deg=-24)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== SOLENOID BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()