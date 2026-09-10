"""
test_m5_challenger_topology.py — Challenger M5-1 Empirical Mesh Topology Verification Suite
Independent verification of mesh topology across all 22 Physics assets in Blender:
1. Verify presence and non-emptiness of out/<asset>.blend, out/<asset>.glb, out/preview.png for all 22 assets.
2. Load each .blend file and inspect every MESH object using bmesh:
   - Non-manifold edge count: MUST BE STRICTLY 0 across all meshes
   - Boundary edge count: MUST BE STRICTLY 0 (watertight solid meshes)
   - Wire edge count: MUST BE STRICTLY 0
   - Degenerate face count (f.calc_area() <= 1e-12): MUST BE STRICTLY 0
   - Micro-feature face count (f.calc_area() <= 1e-7): Documented (fine physical details in meter units)
   - Object transforms (scale and rotation) documented per asset
3. Document empirical counts (vertices, edges, faces, non-manifold edges) per asset and in aggregate.
"""

import os
import sys
import json
from pathlib import Path
from collections import defaultdict

import bpy
import bmesh
from mathutils import Vector

ROOT_DIR = Path(__file__).resolve().parents[2]
PHYSICS_DIR = ROOT_DIR / "assets/physics"

EXPECTED_ASSETS = [
    "ammeter",
    "bar-magnet",
    "battery",
    "bulb",
    "concave-lens",
    "concave-mirror",
    "connecting-wire",
    "convex-lens",
    "convex-mirror",
    "electric-motor",
    "full-circuit",
    "galvanometer",
    "glass-prism",
    "glass-prism-refraction",
    "glass-slab",
    "optical-bench",
    "plane-mirror",
    "resistor",
    "rheostat",
    "solenoid",
    "switch",
    "voltmeter",
]

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


