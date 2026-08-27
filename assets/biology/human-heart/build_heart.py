import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "human-heart"


def build_heart():
    # Materials
    muscle = kit.add_material("heart-muscle", (0.72, 0.15, 0.12), metallic=0.0, roughness=0.65)
    oxygenated = kit.add_material("heart-oxy", (0.85, 0.12, 0.10), metallic=0.0, roughness=0.55)
    deoxy = kit.add_material("heart-deoxy", (0.18, 0.25, 0.65), metallic=0.0, roughness=0.55)
    septum = kit.add_material("heart-septum", (0.60, 0.12, 0.10), metallic=0.0, roughness=0.7)
    valve = kit.add_material("heart-valve", (0.85, 0.75, 0.65), metallic=0.0, roughness=0.4)
    vessel_wall = kit.add_material("heart-vessel", (0.70, 0.15, 0.12), metallic=0.0, roughness=0.6)

    # Heart outline using parametric heart shape (front view)
    bm = bmesh.new()
    # Heart shape parametric: x = 16sin^3(t), y = 13cos(t) - 5cos(2t) - 2cos(3t) - cos(4t)
    # Scale down to ~0.08m
    scale = 0.005
    segments = 64
    front_verts = []
    back_verts = []
    depth = 0.025  # half-depth of heart

    for i in range(segments):
        t = 2 * math.pi * i / segments
        x = 16 * math.sin(t) ** 3 * scale
        y = (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) * scale
        front_verts.append(bm.verts.new((x, y, depth)))
        back_verts.append(bm.verts.new((x, y, -depth)))

    bm.verts.ensure_lookup_table()

    # Front face
    front_faces = []
    for i in range(segments):
        j = (i + 1) % segments
        face = bm.faces.new([front_verts[i], front_verts[j], back_verts[j], back_verts[i]])
        front_faces.append(face)

    # Create mesh
    mesh = bpy.data.meshes.new(f"{ASSET_ID}-body")
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(f"{ASSET_ID}-body", mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(muscle)

    # Interventricular septum (vertical divider inside)
    kit.primitive_object(f"{ASSET_ID}-septum", "cube", septum,
                          size=(0.002, 0.06, 0.045),
                          location=(0.0, 0.0, 0.0))

    # Right atrium (upper right, deoxygenated - blue)
    kit.primitive_object(f"{ASSET_ID}-ra", "cylinder", deoxy,
                          size=(0.025, 0.025, 0.015),
                          location=(0.02, 0.025, 0.0))

    # Left atrium (upper left, oxygenated - red)
    kit.primitive_object(f"{ASSET_ID}-la", "cylinder", oxygenated,
                          size=(0.025, 0.025, 0.015),
                          location=(-0.02, 0.025, 0.0))

    # Right ventricle (lower right, blue)
    kit.primitive_object(f"{ASSET_ID}-rv", "cylinder", deoxy,
                          size=(0.028, 0.028, 0.02),
                          location=(0.015, -0.01, 0.0))

    # Left ventricle (lower left, red - thicker wall)
    kit.primitive_object(f"{ASSET_ID}-lv", "cylinder", oxygenated,
                          size=(0.030, 0.030, 0.025),
                          location=(-0.015, -0.01, 0.0))

    # Aorta (curved arch from left ventricle)
    kit.primitive_object(f"{ASSET_ID}-aorta", "cylinder", oxygenated,
                          size=(0.012, 0.012, 0.04),
                          location=(-0.01, 0.04, 0.0),
                          rotation_euler=(0.3, 0.0, 0.0))

    # Pulmonary artery (from right ventricle)
    kit.primitive_object(f"{ASSET_ID}-pulmonary-artery", "cylinder", deoxy,
                          size=(0.010, 0.010, 0.035),
                          location=(0.01, 0.035, 0.0),
                          rotation_euler=(-0.2, 0.0, 0.0))

    # Superior vena cava (entering right atrium)
    kit.primitive_object(f"{ASSET_ID}-svc", "cylinder", deoxy,
                          size=(0.008, 0.008, 0.025),
                          location=(0.025, 0.04, 0.0))

    # Inferior vena cava
    kit.primitive_object(f"{ASSET_ID}-ivc", "cylinder", deoxy,
                          size=(0.008, 0.008, 0.02),
                          location=(0.02, -0.03, 0.0))

    # Atrioventricular valves (small discs)
    kit.primitive_object(f"{ASSET_ID}-tricuspid", "cylinder", valve,
                          size=(0.015, 0.015, 0.003),
                          location=(0.015, 0.01, 0.0))
    kit.primitive_object(f"{ASSET_ID}-mitral", "cylinder", valve,
                          size=(0.015, 0.015, 0.003),
                          location=(-0.015, 0.01, 0.0))

    return [obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_heart()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
