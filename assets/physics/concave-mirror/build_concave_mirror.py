import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh

ASSET_ID = "concave-mirror"


def build_mirror():
    silver = kit.add_material("mirror-silver", (0.92, 0.92, 0.94), metallic=1.0, roughness=0.02)
    back = kit.add_material("mirror-back", (0.08, 0.08, 0.08), metallic=0.0, roughness=0.8)
    frame = kit.add_material("mirror-frame", (0.55, 0.35, 0.18), metallic=0.0, roughness=0.6)

    # 3D spherical concave dish using bmesh
    bm = bmesh.new()
    radius = 0.05  # dish radius
    depth = 0.012  # concavity depth
    segments = 48

    # Create concave dish surface (front = silver, back = dark)
    for i in range(segments + 1):
        angle = math.pi * i / segments - math.pi / 2
        r = radius * math.cos(angle)
        z = -depth * (math.cos(angle) ** 2)  # parabolic concavity
        bm.verts.new((r, 0, z))
        bm.verts.new((-r, 0, z))

    verts = bm.verts[:]
    for i in range(segments):
        bm.faces.new([verts[i * 2], verts[i * 2 + 1],
                       verts[(i + 1) * 2 + 1], verts[(i + 1) * 2]])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-dish")
    bm.to_mesh(mesh)
    bm.free()
    dish = bpy.data.objects.new(f"{ASSET_ID}-dish", mesh)
    bpy.context.collection.objects.link(dish)
    dish.data.materials.append(silver)

    # Circular frame ring
    frame_ring = kit.primitive_object(f"{ASSET_ID}-frame", "cylinder", frame,
                                       size=(0.105, 0.105, 0.005),
                                       location=(0.0, 0.0, 0.0))

    # Stand rod
    stand = kit.primitive_object(f"{ASSET_ID}-stand", "cylinder", frame,
                                  size=(0.005, 0.005, 0.06),
                                  location=(0.0, 0.0, -0.03))

    # Base
    base = kit.primitive_object(f"{ASSET_ID}-base", "cylinder", frame,
                                 size=(0.03, 0.03, 0.005),
                                 location=(0.0, 0.0, -0.06))

    return [dish, frame_ring, stand, base]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_mirror()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
