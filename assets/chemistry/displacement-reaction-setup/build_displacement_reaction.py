"""
build_displacement_reaction.py — Iron Nail in Copper Sulphate Displacement Setup
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'displacement-reaction-setup'

def build_displacement_reaction():
    wood_mat = kit.add_material('disp-wood', (0.58, 0.38, 0.22), metallic=0.05, roughness=0.6)
    glass_mat = kit.add_glass_material('disp-glass', (0.95, 0.98, 1.0), ior=1.52, roughness=0.015)
    blue_sol = kit.add_glass_material('disp-blue-sol', (0.15, 0.45, 0.95), ior=1.34, roughness=0.02)
    green_sol = kit.add_glass_material('disp-green-sol', (0.28, 0.72, 0.55), ior=1.34, roughness=0.02)
    iron_mat = kit.add_machined_metal_material('disp-iron', (0.70, 0.72, 0.75), metallic=0.92, roughness=0.25)
    copper_mat = kit.add_machined_metal_material('disp-copper', (0.82, 0.38, 0.22), metallic=0.85, roughness=0.45)
    thread_mat = kit.add_material('disp-thread', (0.92, 0.90, 0.85), metallic=0.0, roughness=0.9)
    porcelain_mat = kit.add_material('disp-porcelain', (0.94, 0.94, 0.96), metallic=0.05, roughness=0.25)

    objects = []

    # 1. Beechwood Test Tube Rack (Base, top bar with holes, upright posts)
    # Base slab
    rack_base = kit.primitive_object(f'{ASSET_ID}-rack-base', 'cube', wood_mat,
                                     size=(0.14, 0.07, 0.012),
                                     location=(0.0, 0.0, 0.006))
    # Top bar
    rack_top = kit.primitive_object(f'{ASSET_ID}-rack-top', 'cube', wood_mat,
                                    size=(0.14, 0.05, 0.010),
                                    location=(0.0, 0.0, 0.095))
    # Side uprights
    for x_side in [-0.062, 0.062]:
        post = kit.primitive_object(f'{ASSET_ID}-rack-post-{x_side}', 'cube', wood_mat,
                                    size=(0.012, 0.05, 0.095),
                                    location=(x_side, 0.0, 0.05))
        objects.append(post)
    objects.extend([rack_base, rack_top])

    # 2. Test Tube A (Reference: Deep Blue CuSO4 solution, x = -0.025m)
    # Tube geometry
    tube_a = kit.primitive_object(f'{ASSET_ID}-tube-a', 'cylinder', glass_mat,
                                  size=(0.018, 0.018, 0.12),
                                  location=(-0.025, 0.0, 0.07))
    sol_a = kit.primitive_object(f'{ASSET_ID}-sol-a', 'cylinder', blue_sol,
                                 size=(0.016, 0.016, 0.07),
                                 location=(-0.025, 0.0, 0.046))
    objects.extend([tube_a, sol_a])

    # 3. Test Tube B (Displacement Reaction: Faded Pale Green FeSO4 solution, x = +0.025m)
    tube_b = kit.primitive_object(f'{ASSET_ID}-tube-b', 'cylinder', glass_mat,
                                  size=(0.018, 0.018, 0.12),
                                  location=(0.025, 0.0, 0.07))
    sol_b = kit.primitive_object(f'{ASSET_ID}-sol-b', 'cylinder', green_sol,
                                 size=(0.016, 0.016, 0.07),
                                 location=(0.025, 0.0, 0.046))
    objects.extend([tube_b, sol_b])

    # 4. Iron Nail Suspended in Tube B
    # Upper nail body (above solution level: clean grey iron)
    nail_upper = kit.primitive_object(f'{ASSET_ID}-nail-upper', 'cylinder', iron_mat,
                                      size=(0.0035, 0.0035, 0.025),
                                      location=(0.025, 0.0, 0.088))
    # Nail head
    nail_head = kit.primitive_object(f'{ASSET_ID}-nail-head', 'cylinder', iron_mat,
                                     size=(0.007, 0.007, 0.002),
                                     location=(0.025, 0.0, 0.101))
    # Lower submerged nail body (reddish-brown copper deposit)
    nail_lower = kit.primitive_object(f'{ASSET_ID}-nail-lower', 'cylinder', copper_mat,
                                      size=(0.0038, 0.0038, 0.045),
                                      location=(0.025, 0.0, 0.053))
    # Nail pointed tip
    nail_tip = kit.primitive_object(f'{ASSET_ID}-nail-tip', 'cone', copper_mat,
                                    size=(0.0038, 0.0, 0.006),
                                    location=(0.025, 0.0, 0.027),
                                    rotation_euler=(math.pi, 0.0, 0.0))
    # Thread suspending nail
    thread = kit.primitive_object(f'{ASSET_ID}-thread', 'cylinder', thread_mat,
                                  size=(0.0008, 0.0008, 0.040),
                                  location=(0.025, 0.005, 0.118))
    objects.extend([nail_upper, nail_head, nail_lower, nail_tip, thread])

    # 5. Clean comparison iron nail on watch glass (at rack base, y = 0.04m)
    dish = kit.lathe_object(f'{ASSET_ID}-watch-dish',
                            [(0.0, 0.012), (0.025, 0.012), (0.028, 0.018), (0.027, 0.018), (0.024, 0.013), (0.0, 0.013)],
                            segments=32, material=porcelain_mat, location=(0.0, -0.042, 0.0))
    comp_nail = kit.primitive_object(f'{ASSET_ID}-comp-nail', 'cylinder', iron_mat,
                                     size=(0.0035, 0.0035, 0.045),
                                     location=(0.0, -0.042, 0.015),
                                     rotation_euler=(0.0, math.pi / 2, 0.2))
    objects.extend([dish, comp_nail])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_displacement_reaction()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
