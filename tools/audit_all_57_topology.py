"""
tools/audit_all_57_topology.py
Comprehensive BMesh Topology and Production Verification across all 57 assets in the repository.
Inspects:
- .blend file integrity, mesh count, vertex count, edge count, face count
- Non-manifold edges (is_manifold == False)
- Boundary edges (is_boundary == True)
- Degenerate zero-area faces (calc_area() <= 1e-9)
- .glb presence, size, SHA-256
- preview.png presence, size
- Web parity with apps/interactive-viewer/public/assets/*.glb
"""

import os
import sys
import json
import hashlib
from pathlib import Path
import bpy
import bmesh

ROOT_DIR = Path("/home/sagarv/Projects/edu-animation-framework-v2")
ASSETS_DIR = ROOT_DIR / "assets"
WEB_ASSETS_DIR = ROOT_DIR / "apps/interactive-viewer/public/assets"

CATEGORIES = ["biology", "chemistry", "physics"]

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 110)
    print("COMPREHENSIVE 57-ASSET BMESH TOPOLOGY & PRODUCTION DELIVERY AUDIT")
    print("=" * 110)

    assets = []
    for cat in CATEGORIES:
        cat_dir = ASSETS_DIR / cat
        for item in sorted(os.listdir(cat_dir)):
            item_path = cat_dir / item
            if item_path.is_dir() and (item_path / "asset.json").exists():
                assets.append((cat, item, item_path))

    print(f"Total assets discovered: {len(assets)}")
    assert len(assets) == 57, f"Expected 57 assets, found {len(assets)}"

    results = []
    total_mesh_objs = 0
    total_verts = 0
    total_edges = 0
    total_faces = 0
    total_nm_edges = 0
    total_boundary_edges = 0
    total_degen_faces = 0
    parity_mismatches = 0

    header_fmt = "{:<4} {:<12} {:<32} {:<6} {:<8} {:<8} {:<8} {:<5} {:<6} {:<7} {:<8} {:<6}"
    row_fmt    = "{:<4} {:<12} {:<32} {:<6} {:<8} {:<8} {:<8} {:<5} {:<6} {:<7} {:<8} {:<6}"
    
    print("-" * 115)
    print(header_fmt.format(
        "#", "Category", "Asset ID", "Objs", "Verts", "Edges", "Faces", "NM", "Bound", "Degen", "GLB Size", "Parity"
    ))
    print("-" * 115)

    for idx, (cat, asset_id, asset_dir) in enumerate(assets, 1):
        out_dir = asset_dir / "out"
        blend_file = out_dir / f"{asset_id}.blend"
        glb_file = out_dir / f"{asset_id}.glb"
        png_file = out_dir / "preview.png"
        web_glb_file = WEB_ASSETS_DIR / f"{asset_id}.glb"

        # Check existence
        blend_exists = blend_file.exists() and blend_file.stat().st_size > 0
        glb_exists = glb_file.exists() and glb_file.stat().st_size > 0
        png_exists = png_file.exists() and png_file.stat().st_size > 0

        glb_size = glb_file.stat().st_size if glb_exists else 0
        glb_hash = sha256_file(glb_file) if glb_exists else ""

        parity = False
        if glb_exists and web_glb_file.exists():
            web_hash = sha256_file(web_glb_file)
            parity = (glb_hash == web_hash and glb_size == web_glb_file.stat().st_size)
        if not parity:
            parity_mismatches += 1

        # Topology audit via Blender
        objs_count = 0
        verts_count = 0
        edges_count = 0
        faces_count = 0
        nm_count = 0
        bound_count = 0
        degen_count = 0

        if blend_exists:
            bpy.ops.wm.open_mainfile(filepath=str(blend_file))
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    objs_count += 1
                    bm = bmesh.new()
                    bm.from_mesh(obj.data)
                    verts_count += len(bm.verts)
                    edges_count += len(bm.edges)
                    faces_count += len(bm.faces)
                    nm = sum(1 for e in bm.edges if not e.is_manifold)
                    bound = sum(1 for e in bm.edges if e.is_boundary)
                    degen = sum(1 for f in bm.faces if f.calc_area() <= 1e-9)
                    nm_count += nm
                    bound_count += bound
                    degen_count += degen
                    bm.free()

        total_mesh_objs += objs_count
        total_verts += verts_count
        total_edges += edges_count
        total_faces += faces_count
        total_nm_edges += nm_count
        total_boundary_edges += bound_count
        total_degen_faces += degen_count

        parity_str = "MATCH" if parity else "FAIL"
        print(row_fmt.format(
            idx, cat, asset_id, objs_count, verts_count, edges_count, faces_count,
            nm_count, bound_count, degen_count, glb_size, parity_str
        ))

        results.append({
            "index": idx,
            "category": cat,
            "asset_id": asset_id,
            "blend_exists": blend_exists,
            "blend_size": blend_file.stat().st_size if blend_exists else 0,
            "glb_exists": glb_exists,
            "glb_size": glb_size,
            "glb_sha256": glb_hash,
            "png_exists": png_exists,
            "png_size": png_file.stat().st_size if png_exists else 0,
            "web_parity": parity,
            "mesh_objects": objs_count,
            "vertices": verts_count,
            "edges": edges_count,
            "faces": faces_count,
            "non_manifold_edges": nm_count,
            "boundary_edges": bound_count,
            "degenerate_faces": degen_count
        })

    print("-" * 115)
    print(f"TOTALS: 57 Assets | {total_mesh_objs} Meshes | {total_verts} Verts | {total_edges} Edges | {total_faces} Faces")
    print(f"Non-Manifold Edges: {total_nm_edges} | Boundary Edges: {total_boundary_edges} | Degenerate Faces: {total_degen_faces}")
    print(f"Web Parity Mismatches: {parity_mismatches}")
    print("=" * 115)

    with open(ROOT_DIR / ".agents/worker_m6/topology_audit_results.json", "w") as f:
        json.dump({
            "total_assets": len(results),
            "total_mesh_objects": total_mesh_objs,
            "total_vertices": total_verts,
            "total_edges": total_edges,
            "total_faces": total_faces,
            "total_non_manifold_edges": total_nm_edges,
            "total_boundary_edges": total_boundary_edges,
            "total_degenerate_faces": total_degen_faces,
            "parity_mismatches": parity_mismatches,
            "assets": results
        }, f, indent=2)

    if total_nm_edges > 0 or total_degen_faces > 0 or parity_mismatches > 0:
        print("\n[FAIL] Audit failed: Non-manifold edges, degenerate faces, or parity mismatches found.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] 100% AUDIT PASS: Strictly 0 Non-Manifold Edges, 0 Degenerate Faces, and 100% Web Parity!")

if __name__ == "__main__":
    main()
