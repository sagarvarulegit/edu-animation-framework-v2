"""
build_tripod_gauze.py — Laboratory Tripod Stand with Wire Gauze & China Dish
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'tripod-wire-gauze'

def build_tripod_assembly():
    cast_iron = kit.add_material('tripod-iron', (0.12, 0.13, 0.15), metallic=0.8, roughness=0.6)
    gauze_mesh = kit.add_material('wire-gauze', (0.65, 0.66, 0.68), metallic=0.7, roughness=0.5)
    ceramic_pad = kit.add_material('ceramic-pad', (0.92, 0.91, 0.86), metallic=0.05, roughness=0.8)
    porcelain = kit.add_material('china-dish', (0.95, 0.95, 0.96), metallic=0.05, roughness=0.2)
    copper_powder = kit.add_material('copper-powder', (0.45, 0.22, 0.14), metallic=0.3, roughness=0.9)

    objects = []

    # 1. Cast Iron Tripod Ring (Circular collar at z = 0.16m, r = 0.052m)
    ring_profile = [
        (0.042, 0.155),
        (0.054, 0.155),
        (0.054, 0.165),
        (0.042, 0.165)
    ]
    ring = kit.lathe_object(f'{ASSET_ID}-ring', ring_profile, segments=48, material=cast_iron)
    objects.append(ring)

    # 2. Three Splayed Legs (At 0, 120, 240 degrees)
    leg_len = 0.168
    for i in range(3):
        theta = 2 * math.pi * i / 3
        # Leg starts at ring (r=0.048, z=0.16) and ends at floor (r=0.075, z=0.0)
        leg = kit.primitive_object(f'{ASSET_ID}-leg-{i}', 'cylinder', cast_iron,
                                   size=(0.008, 0.008, leg_len),
                                   location=(0.061 * math.cos(theta), 0.061 * math.sin(theta), 0.08),
                                   rotation_euler=(-0.16 * math.sin(theta), 0.16 * math.cos(theta), theta))
        objects.append(leg)

    # 3. Square Wire Gauze (0.12m x 0.12m resting on ring at z = 0.166m)
    gauze = kit.primitive_object(f'{ASSET_ID}-gauze-sheet', 'cube', gauze_mesh,
                                 size=(0.12, 0.12, 0.002),
                                 location=(0.0, 0.0, 0.166))
    # Circular ceramic center pad
    pad = kit.primitive_object(f'{ASSET_ID}-ceramic-pad', 'cylinder', ceramic_pad,
                               size=(0.072, 0.072, 0.003),
                               location=(0.0, 0.0, 0.168))
    objects.extend([gauze, pad])

    # 4. Porcelain Evaporating Dish (China Dish)
    dish_profile = [
        (0.000, 0.170),
        (0.022, 0.170),
        (0.038, 0.178),
        (0.046, 0.192),
        (0.048, 0.195),
        (0.045, 0.195),
        (0.036, 0.180),
        (0.020, 0.173),
        (0.000, 0.173)
    ]
    dish = kit.lathe_object(f'{ASSET_ID}-china-dish', dish_profile, segments=48, material=porcelain)
    objects.append(dish)

    # 5. Fine Copper Powder with black oxidized surface crust
    powder = kit.primitive_object(f'{ASSET_ID}-copper-powder', 'uv_sphere', copper_powder,
                                  size=(0.036, 0.036, 0.012),
                                  location=(0.0, 0.0, 0.176))
    objects.append(powder)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_tripod_assembly()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
