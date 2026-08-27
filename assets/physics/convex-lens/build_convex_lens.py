import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "convex-lens"


def build_lens():
    glass = kit.add_material("convex-lens-glass", (0.88, 0.92, 0.96), metallic=0.0, roughness=0.03)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.92
    bsdf.inputs["IOR"].default_value = 1.52

    edge_mat = kit.add_material("convex-lens-edge", (0.70, 0.70, 0.72), metallic=0.8, roughness=0.3)

    # Biconvex lens: thick at center, thin at edges — use UV sphere approach
    # Create a lens by intersecting two spheres
    radius = 0.04  # lens radius
    thickness = 0.012  # max thickness at center
    segments = 48

    # Build lens profile and revolve
    bm = bmesh.new()
    for i in range(segments + 1):
        angle = math.pi * i / segments - math.pi / 2
        y = radius * math.sin(angle)
        edge_dist = abs(math.cos(angle))
        x = thickness / 2 * (0.1 + edge_dist * 0.9)  # Convex: thick center
        bm.verts.new((x, y, 0))
        bm.verts.new((-x, y, 0))

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

    # Chrome edge ring
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
