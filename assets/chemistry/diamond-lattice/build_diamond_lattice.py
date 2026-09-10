"""
build_diamond_lattice.py — Rigid 3D Tetrahedral Carbon Diamond Lattice
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'diamond-lattice'

def build_diamond_lattice():
    # Diamond optical material (IOR = 2.42, sparkling high luster)
    diamond_mat = kit.add_glass_material('diamond-carbon', (0.92, 0.96, 1.0), ior=2.42, roughness=0.08)
    bond_mat = kit.add_machined_metal_material('diamond-bond', (0.80, 0.82, 0.85), metallic=0.75, roughness=0.25)

    objects = []

    # Tetrahedral bond length and basis displacement vectors
    # Exact sp3 carbon tetrahedral bond angle: arccos(-1/3) ~ 109.4712 degrees
    d = 0.038
    u = d / math.sqrt(3.0)
    # Sublattice A tetrahedral coordination vectors (4-coordinate sp3 hybridization)
    t_dirs_A = [
        Vector((u, u, u)),
        Vector((u, -u, -u)),
        Vector((-u, u, -u)),
        Vector((-u, -u, u))
    ]
    # Sublattice B inverted tetrahedral coordination vectors (Fd-3m diamond cubic symmetry)
    # Child tetrahedral vectors are inverted: d_child = -d_parent
    t_dirs_B = [-v for v in t_dirs_A]

    # Generate diamond cubic lattice via crystallographic BFS with node merging
    # Sublattice A at origin (0,0,0)
    nodes = [Vector((0.0, 0.0, 0.0))]
    sublattices = ['A']
    edges = set()
    queue = [(0, 0)]  # (node_idx, depth)
    max_depth = 3
    r_cut = 0.085

    while queue:
        curr_idx, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        curr_pos = nodes[curr_idx]
        sub = sublattices[curr_idx]
        dirs = t_dirs_A if sub == 'A' else t_dirs_B
        next_sub = 'B' if sub == 'A' else 'A'

        for dt in dirs:
            next_pos = curr_pos + dt
            if next_pos.length > r_cut + 1e-4:
                continue

            # Identify if this lattice position already matches an existing carbon atom
            match_idx = None
            for i, p in enumerate(nodes):
                if (p - next_pos).length < 0.001:
                    match_idx = i
                    break

            if match_idx is None:
                match_idx = len(nodes)
                nodes.append(next_pos)
                sublattices.append(next_sub)
                queue.append((match_idx, depth + 1))

            edge = tuple(sorted((curr_idx, match_idx)))
            edges.add(edge)

    # 1. Create Carbon Atom Spheres (Radius = 0.012m, 0 non-manifold edges)
    for idx, pos in enumerate(nodes):
        atom = kit.primitive_object(f'{ASSET_ID}-atom-{idx}', 'uv_sphere', diamond_mat,
                                    size=(0.024, 0.024, 0.024),
                                    location=(pos.x, pos.y, pos.z))
        objects.append(atom)

    # 2. Create Tetrahedral Covalent Bond Rods (Capped cylinders, 0 non-manifold edges)
    for b_idx, (i1, i2) in enumerate(sorted(list(edges))):
        p1 = nodes[i1]
        p2 = nodes[i2]
        mid_pt = (p1 + p2) * 0.5
        delta = p2 - p1
        bond_len = delta.length
        direction = delta.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()
        bond = kit.primitive_object(f'{ASSET_ID}-bond-{b_idx}', 'cylinder', bond_mat,
                                    size=(0.005, 0.005, bond_len),
                                    location=(mid_pt.x, mid_pt.y, mid_pt.z),
                                    rotation_euler=rot)
        objects.append(bond)

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_diamond_lattice()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
