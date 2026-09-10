"""Build a real-scale retort stand with an adjustable three-prong clamp."""
import sys
from pathlib import Path
import bpy
from math import cos, sin

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
ASSET_ID = "retort-stand"


def bevel(obj, width=0.0015, segments=3):
    modifier = obj.modifiers.new("rounded manufacturing edges", "BEVEL")
    modifier.width, modifier.segments = width, segments


def build_stand():
    iron = kit.add_machined_metal_material("stand-cast-iron", (0.10, 0.12, 0.14), 0.72, 0.42)
    chrome = kit.add_machined_metal_material("stand-chrome", (0.62, 0.67, 0.72), 0.94, 0.16)
    clamp = kit.add_machined_metal_material("stand-clamp", (0.32, 0.35, 0.39), 0.86, 0.26)
    rubber = kit.add_material("stand-jaw-rubber", (0.08, 0.11, 0.12), 0.0, 0.48)
    objects = []
    base = kit.primitive_object(f"{ASSET_ID}-base", "cube", iron, size=(0.125, 0.080, 0.010), location=(0.0, 0.0, 0.005))
    bevel(base, 0.004, 4); objects.append(base)
    for name, kind, material, size, location, rotation in [
        ("rod-socket", "cylinder", iron, (0.024, 0.024, 0.020), (0.035, 0.020, 0.020), (0, 0, 0)),
        ("support-rod", "cylinder", chrome, (0.009, 0.009, 0.265), (0.035, 0.020, 0.155), (0, 0, 0)),
        ("bosshead-screw", "cylinder", chrome, (0.009, 0.009, 0.020), (0.035, -0.001, 0.185), (1.5708, 0, 0)),
        ("clamp-arm", "cylinder", clamp, (0.008, 0.008, 0.115), (-0.020, 0.020, 0.185), (0, 1.5708, 0)),
        ("jaw-collar", "cylinder", clamp, (0.018, 0.018, 0.018), (-0.080, 0.020, 0.185), (0, 1.5708, 0)),
    ]:
        objects.append(kit.primitive_object(f"{ASSET_ID}-{name}", kind, material, size=size, location=location, rotation_euler=rotation))
    boss = kit.primitive_object(f"{ASSET_ID}-bosshead", "cube", clamp, size=(0.027, 0.025, 0.026), location=(0.035, 0.020, 0.185))
    bevel(boss, 0.003, 3); objects.append(boss)
    for name, position, angle in (
        ("jaw-upper", (-0.098, 0.020, 0.198), -0.26),
        ("jaw-lower-left", (-0.098, 0.006, 0.174), 0.24),
        ("jaw-lower-right", (-0.098, 0.034, 0.174), 0.24),
    ):
        objects.append(kit.primitive_object(f"{ASSET_ID}-{name}", "cylinder", clamp, size=(0.006, 0.006, 0.046), location=position, rotation_euler=(0, angle, 0)))
        # A jaw cylinder's local Z axis is its length; place the rubber pad at its actual free end.
        tip = (position[0] + 0.023 * sin(angle), position[1], position[2] + 0.023 * cos(angle))
        objects.append(kit.primitive_object(f"{ASSET_ID}-{name}-pad", "uv_sphere", rubber, size=(0.010, 0.010, 0.010), location=tip))
    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene(); objects = build_stand(); kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24); kit.frame_camera(objects, lens=55.0)
    kit.save_blend(out / f"{ASSET_ID}.blend"); kit.export_glb(out / f"{ASSET_ID}.glb"); kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
