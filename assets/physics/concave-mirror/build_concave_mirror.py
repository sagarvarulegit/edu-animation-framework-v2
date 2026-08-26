import sys
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "concave-mirror"


def build_concave_mirror():
    # Bright silver reflective surface
    mirror_mat = kit.add_material("concave-mirror-surface", (0.90, 0.92, 0.95),
                                  metallic=1.0, roughness=0.01)
    # Dark backing
    back_mat = kit.add_material("concave-mirror-back", (0.12, 0.12, 0.14),
                                metallic=0.3, roughness=0.7)
    # Frame ring
    frame_mat = kit.add_material("concave-frame", (0.55, 0.38, 0.22),
                                 metallic=0.0, roughness=0.6)

    radius = 0.055
    segments = 48

    # Create concave curved surface using bmesh
    bm = bmesh.new()
    for i in range(segments + 1):
        angle = math.pi * i / segments - math.pi / 2
        x = radius * math.cos(angle)
        z = radius * math.sin(angle) * 0.25  # shallow curve
        bmesh.ops.create_vert(bm, co=(x, 0, z))
        bmesh.ops.create_vert(bm, co=(x, 0.004, z))

    verts = bm.verts[:]
    for i in range(segments):
        v0 = verts[i * 2]
        v1 = verts[i * 2 + 1]
        v2 = verts[(i + 1) * 2]
        v3 = verts[(i + 1) * 2 + 1]
        bm.faces.new([v0, v2, v3, v1])

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-surface")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(f"{ASSET_ID}-surface", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mirror_mat)

    # Back plate (dark, flat)
    back = kit.primitive_object(f"{ASSET_ID}-back", "cylinder", back_mat,
                                size=(0.11, 0.11, 0.005),
                                location=(0.003, 0.0, 0.0))

    # Frame ring around edge
    frame = kit.primitive_object(f"{ASSET_ID}-frame", "cylinder", frame_mat,
                                  size=(0.115, 0.115, 0.008),
                                  location=(0.0, 0.0, 0.0))

    return [obj, back, frame]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_concave_mirror()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
