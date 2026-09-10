"""
build_solenoid.py — Helical Solenoid with Magnetic Field Lines
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'solenoid'

def build_solenoid():
    copper_mat = kit.add_machined_metal_material('solenoid-copper', (0.90, 0.45, 0.20), metallic=0.95, roughness=0.25)
    core_mat = kit.add_material('solenoid-core', (0.15, 0.16, 0.18), metallic=0.1, roughness=0.6)
    stand_mat = kit.add_material('solenoid-stand', (0.10, 0.11, 0.13), metallic=0.5, roughness=0.5)
    brass_mat = kit.add_machined_metal_material('solenoid-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    red_mat = kit.add_material('term-red', (0.85, 0.15, 0.15), metallic=0.1, roughness=0.4)
    black_mat = kit.add_material('term-black', (0.05, 0.05, 0.06), metallic=0.1, roughness=0.4)

    flux_mat = kit.add_material('magnetic-flux', (0.22, 0.74, 0.97), metallic=0.0, roughness=0.2)
    flux_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.22, 0.74, 0.97, 1.0)
    flux_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3.5

    objects = []

    # 1. Central Hollow Insulating Tube (aligned along X axis, length 0.16m, r = 0.018m)
    tube_len = 0.16
    tube = kit.primitive_object(f'{ASSET_ID}-core', 'cylinder', core_mat,
                                size=(0.036, 0.036, tube_len),
                                location=(0.0, 0.0, 0.05),
                                rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.append(tube)

    # 2. Helical Copper Wire Coil
    # Generate continuous 3D helix around cylinder
    bm_helix = bmesh.new()
    turns = 14
    steps_per_turn = 24
    total_steps = turns * steps_per_turn
    helix_r = 0.0195
    wire_r = 0.0016
    ring_res = 8

    pts = []
    for i in range(total_steps + 1):
        frac = i / total_steps
        x = (frac - 0.5) * (tube_len - 0.02)
        theta = 2 * math.pi * turns * frac
        y = helix_r * math.cos(theta)
        z = 0.05 + helix_r * math.sin(theta)
        pts.append((x, y, z))

    verts_rings = []
    for i, (px, py, pz) in enumerate(pts):
        if i < total_steps:
            tx = pts[i+1][0] - px
            ty = pts[i+1][1] - py
            tz = pts[i+1][2] - pz
        else:
            tx = px - pts[i-1][0]
            ty = py - pts[i-1][1]
            tz = pz - pts[i-1][2]
        tangent = Vector((tx, ty, tz)).normalized()
        normal = Vector((0, 0, 1)).cross(tangent)
        if normal.length < 0.001:
            normal = Vector((0, 1, 0)).cross(tangent)
        normal.normalize()
        binormal = tangent.cross(normal).normalized()

        ring = []
        for r_idx in range(ring_res):
            ang = 2 * math.pi * r_idx / ring_res
            vx = px + (normal.x * math.cos(ang) + binormal.x * math.sin(ang)) * wire_r
            vy = py + (normal.y * math.cos(ang) + binormal.y * math.sin(ang)) * wire_r
            vz = pz + (normal.z * math.cos(ang) + binormal.z * math.sin(ang)) * wire_r
            ring.append(bm_helix.verts.new((vx, vy, vz)))
        verts_rings.append(ring)

    for i in range(total_steps):
        for r_idx in range(ring_res):
            next_r = (r_idx + 1) % ring_res
            v1 = verts_rings[i][r_idx]
            v2 = verts_rings[i+1][r_idx]
            v3 = verts_rings[i+1][next_r]
            v4 = verts_rings[i][next_r]
            bm_helix.faces.new([v1, v2, v3, v4])

    # Cap coil endpoints to make fully watertight (0 non-manifold edges)
    bm_helix.faces.new(verts_rings[0])
    bm_helix.faces.new(list(reversed(verts_rings[-1])))

    bmesh.ops.recalc_face_normals(bm_helix, faces=bm_helix.faces)
    mesh_helix = bpy.data.meshes.new(f'{ASSET_ID}-coil')
    bm_helix.to_mesh(mesh_helix)
    bm_helix.free()
    for p in mesh_helix.polygons:
        p.use_smooth = True
    coil_obj = bpy.data.objects.new(f'{ASSET_ID}-coil', mesh_helix)
    bpy.context.collection.objects.link(coil_obj)
    coil_obj.data.materials.append(copper_mat)
    objects.append(coil_obj)

    # 3. Base & Support Pillars
    base = kit.primitive_object(f'{ASSET_ID}-base', 'cube', stand_mat,
                                size=(0.20, 0.09, 0.012),
                                location=(0.0, 0.0, 0.006))
    pillar_left = kit.primitive_object(f'{ASSET_ID}-pillar-left', 'cube', stand_mat,
                                       size=(0.015, 0.04, 0.045),
                                       location=(-0.065, 0.0, 0.03))
    pillar_right = kit.primitive_object(f'{ASSET_ID}-pillar-right', 'cube', stand_mat,
                                        size=(0.015, 0.04, 0.045),
                                        location=(0.065, 0.0, 0.03))
    objects.extend([base, pillar_left, pillar_right])

    # 4. Terminal Posts (+ Red, - Black)
    for side, x_pos, mat, label_mat in [('pos', -0.06, red_mat, red_mat), ('neg', 0.06, black_mat, black_mat)]:
        post = kit.primitive_object(f'{ASSET_ID}-term-{side}', 'cylinder', brass_mat,
                                    size=(0.010, 0.010, 0.016),
                                    location=(x_pos, -0.03, 0.018))
        collar = kit.primitive_object(f'{ASSET_ID}-collar-{side}', 'cylinder', mat,
                                      size=(0.012, 0.012, 0.005),
                                      location=(x_pos, -0.03, 0.014))
        objects.extend([post, collar])

    # 5. Magnetic Field Lines (Uniform interior lines + looping exterior lines)
    # Internal parallel axial lines
    for offset_y, offset_z in [(0.0, 0.0), (-0.008, 0.0), (0.008, 0.0), (0.0, -0.008), (0.0, 0.008)]:
        line = kit.primitive_object(f'{ASSET_ID}-internal-flux', 'cylinder', flux_mat,
                                    size=(0.0012, 0.0012, tube_len + 0.04),
                                    location=(0.0, offset_y, 0.05 + offset_z),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        objects.append(line)

    # External curved return flux loops
    for loop_idx, (a_rad, b_rad) in enumerate([(0.11, 0.045), (0.13, 0.065)]):
        for side in [-1, 1]:
            bm_loop = bmesh.new()
            steps = 36
            loop_pts = []
            for s in range(steps + 1):
                t = math.pi * s / steps
                px = a_rad * math.cos(t)
                py = side * b_rad * math.sin(t)
                pz = 0.05
                loop_pts.append((px, py, pz))

            ring_verts = []
            for i, (px, py, pz) in enumerate(loop_pts):
                if i < steps:
                    tx, ty, tz = loop_pts[i+1][0] - px, loop_pts[i+1][1] - py, loop_pts[i+1][2] - pz
                else:
                    tx, ty, tz = px - loop_pts[i-1][0], py - loop_pts[i-1][1], pz - loop_pts[i-1][2]
                tangent = Vector((tx, ty, tz)).normalized()
                normal = Vector((0, 0, 1)).cross(tangent).normalized()
                binormal = tangent.cross(normal).normalized()
                ring = []
                for r_idx in range(6):
                    ang = 2 * math.pi * r_idx / 6
                    vx = px + (normal.x * math.cos(ang) + binormal.x * math.sin(ang)) * 0.0008
                    vy = py + (normal.y * math.cos(ang) + binormal.y * math.sin(ang)) * 0.0008
                    vz = pz + (normal.z * math.cos(ang) + binormal.z * math.sin(ang)) * 0.0008
                    ring.append(bm_loop.verts.new((vx, vy, vz)))
                ring_verts.append(ring)

            for i in range(steps):
                for r_idx in range(6):
                    next_r = (r_idx + 1) % 6
                    bm_loop.faces.new([ring_verts[i][r_idx], ring_verts[i+1][r_idx],
                                       ring_verts[i+1][next_r], ring_verts[i][next_r]])

            # Cap endpoints to ensure manifold watertight mesh (0 non-manifold edges)
            bm_loop.faces.new(ring_verts[0])
            bm_loop.faces.new(list(reversed(ring_verts[-1])))

            bmesh.ops.recalc_face_normals(bm_loop, faces=bm_loop.faces)
            mesh_l = bpy.data.meshes.new(f'{ASSET_ID}-loop-{loop_idx}-{side}')
            bm_loop.to_mesh(mesh_l)
            bm_loop.free()
            for p in mesh_l.polygons:
                p.use_smooth = True
            l_obj = bpy.data.objects.new(f'{ASSET_ID}-loop-{loop_idx}-{side}', mesh_l)
            bpy.context.collection.objects.link(l_obj)
            l_obj.data.materials.append(flux_mat)
            objects.append(l_obj)

            # Directional arrow indicators on external return flux loops (pointing North to South)
            mid_idx = steps // 2
            mid_p = loop_pts[mid_idx]
            next_p = loop_pts[mid_idx + 1]
            tan_dir = (Vector(next_p) - Vector(mid_p)).normalized()
            arrow_rot = tan_dir.to_track_quat('Z', 'Y').to_euler()
            arrow = kit.primitive_object(f'{ASSET_ID}-arrow-{loop_idx}-{side}', 'cone', flux_mat,
                                        size=(0.0035, 0.0, 0.006),
                                        location=mid_p,
                                        rotation_euler=arrow_rot)
            objects.append(arrow)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_solenoid()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()