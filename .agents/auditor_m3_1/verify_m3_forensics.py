import sys, os, hashlib
from pathlib import Path
import bpy, bmesh

ROOT = Path('/home/sagarv/Projects/edu-animation-framework-v2')
M3_IDS = [
    'nephron',
    'human-respiratory-system',
    'digestive-system',
    'dna-double-helix',
    'human-excretory-system',
    'stoma',
    'trophic-level-pyramid',
    'neuron',
    'reflex-arc'
]

print("=" * 80)
print("INDEPENDENT FORENSIC AUDITOR BMESH TOPOLOGY & INTEGRITY AUDIT")
print("=" * 80)

grand_total_objects = 0
grand_total_meshes = 0
grand_total_verts = 0
grand_total_faces = 0
grand_total_non_manifold = 0
grand_total_boundary = 0
grand_total_wire = 0
grand_total_zero_area = 0

all_passed = True

for aid in M3_IDS:
    blend_path = ROOT / 'assets' / 'biology' / aid / 'out' / f'{aid}.blend'
    glb_path = ROOT / 'assets' / 'biology' / aid / 'out' / f'{aid}.glb'
    web_glb_path = ROOT / 'apps' / 'interactive-viewer' / 'public' / 'assets' / f'{aid}.glb'
    png_path = ROOT / 'assets' / 'biology' / aid / 'out' / 'preview.png'

    # 1. Check file existence
    if not blend_path.exists():
        print(f"[FAIL] Missing {blend_path}")
        all_passed = False
        continue
    if not glb_path.exists():
        print(f"[FAIL] Missing {glb_path}")
        all_passed = False
        continue
    if not web_glb_path.exists():
        print(f"[FAIL] Missing web synced {web_glb_path}")
        all_passed = False
        continue
    if not png_path.exists():
        print(f"[FAIL] Missing {png_path}")
        all_passed = False
        continue

    # 2. Check GLB sync parity
    src_bytes = glb_path.read_bytes()
    web_bytes = web_glb_path.read_bytes()
    src_hash = hashlib.sha256(src_bytes).hexdigest()
    web_hash = hashlib.sha256(web_bytes).hexdigest()
    if src_hash != web_hash:
        print(f"[FAIL] Hash mismatch for {aid}.glb: src={src_hash} web={web_hash}")
        all_passed = False
    if len(src_bytes) < 12 or src_bytes[:4] != b'glTF':
        print(f"[FAIL] Invalid GLB magic in {glb_path}")
        all_passed = False

    # 3. Open blend file and audit bmesh
    bpy.ops.wm.open_mainfile(filepath=str(blend_path))
    mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
    
    asset_verts = 0
    asset_faces = 0
    asset_nm = 0
    asset_boundary = 0
    asset_wire = 0
    asset_zero_area = 0

    for obj in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        nm_edges = sum(1 for e in bm.edges if not e.is_manifold)
        b_edges = sum(1 for e in bm.edges if e.is_boundary)
        w_edges = sum(1 for e in bm.edges if e.is_wire)
        za_faces = sum(1 for f in bm.faces if f.calc_area() <= 1e-12)

        asset_verts += len(bm.verts)
        asset_faces += len(bm.faces)
        asset_nm += nm_edges
        asset_boundary += b_edges
        asset_wire += w_edges
        asset_zero_area += za_faces

        bm.free()

    grand_total_objects += len(bpy.data.objects)
    grand_total_meshes += len(mesh_objs)
    grand_total_verts += asset_verts
    grand_total_faces += asset_faces
    grand_total_non_manifold += asset_nm
    grand_total_boundary += asset_boundary
    grand_total_wire += asset_wire
    grand_total_zero_area += asset_zero_area

    status = "CLEAN" if (asset_nm == 0 and asset_zero_area == 0) else "VIOLATION"
    print(f"[{status}] {aid:28} | Meshes: {len(mesh_objs):3} | Verts: {asset_verts:6} | Faces: {asset_faces:6} | NM-Edges: {asset_nm:2} | Boundary: {asset_boundary:2} | ZeroArea: {asset_zero_area:2} | GLB-Sync: OK ({len(src_bytes)}B)")

print("=" * 80)
print(f"TOTAL AUDITED ASSETS:         {len(M3_IDS)}")
print(f"TOTAL SCENE OBJECTS:          {grand_total_objects}")
print(f"TOTAL MESH OBJECTS:           {grand_total_meshes}")
print(f"TOTAL VERTICES:               {grand_total_verts}")
print(f"TOTAL FACES:                  {grand_total_faces}")
print(f"GRAND TOTAL NON-MANIFOLD:     {grand_total_non_manifold}")
print(f"GRAND TOTAL BOUNDARY EDGES:   {grand_total_boundary}")
print(f"GRAND TOTAL WIRE EDGES:       {grand_total_wire}")
print(f"GRAND TOTAL ZERO-AREA FACES:  {grand_total_zero_area}")
print("=" * 80)

if grand_total_non_manifold == 0 and grand_total_zero_area == 0 and all_passed:
    print("[FINAL AUDIT VERDICT]: CLEAN (Zero non-manifold edges, zero degenerate faces, perfect web sync)")
    sys.exit(0)
else:
    print("[FINAL AUDIT VERDICT]: INTEGRITY VIOLATION DETECTED")
    sys.exit(1)
