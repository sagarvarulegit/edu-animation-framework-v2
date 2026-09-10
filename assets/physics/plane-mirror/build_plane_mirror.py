"""
build_plane_mirror.py — High-Fidelity Laboratory Plane Mirror with Adjustable Stand
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'plane-mirror'

def build_mirror():
    silver_mat = kit.add_material('mirror-silver', (0.95, 0.95, 0.98), metallic=1.0, roughness=0.01)
    frame_mat = kit.add_material('mirror-frame-wood', (0.55, 0.38, 0.22), metallic=0.05, roughness=0.55)
    back_mat = kit.add_material('mirror-back-board', (0.16, 0.14, 0.12), metallic=0.05, roughness=0.75)
    brass_mat = kit.add_machined_metal_material('mirror-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    cast_mat = kit.add_material('stand-cast', (0.15, 0.16, 0.18), metallic=0.7, roughness=0.5)

    objects = []

    # 1. Front Silver Reflective Mirror Pane (100mm wide, 140mm tall)
    w, h = 0.100, 0.140
    mirror = kit.primitive_object(f'{ASSET_ID}-reflective-surface', 'cube', silver_mat,
                                 size=(w, 0.003, h),
                                 location=(0.0, -0.002, 0.110))
    # Protective backing card
    back = kit.primitive_object(f'{ASSET_ID}-backing', 'cube', back_mat,
                               size=(w + 0.004, 0.003, h + 0.004),
                               location=(0.0, 0.001, 0.110))
    objects.extend([mirror, back])

    # 2. Beveled Outer Frame Strips
    fw = 0.008
    # Top & Bottom Frame
    f_top = kit.primitive_object(f'{ASSET_ID}-frame-top', 'cube', frame_mat,
                                size=(w + 2 * fw, 0.010, fw),
                                location=(0.0, 0.0, 0.110 + h / 2 + fw / 2))
    f_bot = kit.primitive_object(f'{ASSET_ID}-frame-bottom', 'cube', frame_mat,
                                size=(w + 2 * fw, 0.010, fw),
                                location=(0.0, 0.0, 0.110 - h / 2 - fw / 2))
    # Left & Right Frame
    f_left = kit.primitive_object(f'{ASSET_ID}-frame-left', 'cube', frame_mat,
                                 size=(fw, 0.010, h),
                                 location=(-w / 2 - fw / 2, 0.0, 0.110))
    f_right = kit.primitive_object(f'{ASSET_ID}-frame-right', 'cube', frame_mat,
                                  size=(fw, 0.010, h),
                                  location=(w / 2 + fw / 2, 0.0, 0.110))
    objects.extend([f_top, f_bot, f_left, f_right])

    # 3. Side Swivel Pivot Studs & Tightening Knobs
    for sign in [-1, 1]:
        stud = kit.primitive_object(f'{ASSET_ID}-pivot-stud-{sign}', 'cylinder', brass_mat,
                                    size=(0.006, 0.006, 0.014),
                                    location=(sign * (w / 2 + fw + 0.006), 0.0, 0.110),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        knob = kit.primitive_object(f'{ASSET_ID}-knob-{sign}', 'cylinder', brass_mat,
                                    size=(0.012, 0.012, 0.006),
                                    location=(sign * (w / 2 + fw + 0.012), 0.0, 0.110),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        # Vertical side support arms
        arm = kit.primitive_object(f'{ASSET_ID}-support-arm-{sign}', 'cube', cast_mat,
                                  size=(0.008, 0.012, 0.110),
                                  location=(sign * (w / 2 + fw + 0.010), 0.0, 0.060))
        objects.extend([stud, knob, arm])

    # 4. Heavy Stepped Bench Stand Base
    base = kit.primitive_object(f'{ASSET_ID}-stand-base', 'cube', cast_mat,
                                size=(w + 2 * fw + 0.040, 0.060, 0.010),
                                location=(0.0, 0.0, 0.005))
    objects.append(base)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_mirror()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
