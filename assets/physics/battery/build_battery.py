import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "battery"


def build_battery():
    # Copper top (like Duracell)
    copper_top = kit.add_material("battery-copper", (0.72, 0.45, 0.18),
                                  metallic=0.9, roughness=0.25)
    # Black body
    black_body = kit.add_material("battery-black", (0.08, 0.08, 0.08),
                                  metallic=0.3, roughness=0.5)
    # Copper/gold label band
    label_band = kit.add_material("battery-gold", (0.85, 0.70, 0.25),
                                  metallic=0.7, roughness=0.3)
    # Silver bottom (negative terminal)
    silver = kit.add_material("battery-silver", (0.7, 0.7, 0.72),
                              metallic=0.95, roughness=0.2)

    # Main body (AA: 14mm dia, 50mm tall)
    body = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", black_body,
                                size=(0.014, 0.014, 0.045),
                                location=(0.0, 0.0, 0.0255))

    # Copper top section
    copper = kit.primitive_object(f"{ASSET_ID}-copper-top", "cylinder", copper_top,
                                   size=(0.014, 0.014, 0.008),
                                   location=(0.0, 0.0, 0.051))

    # Positive terminal nub (+)
    pos = kit.primitive_object(f"{ASSET_ID}-positive", "cylinder", copper_top,
                               size=(0.005, 0.005, 0.004),
                               location=(0.0, 0.0, 0.057))

    # Negative terminal flat (-)
    neg = kit.primitive_object(f"{ASSET_ID}-negative", "cylinder", silver,
                               size=(0.014, 0.014, 0.001),
                               location=(0.0, 0.0, 0.0005))

    # Gold label band (middle section)
    gold_band = kit.primitive_object(f"{ASSET_ID}-gold-band", "cylinder", label_band,
                                      size=(0.0145, 0.0145, 0.020),
                                      location=(0.0, 0.0, 0.025))

    return [body, copper, pos, neg, gold_band]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_battery()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
