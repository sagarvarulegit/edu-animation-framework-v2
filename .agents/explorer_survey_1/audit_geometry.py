"""
audit_geometry.py — Audit 3D geometry of all biology assets.
Runs headlessly in Blender to evaluate mesh statistics, topology, manifoldness, and materials.
"""

import sys
import json
from pathlib import Path
import bpy
import bmesh

BIOLOGY_DIR = Path("/home/sagarv/Projects/edu-animation-framework-v2/assets/biology")

results = {}

for asset_dir in sorted(BIOLOGY_DIR.iterdir()):
    if not asset_dir.is_dir():
        continue
    
    asset_id = asset_dir.name
    blend_path = asset_dir / "out" / f"{asset_id}.blend"
    glb_path = asset_dir / "out" / f"{asset_id}.glb"
    
    if not blend_path.exists():
        results[asset_id] = {"error": f"Blend file not found: {blend_path}"}
        continue
        
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    
    obj_stats = []
    total_verts = 0
    total_faces = 0
    non_manifold_count = 0
    materials_used = set()
    
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue
            
        mesh = obj.data
        v_count = len(mesh.vertices)
        f_count = len(mesh.polygons)
        total_verts += v_count
        total_faces += f_count
        
        # Check manifoldness via bmesh
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        nm_edges = sum(1 for e in bm.edges if not e.is_manifold)
        nm_verts = sum(1 for v in bm.verts if not v.is_manifold)
        non_manifold_count += (nm_edges + nm_verts)
        
        # Check materials
        obj_mats = [m.name for m in obj.data.materials if m]
        materials_used.update(obj_mats)
        
        dims = [round(d, 4) for d in obj.dimensions]
        
        obj_stats.append({
            "name": obj.name,
            "verts": v_count,
            "faces": f_count,
            "dimensions": dims,
            "non_manifold_edges": nm_edges,
            "non_manifold_verts": nm_verts,
            "materials": obj_mats
        })
        bm.free()
        
    results[asset_id] = {
        "total_objects": len(obj_stats),
        "total_verts": total_verts,
        "total_faces": total_faces,
        "total_non_manifold": non_manifold_count,
        "materials": sorted(list(materials_used)),
        "glb_exists": glb_path.exists(),
        "glb_size_bytes": glb_path.stat().st_size if glb_path.exists() else 0,
        "objects": obj_stats
    }

output_path = Path("/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/geometry_audit.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"[OK] Audited {len(results)} biology assets. Saved to {output_path}")
