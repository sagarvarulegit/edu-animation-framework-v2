import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "switch"


def build_switch():
    # Bakelite base (dark brown, like real switches)
    base_mat = kit.add_material("switch-bakelite", (0.25, 0.15, 0.08),
                                metallic=0.0, roughness=0.7)
    # Brass contacts (bright, visible)
    contact_mat = kit.add_material("switch-brass", (0.85, 0.65, 0.20),
                                   metallic=0.95, roughness=0.2)
    # Steel arm
    arm_mat = kit.add_material("switch-steel", (0.60, 0.60, 0.62),
                               metallic=0.9, roughness=0.3)
    # Red indicator (shows switch state)
    indicator_mat = kit.add_material("switch-red", (0.85, 0.15, 0.10),
                                     metallic=0.0, roughness=0.5)

    # Base plate (bakelite)
    base = kit.primitive_object(f"{ASSET_ID}-base", "cube", base_mat,
                                size=(0.05, 0.025, 0.005),
                                location=(0.0, 0.0, 0.0025))

    # Fixed contact points (two brass cylinders)
    contact_l = kit.primitive_object(f"{ASSET_ID}-contact-left", "cylinder", contact_mat,
                                      size=(0.006, 0.006, 0.005),
                                      location=(-0.012, 0.0, 0.0075))
    contact_r = kit.primitive_object(f"{ASSET_ID}-contact-right", "cylinder", contact_mat,
                                      size=(0.006, 0.006, 0.005),
                                      location=(0.012, 0.0, 0.0075))

    # Pivoting arm (in open position, angled up at 30°)
    arm = kit.primitive_object(f"{ASSET_ID}-arm", "cube", arm_mat,
                               size=(0.03, 0.004, 0.004),
                               location=(0.0, 0.0, 0.015),
                               rotation_euler=(0.0, 0.0, 0.5))

    # Pivot point (brass)
    pivot = kit.primitive_object(f"{ASSET_ID}-pivot", "cylinder", contact_mat,
                                  size=(0.007, 0.007, 0.005),
                                  location=(-0.012, 0.0, 0.010))

    # Red indicator dot
    indicator = kit.primitive_object(f"{ASSET_ID}-indicator", "cylinder", indicator_mat,
                                      size=(0.004, 0.004, 0.001),
                                      location=(0.02, 0.0, 0.006))

    return [base, contact_l, contact_r, arm, pivot, indicator]


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
