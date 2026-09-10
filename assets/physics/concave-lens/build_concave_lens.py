"""
build_concave_lens.py — High-Fidelity Optical Biconcave (Diverging) Glass Lens
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'concave-lens'

def build_lens():
    glass_mat = kit.add_glass_material('biconcave-glass', tint=(0.95, 0.98, 1.0), ior=1.52, roughness=0.01)
    brass_mat = kit.add_machined_metal_material('lens-brass-rim', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.28)
    chrome_mat = kit.add_machined_metal_material('lens-chrome-post', (0.90, 0.90, 0.92), metallic=0.98, roughness=0.15)
    cast_mat = kit.add_material('lens-cast-base', (0.15, 0.16, 0.18), metallic=0.75, roughness=0.55)

    objects = []

    # 1. High-Precision Biconcave Glass Lens Profile via Lathe Revolution
    # Radius = 40mm, Center Thickness = 2.4mm, Edge Thickness = 12.0mm
    r_max = 0.040
    t_center = 0.0024
    t_edge = 0.0120
    R_c = 0.160  # Radius of curvature
    num_steps = 24

    # Build closed 2D profile: center is thin, edge flares outward
    bottom_half = []
    top_half = []
    for i in range(num_steps + 1):
        r = r_max * (i / num_steps)
        # Saggita of concave dip
        dip = (R_c - math.sqrt(max(0.0, R_c**2 - r**2)))
        z_top = t_center / 2 + dip
        top_half.append((r, z_top))
        bottom_half.append((r, -z_top))

    # Assemble closed boundary: bottom center -> bottom rim -> top rim -> top center
    lens_profile = [(0.0, -t_center / 2)] + bottom_half + list(reversed(top_half)) + [(0.0, t_center / 2)]

    lens_obj = kit.lathe_object(f'{ASSET_ID}-body', lens_profile, segments=64, material=glass_mat)
    lens_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    lens_obj.location = (0.0, 0.0, 0.110)
    objects.append(lens_obj)

    # 2. Brass Circular Lens Retaining Ring & Clamp
    rim_profile = [
        (0.0395, 0.0065),
        (0.0435, 0.0065),
        (0.0435, -0.0065),
        (0.0395, -0.0065),
        (0.0395, 0.0065)
    ]
    rim_obj = kit.lathe_object(f'{ASSET_ID}-retaining-rim', rim_profile, segments=64, material=brass_mat)
    rim_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)
    rim_obj.location = (0.0, 0.0, 0.110)
    objects.append(rim_obj)

    # 3. Mount Clamp & Knurled Screw
    clamp = kit.primitive_object(f'{ASSET_ID}-clamp', 'cube', brass_mat,
                                 size=(0.020, 0.015, 0.016),
                                 location=(0.0, 0.0, 0.065))
    screw = kit.primitive_object(f'{ASSET_ID}-screw', 'cylinder', brass_mat,
                                 size=(0.010, 0.010, 0.008),
                                 location=(0.013, 0.0, 0.065),
                                 rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.extend([clamp, screw])

    # 4. Vertical Chrome Post
    post = kit.primitive_object(f'{ASSET_ID}-post', 'cylinder', chrome_mat,
                                size=(0.008, 0.008, 0.070),
                                location=(0.0, 0.0, 0.035))
    objects.append(post)

    # 5. Heavy Stepped Cast Iron Base
    base_profile = [
        (0.000, 0.000),
        (0.040, 0.000),
        (0.040, 0.006),
        (0.032, 0.009),
        (0.010, 0.010),
        (0.010, 0.015),
        (0.000, 0.015)
    ]
    base_obj = kit.lathe_object(f'{ASSET_ID}-base', base_profile, segments=48, material=cast_mat,
                               location=(0.0, 0.0, 0.0))
    objects.append(base_obj)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_lens()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
