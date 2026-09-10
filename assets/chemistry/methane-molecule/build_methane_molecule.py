"""
build_methane_molecule.py — Tetrahedral Methane (CH4) Covalent Molecule
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'methane-molecule'

def build_methane():
    carbon_mat = kit.add_material('cpk-carbon', (0.18, 0.20, 0.22), metallic=0.15, roughness=0.3)
    hydrogen_mat = kit.add_material('cpk-hydrogen', (0.95, 0.96, 0.98), metallic=0.05, roughness=0.25)
    bond_mat = kit.add_material('covalent-bond', (0.75, 0.76, 0.78), metallic=0.4, roughness=0.35)

    objects = []

    # 1. Central Carbon Atom (Radius = 0.024m)
    carbon = kit.primitive_object(f'{ASSET_ID}-carbon', 'uv_sphere', carbon_mat,
                                  size=(0.048, 0.048, 0.048),
                                  location=(0.0, 0.0, 0.0))
    objects.append(carbon)

    # 2. Four Tetrahedral Hydrogen Vertices
    # Bond length L = 0.055m, angle = 109.47 degrees
    bond_len = 0.055
    scale = bond_len / math.sqrt(3.0)
    tetra_dirs = [
        Vector((1.0, 1.0, 1.0)) * scale,
        Vector((1.0, -1.0, -1.0)) * scale,
        Vector((-1.0, 1.0, -1.0)) * scale,
        Vector((-1.0, -1.0, 1.0)) * scale
    ]

    for idx, pos in enumerate(tetra_dirs):
        # Hydrogen atom sphere (Radius = 0.015m)
        h_atom = kit.primitive_object(f'{ASSET_ID}-hydrogen-{idx}', 'uv_sphere', hydrogen_mat,
                                      size=(0.030, 0.030, 0.030),
                                      location=(pos.x, pos.y, pos.z))
        objects.append(h_atom)

        # C-H Covalent Bond Cylinder
        mid_pt = pos * 0.5
        direction = pos.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()
        bond = kit.primitive_object(f'{ASSET_ID}-bond-{idx}', 'cylinder', bond_mat,
                                    size=(0.007, 0.007, bond_len),
                                    location=(mid_pt.x, mid_pt.y, mid_pt.z),
                                    rotation_euler=rot)
        objects.append(bond)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_methane()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
