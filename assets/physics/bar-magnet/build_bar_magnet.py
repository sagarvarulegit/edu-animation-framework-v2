"""
build_bar_magnet.py — High-Fidelity AlNiCo Bar Magnet with 3D Magnetic Field Lines
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'bar-magnet'

def build_bar_magnet():
    north_mat = kit.add_material('magnet-north', (0.85, 0.12, 0.12), metallic=0.2, roughness=0.3)
    south_mat = kit.add_material('magnet-south', (0.12, 0.35, 0.85), metallic=0.2, roughness=0.3)
    white_mat = kit.add_material('magnet-label', (0.95, 0.95, 0.95), metallic=0.1, roughness=0.3)
    flux_mat = kit.add_material('magnetic-flux', (0.22, 0.74, 0.97), metallic=0.0, roughness=0.2)
    flux_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.22, 0.74, 0.97, 1.0)
    flux_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3.5

    brass_mat = kit.add_machined_metal_material('compass-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    glass_mat = kit.add_glass_material('compass-glass', (0.98, 0.99, 1.0), ior=1.50, roughness=0.01)

    objects = []

    # 1. North Pole Block (Red, +X half)
    # Size: length 0.06m, width 0.024m, height 0.016m, centered at x = +0.03m
    north_half = kit.primitive_object(f'{ASSET_ID}-north', 'cube', north_mat,
                                      size=(0.06, 0.024, 0.016),
                                      location=(0.03, 0.0, 0.008))
    objects.append(north_half)

    # 2. South Pole Block (Blue, -X half)
    south_half = kit.primitive_object(f'{ASSET_ID}-south', 'cube', south_mat,
                                      size=(0.06, 0.024, 0.016),
                                      location=(-0.03, 0.0, 0.008))
    objects.append(south_half)

    # 3. Pole Labels ('N' and 'S' raised plates)
    n_plate = kit.primitive_object(f'{ASSET_ID}-label-n', 'cube', white_mat,
                                   size=(0.008, 0.008, 0.001),
                                   location=(0.045, 0.0, 0.0165))
    s_plate = kit.primitive_object(f'{ASSET_ID}-label-s', 'cube', white_mat,
                                   size=(0.008, 0.008, 0.001),
                                   location=(-0.045, 0.0, 0.0165))
    objects.extend([n_plate, s_plate])

    # 4. 3D Magnetic Field Lines (Smooth curved parametric tubes)
    # Loops emerge from +X (North), curve in 3D around to -X (South)
    # We generate concentric loops in the XY plane and oblique planes
    radii = [
        (0.08, 0.040, 0.0),
        (0.10, 0.065, 0.0),
        (0.13, 0.095, 0.0),
        (0.08, -0.040, 0.0),
        (0.10, -0.065, 0.0),
        (0.13, -0.095, 0.0),
        (0.09, 0.030, 0.035),
        (0.09, -0.030, 0.035)
    ]

    for idx, (a, b, z_tilt) in enumerate(radii):
        bm = bmesh.new()
        steps = 40
        verts_pts = []
        for s in range(steps + 1):
            t = math.pi * s / steps  # from 0 to pi
            # x = a * cos(t), y = b * sin(t)
            px = a * math.cos(t)
            py = b * math.sin(t)
            pz = 0.008 + z_tilt * math.sin(t)
            verts_pts.append((px, py, pz))

        # Build tube around trajectory
        curve_verts = []
        ring_res = 8
        tube_r = 0.0008
        for i, (px, py, pz) in enumerate(verts_pts):
            # Compute tangent
            if i < steps:
                tx = verts_pts[i+1][0] - px
                ty = verts_pts[i+1][1] - py
                tz = verts_pts[i+1][2] - pz
            else:
                tx = px - verts_pts[i-1][0]
                ty = py - verts_pts[i-1][1]
                tz = pz - verts_pts[i-1][2]
            tangent = Vector((tx, ty, tz)).normalized()
            normal = Vector((0, 0, 1)).cross(tangent)
            if normal.length < 0.001:
                normal = Vector((0, 1, 0)).cross(tangent)
            normal.normalize()
            binormal = tangent.cross(normal).normalized()

            ring = []
            for r_idx in range(ring_res):
                ang = 2 * math.pi * r_idx / ring_res
                vx = px + (normal.x * math.cos(ang) + binormal.x * math.sin(ang)) * tube_r
                vy = py + (normal.y * math.cos(ang) + binormal.y * math.sin(ang)) * tube_r
                vz = pz + (normal.z * math.cos(ang) + binormal.z * math.sin(ang)) * tube_r
                ring.append(bm.verts.new((vx, vy, vz)))
            curve_verts.append(ring)

        for i in range(steps):
            for r_idx in range(ring_res):
                next_r = (r_idx + 1) % ring_res
                v1 = curve_verts[i][r_idx]
                v2 = curve_verts[i+1][r_idx]
                v3 = curve_verts[i+1][next_r]
                v4 = curve_verts[i][next_r]
                bm.faces.new([v1, v2, v3, v4])

        # Cap endpoints to make fully watertight (0 non-manifold edges)
        bm.faces.new(curve_verts[0])
        bm.faces.new(list(reversed(curve_verts[-1])))

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        mesh = bpy.data.meshes.new(f'{ASSET_ID}-flux-{idx}')
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = True
        f_obj = bpy.data.objects.new(f'{ASSET_ID}-flux-{idx}', mesh)
        bpy.context.collection.objects.link(f_obj)
        f_obj.data.materials.append(flux_mat)
        objects.append(f_obj)

        # Directional arrow indicators on external magnetic field lines pointing North (+X) to South (-X)
        mid_idx = steps // 2
        mid_p = verts_pts[mid_idx]
        next_p = verts_pts[mid_idx + 1]
        tan_dir = (Vector(next_p) - Vector(mid_p)).normalized()
        arrow_rot = tan_dir.to_track_quat('Z', 'Y').to_euler()
        arrow = kit.primitive_object(f'{ASSET_ID}-arrow-{idx}', 'cone', flux_mat,
                                    size=(0.0035, 0.0, 0.006),
                                    location=mid_p,
                                    rotation_euler=arrow_rot)
        objects.append(arrow)

    # 5. Magnetic Plotting Compass (placed on field line at x = 0, y = 0.065m)
    c_case = kit.primitive_object(f'{ASSET_ID}-compass-case', 'cylinder', brass_mat,
                                  size=(0.022, 0.022, 0.006),
                                  location=(0.0, 0.065, 0.003))
    c_glass = kit.primitive_object(f'{ASSET_ID}-compass-glass', 'cylinder', glass_mat,
                                   size=(0.020, 0.020, 0.001),
                                   location=(0.0, 0.065, 0.0065))
    # Compass needle (red North tip pointing tangent to field line in -X direction)
    n_needle = kit.primitive_object(f'{ASSET_ID}-needle-n', 'cone', north_mat,
                                    size=(0.004, 0.004, 0.009),
                                    location=(-0.0045, 0.065, 0.0045),
                                    rotation_euler=(0, -math.pi / 2, 0))
    s_needle = kit.primitive_object(f'{ASSET_ID}-needle-s', 'cone', south_mat,
                                    size=(0.004, 0.004, 0.009),
                                    location=(0.0045, 0.065, 0.0045),
                                    rotation_euler=(0, math.pi / 2, 0))
    objects.extend([c_case, c_glass, n_needle, s_needle])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_bar_magnet()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()