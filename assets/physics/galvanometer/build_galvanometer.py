"""
build_galvanometer.py — Sensitive Center-Zero Laboratory Galvanometer
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'galvanometer'

def build_galvanometer():
    case_mat = kit.add_material('galvano-case', (0.15, 0.16, 0.18), metallic=0.2, roughness=0.45)
    dial_mat = kit.add_material('galvano-dial', (0.98, 0.98, 0.96), metallic=0.0, roughness=0.15)
    bsdf = dial_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (0.96, 0.96, 0.94, 1.0)
    bsdf.inputs["Emission Strength"].default_value = 0.20

    needle_mat = kit.add_material('galvano-needle', (0.90, 0.15, 0.12), metallic=0.8, roughness=0.2)
    glass_mat = kit.add_glass_material('galvano-glass', (0.98, 0.99, 1.0), ior=1.50, roughness=0.002)
    brass_mat = kit.add_machined_metal_material('galvano-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    red_mat = kit.add_material('term-red', (0.85, 0.15, 0.15), metallic=0.1, roughness=0.4)
    black_mat = kit.add_material('term-black', (0.05, 0.05, 0.06), metallic=0.1, roughness=0.4)
    label_mat = kit.add_material('galvano-label', (0.85, 0.45, 0.10), metallic=0.0, roughness=0.4)
    tick_mat = kit.add_material('scale-tick', (0.05, 0.05, 0.05), metallic=0.0, roughness=0.5)

    objects = []

    # 1. Main Instrument Housing
    case = kit.primitive_object(f'{ASSET_ID}-case', 'cube', case_mat,
                                size=(0.090, 0.072, 0.070),
                                location=(0.0, 0.004, 0.035))
    objects.append(case)

    # 2. Window Frame Perimeter & Protective Glass
    w_w, w_h, w_thick = 0.074, 0.048, 0.004
    f_thick = 0.004
    f_y = -0.039
    f_top = kit.primitive_object(f'{ASSET_ID}-frame-top', 'cube', case_mat,
                                 size=(w_w, w_thick, f_thick),
                                 location=(0.0, f_y, 0.042 + w_h / 2 + f_thick / 2))
    f_bot = kit.primitive_object(f'{ASSET_ID}-frame-bottom', 'cube', case_mat,
                                 size=(w_w, w_thick, f_thick),
                                 location=(0.0, f_y, 0.042 - w_h / 2 - f_thick / 2))
    f_left = kit.primitive_object(f'{ASSET_ID}-frame-left', 'cube', case_mat,
                                  size=(f_thick, w_thick, w_h + 2 * f_thick),
                                  location=(-w_w / 2 - f_thick / 2, f_y, 0.042))
    f_right = kit.primitive_object(f'{ASSET_ID}-frame-right', 'cube', case_mat,
                                   size=(f_thick, w_thick, w_h + 2 * f_thick),
                                   location=(w_w / 2 + f_thick / 2, f_y, 0.042))
    glass = kit.primitive_object(f'{ASSET_ID}-glass', 'cube', glass_mat,
                                 size=(w_w, 0.001, w_h),
                                 location=(0.0, -0.0385, 0.042))
    objects.extend([f_top, f_bot, f_left, f_right, glass])

    # 3. Dial Face Plate (White background with graduated center-zero arc)
    dial = kit.primitive_object(f'{ASSET_ID}-dial', 'cube', dial_mat,
                                size=(w_w, 0.002, w_h),
                                location=(0.0, -0.035, 0.042))
    objects.append(dial)

    # 4. Center-Zero Scale Arc Ticks (-30 to +30, center at 0)
    for i in range(-6, 7):
        ang = i * 0.10
        tx = 0.024 * math.sin(ang)
        tz = 0.042 + 0.024 * math.cos(ang) - 0.016
        tick_h = 0.005 if i % 3 == 0 else 0.003
        tick = kit.primitive_object(f'{ASSET_ID}-tick-{i}', 'cube', tick_mat,
                                    size=(0.0008, 0.001, tick_h),
                                    location=(tx, -0.0365, tz),
                                    rotation_euler=(0.0, 0.0, -ang))
        objects.append(tick)

    # 5. Center-Zero Indicator Needle
    needle = kit.primitive_object(f'{ASSET_ID}-needle', 'cylinder', needle_mat,
                                  size=(0.0010, 0.0010, 0.030),
                                  location=(0.0, -0.0370, 0.037),
                                  rotation_euler=(0.0, 0.0, 0.0))
    pivot = kit.primitive_object(f'{ASSET_ID}-pivot', 'cylinder', brass_mat,
                                 size=(0.006, 0.006, 0.003),
                                 location=(0.0, -0.0370, 0.027),
                                 rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.extend([needle, pivot])

    # 6. Distinctive Bold 'G' Silkscreen Typographic Indicator on Dial (NCERT Standard)
    symbol_mat = kit.add_material(f'{ASSET_ID}-symbol', (0.04, 0.04, 0.05), metallic=0.0, roughness=0.5)
    letter_g = kit.text_mesh_object(f'{ASSET_ID}-letter-g', 'G', symbol_mat,
                                    size=0.010, extrude=0.0004,
                                    location=(0.0, -0.0362, 0.039),
                                    rotation_euler=(math.pi / 2, 0.0, 0.0))
    bm_g = bmesh.new()
    bm_g.from_mesh(letter_g.data)
    bmesh.ops.dissolve_degenerate(bm_g, dist=1e-5, edges=bm_g.edges)
    bm_g.to_mesh(letter_g.data)
    bm_g.free()
    letter_g.data.update()
    objects.append(letter_g)

    # 7. Zero Adjustment Screw below dial
    adj_screw = kit.primitive_object(f'{ASSET_ID}-zero-screw', 'cylinder', brass_mat,
                                     size=(0.008, 0.008, 0.004),
                                     location=(0.0, -0.034, 0.010),
                                     rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.append(adj_screw)

    # 8. Top Binding Posts (+ Red on right, - Black on left)
    for sign, name, col_mat in [(1, 'pos', red_mat), (-1, 'neg', black_mat)]:
        post = kit.primitive_object(f'{ASSET_ID}-term-{name}', 'cylinder', brass_mat,
                                    size=(0.009, 0.009, 0.016),
                                    location=(sign * 0.028, 0.025, 0.078))
        collar = kit.primitive_object(f'{ASSET_ID}-collar-{name}', 'cylinder', col_mat,
                                      size=(0.011, 0.011, 0.006),
                                      location=(sign * 0.028, 0.025, 0.073))
        objects.extend([post, collar])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_galvanometer()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()