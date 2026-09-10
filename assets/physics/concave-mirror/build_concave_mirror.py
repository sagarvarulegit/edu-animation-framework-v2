"""
build_concave_mirror.py — High-Fidelity Spherical Concave (Converging) Mirror
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'concave-mirror'

def build_concave_mirror():
    silver = kit.add_material('concave-mirror-silver', (0.95, 0.95, 0.98), metallic=1.0, roughness=0.015)
    back_coating = kit.add_material('mirror-back-shell', (0.12, 0.12, 0.14), metallic=0.05, roughness=0.75)
    brass = kit.add_machined_metal_material('mount-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.28)
    chrome = kit.add_machined_metal_material('stand-chrome', (0.90, 0.90, 0.92), metallic=0.98, roughness=0.15)
    cast_iron = kit.add_material('stand-base', (0.15, 0.16, 0.18), metallic=0.75, roughness=0.55)

    objects = []

    # 1. High-Precision Spherical Concave Mirror Dish (Radius = 50mm, Depth = 8mm)
    # Using lathe profile: Center is recessed back at -0.008, edge rim is forward at 0.0
    num_steps = 32
    r_max = 0.050
    R_c = 0.160  # Radius of spherical curvature
    dish_front = []
    for i in range(num_steps + 1):
        r = r_max * (i / num_steps)
        # Concave surface: z starts negative at center and curves up to 0 at rim
        z = - (math.sqrt(max(0.0, R_c**2 - r**2)) - (R_c - 0.008))
        dish_front.append((r, z))

    # Closed watertight glass/silver mirror dish with 2mm thickness
    t_dish = 0.002
    dish_back = [(r, z - t_dish) for r, z in reversed(dish_front)]
    dish_profile = dish_front + dish_back

    # Front reflective concave dish
    dish_obj = kit.lathe_object(f'{ASSET_ID}-dish', dish_profile, segments=64, material=silver)
    dish_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    dish_obj.location = (0.0, 0.0, 0.120)
    objects.append(dish_obj)

    # 2. Back Protective Housing Shell (Watertight closed shell)
    t_back = 0.003
    back_front = [(r, z - t_dish) for r, z in dish_front]
    back_rear  = [(r, z - t_dish - t_back) for r, z in reversed(dish_front)]
    back_profile = back_front + back_rear

    back_obj = kit.lathe_object(f'{ASSET_ID}-back', back_profile, segments=64, material=back_coating)
    back_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    back_obj.location = (0.0, 0.0, 0.120)
    objects.append(back_obj)

    # 3. Outer Brass Bezel Retaining Ring (Closed toroidal profile)
    bezel_profile = [
        (0.0495, 0.002),
        (0.0530, 0.002),
        (0.0530, -0.012),
        (0.0495, -0.012),
        (0.0495, 0.002)
    ]
    bezel_obj = kit.lathe_object(f'{ASSET_ID}-bezel', bezel_profile, segments=64, material=brass)
    bezel_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    bezel_obj.location = (0.0, 0.0, 0.120)
    objects.append(bezel_obj)

    # 4. Swivel Mount Bracket & Knurled Clamp Screw
    bracket = kit.primitive_object(f'{ASSET_ID}-bracket', 'cube', brass,
                                   size=(0.024, 0.015, 0.020),
                                   location=(0.0, -0.008, 0.068))
    screw = kit.primitive_object(f'{ASSET_ID}-screw', 'cylinder', brass,
                                 size=(0.012, 0.012, 0.010),
                                 location=(0.015, -0.008, 0.068),
                                 rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.extend([bracket, screw])

    # 5. Vertical Chrome Post
    post = kit.primitive_object(f'{ASSET_ID}-post', 'cylinder', chrome,
                                size=(0.009, 0.009, 0.075),
                                location=(0.0, -0.008, 0.038))
    objects.append(post)

    # 6. Heavy Stepped Cast Iron Base
    base_profile = [
        (0.000, 0.000),
        (0.045, 0.000),
        (0.045, 0.006),
        (0.038, 0.009),
        (0.012, 0.010),
        (0.012, 0.016),
        (0.000, 0.016)
    ]
    base_obj = kit.lathe_object(f'{ASSET_ID}-base', base_profile, segments=48, material=cast_iron,
                               location=(0.0, -0.008, 0.0))
    objects.append(base_obj)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_concave_mirror()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
