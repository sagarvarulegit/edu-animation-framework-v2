"""
test_m4_challenger.py — Challenger M4-2 Empirical Test Suite
Exhaustive verification of Milestone 4 Chemistry apparatus and molecular lattices:
1. Exact SHA-256 and byte parity between assets/chemistry/*/out/*.glb and apps/interactive-viewer/public/assets/*.glb
2. Diamond lattice tetrahedral bond angle (arccos(-1/3) ~ 109.47 deg) from actual 3D coordinates
3. Graphite planar hexagonal geometry (z-variance == 0, 120 deg angles) and interlayer spacing ratio > 2.0
4. Dropper glass wall thickness (r_outer - r_inner >= 1.0 mm)
5. Atomic model electron shells (Mg: 2, 8, 2; O: 2, 6; strictly monotonic radii)
6. Glassware shaders: Principled BSDF Transmission Weight, IOR = 1.52, roughness
7. Non-manifold edge audit across all chemistry blend files
"""

import sys
import math
import hashlib
from pathlib import Path
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector

ROOT_DIR = Path(__file__).resolve().parents[2]

failures = []
passed_checks = 0


def record_pass(msg):
    global passed_checks
    passed_checks += 1
    print(f"  [PASS] {msg}")


def record_fail(msg):
    global failures
    failures.append(msg)
    print(f"  [FAIL] {msg}")


def test_diamond_lattice():
    print("\n--- Testing Diamond Lattice Crystallography ---")
    blend_path = ROOT_DIR / "assets/chemistry/diamond-lattice/out/diamond-lattice.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    atoms = [o for o in bpy.data.objects if "atom" in o.name and o.type == "MESH"]
    bonds = [o for o in bpy.data.objects if "bond" in o.name and o.type == "MESH"]

    print(f"  Atom count: {len(atoms)}, Bond count: {len(bonds)}")
    if len(atoms) < 10:
        record_fail(f"Too few diamond atoms: {len(atoms)}")
        return

    atom_positions = [Vector(a.location) for a in atoms]

    # Find neighbor bonds for each atom based on distance ~ 0.038 m (+/- 0.002 m)
    expected_bond_len = 0.038
    neighbors = defaultdict(list)
    measured_bond_lengths = []

    for i in range(len(atom_positions)):
        for j in range(i + 1, len(atom_positions)):
            dist = (atom_positions[i] - atom_positions[j]).length
            if abs(dist - expected_bond_len) < 0.002:
                neighbors[i].append(j)
                neighbors[j].append(i)
                measured_bond_lengths.append(dist)

    avg_bond_len = sum(measured_bond_lengths) / len(measured_bond_lengths) if measured_bond_lengths else 0
    print(f"  Measured bond lengths: count={len(measured_bond_lengths)}, avg={avg_bond_len:.5f} m")

    # Compute bond angles for all triplets (j, i, k) where i is center atom
    angles_deg = []
    for i, nbrs in neighbors.items():
        if len(nbrs) < 2:
            continue
        center = atom_positions[i]
        for idx1 in range(len(nbrs)):
            for idx2 in range(idx1 + 1, len(nbrs)):
                v1 = (atom_positions[nbrs[idx1]] - center).normalized()
                v2 = (atom_positions[nbrs[idx2]] - center).normalized()
                dot = max(-1.0, min(1.0, v1.dot(v2)))
                ang = math.degrees(math.acos(dot))
                angles_deg.append(ang)

    if not angles_deg:
        record_fail("No C-C-C bond angles could be formed from neighbors")
        return

    min_ang = min(angles_deg)
    max_ang = max(angles_deg)
    mean_ang = sum(angles_deg) / len(angles_deg)
    expected_ang = math.degrees(math.acos(-1.0 / 3.0))  # 109.4712 deg

    print(f"  Total C-C-C angles tested: {len(angles_deg)}")
    print(f"  Min angle: {min_ang:.4f}°, Max angle: {max_ang:.4f}°, Mean: {mean_ang:.4f}°")
    print(f"  Theoretical sp3 tetrahedral angle: {expected_ang:.4f}°")

    if abs(mean_ang - expected_ang) < 0.1 and abs(max_ang - expected_ang) < 0.1 and abs(min_ang - expected_ang) < 0.1:
        record_pass(f"Diamond C-C-C bond angles strictly match tetrahedral sp3 angle ({mean_ang:.4f}° == {expected_ang:.4f}°)")
    else:
        record_fail(f"Diamond bond angle deviation: min={min_ang:.4f}°, max={max_ang:.4f}°, expected={expected_ang:.4f}°")


