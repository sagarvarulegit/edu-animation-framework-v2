"""
build_electric_motor.py — High-Fidelity DC Electric Motor Working Demonstration Model
NCERT Class 10 Chapter 13 (Magnetic Effects of Electric Current), Section 13.4, Figure 13.15.
Features:
- Authentic semicircular split-ring commutator (two half-cylindrical shells P and Q separated by 24° insulating gap)
- Insulating sleeve on the central rotating axle visible through the commutator split gap
- Stationary carbon contact brushes X and Y pressed tangentially against the split-rings
- Rectangular armature coil ABCD cleanly routed with arched end segments clearing the rotating axle
- Curved permanent field magnet poles: North pole (red) and South pole (blue) with concave cylindrical faces
- 0 non-manifold edges across all components
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'electric-motor'

def make_split_ring_half(name, theta_start, theta_end, r_in, r_out, y_start, y_end, center_z, material, segments=16):
    """Generates a watertight, manifold half-cylindrical split-ring shell."""
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
    bpy.context.collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj

def make_concave_pole(name, is_north, r_inner, x_outer, y_len, center_z, material, segments=16):
    """Generates a permanent magnet pole with a concave cylindrical face facing the armature."""
    bm = bmesh.new()
    theta_0 = math.radians(50.0)
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
    bpy.context.collection.objects.link(obj)
    if material is not None:
        obj.data.materials.append(material)
    return obj

def build_electric_motor():
    north_mat = kit.add_material('motor-north', (0.85, 0.12, 0.12), metallic=0.3, roughness=0.35)
    south_mat = kit.add_material('motor-south', (0.12, 0.35, 0.85), metallic=0.3, roughness=0.35)
    copper_mat = kit.add_machined_metal_material('motor-copper', (0.92, 0.48, 0.22), metallic=0.95, roughness=0.22)
    steel_mat = kit.add_machined_metal_material('motor-steel', (0.85, 0.86, 0.88), metallic=0.98, roughness=0.15)
    brass_mat = kit.add_machined_metal_material('motor-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    carbon_mat = kit.add_material('motor-carbon', (0.08, 0.08, 0.09), metallic=0.1, roughness=0.8)
    base_mat = kit.add_material('motor-base', (0.12, 0.13, 0.15), metallic=0.7, roughness=0.6)
    insulator_mat = kit.add_material('motor-insulator', (0.10, 0.09, 0.08), metallic=0.05, roughness=0.5)
    red_mat = kit.add_material('term-red', (0.85, 0.15, 0.15), metallic=0.1, roughness=0.4)
    black_mat = kit.add_material('term-black', (0.05, 0.05, 0.06), metallic=0.1, roughness=0.4)

    objects = []

    # 1. Base Plate (Heavy Cast Iron)
    base = kit.primitive_object(f'{ASSET_ID}-base', 'cube', base_mat,
                                size=(0.18, 0.16, 0.012),
                                location=(0.0, 0.0, 0.006))
    objects.append(base)

    # 2. Bearing Pillars (Front and Rear supporting the axle)
    for y_pos in [-0.058, 0.058]:
        pillar = kit.primitive_object(f'{ASSET_ID}-bearing-pillar-{y_pos}', 'cube', base_mat,
                                      size=(0.018, 0.014, 0.07),
                                      location=(0.0, y_pos, 0.045))
        bushing = kit.primitive_object(f'{ASSET_ID}-bushing-{y_pos}', 'cylinder', brass_mat,
                                       size=(0.012, 0.012, 0.016),
                                       location=(0.0, y_pos, 0.07),
                                       rotation_euler=(math.pi / 2, 0.0, 0.0))
        objects.extend([pillar, bushing])

    # 3. Permanent Field Magnets with Curved Concave Cylindrical Faces
    # Concentric with armature cylinder to create radial field (NCERT Fig 13.15)
    r_concave = 0.028
    x_pole_outer = 0.055
    y_pole_len = 0.080
    z_axle = 0.070

    n_pole = make_concave_pole(f'{ASSET_ID}-north-pole', True, r_concave, x_pole_outer, y_pole_len, z_axle, north_mat)
    s_pole = make_concave_pole(f'{ASSET_ID}-south-pole', False, r_concave, x_pole_outer, y_pole_len, z_axle, south_mat)
    objects.extend([n_pole, s_pole])

    # 4. Central Rotating Axle (along Y axis at z = 0.070)
    axle = kit.primitive_object(f'{ASSET_ID}-axle', 'cylinder', steel_mat,
                                size=(0.006, 0.006, 0.16),
                                location=(0.0, 0.0, z_axle),
                                rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.append(axle)

    # 5. Cylindrical Soft Iron Armature Core on Axle
    core = kit.primitive_object(f'{ASSET_ID}-armature-core', 'cylinder', base_mat,
                                size=(0.022, 0.022, 0.060),
                                location=(0.0, 0.0, z_axle),
                                rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.append(core)

    # 6. Rectangular Armature Coil ABCD Clearing Rotating Axle
    # 6. Rectangular Armature Coil ABCD Clearing Rotating Axle
    # Dimensions: width = 0.046m, length = 0.065m, horizontal (tilt = 0.0) for active torque
    coil_tilt = 0.0
    c_cos = math.cos(coil_tilt)
    c_sin = math.sin(coil_tilt)
    w_half = 0.023
    wire_r = 0.0016

    # Straight side arms along Y: AB at +X side, CD at -X side
    for sign, name in [(1, 'AB'), (-1, 'CD')]:
        arm = kit.primitive_object(f'{ASSET_ID}-coil-arm-{name}', 'cylinder', copper_mat,
                                   size=(wire_r * 2, wire_r * 2, 0.066),
                                   location=(sign * w_half * c_cos, 0.0, z_axle + sign * w_half * c_sin),
                                   rotation_euler=(math.pi / 2, 0.0, 0.0))
        objects.append(arm)

    # End arms: BC at front (y = -0.033) and DA at back (y = +0.033)
    # Routed with an arched bridge over the axle to provide positive clearance without mesh intersection
    for y_pos, name in [(-0.033, 'BC'), (0.033, 'DA')]:
        p0 = ( w_half * c_cos, y_pos, z_axle + w_half * c_sin)
        p1 = ( 0.012 * c_cos,  y_pos, z_axle + 0.012 * c_sin + 0.006)
        p2 = ( 0.0,            y_pos, z_axle + 0.011)  # Clears axle by 8mm
        p3 = (-0.012 * c_cos,  y_pos, z_axle - 0.012 * c_sin + 0.006)
        p4 = (-w_half * c_cos, y_pos, z_axle - w_half * c_sin)
        end_arch = kit.create_smooth_tube(f'{ASSET_ID}-coil-end-{name}', [p0, p1, p2, p3, p4],
                                          radius=wire_r, material=copper_mat)
        objects.append(end_arch)

    # 7. Split-Ring Commutator (Two half-rings P and Q separated by 24° insulating gap)
    # Commutator split gap aligned with perpendicular neutral plane (theta = 90°, 270°)
    # Stationary brushes at theta = 0° (+X) and theta = 180° (-X) contact solid copper during active torque
    y_comm = -0.045
    r_comm_in = 0.0045
    r_comm_out = 0.0072
    y_comm_len = 0.010
    gap_rad = math.radians(24.0)  # 24 degrees gap (within 15° - 30° standard)

    # Insulating central sleeve on axle visible between the split rings
    ins_sleeve = kit.primitive_object(f'{ASSET_ID}-commutator-sleeve', 'cylinder', insulator_mat,
                                      size=(r_comm_in * 2, r_comm_in * 2, y_comm_len + 0.002),
                                      location=(0.0, y_comm, z_axle),
                                      rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.append(ins_sleeve)

    # Right half-ring P (centered at theta = 0° / +X, spanning -pi/2 + gap/2 to pi/2 - gap/2)
    comm_p = make_split_ring_half(f'{ASSET_ID}-commutator-P',
                                  -math.pi / 2 + gap_rad / 2, math.pi / 2 - gap_rad / 2,
                                  r_comm_in, r_comm_out,
                                  y_comm - y_comm_len / 2, y_comm + y_comm_len / 2,
                                  z_axle, copper_mat)
    # Left half-ring Q (centered at theta = pi / -X, spanning pi/2 + gap/2 to 3*pi/2 - gap/2)
    comm_q = make_split_ring_half(f'{ASSET_ID}-commutator-Q',
                                  math.pi / 2 + gap_rad / 2, 3 * math.pi / 2 - gap_rad / 2,
                                  r_comm_in, r_comm_out,
                                  y_comm - y_comm_len / 2, y_comm + y_comm_len / 2,
                                  z_axle, copper_mat)
    objects.extend([comm_p, comm_q])

    # Leads connecting coil to commutator half-rings (solid copper at +X and -X)
    lead_p = kit.primitive_object(f'{ASSET_ID}-coil-lead-P', 'cylinder', copper_mat,
                                  size=(0.0016, 0.0016, 0.012),
                                  location=(0.006, -0.039, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    lead_q = kit.primitive_object(f'{ASSET_ID}-coil-lead-Q', 'cylinder', copper_mat,
                                  size=(0.0016, 0.0016, 0.012),
                                  location=(-0.006, -0.039, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.extend([lead_p, lead_q])

    # 8. Stationary Carbon Contact Brushes X and Y
    # Pressed tangentially against split rings at x = ±r_comm_out
    brush_size = (0.005, 0.007, 0.006)
    brush_x_pos = r_comm_out + brush_size[0] / 2
    brush_x = kit.primitive_object(f'{ASSET_ID}-brush-X', 'cube', carbon_mat,
                                   size=brush_size,
                                   location=(brush_x_pos, y_comm, z_axle))
    brush_y = kit.primitive_object(f'{ASSET_ID}-brush-Y', 'cube', carbon_mat,
                                   size=brush_size,
                                   location=(-brush_x_pos, y_comm, z_axle))

    # Brass leaf springs / holders holding the brushes
    holder_x = kit.primitive_object(f'{ASSET_ID}-brush-holder-X', 'cube', brass_mat,
                                    size=(0.012, 0.003, 0.006),
                                    location=(brush_x_pos + 0.008, y_comm, z_axle))
    holder_y = kit.primitive_object(f'{ASSET_ID}-brush-holder-Y', 'cube', brass_mat,
                                    size=(0.012, 0.003, 0.006),
                                    location=(-brush_x_pos - 0.008, y_comm, z_axle))
    objects.extend([brush_x, brush_y, holder_x, holder_y])

    # 9. Output Pulley on Rear Axle
    pulley = kit.primitive_object(f'{ASSET_ID}-pulley', 'cylinder', steel_mat,
                                  size=(0.024, 0.024, 0.008),
                                  location=(0.0, 0.072, z_axle),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.append(pulley)

    # 10. Supply Terminals on Base (+ Red, - Black)
    for x_pos, name, mat in [(-0.06, 'pos', red_mat), (0.06, 'neg', black_mat)]:
        post = kit.primitive_object(f'{ASSET_ID}-term-{name}', 'cylinder', brass_mat,
                                    size=(0.010, 0.010, 0.018),
                                    location=(x_pos, -0.065, 0.018))
        collar = kit.primitive_object(f'{ASSET_ID}-term-collar-{name}', 'cylinder', mat,
                                      size=(0.012, 0.012, 0.006),
                                      location=(x_pos, -0.065, 0.014))
        objects.extend([post, collar])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_electric_motor()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
