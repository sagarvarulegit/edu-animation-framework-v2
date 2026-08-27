import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "ammeter"


def build_ammeter():
    # Black bakelite case
    case = kit.add_material("meter-case", (0.12, 0.12, 0.12), metallic=0.3, roughness=0.6)
    # White dial face
    dial = kit.add_material("meter-dial", (0.95, 0.95, 0.92), metallic=0.0, roughness=0.4)
    # Red needle
    needle = kit.add_material("meter-needle", (0.85, 0.15, 0.10), metallic=0.8, roughness=0.3)
    # Brass terminals
    terminal = kit.add_material("meter-terminal", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)
    # Green "A" label background
    label_bg = kit.add_material("meter-label", (0.15, 0.55, 0.25), metallic=0.0, roughness=0.5)

    # Case (rounded rectangle approximation)
    case_obj = kit.primitive_object(f"{ASSET_ID}-case", "cube", case,
                                     size=(0.06, 0.03, 0.05),
                                     location=(0.0, 0.0, 0.0))

    # Dial face
    dial_obj = kit.primitive_object(f"{ASSET_ID}-dial", "cube", dial,
                                     size=(0.055, 0.002, 0.045),
                                     location=(0.0, -0.014, 0.0))

    # Needle (angled, pointing to ~0.5A)
    needle_obj = kit.primitive_object(f"{ASSET_ID}-needle", "cube", needle,
                                       size=(0.025, 0.001, 0.002),
                                       location=(0.0, -0.015, 0.005),
                                       rotation_euler=(0.0, 0.0, 0.4))

    # "A" label background
    label = kit.primitive_object(f"{ASSET_ID}-label", "cube", label_bg,
                                  size=(0.012, 0.001, 0.010),
                                  location=(0.0, -0.015, -0.015))

    # Terminals (positive red, negative black)
    term_pos = kit.primitive_object(f"{ASSET_ID}-terminal-pos", "cylinder", terminal,
                                     size=(0.006, 0.006, 0.008),
                                     location=(0.02, -0.015, -0.03))
    term_neg = kit.primitive_object(f"{ASSET_ID}-terminal-neg", "cylinder", terminal,
                                     size=(0.006, 0.006, 0.008),
                                     location=(-0.02, -0.015, -0.03))

    return [case_obj, dial_obj, needle_obj, label, term_pos, term_neg]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_ammeter()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
