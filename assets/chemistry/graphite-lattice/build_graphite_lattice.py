"""
build_graphite_lattice.py — Layered Hexagonal Carbon Graphite Lattice
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'graphite-lattice'

def build_graphite_lattice():
    carbon_mat = kit.add_material('graphite-carbon', (0.16, 0.17, 0.19), metallic=0.5, roughness=0.4)
    bond_mat = kit.add_machined_metal_material('graphite-bond', (0.70, 0.72, 0.75), metallic=0.8, roughness=0.25)
    vdw_mat = kit.add_material('vdw-link', (0.25, 0.75, 0.95), metallic=0.1, roughness=0.3)
    vdw_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.25, 0.75, 0.95, 1.0)
    vdw_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.0

    objects = []

    # In-plane C-C covalent bond length and interlayer van der Waals spacing
    # Real-world crystallography (NCERT Class 11 Ch 11):
    # In-plane bond length a = 141.5 pm, interlayer spacing = 335.0 pm (ratio 2.367 > 2.0)
    bond_r = 0.024  # C-C in-plane bond length (meters)
    layer_gap = 0.0568  # 2.367 * bond_r (van der Waals interlayer gap)

    # Regular 2D hexagonal honeycomb lattice vectors (sp2 hybridization, 3 coplanar bonds at 120 deg)
    # Basis vectors for triangular Bravais lattice
    tau1 = (bond_r, 0.0)
    a1 = (1.5 * bond_r, -0.5 * math.sqrt(3.0) * bond_r)
    a2 = (1.5 * bond_r, 0.5 * math.sqrt(3.0) * bond_r)

    def generate_planar_hex_layer(shift=(0.0, 0.0), r_cut=0.075):
        """Generates a planar graphene sheet with strictly 0 z-variance and 3-coordinated hexagonal rings."""
        nodes = []
        for i in range(-5, 6):
            for j in range(-5, 6):
                # Sublattice A site
                rx = i * a1[0] + j * a2[0] + shift[0]
                ry = i * a1[1] + j * a2[1] + shift[1]
                if math.hypot(rx, ry) <= r_cut:
                    nodes.append((rx, ry))
                # Sublattice B site
                bx = rx + tau1[0]
                by = ry + tau1[1]
                if math.hypot(bx, by) <= r_cut:
                    nodes.append((bx, by))

        # Covalent bonds: each atom connects to 3 coplanar neighbors at distance ~ bond_r
        bonds = []
        for m in range(len(nodes)):
            for n in range(m + 1, len(nodes)):
                dist = math.hypot(nodes[m][0] - nodes[n][0], nodes[m][1] - nodes[n][1])
                if abs(dist - bond_r) < 1e-4:
                    bonds.append((m, n))
        return nodes, bonds

    # Staggered ABAB stacking:
    # Layer A has shift (0,0); Layer B has in-plane shift tau1 so atoms sit over ring centers & atoms
    pts_layerA, bonds_layerA = generate_planar_hex_layer(shift=(0.0, 0.0), r_cut=0.072)
    pts_layerB, bonds_layerB = generate_planar_hex_layer(shift=tau1, r_cut=0.072)

    layers = [
        (0, -layer_gap / 2, pts_layerA, bonds_layerA, "layerA"),
        (1, layer_gap / 2, pts_layerB, bonds_layerB, "layerB")
    ]

    # Build planar hexagonal graphene sheets
    for l_idx, z_val, pts_layer, bonds_layer, l_name in layers:
        # Carbon atoms (spheres with 0 non-manifold edges)
        for v_idx, (px, py) in enumerate(pts_layer):
            atom = kit.primitive_object(f'{ASSET_ID}-atom-{l_name}-{v_idx}', 'uv_sphere', carbon_mat,
                                        size=(0.020, 0.020, 0.020),
                                        location=(px, py, z_val))
            objects.append(atom)

        # In-plane covalent bonds (capped cylinders with 0 non-manifold edges)
        for b_idx, (i1, i2) in enumerate(bonds_layer):
            p1 = Vector((pts_layer[i1][0], pts_layer[i1][1], z_val))
            p2 = Vector((pts_layer[i2][0], pts_layer[i2][1], z_val))
            mid = (p1 + p2) * 0.5
            delta = p2 - p1
            direction = delta.normalized()
            rot = direction.to_track_quat('Z', 'Y').to_euler()
            bond = kit.primitive_object(f'{ASSET_ID}-bond-{l_name}-{b_idx}', 'cylinder', bond_mat,
                                        size=(0.0042, 0.0042, delta.length),
                                        location=(mid.x, mid.y, mid.z),
                                        rotation_euler=rot)
            objects.append(bond)

    # Van der Waals interlayer vertical links between vertically aligned atom pairs in ABAB stacking
    vdw_count = 0
    for pA in pts_layerA:
        for pB in pts_layerB:
            if math.hypot(pA[0] - pB[0], pA[1] - pB[1]) < 0.002:
                link = kit.primitive_object(f'{ASSET_ID}-vdw-{vdw_count}', 'cylinder', vdw_mat,
                                            size=(0.0018, 0.0018, layer_gap),
                                            location=(pA[0], pA[1], 0.0))
                objects.append(link)
                vdw_count += 1
                break

    return objects

def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_graphite_lattice()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')

if __name__ == '__main__':
    main()
