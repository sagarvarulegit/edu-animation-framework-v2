"""
build_battery.py — High-Fidelity Cylindrical Dry Cell / Chemical Battery (1.5V)
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'battery'

def build_battery():
    body_mat = kit.add_material('batt-body-dark', (0.10, 0.12, 0.15), metallic=0.3, roughness=0.4)
    gold_mat = kit.add_machined_metal_material('batt-gold-jacket', (0.85, 0.68, 0.22), metallic=0.85, roughness=0.25)
    brass_mat = kit.add_machined_metal_material('batt-brass-pip', (0.88, 0.72, 0.30), metallic=0.95, roughness=0.20)
    silver_mat = kit.add_machined_metal_material('batt-zinc-base', (0.82, 0.84, 0.88), metallic=0.95, roughness=0.25)
    insulator_mat = kit.add_material('batt-insulator', (0.85, 0.15, 0.12), metallic=0.1, roughness=0.4)
    mark_mat = kit.add_material('batt-polarity', (0.95, 0.95, 0.98), metallic=0.2, roughness=0.3)

    objects = []

    # 1. Main Cylindrical Cell (AA / Standard Cell: 14mm diameter, 50mm height)
    body = kit.primitive_object(f'{ASSET_ID}-body', 'cylinder', body_mat,
                                size=(0.014, 0.014, 0.046),
                                location=(0.0, 0.0, 0.024))
    objects.append(body)

    # 2. Golden Metallic Upper Jacket Sleeve
    jacket = kit.primitive_object(f'{ASSET_ID}-jacket', 'cylinder', gold_mat,
                                 size=(0.0143, 0.0143, 0.016),
                                 location=(0.0, 0.0, 0.038))
    objects.append(jacket)

    # 3. Crimped Insulating Plastic Ring at Top Shoulder
    ring = kit.primitive_object(f'{ASSET_ID}-insulator-ring', 'cylinder', insulator_mat,
                                size=(0.0125, 0.0125, 0.002),
                                location=(0.0, 0.0, 0.0475))
    objects.append(ring)

    # 4. Raised Positive (+) Terminal Pip (Brass Nub)
    pip = kit.primitive_object(f'{ASSET_ID}-pos-pip', 'cylinder', brass_mat,
                               size=(0.0055, 0.0055, 0.004),
                               location=(0.0, 0.0, 0.0495))
    objects.append(pip)

    # 5. Negative (-) Terminal Zinc Base Cup with peripheral crimp
    base_plate = kit.primitive_object(f'{ASSET_ID}-neg-base', 'cylinder', silver_mat,
                                      size=(0.0138, 0.0138, 0.0025),
                                      location=(0.0, 0.0, 0.0012))
    objects.append(base_plate)

    # 6. Polarity Indicators (+ near top, - near bottom)
    # Positive '+' horizontal and vertical bar on jacket front (-Y)
    plus_h = kit.primitive_object(f'{ASSET_ID}-plus-h', 'cube', mark_mat,
                                 size=(0.003, 0.0005, 0.001),
                                 location=(0.0, -0.0073, 0.040))
    plus_v = kit.primitive_object(f'{ASSET_ID}-plus-v', 'cube', mark_mat,
                                 size=(0.001, 0.0005, 0.003),
                                 location=(0.0, -0.0073, 0.040))
    # Negative '-' horizontal bar on lower body front (-Y)
    minus = kit.primitive_object(f'{ASSET_ID}-minus', 'cube', mark_mat,
                                size=(0.003, 0.0005, 0.001),
                                location=(0.0, -0.0072, 0.010))
    objects.extend([plus_h, plus_v, minus])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_battery()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
