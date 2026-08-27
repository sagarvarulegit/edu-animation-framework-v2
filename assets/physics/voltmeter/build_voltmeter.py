import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "voltmeter"


def build_voltmeter():
    case = kit.add_material("meter-case", (0.12, 0.12, 0.12), metallic=0.3, roughness=0.6)
    dial = kit.add_material("meter-dial", (0.95, 0.95, 0.92), metallic=0.0, roughness=0.4)
    needle = kit.add_material("meter-needle", (0.85, 0.15, 0.10), metallic=0.8, roughness=0.3)
    terminal = kit.add_material("meter-terminal", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)
    label_bg = kit.add_material("meter-label-v", (0.15, 0.30, 0.70), metallic=0.0, roughness=0.5)
    scale_mark = kit.add_material("meter-scale", (0.05, 0.05, 0.05), metallic=0.0, roughness=0.4)

    kit.primitive_object(f"{ASSET_ID}-case", "cube", case,
                          size=(0.06, 0.03, 0.05),
                          location=(0.0, 0.0, 0.0))
    kit.primitive_object(f"{ASSET_ID}-dial", "cube", dial,
                          size=(0.055, 0.002, 0.045),
                          location=(0.0, -0.014, 0.0))

    for i in range(9):
        angle = -0.6 + i * 0.15
        x = 0.015 * math.sin(angle)
        z = 0.015 * math.cos(angle) - 0.005
        kit.primitive_object(f"{ASSET_ID}-scale-{i}", "cube", scale_mark,
                              size=(0.001, 0.001, 0.004),
                              location=(x, -0.014, z),
                              rotation_euler=(0.0, 0.0, -angle))

    kit.primitive_object(f"{ASSET_ID}-needle", "cube", needle,
                          size=(0.022, 0.001, 0.002),
                          location=(-0.002, -0.015, 0.010),
                          rotation_euler=(0.0, 0.0, 0.7))

    kit.primitive_object(f"{ASSET_ID}-label", "cube", label_bg,
                          size=(0.012, 0.001, 0.010),
                          location=(0.0, -0.015, -0.015))

    # Binding posts on TOP
    kit.primitive_object(f"{ASSET_ID}-terminal-pos", "cylinder", terminal,
                          size=(0.005, 0.005, 0.008),
                          location=(0.02, 0.0, 0.028))
    kit.primitive_object(f"{ASSET_ID}-terminal-neg", "cylinder", terminal,
                          size=(0.005, 0.005, 0.008),
                          location=(-0.02, 0.0, 0.028))

    return []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_voltmeter()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
