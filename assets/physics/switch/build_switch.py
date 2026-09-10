"""
build_switch.py — High-Fidelity Laboratory Single-Pole Knife Switch
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'switch'

def build_switch():
    base_mat = kit.add_material('switch-bakelite', (0.12, 0.10, 0.09), metallic=0.1, roughness=0.6)
    brass_mat = kit.add_machined_metal_material('switch-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    contact_mat = kit.add_machined_metal_material('switch-copper', (0.88, 0.55, 0.25), metallic=0.90, roughness=0.28)
    handle_mat = kit.add_material('switch-handle', (0.85, 0.15, 0.12), metallic=0.05, roughness=0.4)
    screw_mat = kit.add_machined_metal_material('switch-steel', (0.75, 0.78, 0.82), metallic=0.95, roughness=0.20)

    objects = []

    # 1. Beveled Bakelite / Ebonite Insulating Base Plate
    base = kit.primitive_object(f'{ASSET_ID}-base', 'cube', base_mat,
                                size=(0.090, 0.050, 0.012),
                                location=(0.0, 0.0, 0.006))
    objects.append(base)

    # 2. Mounting Corner Feet (4 rubber/brass pads)
    for sx in [-0.038, 0.038]:
        for sy in [-0.018, 0.018]:
            foot = kit.primitive_object(f'{ASSET_ID}-foot-{sx}-{sy}', 'cylinder', base_mat,
                                        size=(0.006, 0.006, 0.003),
                                        location=(sx, sy, -0.0015))
            objects.append(foot)

    # 3. Fixed Hinge Block (-X end)
    hinge_block = kit.primitive_object(f'{ASSET_ID}-hinge-block', 'cube', brass_mat,
                                      size=(0.016, 0.014, 0.014),
                                      location=(-0.026, 0.0, 0.019))
    hinge_pin = kit.primitive_object(f'{ASSET_ID}-hinge-pin', 'cylinder', screw_mat,
                                     size=(0.004, 0.004, 0.018),
                                     location=(-0.026, 0.0, 0.022),
                                     rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.extend([hinge_block, hinge_pin])

    # 4. Receiving Contact Jaws (+X end) — U-shaped copper spring clip
    for side in [-1, 1]:
        jaw = kit.primitive_object(f'{ASSET_ID}-jaw-{side}', 'cube', contact_mat,
                                   size=(0.012, 0.0025, 0.016),
                                   location=(0.026, side * 0.0028, 0.020))
        objects.append(jaw)
    jaw_base = kit.primitive_object(f'{ASSET_ID}-jaw-base', 'cube', brass_mat,
                                    size=(0.016, 0.014, 0.008),
                                    location=(0.026, 0.0, 0.016))
    objects.append(jaw_base)

    # 5. Pivoting Knife Arm (Solid brass blade, open at ~32 degrees)
    open_angle = 0.55  # ~32 degrees tilt
    arm_length = 0.052
    arm_cx = -0.026 + (arm_length / 2) * math.cos(open_angle)
    arm_cz = 0.022 + (arm_length / 2) * math.sin(open_angle)
    arm = kit.primitive_object(f'{ASSET_ID}-arm', 'cube', brass_mat,
                              size=(arm_length, 0.003, 0.008),
                              location=(arm_cx, 0.0, arm_cz),
                              rotation_euler=(0.0, -open_angle, 0.0))
    objects.append(arm)

    # 6. Cylindrical Insulated Red Handle Grip at tip of blade
    handle_x = -0.026 + arm_length * math.cos(open_angle)
    handle_z = 0.022 + arm_length * math.sin(open_angle)
    handle = kit.primitive_object(f'{ASSET_ID}-handle', 'cylinder', handle_mat,
                                 size=(0.008, 0.008, 0.022),
                                 location=(handle_x, 0.0, handle_z + 0.006),
                                 rotation_euler=(0.0, -open_angle, 0.0))
    objects.append(handle)

    # 7. Knurled Brass Binding Post Terminals (One at each end)
    for sign, name in [(-1, 'term-1'), (1, 'term-2')]:
        stud = kit.primitive_object(f'{ASSET_ID}-{name}-stud', 'cylinder', screw_mat,
                                    size=(0.005, 0.005, 0.018),
                                    location=(sign * 0.038, 0.0, 0.021))
        nut = kit.primitive_object(f'{ASSET_ID}-{name}-nut', 'cylinder', brass_mat,
                                   size=(0.010, 0.010, 0.008),
                                   location=(sign * 0.038, 0.0, 0.023))
        objects.extend([stud, nut])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_switch()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
