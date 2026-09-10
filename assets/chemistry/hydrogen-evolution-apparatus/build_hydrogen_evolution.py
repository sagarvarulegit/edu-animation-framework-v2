"""
build_hydrogen_evolution.py — Reaction of Zinc with Acid & H2 Gas Evolution
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'hydrogen-evolution-apparatus'

def build_hydrogen_evolution():
    glass_mat = kit.add_glass_material('h2-glass', (0.95, 0.98, 1.0), ior=1.52, roughness=0.015)
    acid_mat = kit.add_glass_material('h2-acid', (0.92, 0.96, 0.98), ior=1.34, roughness=0.02)
    soap_mat = kit.add_glass_material('h2-soap-sol', (0.80, 0.90, 0.95), ior=1.335, roughness=0.03)
    bubble_mat = kit.add_glass_material('h2-soap-bubble', (0.90, 0.96, 1.0), ior=1.05, roughness=0.02)
    zinc_mat = kit.add_machined_metal_material('h2-zinc', (0.75, 0.78, 0.82), metallic=0.90, roughness=0.35)
    rubber_mat = kit.add_material('h2-rubber', (0.08, 0.08, 0.09), metallic=0.05, roughness=0.75)
    wax_mat = kit.add_material('h2-candle-wax', (0.92, 0.90, 0.82), metallic=0.0, roughness=0.4)
    flame_mat = kit.add_material('h2-flame', (1.0, 0.65, 0.1), metallic=0.0, roughness=0.2)
    flame_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1.0, 0.6, 0.1, 1.0)
    flame_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 7.0

    objects = []

    # 1. Conical Flask at x = -0.06m (Lathed Erlenmeyer profile)
    flask_profile = [
        (0.000, 0.000),
        (0.044, 0.000),
        (0.046, 0.004),
        (0.016, 0.085),
        (0.014, 0.095),
        (0.017, 0.100),
        (0.015, 0.100),
        (0.013, 0.094),
        (0.014, 0.084),
        (0.044, 0.004),
        (0.000, 0.004)
    ]
    flask = kit.lathe_object(f'{ASSET_ID}-flask', flask_profile, segments=48, material=glass_mat,
                             location=(-0.06, 0.0, 0.0))
    objects.append(flask)

    # 2. Acid Solution Bulk in Flask
    acid_bulk = kit.primitive_object(f'{ASSET_ID}-acid-bulk', 'cylinder', acid_mat,
                                     size=(0.076, 0.076, 0.026),
                                     location=(-0.06, 0.0, 0.016))
    objects.append(acid_bulk)

    # 3. Zinc Granules (Irregular clustered pieces at bottom of flask)
    for z_idx in range(6):
        za = 2 * math.pi * z_idx / 6
        zx = -0.06 + 0.018 * math.cos(za)
        zy = 0.018 * math.sin(za)
        granule = kit.primitive_object(f'{ASSET_ID}-zinc-{z_idx}', 'cube', zinc_mat,
                                       size=(0.007, 0.007, 0.005),
                                       location=(zx, zy, 0.006),
                                       rotation_euler=(0.2 * z_idx, 0.3 * z_idx, 0.1 * z_idx))
        objects.append(granule)

    # 4. Two-Hole Rubber Cork at Flask Neck (z = 0.095m)
    cork = kit.primitive_object(f'{ASSET_ID}-cork', 'cylinder', rubber_mat,
                                size=(0.026, 0.026, 0.015),
                                location=(-0.06, 0.0, 0.095))
    objects.append(cork)

    # 5. Thistle Funnel (Enters cork at x = -0.065m, stem goes down to z = 0.012m)
    # Stem
    t_stem = kit.primitive_object(f'{ASSET_ID}-thistle-stem', 'cylinder', glass_mat,
                                  size=(0.004, 0.004, 0.14),
                                  location=(-0.065, 0.0, 0.08))
    # Funnel cup at top (z = 0.155m)
    t_cup = kit.primitive_object(f'{ASSET_ID}-thistle-cup', 'cone', glass_mat,
                                 size=(0.004, 0.022, 0.022),
                                 location=(-0.065, 0.0, 0.16))
    objects.extend([t_stem, t_cup])

    # 6. Continuous Smoothly Bent Glass Delivery Tube
    # Curves from conical flask stopper down into the soap solution trough
    tube_points = [
        Vector((-0.052, 0.0, 0.098)),  # Inside upper flask stopper
        Vector((-0.052, 0.0, 0.125)),  # Vertical rise out of cork
        Vector((-0.038, 0.0, 0.142)),  # Smooth 90-degree curve to horizontal
        Vector((0.015, 0.0, 0.142)),   # Horizontal bridge across apparatus
        Vector((0.052, 0.0, 0.125)),   # Smooth downward bend towards trough
        Vector((0.064, 0.0, 0.065)),   # Delivery stem entering soap trough
        Vector((0.068, 0.0, 0.015))    # Dipping into soap solution for gas bubbling
    ]
    deliv_tube = kit.create_smooth_tube(f'{ASSET_ID}-delivery-tube', tube_points,
                                       radius=0.0024, resolution=24,
                                       material=glass_mat, cap_ends=True)
    objects.append(deliv_tube)

    # 7. Soap Solution Trough at x = +0.07m
    trough_profile = [
        (0.000, 0.000),
        (0.046, 0.000),
        (0.048, 0.004),
        (0.048, 0.042),
        (0.045, 0.042),
        (0.045, 0.004),
        (0.000, 0.004)
    ]
    trough = kit.lathe_object(f'{ASSET_ID}-trough', trough_profile, segments=48, material=glass_mat,
                              location=(0.07, 0.0, 0.0))
    # Soap liquid inside trough
    soap_liquid = kit.primitive_object(f'{ASSET_ID}-soap-bulk', 'cylinder', soap_mat,
                                       size=(0.088, 0.088, 0.025),
                                       location=(0.07, 0.0, 0.016))
    objects.extend([trough, soap_liquid])

    # 8. Floating & Rising Soap Bubbles with Hydrogen gas
    bubbles_pos = [
        (0.065, 0.005, 0.038, 0.014),
        (0.075, -0.008, 0.046, 0.018),
        (0.070, 0.012, 0.085, 0.022),
        (0.082, 0.005, 0.130, 0.025)
    ]
    for b_idx, (bx, by, bz, b_rad) in enumerate(bubbles_pos):
        bub = kit.primitive_object(f'{ASSET_ID}-bubble-{b_idx}', 'uv_sphere', bubble_mat,
                                   size=(b_rad, b_rad, b_rad),
                                   location=(bx, by, bz))
        objects.append(bub)

    # 9. Test Burning Candle near rising top bubble
    candle_wax = kit.primitive_object(f'{ASSET_ID}-candle-wax', 'cylinder', wax_mat,
                                      size=(0.014, 0.014, 0.05),
                                      location=(0.125, 0.0, 0.11))
    candle_flame = kit.primitive_object(f'{ASSET_ID}-candle-flame', 'cone', flame_mat,
                                        size=(0.006, 0.006, 0.015),
                                        location=(0.125, 0.0, 0.142))
    objects.extend([candle_wax, candle_flame])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_hydrogen_evolution()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
