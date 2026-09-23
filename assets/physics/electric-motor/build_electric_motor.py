"""
build_electric_motor.py — DC Electric Motor Working Demonstration Model
NCERT Class 10 Chapter 13 (Magnetic Effects of Electric Current), Section 13.4, Figure 13.15.

Dual Collections:
- Motor_Full: Complete authentic working DC motor apparatus (armature ABCD, N/S concave poles,
  split-ring commutator P/Q, carbon brushes X/Y, axle, base, battery terminals, plug key).
- Motor_Section: Working physics demonstration view with magnetic field lines (B), current vectors (I),
  and Fleming's Left-Hand Rule force vectors (F) acting downward on AB and upward on CD.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'electric-motor'

# Realistic Materials
COLOR_NORTH = (0.85, 0.12, 0.12)       # Permanent magnet North (vivid red)
COLOR_SOUTH = (0.12, 0.35, 0.88)       # Permanent magnet South (vivid blue)
COLOR_COPPER = (0.94, 0.52, 0.22)      # Enamelled copper winding
COLOR_STEEL = (0.88, 0.89, 0.92)       # Polished stainless steel axle
COLOR_BRASS = (0.88, 0.72, 0.25)       # Machined brass commutator and bushings
COLOR_CARBON = (0.10, 0.10, 0.11)      # Graphite carbon brushes
COLOR_BASE = (0.14, 0.15, 0.18)        # Cast iron machinery base
COLOR_INSULATOR = (0.08, 0.08, 0.08)   # Hard phenolic insulating sleeve
COLOR_WIRE_POS = (0.85, 0.15, 0.15)    # Red positive wire
COLOR_WIRE_NEG = (0.15, 0.15, 0.18)    # Black negative wire
COLOR_B_FIELD = (0.15, 0.85, 0.95)     # Cyan magnetic field lines
COLOR_FORCE = (0.98, 0.85, 0.10)       # Golden yellow force vectors
COLOR_CURRENT = (0.95, 0.30, 0.15)     # Orange current chevrons

def link_strictly(obj, target_col):
    """Ensures obj is linked ONLY to target_col and not root scene collection."""
    if obj.name not in target_col.objects:
        target_col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_pbr_metal(name, color, metallic=0.92, roughness=0.25):
    return kit.add_machined_metal_material(name, color, metallic=metallic, roughness=roughness)

def create_curved_tube(name, points, radius, mat, collection, resolution=12):
    curve_data = bpy.data.curves.new(name=f"{name}_data", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = resolution
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    obj.data.materials.append(mat)
    link_strictly(obj, collection)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    return obj

def make_split_ring_half(name, theta_start, theta_end, r_in, r_out, y_start, y_end, center_z, mat, collection, segments=16):
    bm = bmesh.new()
    ring_verts = []
    for s in range(segments + 1):
        frac = s / segments
        theta = theta_start + frac * (theta_end - theta_start)
        ct = math.cos(theta)
        st = math.sin(theta)
        v_of = bm.verts.new((r_out * ct, y_start, center_z + r_out * st))
        v_if = bm.verts.new((r_in  * ct, y_start, center_z + r_in  * st))
        v_ib = bm.verts.new((r_in  * ct, y_end,   center_z + r_in  * st))
        v_ob = bm.verts.new((r_out * ct, y_end,   center_z + r_out * st))
        ring_verts.append((v_of, v_if, v_ib, v_ob))

    for s in range(segments):
        (of1, if1, ib1, ob1) = ring_verts[s]
        (of2, if2, ib2, ob2) = ring_verts[s+1]
        bm.faces.new([of1, ob1, ob2, of2])
        bm.faces.new([if1, if2, ib2, ib1])
        bm.faces.new([of1, of2, if2, if1])
        bm.faces.new([ob1, ib1, ib2, ob2])

    (of_s, if_s, ib_s, ob_s) = ring_verts[0]
    (of_e, if_e, ib_e, ob_e) = ring_verts[-1]
    bm.faces.new([of_s, if_s, ib_s, ob_s])
    bm.faces.new([of_e, ob_e, ib_e, if_e])

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

def make_concave_pole(name, is_north, r_inner, x_outer, y_len, center_z, mat, collection, segments=16):
    bm = bmesh.new()
    theta_0 = math.radians(45.0)
    sign = 1.0 if is_north else -1.0
    slices = []
    y1, y2 = -y_len / 2, y_len / 2
    for s in range(segments + 1):
        frac = s / segments
        theta = -theta_0 + frac * (2 * theta_0)
        ct = math.cos(theta)
        st = math.sin(theta)
        v_in_front  = bm.verts.new((sign * r_inner * ct, y1, center_z + r_inner * st))
        v_in_back   = bm.verts.new((sign * r_inner * ct, y2, center_z + r_inner * st))
        v_out_back  = bm.verts.new((sign * x_outer,      y2, center_z + r_inner * st))
        v_out_front = bm.verts.new((sign * x_outer,      y1, center_z + r_inner * st))
        slices.append((v_in_front, v_in_back, v_out_back, v_out_front))

    for s in range(segments):
        (inf1, inb1, oub1, ouf1) = slices[s]
        (inf2, inb2, oub2, ouf2) = slices[s+1]
        bm.faces.new([inf1, inf2, inb2, inb1])
        bm.faces.new([ouf1, oub1, oub2, ouf2])
        bm.faces.new([inf1, ouf1, ouf2, inf2])
        bm.faces.new([inb1, inb2, oub2, oub1])

    (inf_s, inb_s, oub_s, ouf_s) = slices[0]
    (inf_e, inb_e, oub_e, ouf_e) = slices[-1]
    bm.faces.new([inf_s, inb_s, oub_s, ouf_s])
    bm.faces.new([inf_e, ouf_e, oub_e, inb_e])

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

def build_vector_arrow(name, start, end, radius, mat, collection):
    objs = []
    direction = end - start
    length = direction.length
    if length < 1e-5:
        return objs

    head_len = min(0.012, length * 0.35)
    shaft_len = length - head_len
    shaft_mid = start + direction.normalized() * (shaft_len * 0.5)

    shaft = kit.primitive_object(f"{name}_shaft", 'cylinder', mat,
                                size=(radius * 2, radius * 2, shaft_len),
                                location=shaft_mid)
    rot_quat = direction.to_track_quat('Z', 'Y')
    shaft.rotation_euler = rot_quat.to_euler()
    link_strictly(shaft, collection)
    objs.append(shaft)

    head_pos = start + direction.normalized() * (shaft_len + head_len * 0.5)
    head = kit.primitive_object(f"{name}_head", 'cone', mat,
                               size=(radius * 4.5, radius * 4.5, head_len),
                               location=head_pos)
    head.rotation_euler = rot_quat.to_euler()
    link_strictly(head, collection)
    objs.append(head)

    return objs

def build_motor_model(prefix, is_section, collection):
    objs = []

    mat_north = kit.add_material(f"{prefix}_north", COLOR_NORTH, metallic=0.35, roughness=0.30)
    mat_south = kit.add_material(f"{prefix}_south", COLOR_SOUTH, metallic=0.35, roughness=0.30)
    mat_copper = create_pbr_metal(f"{prefix}_copper", COLOR_COPPER, metallic=0.96, roughness=0.18)
    mat_steel = create_pbr_metal(f"{prefix}_steel", COLOR_STEEL, metallic=0.98, roughness=0.14)
    mat_brass = create_pbr_metal(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    mat_carbon = kit.add_material(f"{prefix}_carbon", COLOR_CARBON, metallic=0.08, roughness=0.75)
    mat_base = kit.add_material(f"{prefix}_base", COLOR_BASE, metallic=0.65, roughness=0.55)
    mat_insulator = kit.add_material(f"{prefix}_insulator", COLOR_INSULATOR, metallic=0.05, roughness=0.45)
    mat_pos = kit.add_material(f"{prefix}_pos", COLOR_WIRE_POS, metallic=0.1, roughness=0.4)
    mat_neg = kit.add_material(f"{prefix}_neg", COLOR_WIRE_NEG, metallic=0.1, roughness=0.4)

    # 1. Base Plate
    base = kit.primitive_object(f"{prefix}_Base_Plate", 'cube', mat_base,
                                size=(0.19, 0.17, 0.012),
                                location=(0.0, 0.0, 0.006))
    link_strictly(base, collection)
    objs.append(base)

    # 2. Bearing Pillars & Bushings
    z_axle = 0.072
    for y_pos in [-0.058, 0.058]:
        pillar = kit.primitive_object(f"{prefix}_Pillar_{y_pos}", 'cube', mat_base,
                                      size=(0.016, 0.012, 0.072),
                                      location=(0.0, y_pos, 0.046))
        bushing = kit.primitive_object(f"{prefix}_Bushing_{y_pos}", 'cylinder', mat_brass,
                                       size=(0.012, 0.012, 0.014),
                                       location=(0.0, y_pos, z_axle),
                                       rotation_euler=(math.pi / 2, 0.0, 0.0))
        link_strictly(pillar, collection)
        link_strictly(bushing, collection)
        objs.extend([pillar, bushing])

    # 3. Permanent Field Magnets (North on +X / red, South on -X / blue)
    r_concave = 0.028
    x_pole_outer = 0.056
    y_pole_len = 0.076

    n_pole = make_concave_pole(f"{prefix}_North_Pole", True, r_concave, x_pole_outer, y_pole_len, z_axle, mat_north, collection)
    s_pole = make_concave_pole(f"{prefix}_South_Pole", False, r_concave, x_pole_outer, y_pole_len, z_axle, mat_south, collection)
    objs.extend([n_pole, s_pole])

    # 4. Central Rotating Axle
    axle = kit.primitive_object(f"{prefix}_Axle", 'cylinder', mat_steel,
                                size=(0.006, 0.006, 0.165),
                                location=(0.0, 0.0, z_axle),
                                rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(axle, collection)
    objs.append(axle)

    # 5. Cylindrical Soft Iron Armature Core
    core = kit.primitive_object(f"{prefix}_Armature_Core", 'cylinder', mat_base,
                                size=(0.021, 0.021, 0.056),
                                location=(0.0, 0.0, z_axle),
                                rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(core, collection)
    objs.append(core)

    # 6. Rectangular Armature Coil ABCD
    w_half = 0.023
    wire_r = 0.0016

    arm_ab = kit.primitive_object(f"{prefix}_Coil_Arm_AB", 'cylinder', mat_copper,
                                  size=(wire_r * 2, wire_r * 2, 0.062),
                                  location=(w_half, 0.0, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    arm_cd = kit.primitive_object(f"{prefix}_Coil_Arm_CD", 'cylinder', mat_copper,
                                  size=(wire_r * 2, wire_r * 2, 0.062),
                                  location=(-w_half, 0.0, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(arm_ab, collection)
    link_strictly(arm_cd, collection)
    objs.extend([arm_ab, arm_cd])

    for y_pos, name in [(-0.031, 'BC'), (0.031, 'DA')]:
        arch_pts = [
            Vector((w_half, y_pos, z_axle)),
            Vector((0.012, y_pos, z_axle + 0.007)),
            Vector((0.0, y_pos, z_axle + 0.011)),
            Vector((-0.012, y_pos, z_axle + 0.007)),
            Vector((-w_half, y_pos, z_axle)),
        ]
        arch = create_curved_tube(f"{prefix}_Coil_End_{name}", arch_pts, wire_r, mat_copper, collection)
        objs.append(arch)

    # 7. Split-Ring Commutator (P and Q) & Insulating Sleeve
    y_comm = -0.044
    r_comm_in = 0.0045
    r_comm_out = 0.0072
    y_comm_len = 0.010
    gap_rad = math.radians(24.0)

    sleeve = kit.primitive_object(f"{prefix}_Commutator_Sleeve", 'cylinder', mat_insulator,
                                  size=(r_comm_in * 2, r_comm_in * 2, y_comm_len + 0.002),
                                  location=(0.0, y_comm, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(sleeve, collection)
    objs.append(sleeve)

    comm_p = make_split_ring_half(f"{prefix}_Commutator_P",
                                  -math.pi / 2 + gap_rad / 2, math.pi / 2 - gap_rad / 2,
                                  r_comm_in, r_comm_out,
                                  y_comm - y_comm_len / 2, y_comm + y_comm_len / 2,
                                  z_axle, mat_brass, collection)
    comm_q = make_split_ring_half(f"{prefix}_Commutator_Q",
                                  math.pi / 2 + gap_rad / 2, 3 * math.pi / 2 - gap_rad / 2,
                                  r_comm_in, r_comm_out,
                                  y_comm - y_comm_len / 2, y_comm + y_comm_len / 2,
                                  z_axle, mat_brass, collection)
    objs.extend([comm_p, comm_q])

    lead_p_pts = [Vector((0.008, -0.031, z_axle)), Vector((0.006, y_comm + y_comm_len/2, z_axle))]
    lead_q_pts = [Vector((-0.008, -0.031, z_axle)), Vector((-0.006, y_comm + y_comm_len/2, z_axle))]
    lead_p = create_curved_tube(f"{prefix}_Lead_P", lead_p_pts, 0.0009, mat_copper, collection)
    lead_q = create_curved_tube(f"{prefix}_Lead_Q", lead_q_pts, 0.0009, mat_copper, collection)
    objs.extend([lead_p, lead_q])

    # 8. Stationary Carbon Contact Brushes X and Y
    brush_w, brush_d, brush_h = 0.005, 0.007, 0.006
    brush_x_pos = r_comm_out + brush_w / 2
    brush_x = kit.primitive_object(f"{prefix}_Brush_X", 'cube', mat_carbon,
                                   size=(brush_w, brush_d, brush_h),
                                   location=(brush_x_pos, y_comm, z_axle))
    brush_y = kit.primitive_object(f"{prefix}_Brush_Y", 'cube', mat_carbon,
                                   size=(brush_w, brush_d, brush_h),
                                   location=(-brush_x_pos, y_comm, z_axle))
    link_strictly(brush_x, collection)
    link_strictly(brush_y, collection)
    objs.extend([brush_x, brush_y])

    holder_x = kit.primitive_object(f"{prefix}_Holder_X", 'cube', mat_brass,
                                    size=(0.012, 0.003, 0.006),
                                    location=(brush_x_pos + 0.008, y_comm, z_axle))
    holder_y = kit.primitive_object(f"{prefix}_Holder_Y", 'cube', mat_brass,
                                    size=(0.012, 0.003, 0.006),
                                    location=(-brush_x_pos - 0.008, y_comm, z_axle))
    link_strictly(holder_x, collection)
    link_strictly(holder_y, collection)
    objs.extend([holder_x, holder_y])

    # 9. Supply Terminals & Circuit Connections
    for x_pos, name, mat_term in [(-0.065, 'Pos', mat_pos), (0.065, 'Neg', mat_neg)]:
        post = kit.primitive_object(f"{prefix}_Terminal_{name}", 'cylinder', mat_brass,
                                    size=(0.010, 0.010, 0.020),
                                    location=(x_pos, -0.068, 0.022))
        collar = kit.primitive_object(f"{prefix}_Collar_{name}", 'cylinder', mat_term,
                                      size=(0.012, 0.012, 0.007),
                                      location=(x_pos, -0.068, 0.016))
        link_strictly(post, collection)
        link_strictly(collar, collection)
        objs.extend([post, collar])

    wire_pos_pts = [
        Vector((-0.065, -0.068, 0.022)),
        Vector((-0.045, -0.055, 0.016)),
        Vector((-brush_x_pos - 0.014, y_comm, z_axle)),
    ]
    wire_neg_pts = [
        Vector((0.065, -0.068, 0.022)),
        Vector((0.045, -0.055, 0.016)),
        Vector((brush_x_pos + 0.014, y_comm, z_axle)),
    ]
    w_pos = create_curved_tube(f"{prefix}_Wire_Pos", wire_pos_pts, 0.0014, mat_pos, collection)
    w_neg = create_curved_tube(f"{prefix}_Wire_Neg", wire_neg_pts, 0.0014, mat_neg, collection)
    objs.extend([w_pos, w_neg])

    key_base = kit.primitive_object(f"{prefix}_Key_Base", 'cube', mat_base,
                                   size=(0.035, 0.020, 0.010),
                                   location=(0.0, -0.068, 0.017))
    key_brass = kit.primitive_object(f"{prefix}_Key_Plug", 'cylinder', mat_brass,
                                    size=(0.006, 0.006, 0.016),
                                    location=(0.0, -0.068, 0.028))
    link_strictly(key_base, collection)
    link_strictly(key_brass, collection)
    objs.extend([key_base, key_brass])

    # 10. Output Pulley
    pulley = kit.primitive_object(f"{prefix}_Pulley", 'cylinder', mat_steel,
                                  size=(0.026, 0.026, 0.008),
                                  location=(0.0, 0.074, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    link_strictly(pulley, collection)
    objs.append(pulley)

    # 11. Physics Vectors (ONLY in section view!)
    if is_section:
        mat_b = kit.add_material(f"{prefix}_mat_B", COLOR_B_FIELD, metallic=0.1, roughness=0.3)
        mat_f = kit.add_material(f"{prefix}_mat_F", COLOR_FORCE, metallic=0.2, roughness=0.25)
        mat_i = kit.add_material(f"{prefix}_mat_I", COLOR_CURRENT, metallic=0.2, roughness=0.3)

        # B field lines across pole gap
        for y_b in [-0.020, 0.0, 0.020]:
            b_arrow = build_vector_arrow(f"{prefix}_B_Field_{y_b}",
                                        Vector((0.026, y_b, z_axle + 0.018)),
                                        Vector((-0.026, y_b, z_axle + 0.018)),
                                        0.0009, mat_b, collection)
            objs.extend(b_arrow)

        # Current vectors along arms
        i_ab = build_vector_arrow(f"{prefix}_Current_AB",
                                  Vector((w_half, -0.022, z_axle + 0.004)),
                                  Vector((w_half, 0.022, z_axle + 0.004)),
                                  0.0011, mat_i, collection)
        i_cd = build_vector_arrow(f"{prefix}_Current_CD",
                                  Vector((-w_half, 0.022, z_axle + 0.004)),
                                  Vector((-w_half, -0.022, z_axle + 0.004)),
                                  0.0011, mat_i, collection)
        objs.extend(i_ab)
        objs.extend(i_cd)

        # Fleming's Left-Hand Rule Force vectors:
        # Downward force on AB
        f_ab = build_vector_arrow(f"{prefix}_Force_AB",
                                  Vector((w_half, 0.0, z_axle)),
                                  Vector((w_half, 0.0, z_axle - 0.038)),
                                  0.0014, mat_f, collection)
        # Upward force on CD
        f_cd = build_vector_arrow(f"{prefix}_Force_CD",
                                  Vector((-w_half, 0.0, z_axle)),
                                  Vector((-w_half, 0.0, z_axle + 0.038)),
                                  0.0014, mat_f, collection)
        objs.extend(f_ab)
        objs.extend(f_cd)

    return objs

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.45, -0.55, 0.40), (9.5, 9.5, 9.2), 9.5, 0.45),
        ("Fill_Light", 'AREA', (-0.50, -0.45, 0.30), (5.5, 5.5, 6.0), 5.5, 0.55),
        ("Rim_Light", 'SPOT', (0.0, 0.55, 0.45), (8.5, 8.5, 8.5), 8.5, 0.35),
        ("Bottom_Bounce", 'POINT', (0.0, -0.25, 0.02), (3.0, 3.0, 3.2), 3.0, 0.20),
    ]

    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.1
            light_data.spot_blend = 0.35

        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance, elev_deg=22, azim_deg=-30):
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

    world = bpy.data.worlds.new("Motor_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Motor_Full
    col_full = bpy.data.collections.new("Motor_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_motor_model("Full", is_section=False, collection=col_full)

    # 2. Collection: Motor_Section
    col_section = bpy.data.collections.new("Motor_Section")
    bpy.context.scene.collection.children.link(col_section)
    sec_objs = build_motor_model("Sec", is_section=True, collection=col_section)

    # Camera setup (55mm macro lens)
    cam_data = bpy.data.cameras.new("Macro_Camera")
    cam_data.lens = 55.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Macro_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    # Make all visible for glTF export
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

    # Render Preview 1: Motor_Full (Isometric beauty angle)
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.055)), distance=0.38, elev_deg=26, azim_deg=-45)
    kit.configure_render(width=1280, height=720, samples=32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Motor_Section (Focused demonstration shot with B-field, I, and F vectors)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.065)), distance=0.30, elev_deg=28, azim_deg=-52)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== ELECTRIC MOTOR BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
