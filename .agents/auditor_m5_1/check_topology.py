import os, sys, bpy, bmesh

physics_dir = "assets/physics"
total_assets = 0
failed_assets = []

print("=== REAL EMPIRICAL TOPOLOGY AUDIT ===")
for asset in sorted(os.listdir(physics_dir)):
    blend_path = os.path.join(physics_dir, asset, "out", f"{asset}.blend")
    if not os.path.exists(blend_path):
        print(f"MISSING: {asset} has no blend file at {blend_path}")
        failed_assets.append((asset, "missing blend"))
        continue
    bpy.ops.wm.open_mainfile(filepath=blend_path)
    total_nm = 0
    total_boundary = 0
    total_zero_area = 0
    mesh_count = 0
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            mesh_count += 1
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            nm = sum(1 for e in bm.edges if not e.is_manifold)
            boundary = sum(1 for e in bm.edges if e.is_boundary)
            za = sum(1 for f in bm.faces if f.calc_area() < 1e-7)
            total_nm += nm
            total_boundary += boundary
            total_zero_area += za
            bm.free()
    total_assets += 1
    status = "PASS" if total_nm == 0 else "FAIL"
    print(f"[{status}] {asset}: {total_nm} NM edges ({total_boundary} boundary), {total_zero_area} zero-area faces in {mesh_count} meshes")
    if total_nm > 0:
        failed_assets.append((asset, f"{total_nm} NM edges"))

print(f"\nTotal audited: {total_assets}")
print(f"Failed count: {len(failed_assets)}")
if failed_assets:
    print(f"FAILED ASSETS: {failed_assets}")
    sys.exit(1)
else:
    print("ALL AUDITED ASSETS ARE 100% MANIFOLD!")
    sys.exit(0)
