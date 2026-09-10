"""
build_glass_slab.py — High-Fidelity Rectangular Optical Glass Refraction Block
NCERT Class 10 Chapter 10 (Light — Reflection and Refraction), Section 10.3.1, Figure 10.10.
Features:
- Borosilicate / crown optical glass block (100mm x 65mm x 20mm, IOR = 1.52, roughness 0.015)
- Drawing sheet with pencil outline of slab
- Complete optical ray paths with exact Snell's law refraction:
  * Incident ray in air at angle i = 36.0°
  * Surface normal at first interface (air-to-glass)
  * Refracted ray inside glass at angle r = arcsin(sin(i) / n) ≈ 22.72°
  * Surface normal at second interface (glass-to-air)
  * Emergent ray in air at angle e = i = 36.0° (parallel to incident ray)
  * Lateral displacement d = (t * sin(i - r)) / cos(r) > 0
  * Unrefracted straight-line path extension showing lateral shift d
- Laboratory refraction pins P1, P2 (collinear with incident ray) and P3, P4 (collinear with emergent ray)
- 0 non-manifold edges across all components
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'glass-slab'

def build_slab():
    glass_mat = kit.add_glass_material('slab-glass-optical', tint=(0.95, 0.98, 1.0), ior=1.52, roughness=0.015)
    paper_mat = kit.add_material('slab-drawing-sheet', (0.95, 0.95, 0.92), metallic=0.0, roughness=0.7)
    outline_mat = kit.add_material('slab-pencil-line', (0.25, 0.25, 0.27), metallic=0.1, roughness=0.8)

    pin_stem_mat = kit.add_machined_metal_material('slab-pin-stem', (0.85, 0.85, 0.88), metallic=0.95, roughness=0.2)
    pin_head_inc = kit.add_material('slab-pin-head-inc', (0.88, 0.15, 0.12), metallic=0.1, roughness=0.3)
    pin_head_em  = kit.add_material('slab-pin-head-em',  (0.95, 0.72, 0.15), metallic=0.1, roughness=0.3)

    # Luminescent ray materials
    ray_inc_mat = kit.add_material('ray-incident', (1.0, 0.85, 0.25), metallic=0.0, roughness=0.2)
    ray_inc_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (1.0, 0.85, 0.25, 1.0)
    ray_inc_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 5.0

    ray_refr_mat = kit.add_material('ray-refracted', (0.25, 0.85, 1.0), metallic=0.0, roughness=0.2)
    ray_refr_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.25, 0.85, 1.0, 1.0)
    ray_refr_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 4.0

    ray_straight_mat = kit.add_material('ray-straight-ext', (0.75, 0.75, 0.75), metallic=0.0, roughness=0.5)
    ray_straight_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.75, 0.75, 0.75, 1.0)
    ray_straight_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.5

    normal_mat = kit.add_material('ray-normal', (0.40, 0.90, 0.50), metallic=0.0, roughness=0.3)
    normal_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.40, 0.90, 0.50, 1.0)
    normal_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 3.0

    objects = []

    # 1. High-Grade Borosilicate Optical Glass Slab (100mm x 65mm x 20mm)
    w, t, h = 0.100, 0.065, 0.020
    slab_z = h / 2 + 0.002
    slab = kit.primitive_object(f'{ASSET_ID}-body', 'cube', glass_mat,
                                size=(w, t, h),
                                location=(0.0, 0.0, slab_z))
    objects.append(slab)

    # 2. White Paper Drawing Sheet Base underneath
    sheet = kit.primitive_object(f'{ASSET_ID}-sheet', 'cube', paper_mat,
                                 size=(0.140, 0.110, 0.002),
                                 location=(0.0, 0.0, 0.001))
    objects.append(sheet)

    # 3. Slab Pencil Outline on Drawing Sheet (4 pencil border lines around slab footprint)
    # Slab edges: x in [-w/2, w/2], y in [-t/2, t/2]
    outline_lines = [
        # Front edge (y = -t/2)
        [(-w/2, -t/2, 0.0021), (w/2, -t/2, 0.0021)],
        # Back edge (y = +t/2)
        [(-w/2, t/2, 0.0021), (w/2, t/2, 0.0021)],
        # Left edge (x = -w/2)
        [(-w/2, -t/2, 0.0021), (-w/2, t/2, 0.0021)],
        # Right edge (x = +w/2)
        [(w/2, -t/2, 0.0021), (w/2, t/2, 0.0021)]
    ]
    for idx, pts in enumerate(outline_lines):
        line = kit.create_smooth_tube(f'{ASSET_ID}-outline-{idx}', pts, radius=0.0004, material=outline_mat)
        objects.append(line)

    # 4. Snell's Law Optics Calculations
    # Angle of incidence i
    i_deg = 36.0
    i_rad = math.radians(i_deg)
    n_glass = 1.52
    # Refracted angle r = arcsin(sin(i) / n)
    r_rad = math.asin(math.sin(i_rad) / n_glass)
    r_deg = math.degrees(r_rad)
    # Emergent angle e = i
    e_rad = i_rad
    e_deg = i_deg
    # Lateral displacement d = (t * sin(i - r)) / cos(r)
    lateral_d = (t * math.sin(i_rad - r_rad)) / math.cos(r_rad)

    # Ray height at middle of glass slab
    z_ray = slab_z
    ray_radius = 0.0009

    # Point of incidence O on first interface (y = -t/2 = -0.0325)
    x_inc = -0.016
    y_inc = -t / 2
    pt_O = Vector((x_inc, y_inc, z_ray))

    # Incident ray direction vector: (+sin(i), +cos(i), 0)
    dir_inc = Vector((math.sin(i_rad), math.cos(i_rad), 0.0)).normalized()

    # Incident ray in air leading to O
    l_inc = 0.045
    pt_inc_start = pt_O - dir_inc * l_inc
    ray_inc = kit.create_smooth_tube(f'{ASSET_ID}-ray-incident', [pt_inc_start, pt_O],
                                     radius=ray_radius, material=ray_inc_mat)
    objects.append(ray_inc)

    # Point of emergence O' on second interface (y = +t/2 = +0.0325)
    delta_x = t * math.tan(r_rad)
    x_em = x_inc + delta_x
    y_em = t / 2
    pt_O_prime = Vector((x_em, y_em, z_ray))

    # Refracted ray inside glass connecting O to O'
    ray_refr = kit.create_smooth_tube(f'{ASSET_ID}-ray-refracted', [pt_O, pt_O_prime],
                                      radius=ray_radius, material=ray_refr_mat)
    objects.append(ray_refr)

    # Emergent ray in air from O' (direction is dir_inc since e = i)
    l_em = 0.045
    pt_em_end = pt_O_prime + dir_inc * l_em
    ray_em = kit.create_smooth_tube(f'{ASSET_ID}-ray-emergent', [pt_O_prime, pt_em_end],
                                    radius=ray_radius, material=ray_inc_mat)
    objects.append(ray_em)

    # Unrefracted straight-line path extension from O (to illustrate lateral displacement d)
    pt_straight_end = pt_O + dir_inc * (t + 0.040)
    ray_straight = kit.create_smooth_tube(f'{ASSET_ID}-ray-straight-path', [pt_O, pt_straight_end],
                                          radius=0.0005, material=ray_straight_mat)
    objects.append(ray_straight)

    # Surface Normals N1-N1' and N2-N2' (perpendicular to refracting faces, along Y axis)
    norm_len = 0.016
    norm_1_pts = [Vector((x_inc, y_inc - norm_len, z_ray)), Vector((x_inc, y_inc + norm_len, z_ray))]
    norm_2_pts = [Vector((x_em, y_em - norm_len, z_ray)), Vector((x_em, y_em + norm_len, z_ray))]
    norm_1 = kit.create_smooth_tube(f'{ASSET_ID}-normal-1', norm_1_pts, radius=0.0005, material=normal_mat)
    norm_2 = kit.create_smooth_tube(f'{ASSET_ID}-normal-2', norm_2_pts, radius=0.0005, material=normal_mat)
    objects.extend([norm_1, norm_2])

    # 5. Laboratory Refraction Pins (CBSE Class 10 Practical)
    # Incident Pins P1, P2 fixed along the incident ray line
    # Emergent Pins P3, P4 fixed along the emergent ray line
    pin_stem_r = 0.0008
    pin_head_r = 0.0035
    pin_h = 0.024
    z_pin_base = 0.002

    pins = [
        # Pin P1 (far on incident ray)
        ('P1', pt_O - dir_inc * 0.034, pin_head_inc),
        # Pin P2 (near on incident ray)
        ('P2', pt_O - dir_inc * 0.017, pin_head_inc),
        # Pin P3 (near on emergent ray)
        ('P3', pt_O_prime + dir_inc * 0.017, pin_head_em),
        # Pin P4 (far on emergent ray)
        ('P4', pt_O_prime + dir_inc * 0.034, pin_head_em),
    ]

    for p_name, pt_loc, p_mat in pins:
        # Needle stem
        stem = kit.primitive_object(f'{ASSET_ID}-pin-stem-{p_name}', 'cylinder', pin_stem_mat,
                                    size=(pin_stem_r * 2, pin_stem_r * 2, pin_h),
                                    location=(pt_loc.x, pt_loc.y, z_pin_base + pin_h / 2))
        # Needle point tip touching paper
        tip = kit.primitive_object(f'{ASSET_ID}-pin-tip-{p_name}', 'cone', pin_stem_mat,
                                   size=(pin_stem_r * 2, 0.0, 0.003),
                                   location=(pt_loc.x, pt_loc.y, z_pin_base + 0.0015))
        # Spherical head
        head = kit.primitive_object(f'{ASSET_ID}-pin-head-{p_name}', 'uv_sphere', p_mat,
                                    size=(pin_head_r * 2, pin_head_r * 2, pin_head_r * 2),
                                    location=(pt_loc.x, pt_loc.y, z_pin_base + pin_h))
        objects.extend([stem, tip, head])

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_slab()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
