"""
build_circuit.py — High-Fidelity Closed Electric Circuit Demonstration Board
NCERT Class 10 Chapter 12 (Electricity), Figure 12.1.
Physical Law: Ohm's Law I = V/R.
In a closed circuit, current flows and the incandescent bulb filament glows.
In an open circuit (switch open), I = 0 and the bulb filament does NOT glow.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'full-circuit'

def build_circuit(switch_closed=True, voltage=1.5, resistance=100.0):
    # Physical Law: Ohm's Law I = V/R
    current = (voltage / resistance) if switch_closed else 0.0
    # Bulb filament emission wired to circuit continuity
    emission_strength = 4.0 if (switch_closed and current > 0) else 0.0
    # Warm incandescent emission color (#ffaa44)
    emission_color = (1.0, 0.667, 0.267, 1.0)

    board_mat = kit.add_material('board-wood', (0.75, 0.65, 0.50), metallic=0.05, roughness=0.6)
    brass_mat = kit.add_machined_metal_material('circuit-brass', (0.86, 0.70, 0.28), metallic=0.92, roughness=0.25)
    copper_mat = kit.add_machined_metal_material('circuit-copper', (0.88, 0.55, 0.25), metallic=0.90, roughness=0.28)
    batt_mat = kit.add_material('circuit-batt', (0.10, 0.12, 0.15), metallic=0.3, roughness=0.4)
    gold_mat = kit.add_machined_metal_material('circuit-gold', (0.85, 0.68, 0.22), metallic=0.85, roughness=0.25)
    glass_mat = kit.add_glass_material('circuit-bulb-glass', (0.98, 0.99, 1.0), ior=1.52, roughness=0.02)
    handle_mat = kit.add_material('circuit-switch-handle', (0.85, 0.15, 0.12), metallic=0.05, roughness=0.4)

    glow_mat = kit.add_material('circuit-bulb-glow', (1.0, 0.667, 0.267), metallic=0.1, roughness=0.2)
    glow_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = emission_color
    glow_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = emission_strength

    meter_mat = kit.add_material('circuit-meter-case', (0.12, 0.13, 0.15), metallic=0.2, roughness=0.5)
    dial_mat = kit.add_material('circuit-dial', (0.95, 0.95, 0.92), metallic=0.0, roughness=0.3)
    red_wire_mat = kit.add_material('wire-pos-red', (0.88, 0.15, 0.12), metallic=0.05, roughness=0.5)
    black_wire_mat = kit.add_material('wire-neg-black', (0.08, 0.08, 0.10), metallic=0.05, roughness=0.5)
    res_body_mat = kit.add_material('circuit-resistor', (0.82, 0.75, 0.55), metallic=0.05, roughness=0.5)

    objects = []

    # 1. Main Demonstration Mounting Board with Rubber Feet
    board = kit.primitive_object(f'{ASSET_ID}-board', 'cube', board_mat,
                                size=(0.180, 0.140, 0.010),
                                location=(0.0, 0.0, 0.005))
    objects.append(board)
    for fx in [-0.08, 0.08]:
        for fy in [-0.06, 0.06]:
            foot = kit.primitive_object(f'{ASSET_ID}-foot-{fx}-{fy}', 'cylinder', meter_mat,
                                        size=(0.010, 0.010, 0.004),
                                        location=(fx, fy, -0.002))
            objects.append(foot)

    # 2. Battery & Holder at Upper Left (-X, +Y)
    # Negative terminal at -X, Positive terminal at +X
    bx, by = -0.050, 0.040
    holder = kit.primitive_object(f'{ASSET_ID}-batt-holder', 'cube', meter_mat,
                                 size=(0.055, 0.020, 0.012),
                                 location=(bx, by, 0.016))
    batt = kit.primitive_object(f'{ASSET_ID}-battery', 'cylinder', batt_mat,
                               size=(0.014, 0.014, 0.048),
                               location=(bx, by, 0.020),
                               rotation_euler=(0.0, math.pi / 2, 0.0))
    batt_cap = kit.primitive_object(f'{ASSET_ID}-batt-cap', 'cylinder', gold_mat,
                                   size=(0.006, 0.006, 0.004),
                                   location=(bx + 0.025, by, 0.020),
                                   rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.extend([holder, batt, batt_cap])

    # 3. Knife Switch at Lower Left (-X, -Y)
    sx, sy = -0.050, -0.035
    sw_base = kit.primitive_object(f'{ASSET_ID}-switch-base', 'cube', meter_mat,
                                  size=(0.045, 0.024, 0.008),
                                  location=(sx, sy, 0.014))
    objects.append(sw_base)

    # Hinge block at -X end (-0.065, sy)
    sw_hinge = kit.primitive_object(f'{ASSET_ID}-switch-hinge', 'cube', brass_mat,
                                    size=(0.010, 0.010, 0.012),
                                    location=(sx - 0.014, sy, 0.020))
    sw_pin = kit.primitive_object(f'{ASSET_ID}-switch-pin', 'cylinder', brass_mat,
                                  size=(0.003, 0.003, 0.012),
                                  location=(sx - 0.014, sy, 0.022),
                                  rotation_euler=(math.pi / 2, 0.0, 0.0))
    objects.extend([sw_hinge, sw_pin])

    # Receiving copper U-jaw clips at +X end (-0.036, sy)
    sw_jaw_base = kit.primitive_object(f'{ASSET_ID}-switch-jaw-base', 'cube', brass_mat,
                                       size=(0.010, 0.010, 0.008),
                                       location=(sx + 0.014, sy, 0.018))
    sw_jaw_1 = kit.primitive_object(f'{ASSET_ID}-switch-jaw-1', 'cube', copper_mat,
                                    size=(0.008, 0.002, 0.012),
                                    location=(sx + 0.014, sy - 0.0025, 0.022))
    sw_jaw_2 = kit.primitive_object(f'{ASSET_ID}-switch-jaw-2', 'cube', copper_mat,
                                    size=(0.008, 0.002, 0.012),
                                    location=(sx + 0.014, sy + 0.0025, 0.022))
    objects.extend([sw_jaw_base, sw_jaw_1, sw_jaw_2])

    # Pivoting Knife Switch Blade (closed into U-jaw at rotation_euler = (0, 0, 0))
    blade_angle = 0.0 if switch_closed else -0.55
    blade_len = 0.032
    blade_cx = (sx - 0.014) + (blade_len / 2) * math.cos(blade_angle)
    blade_cz = 0.022 + (blade_len / 2) * math.sin(-blade_angle)
    sw_blade = kit.primitive_object(f'{ASSET_ID}-switch-blade', 'cube', brass_mat,
                                   size=(blade_len, 0.0024, 0.006),
                                   location=(blade_cx, sy, blade_cz),
                                   rotation_euler=(0.0, blade_angle, 0.0))
    # Red insulated handle at the tip of the knife switch blade
    handle_x = (sx - 0.014) + blade_len * math.cos(blade_angle)
    handle_z = 0.022 + blade_len * math.sin(-blade_angle)
    sw_handle = kit.primitive_object(f'{ASSET_ID}-switch-handle', 'cylinder', handle_mat,
                                     size=(0.006, 0.006, 0.014),
                                     location=(handle_x, sy, handle_z + 0.005),
                                     rotation_euler=(0.0, blade_angle, 0.0))
    objects.extend([sw_blade, sw_handle])

    # 4. Light Bulb in Socket at Upper Right (+X, +Y)
    lx, ly = 0.050, 0.040
    sock = kit.primitive_object(f'{ASSET_ID}-socket', 'cylinder', meter_mat,
                               size=(0.024, 0.024, 0.014),
                               location=(lx, ly, 0.017))
    bulb_globe = kit.primitive_object(f'{ASSET_ID}-bulb-globe', 'uv_sphere', glass_mat,
                                      size=(0.022, 0.022, 0.022),
                                      location=(lx, ly, 0.032))
    bulb_fil = kit.primitive_object(f'{ASSET_ID}-filament', 'uv_sphere', glow_mat,
                                    size=(0.006, 0.006, 0.006),
                                    location=(lx, ly, 0.032))
    objects.extend([sock, bulb_globe, bulb_fil])

    # 5. DC Ammeter at Center-Right (+X, -Y)
    ax, ay = 0.055, -0.010
    amm_case = kit.primitive_object(f'{ASSET_ID}-ammeter-case', 'cube', meter_mat,
                                   size=(0.036, 0.032, 0.026),
                                   location=(ax, ay, 0.023))
    amm_dial = kit.primitive_object(f'{ASSET_ID}-ammeter-dial', 'cube', dial_mat,
                                   size=(0.028, 0.002, 0.018),
                                   location=(ax, ay - 0.016, 0.025))
    # Needle deflected when current flows
    needle_angle = 0.35 if (switch_closed and current > 0) else 0.0
    amm_needle = kit.primitive_object(f'{ASSET_ID}-ammeter-needle', 'cylinder', handle_mat,
                                      size=(0.001, 0.001, 0.012),
                                      location=(ax, ay - 0.015, 0.027),
                                      rotation_euler=(0.0, 0.0, needle_angle))
    objects.extend([amm_case, amm_dial, amm_needle])

    # 6. Resistor at Lower Center
    rx, ry = 0.005, -0.040
    res = kit.primitive_object(f'{ASSET_ID}-resistor', 'cylinder', res_body_mat,
                               size=(0.0045, 0.0045, 0.018),
                               location=(rx, ry, 0.015),
                               rotation_euler=(0.0, math.pi / 2, 0.0))
    res_band = kit.primitive_object(f'{ASSET_ID}-resistor-band', 'cylinder', gold_mat,
                                    size=(0.0048, 0.0048, 0.002),
                                    location=(rx, ry, 0.015),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.extend([res, res_band])

    # 7. Complete Closed-Loop Topological Chain: battery -> switch -> bulb -> resistor -> battery
    # Smooth interconnecting wire tubes routing current through the complete circuit
    wire_r = 0.0014

    # Segment 1: Battery (+) to Switch Hinge (Red Wire)
    # Battery cap at (bx + 0.025, by, 0.020) -> down to Switch Hinge at (sx - 0.014, sy, 0.020)
    w1_pts = [
        (bx + 0.027, by, 0.020),
        (-0.015, by, 0.020),
        (-0.015, 0.005, 0.020),
        (sx - 0.025, 0.005, 0.020),
        (sx - 0.025, sy, 0.020),
        (sx - 0.018, sy, 0.020)
    ]
    w1 = kit.create_smooth_tube(f'{ASSET_ID}-wire-battery-to-switch', w1_pts, radius=wire_r, material=red_wire_mat)
    objects.append(w1)

    # Knife switch blade connects hinge to jaw: completes circuit when closed!

    # Segment 2: Switch Jaw to Bulb (+) Terminal (Red Wire)
    # Switch jaw at (sx + 0.014, sy, 0.020) -> routes up to Bulb socket at (lx - 0.012, ly, 0.020)
    w2_pts = [
        (sx + 0.018, sy, 0.020),
        (sx + 0.030, sy, 0.020),
        (sx + 0.030, 0.015, 0.020),
        (lx - 0.025, 0.015, 0.020),
        (lx - 0.025, ly, 0.020),
        (lx - 0.012, ly, 0.020)
    ]
    w2 = kit.create_smooth_tube(f'{ASSET_ID}-wire-switch-to-bulb', w2_pts, radius=wire_r, material=red_wire_mat)
    objects.append(w2)

    # Segment 3: Bulb (-) Terminal to Ammeter (+) (Red Wire)
    # Bulb socket at (lx, ly - 0.012, 0.020) -> Ammeter at (ax, ay + 0.016, 0.020)
    w3_pts = [
        (lx, ly - 0.012, 0.020),
        (lx, 0.020, 0.020),
        (ax, 0.020, 0.020),
        (ax, ay + 0.016, 0.020)
    ]
    w3 = kit.create_smooth_tube(f'{ASSET_ID}-wire-bulb-to-ammeter', w3_pts, radius=wire_r, material=red_wire_mat)
    objects.append(w3)

    # Segment 4: Ammeter (-) to Resistor (Red Wire)
    # Ammeter at (ax, ay - 0.016, 0.020) -> Resistor right lead at (rx + 0.012, ry, 0.015)
    w4_pts = [
        (ax, ay - 0.016, 0.020),
        (ax, ry, 0.018),
        (rx + 0.015, ry, 0.016),
        (rx + 0.010, ry, 0.015)
    ]
    w4 = kit.create_smooth_tube(f'{ASSET_ID}-wire-ammeter-to-resistor', w4_pts, radius=wire_r, material=red_wire_mat)
    objects.append(w4)

    # Segment 5: Resistor to Battery (-) Return (Black Wire)
    # Resistor left lead at (rx - 0.010, ry, 0.015) -> bottom left corner -> Battery (-) at (bx - 0.028, by, 0.020)
    w5_pts = [
        (rx - 0.010, ry, 0.015),
        (-0.065, ry, 0.018),
        (-0.075, ry, 0.018),
        (-0.075, by, 0.020),
        (bx - 0.028, by, 0.020)
    ]
    w5 = kit.create_smooth_tube(f'{ASSET_ID}-wire-resistor-to-battery', w5_pts, radius=wire_r, material=black_wire_mat)
    objects.append(w5)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_circuit(switch_closed=True)
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
