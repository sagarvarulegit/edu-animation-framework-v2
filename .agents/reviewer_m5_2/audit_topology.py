import os, sys
import bpy, bmesh

physics_dir = "/home/sagarv/Projects/edu-animation-framework-v2/assets/physics"
results = {}
total_nm_all = 0

print("=== ACTUAL AUDIT OF PHYSICS ASSET TOPOLOGY ===")
for asset in sorted(os.listdir(physics_dir)):
    blend_path = os.path.join(physics_dir, asset, "out", f"{asset}.blend")
    if not os.path.exists(blend_path):
        print(f"[MISSING] {asset}: no blend file at {blend_path}")
        continue
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    total_nm = 0
    total_boundary = 0
    total_zero_area = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            nm = sum(1 for e in bm.edges if not e.is_manifold)
            boundary = sum(1 for e in bm.edges if e.is_boundary)
            zero_area = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
            total_nm += nm
            total_boundary += boundary
            total_zero_area += zero_area
            bm.free()
    total_nm_all += total_nm
    print(f"[{'PASS' if total_nm == 0 else 'FAIL'}] {asset}: {total_nm} NM edges ({total_boundary} boundary), {total_zero_area} zero-area faces")

print(f"\nTOTAL NM EDGES ACROSS ALL PHYSICS ASSETS: {total_nm_all}")
