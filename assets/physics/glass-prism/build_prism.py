"""
build_prism.py — High-Fidelity Optical Glass Triangular Prism
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "glass-prism"


def build_prism():
    # 1. Physically accurate Crown Glass (IOR 1.52) with slight blue-cyan optical edge tint
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.88, 0.94, 0.98), ior=1.52, roughness=0.005)

    # 2. Equilateral Prism Dimensions (60mm equilateral side, 80mm length)
    side = 0.060
    length = 0.080
    h = side * math.sqrt(3) / 2 # Height of equilateral triangle
    
    # 3. Create Prism with Sharp Optical Chamfers using bmesh
    bm = bmesh.new()
    
    y_front = -length / 2
    y_back = length / 2
    z_center_offset = h / 3
    
    # Vertex coordinates (triangular cross-section along Y axis)
    v0 = bm.verts.new((-side / 2, y_front, -z_center_offset))
    v1 = bm.verts.new((side / 2, y_front, -z_center_offset))
    v2 = bm.verts.new((0.0, y_front, 2 * z_center_offset))
    
    v3 = bm.verts.new((-side / 2, y_back, -z_center_offset))
    v4 = bm.verts.new((side / 2, y_back, -z_center_offset))
    v5 = bm.verts.new((0.0, y_back, 2 * z_center_offset))
    
    # Build 5 primary optical faces
    bm.faces.new([v0, v1, v2])
    bm.faces.new([v5, v4, v3])
    bm.faces.new([v0, v3, v4, v1])
    bm.faces.new([v0, v2, v5, v3])
    bm.faces.new([v1, v4, v5, v2])
    
    # Recalculate face normals for flat polished optical facet reflections
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    
    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    
    # Keep flat shading on optical planar faces so prism facets reflect cleanly
    for poly in mesh.polygons:
        poly.use_smooth = False
        
    obj = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(glass_mat)
    
    # Standard laboratory bench orientation: standing upright on triangular base
    obj.location = (0.0, 0.0, z_center_offset)
    obj.rotation_euler = (0.0, 0.0, 0.45)

    return [obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_prism()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
