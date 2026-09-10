"""
build_rheostat.py — High-Fidelity Laboratory Slide-Wire Rheostat (Variable Resistor)
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'rheostat'

def build_rheostat():
    ceramic_mat = kit.add_material('rheo-ceramic', (0.92, 0.90, 0.86), metallic=0.05, roughness=0.6)
    wire_mat = kit.add_material('rheo-wire-coil', (0.65, 0.42, 0.25), metallic=0.85, roughness=0.35)
    bracket_mat = kit.add_material('rheo-bracket', (0.16, 0.17, 0.19), metallic=0.7, roughness=0.5)
    brass_mat = kit.add_machined_metal_material('rheo-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    knob_mat = kit.add_material('rheo-knob', (0.08, 0.08, 0.09), metallic=0.1, roughness=0.4)

    objects = []

    # 1. Heavy End Support Brackets (Left at -X, Right at +X)
    tube_len = 0.120
    tube_r = 0.016
    for sign, name in [(-1, 'left'), (1, 'right')]:
        # Upright bracket plate
        upright = kit.primitive_object(f'{ASSET_ID}-bracket-{name}', 'cube', bracket_mat,
                                      size=(0.012, 0.046, 0.055),
                                      location=(sign * (tube_len / 2 + 0.006), 0.0, 0.024))
        # Foot base
        foot = kit.primitive_object(f'{ASSET_ID}-foot-{name}', 'cube', bracket_mat,
                                   size=(0.018, 0.052, 0.008),
                                   location=(sign * (tube_len / 2 + 0.006), 0.0, 0.004))
        objects.extend([upright, foot])

    # 2. Porcelain / Ceramic Core Tube
    core = kit.primitive_object(f'{ASSET_ID}-core', 'cylinder', ceramic_mat,
                               size=(tube_r * 2, tube_r * 2, tube_len),
                               location=(0.0, 0.0, 0.024),
                               rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.append(core)

    # 3. Nichrome / Constantan Resistance Wire Coil Ribs (16 closely-spaced turns)
    for i in range(16):
        x = -0.052 + i * 0.007
        coil_ring = kit.primitive_object(f'{ASSET_ID}-coil-{i}', 'cylinder', wire_mat,
                                        size=(tube_r * 2 + 0.0012, tube_r * 2 + 0.0012, 0.005),
                                        location=(x, 0.0, 0.024),
                                        rotation_euler=(0.0, math.pi / 2, 0.0))
        objects.append(coil_ring)

    # 4. Top Square Slider Guide Bar
    slider_bar = kit.primitive_object(f'{ASSET_ID}-slider-bar', 'cube', brass_mat,
                                     size=(tube_len + 0.012, 0.005, 0.005),
                                     location=(0.0, 0.0, 0.048))
    objects.append(slider_bar)

    # 5. Moveable Slider Block & Insulated Adjusting Knob (Positioned around x = 0.015m)
    slider_x = 0.015
    slider_block = kit.primitive_object(f'{ASSET_ID}-slider-block', 'cube', brass_mat,
                                       size=(0.014, 0.014, 0.012),
                                       location=(slider_x, 0.0, 0.046))
    slider_contact = kit.primitive_object(f'{ASSET_ID}-slider-contact', 'cube', brass_mat,
                                         size=(0.006, 0.008, 0.010),
                                         location=(slider_x, 0.0, 0.036))
    slider_knob = kit.primitive_object(f'{ASSET_ID}-slider-knob', 'cylinder', knob_mat,
                                      size=(0.016, 0.016, 0.012),
                                      location=(slider_x, 0.0, 0.058))
    objects.extend([slider_block, slider_contact, slider_knob])

    # 6. Three Knurled Brass Binding Terminals:
    # Two fixed base terminals (one at left, one at right)
    for sign, name in [(-1, 'fixed-left'), (1, 'fixed-right')]:
        term = kit.primitive_object(f'{ASSET_ID}-term-{name}', 'cylinder', brass_mat,
                                   size=(0.008, 0.008, 0.014),
                                   location=(sign * (tube_len / 2 + 0.006), -0.018, 0.014))
        objects.append(term)
    # One variable terminal on top of slider rod (at right bracket top)
    term_slider = kit.primitive_object(f'{ASSET_ID}-term-variable', 'cylinder', brass_mat,
                                      size=(0.008, 0.008, 0.014),
                                      location=((tube_len / 2 + 0.006), 0.0, 0.056))
    objects.append(term_slider)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_rheostat()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
