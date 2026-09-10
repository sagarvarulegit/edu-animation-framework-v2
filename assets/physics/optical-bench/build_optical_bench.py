"""
build_optical_bench.py — Dual-Rail Laboratory Optical Bench Apparatus
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'optical-bench'

def build_optical_bench():
    steel = kit.add_machined_metal_material('rail-steel', (0.85, 0.86, 0.88), metallic=0.98, roughness=0.18)
    cast_iron = kit.add_material('bench-cast-iron', (0.12, 0.13, 0.15), metallic=0.8, roughness=0.6)
    brass = kit.add_machined_metal_material('bench-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    glass = kit.add_glass_material('bench-lens-glass', (0.95, 0.98, 1.0), ior=1.52, roughness=0.015)
    white_screen = kit.add_material('bench-white-screen', (0.95, 0.95, 0.95), metallic=0.0, roughness=0.9)
    candle_wax = kit.add_material('candle-wax', (0.92, 0.90, 0.82), metallic=0.0, roughness=0.4)
    flame_mat = kit.add_material('candle-flame', (1.0, 0.65, 0.1), metallic=0.0, roughness=0.2)
    flame_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1.0, 0.6, 0.1, 1.0)
    flame_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 8.0

    objects = []

    # 1. Dual stainless steel guide rails along X axis (Length = 1.0m, Spacing = 0.06m in Y)
    rail_len = 1.0
    for y_offset in [-0.03, 0.03]:
        rail = kit.primitive_object(f'{ASSET_ID}-rail-{y_offset}', 'cylinder', steel,
                                     size=(0.016, 0.016, rail_len),
                                     location=(0.0, y_offset, 0.05),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
        objects.append(rail)

    # 2. Central graduated scale bar (aluminum strip between rails)
    scale_bar = kit.primitive_object(f'{ASSET_ID}-scale-bar', 'cube', steel,
                                     size=(rail_len, 0.024, 0.003),
                                     location=(0.0, 0.0, 0.048))
    objects.append(scale_bar)

    # 3. Cast Iron End Support Feet (Left and Right)
    for side in [-1, 1]:
        foot_x = side * (rail_len / 2 + 0.015)
        foot = kit.primitive_object(f'{ASSET_ID}-foot-{side}', 'cube', cast_iron,
                                    size=(0.04, 0.14, 0.06),
                                    location=(foot_x, 0.0, 0.03))
        objects.append(foot)
        # Leveling screws on feet
        for y_pos in [-0.05, 0.05]:
            screw = kit.primitive_object(f'{ASSET_ID}-level-screw-{side}-{y_pos}', 'cylinder', brass,
                                         size=(0.018, 0.018, 0.02),
                                         location=(foot_x, y_pos, 0.01))
            objects.append(screw)

    # Helper to build a sliding rider block
    def make_rider(name, x_pos):
        block = kit.primitive_object(f'{name}-block', 'cube', cast_iron,
                                     size=(0.06, 0.11, 0.035),
                                     location=(x_pos, 0.0, 0.055))
        # Brass knurled clamping screw on side
        screw = kit.primitive_object(f'{name}-clamp-screw', 'cylinder', brass,
                                     size=(0.014, 0.014, 0.012),
                                     location=(x_pos, -0.06, 0.055),
                                     rotation_euler=(math.pi / 2, 0.0, 0.0))
        # Upright stem socket collar
        collar = kit.primitive_object(f'{name}-collar', 'cylinder', brass,
                                      size=(0.018, 0.018, 0.03),
                                      location=(x_pos, 0.0, 0.08))
        return [block, screw, collar]

    # --- Rider 1: Candle Object Rider (x = -0.35m) ---
    objects.extend(make_rider(f'{ASSET_ID}-rider-obj', -0.35))
    # Vertical post
    c_post = kit.primitive_object(f'{ASSET_ID}-candle-post', 'cylinder', steel,
                                  size=(0.01, 0.01, 0.08),
                                  location=(-0.35, 0.0, 0.12))
    # Brass candle cup
    c_cup = kit.primitive_object(f'{ASSET_ID}-candle-cup', 'cylinder', brass,
                                 size=(0.032, 0.032, 0.015),
                                 location=(-0.35, 0.0, 0.16))
    # Wax candle
    c_wax = kit.primitive_object(f'{ASSET_ID}-candle-wax', 'cylinder', candle_wax,
                                 size=(0.022, 0.022, 0.06),
                                 location=(-0.35, 0.0, 0.19))
    # Candle flame (teardrop shape)
    c_flame = kit.primitive_object(f'{ASSET_ID}-candle-flame', 'cone', flame_mat,
                                   size=(0.008, 0.008, 0.018),
                                   location=(-0.35, 0.0, 0.23))
    objects.extend([c_post, c_cup, c_wax, c_flame])

    # --- Rider 2: Lens Mount Rider (x = 0.0m) ---
    objects.extend(make_rider(f'{ASSET_ID}-rider-lens', 0.0))
    # Vertical post
    l_post = kit.primitive_object(f'{ASSET_ID}-lens-post', 'cylinder', steel,
                                  size=(0.01, 0.01, 0.12),
                                  location=(0.0, 0.0, 0.14))
    # Lens rim frame (annulus)
    l_rim = kit.primitive_object(f'{ASSET_ID}-lens-rim', 'cylinder', brass,
                                 size=(0.082, 0.082, 0.008),
                                 location=(0.0, 0.0, 0.22),
                                 rotation_euler=(0.0, math.pi / 2, 0.0))
    # Convex lens glass element (UV sphere scaled thin along X)
    l_glass = kit.primitive_object(f'{ASSET_ID}-lens-glass', 'uv_sphere', glass,
                                   size=(0.076, 0.076, 0.076),
                                   location=(0.0, 0.0, 0.22))
    l_glass.scale = (0.16, 1.0, 1.0)
    objects.extend([l_post, l_rim, l_glass])

    # --- Rider 3: Projection Screen Rider (x = +0.35m) ---
    objects.extend(make_rider(f'{ASSET_ID}-rider-screen', 0.35))
    s_post = kit.primitive_object(f'{ASSET_ID}-screen-post', 'cylinder', steel,
                                  size=(0.01, 0.01, 0.12),
                                  location=(0.35, 0.0, 0.14))
    s_frame = kit.primitive_object(f'{ASSET_ID}-screen-frame', 'cube', cast_iron,
                                   size=(0.008, 0.11, 0.11),
                                   location=(0.35, 0.0, 0.22))
    s_face = kit.primitive_object(f'{ASSET_ID}-screen-face', 'cube', white_screen,
                                  size=(0.004, 0.096, 0.096),
                                  location=(0.347, 0.0, 0.22))
    objects.extend([s_post, s_frame, s_face])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_optical_bench()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=45.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()