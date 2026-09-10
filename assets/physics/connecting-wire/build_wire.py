"""
build_wire.py — High-Fidelity Flexible Laboratory Connecting Wire with Spade Plugs
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'connecting-wire'

def build_wire():
    insul_mat = kit.add_material('wire-pvc-red', (0.88, 0.15, 0.12), metallic=0.05, roughness=0.45)
    copper_mat = kit.add_machined_metal_material('wire-copper-core', (0.88, 0.55, 0.22), metallic=0.92, roughness=0.25)
    spade_mat = kit.add_machined_metal_material('wire-spade-lug', (0.82, 0.84, 0.88), metallic=0.95, roughness=0.20)
    boot_mat = kit.add_material('wire-boot-black', (0.08, 0.08, 0.09), metallic=0.1, roughness=0.5)

    objects = []

    # 1. Realistic Curved Flexible Wire Path (U-shaped loop lying comfortably on bench)
    pts = [
        Vector((-0.060, -0.020, 0.005)),
        Vector((-0.045,  0.015, 0.012)),
        Vector((-0.020,  0.035, 0.018)),
        Vector(( 0.000,  0.038, 0.020)),
        Vector(( 0.020,  0.035, 0.018)),
        Vector(( 0.045,  0.015, 0.012)),
        Vector(( 0.060, -0.020, 0.005))
    ]

    for i in range(len(pts) - 1):
        p1 = pts[i]
        p2 = pts[i + 1]
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        rot = delta.normalized().to_track_quat('Z', 'Y').to_euler()
        seg = kit.primitive_object(f'{ASSET_ID}-seg-{i}', 'cylinder', insul_mat,
                                   size=(0.0045, 0.0045, delta.length),
                                   location=(mid.x, mid.y, mid.z),
                                   rotation_euler=rot)
        objects.append(seg)

    # 2. Both Terminations: Strain Relief Boots, Stripped Copper, and Spade Lugs
    for side, end_pt, dir_vec, name in [
        (-1, pts[0], (pts[0] - pts[1]).normalized(), 'end-left'),
        ( 1, pts[-1], (pts[-1] - pts[-2]).normalized(), 'end-right')
    ]:
        rot = dir_vec.to_track_quat('Z', 'Y').to_euler()
        
        # Black molded strain-relief boot
        boot = kit.primitive_object(f'{ASSET_ID}-boot-{name}', 'cylinder', boot_mat,
                                    size=(0.0065, 0.0065, 0.012),
                                    location=(end_pt.x + dir_vec.x * 0.006, end_pt.y + dir_vec.y * 0.006, end_pt.z),
                                    rotation_euler=rot)
        # Stripped shiny copper strand
        copper = kit.primitive_object(f'{ASSET_ID}-copper-{name}', 'cylinder', copper_mat,
                                      size=(0.0025, 0.0025, 0.008),
                                      location=(end_pt.x + dir_vec.x * 0.014, end_pt.y + dir_vec.y * 0.014, end_pt.z),
                                      rotation_euler=rot)
        # U-shaped Spade Connector Lug
        spade_stem = kit.primitive_object(f'{ASSET_ID}-spade-stem-{name}', 'cube', spade_mat,
                                          size=(0.005, 0.001, 0.008),
                                          location=(end_pt.x + dir_vec.x * 0.020, end_pt.y + dir_vec.y * 0.020, end_pt.z),
                                          rotation_euler=rot)
        spade_fork_l = kit.primitive_object(f'{ASSET_ID}-fork-l-{name}', 'cube', spade_mat,
                                           size=(0.0015, 0.001, 0.008),
                                           location=(end_pt.x + dir_vec.x * 0.026 - dir_vec.y * 0.002,
                                                     end_pt.y + dir_vec.y * 0.026 + dir_vec.x * 0.002, end_pt.z),
                                           rotation_euler=rot)
        spade_fork_r = kit.primitive_object(f'{ASSET_ID}-fork-r-{name}', 'cube', spade_mat,
                                           size=(0.0015, 0.001, 0.008),
                                           location=(end_pt.x + dir_vec.x * 0.026 + dir_vec.y * 0.002,
                                                     end_pt.y + dir_vec.y * 0.026 - dir_vec.x * 0.002, end_pt.z),
                                           rotation_euler=rot)
        objects.extend([boot, copper, spade_stem, spade_fork_l, spade_fork_r])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_wire()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
