import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "glass-prism"


def build_prism():
    # Clear glass with very slight blue tint
    glass = kit.add_material("prism-glass", (0.88, 0.92, 0.96),
                             metallic=0.0, roughness=0.02)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.93
    bsdf.inputs["IOR"].default_value = 1.52

    side = 0.065
    depth = 0.09
    h = side * math.sqrt(3) / 2

    # Equilateral triangle cross-section
    bm = bmesh.new()
    # Front face vertices
    v0 = bmesh.ops.create_vert(bm, co=(-side/2, 0, -h/3))["vert"]
    v1 = bmesh.ops.create_vert(bm, co=(side/2, 0, -h/3))["vert"]
    v2 = bmesh.ops.create_vert(bm, co=(0, 0, 2*h/3))["vert"]
    # Back face vertices
    v3 = bmesh.ops.create_vert(bm, co=(-side/2, depth, -h/3))["vert"]
    v4 = bmesh.ops.create_vert(bm, co=(side/2, depth, -h/3))["vert"]
    v5 = bmesh.ops.create_vert(bm, co=(0, depth, 2*h/3))["vert"]

    # 5 faces
    bm.faces.new([v0, v1, v2])
    bm.faces.new([v5, v4, v3])
    bm.faces.new([v0, v3, v4, v1])
    bm.faces.new([v0, v2, v5, v3])
    bm.faces.new([v1, v4, v5, v2])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(glass)

    return [obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_prism()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
