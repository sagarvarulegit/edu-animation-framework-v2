import argparse
import json
import sys
from math import radians
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "assets" / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import edu_asset_kit as kit
import semantic_primitives as prim


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", required=True)
    parser.add_argument("--out", default=None)
    parser.add_argument("--qa-frames", default="")
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--samples", type=int, default=48)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args, _ = parser.parse_known_args(argv)
    return args


def asset_registry():
    registry = {}
    for path in (ROOT / "assets").rglob("asset.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        registry[data["id"]] = path.parent
    return registry


def append_asset(asset_dir, asset_id):
    blend_file = asset_dir / "out" / f"{asset_id}.blend"
    with bpy.data.libraries.load(str(blend_file), link=False) as (source, destination):
        destination.objects = source.objects
    scene_collection = bpy.context.scene.collection
    renderables = []
    for obj in destination.objects:
        if obj is None:
            continue
        # Asset cameras and studio lights must not override the lesson camera/lighting;
        # meshes and curves are both required for reusable apparatus such as the tongs.
        if obj.type in {"MESH", "CURVE", "EMPTY"}:
            scene_collection.objects.link(obj)
            renderables.append(obj)
    return renderables


def build_instances(scene, registry):
    parents = {}
    for instance in scene["instances"]:
        asset_id = instance["asset"]
        objects = append_asset(registry[asset_id], asset_id)
        parent = bpy.data.objects.new(f"instance-{asset_id}", None)
        bpy.context.collection.objects.link(parent)
        parent.location = Vector(instance["position"])
        parent.rotation_euler = (0.0, 0.0, radians(instance.get("rotationZ", 0.0)))
        for obj in objects:
            obj.parent = parent
        parents[asset_id] = parent
    return parents


def build_bench():
    material = kit.add_material("bench-surface", (0.35, 0.30, 0.26),
                                metallic=0.0, roughness=0.85)
    kit.primitive_object("bench-plane", "cube", material,
                         size=(1.4, 1.4, 0.01), location=(0.05, -0.05, -0.005))


def build_camera():
    cam_data = bpy.data.cameras.new("edu_scene_camera")
    cam_data.lens = 50.0
    cam = bpy.data.objects.new("edu_scene_camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam, cam_data


def apply_timeline(scene, parents, cam, cam_data):
    shots = scene.get("camera", {}).get("shots", {})
    current_shot = None
    label_material_targets = []
    for entry in sorted(scene["timeline"], key=lambda e: e["start"]):
        primitive = entry["primitive"]
        fps = scene["fps"]
        if primitive == "cameraMove":
            shot = shots[entry["shot"]]
            prim.camera_move(cam, cam_data,
                             current_shot or shot, shot,
                             entry["start"], entry.get("duration", 0.0), fps)
            current_shot = shot
        elif primitive == "appear":
            prim.appear(parents[entry["target"]], entry["start"], entry.get("duration", 0.5), fps)
        elif primitive == "disappear":
            prim.disappear(parents[entry["target"]], entry["start"], entry.get("duration", 0.5), fps)
        elif primitive == "move":
            prim.move(parents[entry["target"]], entry["start"], entry["duration"],
                      Vector(entry["offset"]), fps)
        elif primitive == "heat":
            prim.heat(parents[entry["target"]], entry["start"], entry["duration"],
                      entry.get("color", (1.0, 0.25, 0.05)), entry.get("strength", 2.0), fps)
        elif primitive == "burn":
            prim.burn(parents[entry["target"]], entry["start"], entry["duration"],
                      entry.get("strength", 40.0), fps)
        elif primitive == "showFlame":
            prim.show_flame(parents[entry["target"]],
                            Vector(entry.get("offset", (0.0, 0.0, 0.135))),
                            entry, fps)
        elif primitive == "transform":
            prim.transform(parents[entry["target"]], entry["look"], entry["start"], fps)
        elif primitive == "showLabel":
            target_pos = Vector(parents[entry["target"]].location)
            offset = Vector(entry.get("offset", (0.0, 0.0, 0.05)))
            label = prim.show_label(entry["text"], target_pos + offset,
                                    entry["end"], cam,
                                    name=f"label-{entry['target']}")
            prim.label_pop(label, entry["start"], entry["end"], fps)
        elif primitive == "showMolecule":
            molecule = prim.show_molecule(entry["model"], entry["id"], entry["position"])
            parents[entry["id"]] = molecule
            prim.appear(molecule, entry["start"], entry.get("duration", 0.45), fps)
        elif primitive == "showEquation":
            equation = prim.show_equation(entry["text"], entry["position"], cam, entry["id"], entry.get("size", 0.026))
            parents[entry["id"]] = equation
            prim.label_pop(equation, entry["start"], entry["end"], fps)
        else:
            raise ValueError(f"primitive not implemented in blender renderer: {primitive}")


def configure_output(scene, out_dir, width, height, samples):
    scene_render = bpy.context.scene.render
    scene_render.fps = scene["fps"]
    bpy.context.scene.frame_end = round(scene["duration"] * scene["fps"])
    kit.configure_render(width, height, samples)
    scene_render.filepath = str(out_dir)


def render_qa_stills(frames, out_dir, scene_name):
    for frame in frames:
        bpy.context.scene.frame_set(frame)
        bpy.context.scene.render.filepath = str(
            out_dir / f"qa_{scene_name}_frame_{frame:04d}.png")
        bpy.ops.render.render(write_still=True)


def render_video(out_dir, scene_name):
    frames_dir = out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    render = bpy.context.scene.render
    render.image_settings.file_format = "PNG"
    render.filepath = str(frames_dir / "frame_")
    bpy.context.scene.frame_set(bpy.context.scene.frame_start)
    bpy.ops.render.render(animation=True)


def main():
    args = parse_args()
    scene_path = Path(args.scene)
    if not scene_path.is_absolute():
        scene_path = ROOT / scene_path
    out_dir = Path(args.out) if args.out else scene_path.parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    scene_name = scene["id"]

    kit.reset_scene()
    registry = asset_registry()
    parents = build_instances(scene, registry)
    build_bench()
    kit.setup_world_and_light()
    cam, cam_data = build_camera()
    apply_timeline(scene, parents, cam, cam_data)
    configure_output(scene, out_dir, args.width, args.height, args.samples)

    if args.qa_frames:
        frames = [int(f) for f in args.qa_frames.split(",")]
        render_qa_stills(frames, out_dir, scene_name)

    if args.video:
        render_video(out_dir, scene_name)

    if not args.qa_frames and not args.video:
        kit.save_blend(out_dir / f"{scene_name}.blend")


if __name__ == "__main__":
    main()
