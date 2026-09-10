"""
build_flower_anatomy.py — Longitudinal Section of a Typical Bisexual Flower
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'flower-anatomy'

def build_flower():
    petal_mat = kit.add_material('flower-petal', (0.92, 0.22, 0.55), metallic=0.05, roughness=0.4)
    green_mat = kit.add_material('flower-stem', (0.28, 0.65, 0.25), metallic=0.05, roughness=0.5)
    anther_mat = kit.add_material('stamen-anther', (0.95, 0.78, 0.15), metallic=0.1, roughness=0.35)
    ovule_mat = kit.add_material('carpel-ovule', (0.95, 0.94, 0.88), metallic=0.05, roughness=0.3)
    filament_mat = kit.add_material('stamen-filament', (0.85, 0.92, 0.75), metallic=0.05, roughness=0.4)

    objects = []

    # 1. Pedicel (Stalk) & Receptacle (Swollen green floral base)
    stalk = kit.primitive_object(f'{ASSET_ID}-pedicel', 'cylinder', green_mat,
                                 size=(0.008, 0.008, 0.045),
                                 location=(0.0, 0.0, 0.015))
    receptacle = kit.lathe_object(f'{ASSET_ID}-receptacle',
                                  [(0.0, 0.035), (0.018, 0.035), (0.024, 0.048), (0.000, 0.048)],
                                  segments=32, material=green_mat)
    objects.extend([stalk, receptacle])

    # 2. Sepals (Calyx — Outward curved green leaves)
    for s_idx in [-1, 1]:
        sepal = kit.primitive_object(f'{ASSET_ID}-sepal-{s_idx}', 'cone', green_mat,
                                     size=(0.008, 0.002, 0.042),
                                     location=(s_idx * 0.024, 0.0, 0.055),
                                     rotation_euler=(0.0, s_idx * -0.75, 0.0))
        objects.append(sepal)

    # 3. Flared Petals (Corolla — Velvety magenta petals arrayed behind and to sides)
    for p_idx, p_rot in enumerate([-1.1, 0.0, 1.1]):
        petal = kit.primitive_object(f'{ASSET_ID}-petal-{p_idx}', 'uv_sphere', petal_mat,
                                     size=(0.045, 0.010, 0.085),
                                     location=(0.035 * math.sin(p_rot), 0.025 * math.cos(p_rot), 0.095),
                                     rotation_euler=(0.3, p_rot, 0.0))
        objects.append(petal)

    # 4. Central Pistil / Carpel (Gynoecium)
    # Basal Ovary (Half-cutaway revealing interior)
    ovary_wall = kit.primitive_object(f'{ASSET_ID}-ovary', 'uv_sphere', green_mat,
                                      size=(0.028, 0.020, 0.032),
                                      location=(0.0, 0.005, 0.058))
    # Interior Ovules (Female egg cell embryo sacs inside ovary chamber)
    for ov_idx, ox in enumerate([-0.005, 0.005]):
        ovule = kit.primitive_object(f'{ASSET_ID}-ovule-{ov_idx}', 'uv_sphere', ovule_mat,
                                     size=(0.007, 0.007, 0.009),
                                     location=(ox, -0.002, 0.058))
        objects.append(ovule)

    # Elongated Style (Neck)
    style = kit.primitive_object(f'{ASSET_ID}-style', 'cylinder', green_mat,
                                 size=(0.004, 0.004, 0.050),
                                 location=(0.0, 0.0, 0.095))
    # Terminal Sticky Stigma (3-lobed platform)
    stigma = kit.primitive_object(f'{ASSET_ID}-stigma', 'uv_sphere', green_mat,
                                  size=(0.012, 0.012, 0.008),
                                  location=(0.0, 0.0, 0.122))
    objects.extend([ovary_wall, style, stigma])

    # 5. Stamens (Androecium — 4 male stamens with slender filaments and golden anthers)
    stamen_angles = [-0.65, -0.25, 0.25, 0.65]
    for s_idx, s_ang in enumerate(stamen_angles):
        # Filament
        fil_x = 0.022 * math.sin(s_ang)
        fil_z = 0.048 + 0.030 * math.cos(s_ang)
        fil = kit.primitive_object(f'{ASSET_ID}-filament-{s_idx}', 'cylinder', filament_mat,
                                   size=(0.002, 0.002, 0.065),
                                   location=(fil_x, -0.005, fil_z),
                                   rotation_euler=(0.0, -s_ang * 0.8, 0.0))
        # Bilobed Golden Anther at tip
        anther_x = fil_x + 0.012 * math.sin(s_ang)
        anther_z = fil_z + 0.026
        anther = kit.primitive_object(f'{ASSET_ID}-anther-{s_idx}', 'uv_sphere', anther_mat,
                                      size=(0.008, 0.006, 0.012),
                                      location=(anther_x, -0.005, anther_z),
                                      rotation_euler=(0.0, 0.0, s_ang))
        objects.extend([fil, anther])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_flower()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
