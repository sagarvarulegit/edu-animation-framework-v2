"""
build_water_electrolysis.py — High-Fidelity Electrolysis of Water Apparatus
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'water-electrolysis-apparatus'

def build_electrolysis_cell():
    # Physically tuned PBR materials for stable WebGL multi-layer transparency
    # Outer beaker vessel glass
    vessel_mat = kit.add_material('elec-vessel-glass', (0.92, 0.96, 0.98), roughness=0.08)
    v_bsdf = vessel_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in v_bsdf.inputs:
        v_bsdf.inputs["Transmission Weight"].default_value = 0.82
    if "IOR" in v_bsdf.inputs:
        v_bsdf.inputs["IOR"].default_value = 1.48

    # Acidified water bulk
    water_bulk_mat = kit.add_material('elec-water-bulk', (0.75, 0.90, 0.96), roughness=0.04)
    wb_bsdf = water_bulk_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in wb_bsdf.inputs:
        wb_bsdf.inputs["Transmission Weight"].default_value = 0.68
    if "IOR" in wb_bsdf.inputs:
        wb_bsdf.inputs["IOR"].default_value = 1.33

    # Inverted graduated test tubes glass
    tube_mat = kit.add_material('elec-tube-glass', (0.94, 0.98, 1.0), roughness=0.03)
    t_bsdf = tube_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in t_bsdf.inputs:
        t_bsdf.inputs["Transmission Weight"].default_value = 0.88
    if "IOR" in t_bsdf.inputs:
        t_bsdf.inputs["IOR"].default_value = 1.50

    # Water inside tube
    tube_water_mat = kit.add_material('elec-tube-water', (0.70, 0.88, 0.96), roughness=0.05)
    tw_bsdf = tube_water_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in tw_bsdf.inputs:
        tw_bsdf.inputs["Transmission Weight"].default_value = 0.60

    # Meniscus ring at gas-liquid boundary
    meniscus_mat = kit.add_material('elec-meniscus', (0.85, 0.95, 1.0), roughness=0.10)
    m_bsdf = meniscus_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in m_bsdf.inputs:
        m_bsdf.inputs["Transmission Weight"].default_value = 0.75

    # Graphite Carbon Electrodes
    graphite_mat = kit.add_material('elec-graphite', (0.12, 0.12, 0.14), metallic=0.35, roughness=0.65)
    rubber_mat = kit.add_material('elec-rubber', (0.05, 0.05, 0.06), metallic=0.02, roughness=0.85)
    base_stand_mat = kit.add_material('elec-base', (0.16, 0.18, 0.22), metallic=0.25, roughness=0.45)
    brass_mat = kit.add_material('elec-brass', (0.82, 0.68, 0.24), metallic=0.88, roughness=0.28)
    red_term = kit.add_material('term-red', (0.82, 0.10, 0.12), metallic=0.15, roughness=0.30)
    black_term = kit.add_material('term-black', (0.04, 0.04, 0.05), metallic=0.15, roughness=0.30)
    enamel_mat = kit.add_material('grad-enamel', (0.95, 0.95, 0.95), metallic=0.0, roughness=0.35)
    bubble_mat = kit.add_material('elec-bubble', (0.92, 0.96, 1.0), roughness=0.05)
    bub_bsdf = bubble_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in bub_bsdf.inputs:
        bub_bsdf.inputs["Transmission Weight"].default_value = 0.90

    objects = []

    # 1. Laboratory Support Base (Heavy acrylic/plastic stand)
    base = kit.primitive_object(
        f'{ASSET_ID}-base', 'cube', base_stand_mat,
        size=(0.150, 0.125, 0.016),
        location=(0.0, 0.0, 0.008)
    )
    objects.append(base)

    # 2. Outer Transparent Electrolysis Vessel (Graduated reaction beaker)
    vessel_profile = [
        (0.000, 0.016),
        (0.048, 0.016),
        (0.050, 0.019),
        (0.050, 0.098),
        (0.053, 0.100),
        (0.050, 0.100),
        (0.047, 0.019),
        (0.000, 0.019)
    ]
    vessel = kit.lathe_object(f'{ASSET_ID}-vessel', vessel_profile, segments=48, material=vessel_mat)
    objects.append(vessel)

    # 3. Acidified Water Liquid Body inside vessel
    water_bulk = kit.primitive_object(
        f'{ASSET_ID}-water-bulk', 'cylinder', water_bulk_mat,
        size=(0.094, 0.094, 0.068),
        location=(0.0, 0.0, 0.054)
    )
    objects.append(water_bulk)

    # 4. Two Rubber Stoppers at Base (Sealing electrode perforations)
    for x_pos in [-0.022, 0.022]:
        stopper = kit.primitive_object(
            f'{ASSET_ID}-stopper-{x_pos}', 'cylinder', rubber_mat,
            size=(0.015, 0.015, 0.018),
            location=(x_pos, 0.0, 0.018)
        )
        objects.append(stopper)

    # 5. Graphite Carbon Electrodes (Anode at -0.022m, Cathode at +0.022m)
    for x_pos, name in [(-0.022, 'anode'), (0.022, 'cathode')]:
        rod = kit.primitive_object(
            f'{ASSET_ID}-electrode-{name}', 'cylinder', graphite_mat,
            size=(0.006, 0.006, 0.062),
            location=(x_pos, 0.0, 0.054)
        )
        objects.append(rod)

    # 6. Electrical Leads and Terminal Posts at Base
    # Anode (+ Red, Left)
    t_anode = kit.primitive_object(
        f'{ASSET_ID}-term-anode', 'cylinder', red_term,
        size=(0.009, 0.009, 0.014),
        location=(-0.042, -0.045, 0.020)
    )
    # Cathode (- Black, Right)
    t_cathode = kit.primitive_object(
        f'{ASSET_ID}-term-cathode', 'cylinder', black_term,
        size=(0.009, 0.009, 0.014),
        location=(0.042, -0.045, 0.020)
    )
    objects.extend([t_anode, t_cathode])

    # 7. Inverted Graduated Test Tubes (2:1 Stoichiometric Volume Ratio)
    # Left Tube (Anode): collects O2 gas in upper portion (1 volume unit = 0.024m)
    # Right Tube (Cathode): collects H2 gas in upper portion (2 volume units = 0.048m)
    tubes_config = [
        (-0.022, 'anode-o2', 0.024, 4),   # 1 volume O2, fewer bubbles
        (0.022, 'cathode-h2', 0.048, 8)   # 2 volumes H2, twice as many bubbles
    ]
    for x_pos, name, gas_h, num_bubs in tubes_config:
        # Inverted Test Tube Lathe Profile
        tube_profile = [
            (0.000, 0.170),
            (0.0085, 0.168),
            (0.0095, 0.165),
            (0.0095, 0.032),
            (0.0105, 0.030),
            (0.0082, 0.030),
            (0.0082, 0.164),
            (0.000, 0.166)
        ]
        tube = kit.lathe_object(f'{ASSET_ID}-tube-{name}', tube_profile, segments=36, material=tube_mat,
                                location=(x_pos, 0.0, 0.0))
        objects.append(tube)

        # Water column inside inverted tube (liquid fills from bottom to meniscus)
        water_col_h = (0.165 - gas_h) - 0.032
        water_z = 0.032 + water_col_h / 2.0
        w_col = kit.primitive_object(
            f'{ASSET_ID}-water-col-{name}', 'cylinder', tube_water_mat,
            size=(0.0155, 0.0155, water_col_h),
            location=(x_pos, 0.0, water_z)
        )
        objects.append(w_col)

        # Distinct Meniscus Disc at gas-liquid interface
        meniscus = kit.primitive_object(
            f'{ASSET_ID}-meniscus-{name}', 'cylinder', meniscus_mat,
            size=(0.0158, 0.0158, 0.0015),
            location=(x_pos, 0.0, 0.165 - gas_h)
        )
        objects.append(meniscus)

        # White Enamel Graduation Markings along the tube
        for g_idx in range(6):
            gz = 0.050 + g_idx * 0.018
            tick = kit.primitive_object(
                f'{ASSET_ID}-tick-{name}-{g_idx}', 'cylinder', enamel_mat,
                size=(0.0195, 0.0195, 0.001),
                location=(x_pos, 0.0, gz)
            )
            objects.append(tick)

        # Effervescent Gas Bubbles rising from electrode
        for b_idx in range(num_bubs):
            bz = 0.040 + b_idx * (water_col_h / num_bubs)
            bx = x_pos + 0.0025 * math.sin(b_idx * 2.0)
            by = 0.0025 * math.cos(b_idx * 2.0)
            bub = kit.primitive_object(
                f'{ASSET_ID}-bub-{name}-{b_idx}', 'uv_sphere', bubble_mat,
                size=(0.0025, 0.0025, 0.0025),
                location=(bx, by, bz)
            )
            objects.append(bub)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_electrolysis_cell()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()