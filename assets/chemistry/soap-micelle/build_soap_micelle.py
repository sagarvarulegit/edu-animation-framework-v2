"""
build_soap_micelle.py — 3D Spherical Soap Micelle with Central Oil Droplet
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'soap-micelle'

def build_soap_micelle():
    oil_mat = kit.add_glass_material('micelle-oil', (0.95, 0.82, 0.25), ior=1.45, roughness=0.15)
    tail_mat = kit.add_material('micelle-tail', (0.85, 0.70, 0.28), metallic=0.1, roughness=0.5)
    head_mat = kit.add_material('micelle-head', (0.20, 0.55, 0.95), metallic=0.2, roughness=0.25)
    head_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.15, 0.45, 0.95, 1.0)
    head_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.2

    objects = []

    # 1. Central Spherical Oil/Grease Droplet (Radius = 0.020m)
    oil_droplet = kit.primitive_object(f'{ASSET_ID}-oil-core', 'uv_sphere', oil_mat,
                                       size=(0.040, 0.040, 0.040),
                                       location=(0.0, 0.0, 0.0))
    objects.append(oil_droplet)

    # 2. Radial Soap Molecules (Fibonacci sphere distribution of 20 molecules)
    num_mols = 20
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0

    for i in range(num_mols):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / num_mols)

        dir_vec = Vector((
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        )).normalized()

        # Hydrocarbon tail (cylinder starting at r=0.018m and ending at r=0.045m)
        tail_start = dir_vec * 0.018
        tail_end = dir_vec * 0.045
        tail_mid = (tail_start + tail_end) * 0.5
        tail_len = (tail_end - tail_start).length
        rot = dir_vec.to_track_quat('Z', 'Y').to_euler()

        tail = kit.primitive_object(f'{ASSET_ID}-tail-{i}', 'cylinder', tail_mat,
                                    size=(0.0032, 0.0032, tail_len),
                                    location=(tail_mid.x, tail_mid.y, tail_mid.z),
                                    rotation_euler=rot)
        objects.append(tail)

        # Polar Ionic Head (-COO- Na+) sphere at r = 0.052m
        head_pos = dir_vec * 0.052
        head = kit.primitive_object(f'{ASSET_ID}-head-{i}', 'uv_sphere', head_mat,
                                    size=(0.012, 0.012, 0.012),
                                    location=(head_pos.x, head_pos.y, head_pos.z))
        objects.append(head)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_soap_micelle()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