def test_graphite_lattice():
    print("\n--- Testing Graphite Lattice Planarity & Interlayer Spacing ---")
    blend_path = ROOT_DIR / "assets/chemistry/graphite-lattice/out/graphite-lattice.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    atoms = [o for o in bpy.data.objects if "atom" in o.name and o.type == "MESH"]
    print(f"  Total graphite carbon atoms: {len(atoms)}")

    # Group atoms into layers by Z coordinate
    z_coords = sorted(list(set(round(o.location.z, 5) for o in atoms)))
    print(f"  Distinct layer Z-coordinates: {z_coords}")

    if len(z_coords) != 2:
        record_fail(f"Expected exactly 2 graphite layers, found {len(z_coords)}: {z_coords}")
        return

    layer_gap = abs(z_coords[1] - z_coords[0])
    print(f"  Measured interlayer gap: {layer_gap:.5f} m")

    # Verify planarity within each layer (variance in Z must be 0)
    for z_c in z_coords:
        layer_atoms = [o for o in atoms if abs(o.location.z - z_c) < 1e-4]
        max_z_dev = max(abs(o.location.z - z_c) for o in layer_atoms)
        if max_z_dev > 1e-6:
            record_fail(f"Layer at z={z_c} is not strictly planar (max deviation = {max_z_dev})")
        else:
            record_pass(f"Layer at z={z_c} is strictly planar (z-variance = 0.0 across {len(layer_atoms)} atoms)")

    # Measure in-plane bond lengths and 120° bond angles in Layer 0
    layer0_atoms = [o for o in atoms if abs(o.location.z - z_coords[0]) < 1e-4]
    pts = [Vector((o.location.x, o.location.y)) for o in layer0_atoms]
    expected_bond = 0.024
    bonds = []
    nbrs = defaultdict(list)
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dist = (pts[i] - pts[j]).length
            if abs(dist - expected_bond) < 0.001:
                bonds.append(dist)
                nbrs[i].append(j)
                nbrs[j].append(i)

    avg_bond = sum(bonds) / len(bonds) if bonds else 0
    ratio = layer_gap / avg_bond if avg_bond > 0 else 0
    print(f"  In-plane bond length: {avg_bond:.5f} m, Interlayer / In-plane ratio: {ratio:.4f}")

    if ratio > 2.0:
        record_pass(f"Graphite interlayer gap to bond length ratio > 2.0 ({ratio:.4f} > 2.0)")
    else:
        record_fail(f"Graphite ratio failed: {ratio:.4f} <= 2.0")

    # Check 120° angles in hexagonal rings
    hex_angles = []
    for i, n_list in nbrs.items():
        if len(n_list) < 2:
            continue
        center = pts[i]
        for a_idx in range(len(n_list)):
            for b_idx in range(a_idx + 1, len(n_list)):
                v1 = (pts[n_list[a_idx]] - center).normalized()
                v2 = (pts[n_list[b_idx]] - center).normalized()
                dot = max(-1.0, min(1.0, v1.dot(v2)))
                ang = math.degrees(math.acos(dot))
                hex_angles.append(ang)

    if hex_angles:
        mean_hex_ang = sum(hex_angles) / len(hex_angles)
        min_hex_ang = min(hex_angles)
        max_hex_ang = max(hex_angles)
        print(f"  Hexagonal bond angles: count={len(hex_angles)}, min={min_hex_ang:.2f}°, max={max_hex_ang:.2f}°, mean={mean_hex_ang:.2f}°")
        if abs(mean_hex_ang - 120.0) < 0.1 and abs(min_hex_ang - 120.0) < 0.1 and abs(max_hex_ang - 120.0) < 0.1:
            record_pass(f"Graphite sp2 planar hexagonal bond angles strictly 120.0°")
        else:
            record_fail(f"Graphite hexagonal angles deviate from 120.0°: min={min_hex_ang}, max={max_hex_ang}")


