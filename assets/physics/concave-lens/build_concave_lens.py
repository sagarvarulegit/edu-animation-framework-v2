import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh

ASSET_ID = "concave-lens"


def build_lens():
    glass = kit.add_material("concave-lens-glass", (0.88, 0.92, 0.96), metallic=0.0, roughness=0.03)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.92
    bsdf.inputs["IOR"].default_value = 1.52

    edge_mat = kit.add_material("concave-lens-edge", (0.70, 0.70, 0.72), metallic=0.8, roughness=0.3)

    radius = 0.04
    thickness = 0.022
    segments = 48

    # Biconcave lens: thin at center, thick at edges
    bm = bmesh.new()
    for i in range(segments + 1):
        angle = math.pi * i / segments - math.pi / 2
        y = radius * math.sin(angle)
        edge_dist = abs(math.cos(angle))
        x = thickness / 2 * (0.2 + edge_dist * 0.8)  # Concave: thin center
        bm.verts.new((-x, y, 0))
        bm.verts.new((x, y, 0))

    verts = bm.verts[:]
    for i in range(segments):
        bm.faces.new([verts[i * 2], verts[i * 2 + 1],
                       verts[(i + 1) * 2 + 1], verts[(i + 1) * 2]])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(glass)

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
