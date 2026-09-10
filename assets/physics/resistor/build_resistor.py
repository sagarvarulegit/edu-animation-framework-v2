"""
build_resistor.py — High-Fidelity Axial Carbon/Ceramic Film Resistor (1kΩ ±5%)
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'resistor'

def build_resistor():
    body_mat = kit.add_material('resistor-ceramic', (0.84, 0.76, 0.58), metallic=0.05, roughness=0.55)
    lead_mat = kit.add_machined_metal_material('resistor-lead', (0.85, 0.86, 0.90), metallic=0.95, roughness=0.20)
    
    # 4-Band Standard Color Code: Brown (1), Black (0), Red (x10^2 = 1000Ω = 1kΩ), Gold (±5%)
    brown_mat = kit.add_material('band-brown', (0.36, 0.18, 0.08), metallic=0.1, roughness=0.3)
    black_mat = kit.add_material('band-black', (0.04, 0.04, 0.04), metallic=0.1, roughness=0.3)
    red_mat = kit.add_material('band-red', (0.82, 0.14, 0.12), metallic=0.1, roughness=0.3)
    gold_mat = kit.add_machined_metal_material('band-gold', (0.85, 0.72, 0.22), metallic=0.90, roughness=0.25)

    objects = []

    # 1. Authentic Contoured Ceramic Resistor Body (6.5mm length, 2.5mm max diameter, tapered ends)
    # Using lathe profile along Z, then rotated to lie horizontally along X
    profile = [
        (0.0000, 0.0000),  # Sealed center cap
        (0.0006, 0.0000),  # Lead entry collar
        (0.0011, 0.0005),  # Tapered flare
        (0.0013, 0.0012),  # Main cylinder shoulder
        (0.0013, 0.0053),  # Main cylinder body
        (0.0011, 0.0060),  # Tapered neck
        (0.0006, 0.0065),  # Opposite lead collar
        (0.0000, 0.0065)   # Sealed opposite center cap
    ]
    body = kit.lathe_object(f'{ASSET_ID}-body', profile, segments=48, material=body_mat)
    # Center and rotate to lay horizontally along X axis
    body.location = (-0.00325, 0.0, 0.0)
    body.rotation_euler = (0.0, math.pi / 2, 0.0)
    objects.append(body)

    # 2. 4 Coaxial Color Bands
    bands = [
        (-0.0020, brown_mat, 'brown-1'),
        (-0.0008, black_mat, 'black-0'),
        ( 0.0004, red_mat,   'red-mult'),
        ( 0.0018, gold_mat,  'gold-tol')
    ]
    for pos_x, mat, name in bands:
        band = kit.primitive_object(f'{ASSET_ID}-band-{name}', 'cylinder', mat,
                                   size=(0.0027, 0.0027, 0.0006),
                                   location=(pos_x, 0.0, 0.0),
                                   rotation_euler=(0.0, math.pi / 2, 0.0))
        objects.append(band)

    # 3. Axial Tinned Copper Wire Leads extending horizontally left and right
    for sign, name in [(-1, 'left'), (1, 'right')]:
        lead = kit.primitive_object(f'{ASSET_ID}-lead-{name}', 'cylinder', lead_mat,
                                   size=(0.0006, 0.0006, 0.022),
                                   location=(sign * 0.014, 0.0, 0.0),
                                   rotation_euler=(0.0, math.pi / 2, 0.0))
        objects.append(lead)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_resistor()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
