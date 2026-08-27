import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "switch"


def build_switch():
    # Bakelite base: dark brown/black
    base_mat = kit.add_material("switch-base", (0.15, 0.12, 0.10), metallic=0.0, roughness=0.7)
    # Brass contacts
    contact = kit.add_material("switch-contact", (0.82, 0.62, 0.22), metallic=0.9, roughness=0.25)
    # Steel arm
    arm = kit.add_material("switch-arm", (0.65, 0.65, 0.68), metallic=0.85, roughness=0.3)
    # Red indicator
    indicator = kit.add_material("switch-indicator", (0.85, 0.12, 0.10), metallic=0.0, roughness=0.4)

    # Base plate
    kit.primitive_object(f"{ASSET_ID}-base", "cube", base_mat,
                          size=(0.04, 0.015, 0.025),
                          location=(0.0, 0.0, 0.0))

    # Fixed contact (bottom)
    kit.primitive_object(f"{ASSET_ID}-contact-fixed", "cylinder", contact,
                          size=(0.004, 0.004, 0.003),
                          location=(0.01, 0.005, 0.008))

    # Pivot contact (hinge point)
    kit.primitive_object(f"{ASSET_ID}-contact-pivot", "cylinder", contact,
                          size=(0.004, 0.004, 0.003),
                          location=(-0.01, 0.005, 0.008))

    # Knife arm — tilted UPWARD along Y-axis (open position)
    kit.primitive_object(f"{ASSET_ID}-arm", "cube", arm,
                          size=(0.022, 0.003, 0.002),
                          location=(-0.005, 0.008, 0.014),
                          rotation_euler=(0.0, 0.6, 0.0))  # Tilt up along Y

    # Handle grip (insulated end)
    kit.primitive_object(f"{ASSET_ID}-grip", "cube", indicator,
                          size=(0.005, 0.005, 0.005),
                          location=(0.008, 0.008, 0.018))

    # Red indicator dot
    kit.primitive_object(f"{ASSET_ID}-indicator", "cylinder", indicator,
                          size=(0.003, 0.003, 0.001),
                          location=(0.0, 0.008, 0.008))

    # Terminal posts
    kit.primitive_object(f"{ASSET_ID}-terminal-1", "cylinder", contact,
                          size=(0.004, 0.004, 0.008),
                          location=(-0.015, 0.0, -0.01))
    kit.primitive_object(f"{ASSET_ID}-terminal-2", "cylinder", contact,
                          size=(0.004, 0.004, 0.008),
                          location=(0.015, 0.0, -0.01))

    return []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_switch()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
