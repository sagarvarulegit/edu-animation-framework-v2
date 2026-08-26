import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "connecting-wire"


def build_wire():
    # Bright red insulation (easy to see)
    insulation = kit.add_material("wire-red", (0.90, 0.15, 0.12),
                                  metallic=0.0, roughness=0.65)
    # Bright copper conductor
    copper = kit.add_material("wire-copper", (0.85, 0.55, 0.22),
                              metallic=0.92, roughness=0.25)

    # Insulated section (main length, thicker for visibility)
    insulation_body = kit.primitive_object(f"{ASSET_ID}-insulation", "cylinder", insulation,
                                            size=(0.004, 0.004, 0.14),
                                            location=(0.0, 0.0, 0.0))

    # Stripped end left (copper visible)
    strip_l = kit.primitive_object(f"{ASSET_ID}-strip-left", "cylinder", copper,
                                    size=(0.002, 0.002, 0.018),
                                    location=(0.0, 0.0, -0.079))

    # Stripped end right
    strip_r = kit.primitive_object(f"{ASSET_ID}-strip-right", "cylinder", copper,
                                    size=(0.002, 0.002, 0.018),
                                    location=(0.0, 0.0, 0.079))

    # Connector pins at ends (tiny brass tips)
    pin_mat = kit.add_material("wire-pin", (0.80, 0.60, 0.20),
                               metallic=0.9, roughness=0.2)
    pin_l = kit.primitive_object(f"{ASSET_ID}-pin-left", "cylinder", pin_mat,
                                  size=(0.001, 0.001, 0.005),
                                  location=(0.0, 0.0, -0.0905))
    pin_r = kit.primitive_object(f"{ASSET_ID}-pin-right", "cylinder", pin_mat,
                                  size=(0.001, 0.001, 0.005),
                                  location=(0.0, 0.0, 0.0905))

    return [insulation_body, strip_l, strip_r, pin_l, pin_r]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_wire()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