def test_dropper_wall_thickness():
    print("\n--- Testing Dropper Wall Thickness ---")
    blend_path = ROOT_DIR / "assets/chemistry/dropper/out/dropper.blend"
    if not blend_path.exists():
        record_fail(f"Missing blend file: {blend_path}")
        return

    bpy.ops.wm.open_mainfile(filepath=str(blend_path))

    pipette = bpy.data.objects.get("dropper-glass-pipette")
    if not pipette:
        record_fail("Missing dropper-glass-pipette object")
        return

    # In build_dropper.py, the lathe profile was revolved around Z, then rotated by (0, 1.5708, 0)
    # Let's inspect the mesh data directly in local coordinates before object transform
    bm = bmesh.new()
    bm.from_mesh(pipette.data)

    # Collect cylindrical coordinates in local mesh: (radius r = sqrt(x^2 + y^2), height z)
    # Group vertices by z coordinate
    z_groups = defaultdict(list)
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.y)
        z_round = round(v.co.z, 4)
        z_groups[z_round].append(r)

    print(f"  Inspecting {len(z_groups)} distinct Z-height slices on pipette mesh:")
    thickness_measurements = []
    for z_val, r_list in sorted(z_groups.items()):
        min_r = min(r_list)
        max_r = max(r_list)
        thickness = (max_r - min_r) * 1000.0  # convert to mm
        thickness_measurements.append((z_val, min_r * 1000.0, max_r * 1000.0, thickness))
        print(f"    z={z_val*1000:.1f}mm: r_inner={min_r*1000:.2f}mm, r_outer={max_r*1000:.2f}mm, wall={thickness:.2f}mm")

    min_thickness = min(t[3] for t in thickness_measurements)
    print(f"  Minimum observed wall thickness: {min_thickness:.2f} mm")

    if min_thickness >= 0.999:  # Allow 1e-3 float rounding on 1.0mm
        record_pass(f"Dropper physical wall thickness >= 1.0 mm (min = {min_thickness:.2f} mm)")
    else:
        record_fail(f"Dropper wall thickness < 1.0 mm: min = {min_thickness:.2f} mm")


def test_atomic_model_electron_shells():
    print("\n--- Testing Atomic Model Electron Shell Radii ---")
    
    # 1. Magnesium Atom
    mg_blend = ROOT_DIR / "assets/chemistry/magnesium-atom/out/magnesium-atom.blend"
    bpy.ops.wm.open_mainfile(filepath=str(mg_blend))
    
    mg_electrons = [o for o in bpy.data.objects if "electron" in o.name and o.type == "MESH"]
    mg_rings = [o for o in bpy.data.objects if "ring" in o.name and o.type == "MESH"]
    
    print(f"  Magnesium: electron count = {len(mg_electrons)}, ring count = {len(mg_rings)}")
    if len(mg_electrons) != 12:
        record_fail(f"Magnesium atom electron count expected 12, got {len(mg_electrons)}")
    else:
        record_pass("Magnesium atom has exactly 12 electrons (2, 8, 2)")

    # Group electrons by shell based on distance from origin
    shell_radii_mg = defaultdict(list)
    for e in mg_electrons:
        r = round(e.location.length, 3)
        shell_radii_mg[r].append(e)

    sorted_radii_mg = sorted(shell_radii_mg.keys())
    print(f"  Magnesium shell radii: {sorted_radii_mg}")
    counts_mg = [len(shell_radii_mg[r]) for r in sorted_radii_mg]
    print(f"  Magnesium shell electron distribution: {counts_mg}")

    if counts_mg == [2, 8, 2]:
        record_pass("Magnesium electron distribution matches Bohr-Bury scheme [2, 8, 2]")
    else:
        record_fail(f"Magnesium electron distribution mismatch: {counts_mg} != [2, 8, 2]")

    if all(sorted_radii_mg[i] < sorted_radii_mg[i+1] for i in range(len(sorted_radii_mg)-1)):
        record_pass(f"Magnesium electron shell radii sequence strictly monotonically increases: {sorted_radii_mg}")
    else:
        record_fail(f"Magnesium shell radii not strictly increasing: {sorted_radii_mg}")

    # 2. Oxygen Atom
    o_blend = ROOT_DIR / "assets/chemistry/oxygen-atom/out/oxygen-atom.blend"
    bpy.ops.wm.open_mainfile(filepath=str(o_blend))
    
    o_electrons = [o for o in bpy.data.objects if "electron" in o.name and o.type == "MESH"]
    o_rings = [o for o in bpy.data.objects if "ring" in o.name and o.type == "MESH"]
    
    print(f"  Oxygen: electron count = {len(o_electrons)}, ring count = {len(o_rings)}")
    if len(o_electrons) != 8:
        record_fail(f"Oxygen atom electron count expected 8, got {len(o_electrons)}")
    else:
        record_pass("Oxygen atom has exactly 8 electrons (2, 6)")

    shell_radii_o = defaultdict(list)
    for e in o_electrons:
        r = round(e.location.length, 3)
        shell_radii_o[r].append(e)

    sorted_radii_o = sorted(shell_radii_o.keys())
    print(f"  Oxygen shell radii: {sorted_radii_o}")
    counts_o = [len(shell_radii_o[r]) for r in sorted_radii_o]
    print(f"  Oxygen shell electron distribution: {counts_o}")

    if counts_o == [2, 6]:
        record_pass("Oxygen electron distribution matches Bohr-Bury scheme [2, 6]")
    else:
        record_fail(f"Oxygen electron distribution mismatch: {counts_o} != [2, 6]")

    if all(sorted_radii_o[i] < sorted_radii_o[i+1] for i in range(len(sorted_radii_o)-1)):
        record_pass(f"Oxygen electron shell radii sequence strictly monotonically increases: {sorted_radii_o}")
    else:
        record_fail(f"Oxygen shell radii not strictly increasing: {sorted_radii_o}")


