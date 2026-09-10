import bpy
import bmesh
import mathutils

models = [
    ("Heart", "assets/biology/human-heart/out/human-heart.blend"),
    ("Eye", "assets/biology/human-eye/out/human-eye.blend"),
    ("Brain", "assets/biology/brain/out/brain.blend")
]

for name, path in models:
    print(f"\n==================== AUDITING {name} ({path}) ====================")
    bpy.ops.wm.open_mainfile(filepath=path)
    total_objs = len(bpy.data.objects)
    mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
    print(f"Total Objects: {total_objs}, Mesh Objects: {len(mesh_objs)}")
    
    total_verts = 0
    total_faces = 0
    non_manifold_edges_total = 0
    loose_verts_total = 0
    
    for obj in mesh_objs:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
        loose_verts = sum(1 for v in bm.verts if len(v.link_edges) == 0)
        total_verts += len(bm.verts)
        total_faces += len(bm.faces)
        non_manifold_edges_total += non_manifold
        loose_verts_total += loose_verts
        if non_manifold > 0 or loose_verts > 0:
            print(f"  [WARNING] Object {obj.name}: non_manifold={non_manifold}, loose_verts={loose_verts}")
        bm.free()
        
    print(f"Total Vertices: {total_verts}, Total Faces: {total_faces}")
    print(f"Total Non-Manifold Edges: {non_manifold_edges_total}")
    print(f"Total Loose Vertices: {loose_verts_total}")
    
    print("\nMaterials:")
    for mat in bpy.data.materials:
        nodes = mat.node_tree.nodes if mat.node_tree else []
        bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf:
            has_sss = False
            for input_name in ["Subsurface Weight", "Subsurface"]:
                if input_name in bsdf.inputs and bsdf.inputs[input_name].default_value > 0:
                    has_sss = True
            has_trans = False
            for input_name in ["Transmission Weight", "Transmission"]:
                if input_name in bsdf.inputs and bsdf.inputs[input_name].default_value > 0:
                    has_trans = True
            print(f"  Mat: {mat.name} | BSDF: present | SSS: {has_sss} | Transmission: {has_trans}")
        else:
            print(f"  Mat: {mat.name} | BSDF: None")

