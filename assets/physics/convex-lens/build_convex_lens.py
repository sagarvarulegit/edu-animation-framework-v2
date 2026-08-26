import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "convex-lens"


def build_lens():
    # Clear glass with slight blue tint (like real optical glass)
    glass = kit.add_material("lens-glass", (0.88, 0.92, 0.96),
                             metallic=0.0, roughness=0.03)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.92
    bsdf.inputs["IOR"].default_value = 1.52

    # Edge ring (visible rim)
    edge_mat = kit.add_material("lens-edge", (0.70, 0.70, 0.72),
                                metallic=0.8, roughness=0.3)

    radius = 0.04
    thickness = 0.022
    segments = 48

    # Biconvex lens from bmesh
    bm = bmesh.new()
    for i in range(segments + 1):
        angle = math.pi * i / segments - math.pi / 2
        y = radius * math.sin(angle)
        # Biconvex: thickest at center, thin at edges
        edge_dist = abs(math.cos(angle))
        x = thickness / 2 * (1 - edge_dist * 0.85)
        bmesh.ops.create_vert(bm, co=(-x, y, 0))
        bmesh.ops.create_vert(bm, co=(x, y, 0))

    verts = bm.verts[:]
    for i in range(segments):
        v0 = verts[i * 2]
        v1 = verts[i * 2 + 1]
        v2 = verts[(i + 1) * 2]
        v3 = verts[(i + 1) * 2 + 1]
        bm.faces.new([v0, v1, v3, v2])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(glass)

    # Edge ring
    edge = kit.primitive_object(f"{ASSET_ID}-edge", "cylinder", edge_mat,
                                 size=(0.082, 0.082, 0.003),
                                 location=(0.0, 0.0, 0.0))

    return [obj, edge]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_lens()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