def main():
    print("=" * 80)
    print("CHALLENGER M5-1: EMPIRICAL MESH TOPOLOGY AUDIT (ALL 22 PHYSICS ASSETS)")
    print("=" * 80)

    # 1. Verify directory listing matches expected 22 assets
    found_assets = sorted([d.name for d in PHYSICS_DIR.iterdir() if d.is_dir()])
    print(f"Discovered {len(found_assets)} physics asset directories:")
    for a in found_assets:
        print(f"  - {a}")

    if found_assets != EXPECTED_ASSETS:
        record_fail(f"Asset directory mismatch: expected {EXPECTED_ASSETS}, found {found_assets}")
    else:
        record_pass(f"All {len(EXPECTED_ASSETS)} physics asset directories match expected catalog")

    print("\n--- Auditing Mesh Topology per Asset in Blender ---")
    audit_results = {}
    total_verts_all = 0
    total_edges_all = 0
    total_faces_all = 0
    total_nm_edges_all = 0
    total_boundary_edges_all = 0
    total_wire_edges_all = 0
    total_degenerate_faces_all = 0
    total_micro_faces_all = 0
    total_mesh_objects_all = 0

    table_rows = []

    for asset_name in EXPECTED_ASSETS:
        asset_dir = PHYSICS_DIR / asset_name
        out_dir = asset_dir / "out"
        blend_file = out_dir / f"{asset_name}.blend"
        glb_file = out_dir / f"{asset_name}.glb"
        preview_file = out_dir / "preview.png"

        # Check required output files exist and are non-empty
        missing_files = []
        for f, name in [(blend_file, "blend"), (glb_file, "glb"), (preview_file, "preview.png")]:
            if not f.exists() or f.stat().st_size == 0:
                missing_files.append(name)

        if missing_files:
            record_fail(f"{asset_name}: Missing or empty output files: {missing_files}")
            continue
        else:
            record_pass(f"{asset_name}: Output files exist (blend={blend_file.stat().st_size}B, glb={glb_file.stat().st_size}B, png={preview_file.stat().st_size}B)")

        # Open .blend file
        bpy.ops.wm.open_mainfile(filepath=str(blend_file))

        mesh_objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
        if not mesh_objs:
            record_fail(f"{asset_name}: No MESH objects found in {blend_file.name}")
            continue

        asset_stats = {
            "asset": asset_name,
            "mesh_objects_count": len(mesh_objs),
            "vertices": 0,
            "edges": 0,
            "faces": 0,
            "non_manifold_edges": 0,
            "boundary_edges": 0,
            "wire_edges": 0,
            "degenerate_faces": 0,
            "micro_faces": 0,
            "unapplied_transforms": [],
            "objects_detail": []
        }

        for obj in mesh_objs:
            bm = bmesh.new()
            bm.from_mesh(obj.data)

            v_count = len(bm.verts)
            e_count = len(bm.edges)
            f_count = len(bm.faces)

            nm_edges = sum(1 for e in bm.edges if not e.is_manifold)
            boundary_edges = sum(1 for e in bm.edges if e.is_boundary)
            wire_edges = sum(1 for e in bm.edges if e.is_wire)
            degenerate_faces = sum(1 for f in bm.faces if f.calc_area() <= 1e-12)
            micro_faces = sum(1 for f in bm.faces if f.calc_area() <= 1e-7)

            # Check transforms
            scale_applied = all(abs(s - 1.0) < 1e-4 for s in obj.scale)
            rot_applied = all(abs(r) < 1e-4 for r in obj.rotation_euler)
            if not scale_applied or not rot_applied:
                asset_stats["unapplied_transforms"].append({
                    "object": obj.name,
                    "scale": [round(s, 4) for s in obj.scale],
                    "rotation": [round(r, 4) for r in obj.rotation_euler]
                })

            asset_stats["vertices"] += v_count
            asset_stats["edges"] += e_count
            asset_stats["faces"] += f_count
            asset_stats["non_manifold_edges"] += nm_edges
            asset_stats["boundary_edges"] += boundary_edges
            asset_stats["wire_edges"] += wire_edges
            asset_stats["degenerate_faces"] += degenerate_faces
            asset_stats["micro_faces"] += micro_faces

            asset_stats["objects_detail"].append({
                "name": obj.name,
                "verts": v_count,
                "edges": e_count,
                "faces": f_count,
                "nm_edges": nm_edges,
                "boundary_edges": boundary_edges,
                "wire_edges": wire_edges,
                "degenerate_faces": degenerate_faces,
                "micro_faces": micro_faces,
                "scale": [round(s, 4) for s in obj.scale],
                "rot": [round(r, 4) for r in obj.rotation_euler]
            })

            bm.free()

        total_verts_all += asset_stats["vertices"]
        total_edges_all += asset_stats["edges"]
        total_faces_all += asset_stats["faces"]
        total_nm_edges_all += asset_stats["non_manifold_edges"]
        total_boundary_edges_all += asset_stats["boundary_edges"]
        total_wire_edges_all += asset_stats["wire_edges"]
        total_degenerate_faces_all += asset_stats["degenerate_faces"]
        total_micro_faces_all += asset_stats["micro_faces"]
        total_mesh_objects_all += asset_stats["mesh_objects_count"]

        audit_results[asset_name] = asset_stats

        if asset_stats["non_manifold_edges"] == 0:
            record_pass(f"{asset_name}: 0 non-manifold edges across {len(mesh_objs)} objects (V={asset_stats['vertices']}, E={asset_stats['edges']}, F={asset_stats['faces']})")
        else:
            record_fail(f"{asset_name}: FOUND {asset_stats['non_manifold_edges']} NON-MANIFOLD EDGES! (Boundary={asset_stats['boundary_edges']}, Wire={asset_stats['wire_edges']})")

        if asset_stats["degenerate_faces"] == 0:
            record_pass(f"{asset_name}: 0 degenerate faces (<= 1e-12)")
        else:
            record_fail(f"{asset_name}: FOUND {asset_stats['degenerate_faces']} DEGENERATE FACES!")

        status_str = "PASS" if asset_stats["non_manifold_edges"] == 0 and asset_stats["degenerate_faces"] == 0 else "FAIL"
        table_rows.append((
            asset_name,
            asset_stats["mesh_objects_count"],
            asset_stats["vertices"],
            asset_stats["edges"],
            asset_stats["faces"],
            asset_stats["non_manifold_edges"],
            asset_stats["boundary_edges"],
            asset_stats["degenerate_faces"],
            asset_stats["micro_faces"],
            len(asset_stats["unapplied_transforms"]),
            status_str
        ))

    print("\n" + "=" * 120)
    print(f"{'Asset ID':<24} | {'Objs':<5} | {'Verts':<7} | {'Edges':<8} | {'Faces':<7} | {'NM':<4} | {'Bound':<6} | {'Degen':<6} | {'MicroF':<7} | {'UnappT':<6} | {'Status':<6}")
    print("-" * 120)
    for row in table_rows:
        print(f"{row[0]:<24} | {row[1]:<5} | {row[2]:<7} | {row[3]:<8} | {row[4]:<7} | {row[5]:<4} | {row[6]:<6} | {row[7]:<6} | {row[8]:<7} | {row[9]:<6} | {row[10]:<6}")
    print("=" * 120)
    print(f"{'TOTALS':<24} | {total_mesh_objects_all:<5} | {total_verts_all:<7} | {total_edges_all:<8} | {total_faces_all:<7} | {total_nm_edges_all:<4} | {total_boundary_edges_all:<6} | {total_degenerate_faces_all:<6} | {total_micro_faces_all:<7} | {'--':<6} | {'PASS' if total_nm_edges_all == 0 and total_degenerate_faces_all == 0 else 'FAIL':<6}")
    print("=" * 120)

    # Save empirical results to JSON
    json_out_path = ROOT_DIR / "tests/empirical/physics_topology_audit.json"
    with open(json_out_path, "w") as fp:
        json.dump({
            "summary": {
                "total_assets": len(EXPECTED_ASSETS),
                "total_mesh_objects": total_mesh_objects_all,
                "total_vertices": total_verts_all,
                "total_edges": total_edges_all,
                "total_faces": total_faces_all,
                "total_non_manifold_edges": total_nm_edges_all,
                "total_boundary_edges": total_boundary_edges_all,
                "total_wire_edges": total_wire_edges_all,
                "total_degenerate_faces": total_degenerate_faces_all,
                "total_micro_faces": total_micro_faces_all,
            },
            "per_asset": audit_results
        }, fp, indent=2)
    print(f"\nWrote machine-readable results to {json_out_path}")

    print("\n" + "=" * 80)
    print(f"AUDIT COMPLETE: {passed_checks} checks passed, {len(failures)} failures.")
    print("=" * 80)

    if failures:
        print("\nSUMMARY OF FAILURES:")
        for f in failures:
            print(f"  ❌ {f}")
        sys.exit(1)
    else:
        print("\nALL TOPOLOGY AND INTEGRITY CRITERIA EMPIRICALLY SATISFIED (0 NON-MANIFOLD EDGES).")
        sys.exit(0)


if __name__ == "__main__":
    main()