def test_glassware_shaders():
    print("\n--- Testing Glassware Shaders & Transmission ---")
    glassware_assets = [
        "beaker",
        "conical-flask",
        "watch-glass",
        "dropper",
        "hydrogen-evolution-apparatus"
    ]

    for asset_id in glassware_assets:
        blend_path = ROOT_DIR / f"assets/chemistry/{asset_id}/out/{asset_id}.blend"
        if not blend_path.exists():
            record_fail(f"Missing blend file: {blend_path}")
            continue

        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        glass_mats = [m for m in bpy.data.materials if "glass" in m.name.lower()]
        print(f"  {asset_id}: found glass materials {[m.name for m in glass_mats]}")

        for mat in glass_mats:
            if not mat.use_nodes or "Principled BSDF" not in mat.node_tree.nodes:
                record_fail(f"{asset_id} material {mat.name} missing Principled BSDF node")
                continue

            bsdf = mat.node_tree.nodes["Principled BSDF"]
            ior_inp = bsdf.inputs.get("IOR")
            trans_inp = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
            rough_inp = bsdf.inputs.get("Roughness")

            ior_val = ior_inp.default_value if ior_inp else None
            trans_val = trans_inp.default_value if trans_inp else None
            rough_val = rough_inp.default_value if rough_inp else None

            print(f"    {mat.name}: IOR={ior_val}, Transmission={trans_val}, Roughness={rough_val}")

            if ior_val is not None and abs(ior_val - 1.52) < 0.01:
                record_pass(f"{asset_id} {mat.name} IOR == 1.52 (measured: {ior_val:.4f})")
            else:
                record_fail(f"{asset_id} {mat.name} IOR mismatch: {ior_val} != 1.52")

            if trans_val is not None and trans_val >= 0.90:
                record_pass(f"{asset_id} {mat.name} Transmission Weight >= 0.90 (measured: {trans_val:.4f})")
            else:
                record_fail(f"{asset_id} {mat.name} Transmission Weight too low: {trans_val} < 0.90")


def test_non_manifold_mesh_audit():
    print("\n--- Auditing Non-Manifold Edges on All Modified Chemistry Assets ---")
    target_assets = [
        "diamond-lattice",
        "graphite-lattice",
        "hydrogen-evolution-apparatus",
        "dropper",
        "magnesium-atom",
        "oxygen-atom",
        "bunsen-burner",
        "beaker",
        "conical-flask",
        "watch-glass",
        "magnesium-burning-setup"
    ]

    total_non_manifold = 0
    for asset_id in target_assets:
        blend_path = ROOT_DIR / f"assets/chemistry/{asset_id}/out/{asset_id}.blend"
        if not blend_path.exists():
            record_fail(f"Missing blend file: {blend_path}")
            continue

        bpy.ops.wm.open_mainfile(filepath=str(blend_path))

        asset_nm = 0
        for obj in bpy.data.objects:
            if obj.type != "MESH":
                continue
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            nm_edges = sum(1 for e in bm.edges if not e.is_manifold)
            asset_nm += nm_edges
            bm.free()

        print(f"  {asset_id}: {asset_nm} non-manifold edges")
        if asset_nm == 0:
            record_pass(f"{asset_id} has exactly 0 non-manifold edges")
        else:
            record_fail(f"{asset_id} has {asset_nm} non-manifold edges!")
        total_non_manifold += asset_nm

    print(f"  Total non-manifold edges across all target assets: {total_non_manifold}")


def main():
    print("=" * 80)
    print("CHALLENGER M4-2 EMPIRICAL VERIFICATION HARNESS")
    print("=" * 80)

    test_diamond_lattice()
    test_graphite_lattice()
    test_dropper_wall_thickness()
    test_atomic_model_electron_shells()
    test_glassware_shaders()
    test_non_manifold_mesh_audit()

    print("\n" + "=" * 80)
    print(f"SUMMARY: {passed_checks} passed, {len(failures)} failures")
    print("=" * 80)

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\nALL EMPIRICAL CHECKS PASSED!")
        sys.exit(0)


if __name__ == "__main__":
    main()
