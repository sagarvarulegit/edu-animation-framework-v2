import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "retort-stand"


def build_stand():
    # Iron: brighter, more visible against dark backgrounds
    iron = kit.add_material("stand-iron", (0.25, 0.25, 0.28),
                            metallic=0.85, roughness=0.4)
    # Chrome highlight for clamp
    chrome = kit.add_material("stand-chrome", (0.65, 0.65, 0.68),
                              metallic=0.95, roughness=0.15)

    # Heavy base plate (wider for stability)
    base = kit.primitive_object(f"{ASSET_ID}-base", "cube", iron,
                                size=(0.12, 0.08, 0.010),
                                location=(0.0, 0.0, 0.005))

    # Vertical rod (thicker for visibility)
    rod = kit.primitive_object(f"{ASSET_ID}-rod", "cylinder", chrome,
                               size=(0.008, 0.008, 0.16),
                               location=(0.0, 0.0, 0.09))

    # Clamp arm (horizontal)
    clamp = kit.primitive_object(f"{ASSET_ID}-clamp-arm", "cube", chrome,
                                 size=(0.06, 0.010, 0.010),
                                 location=(0.03, 0.0, 0.14))

    # Clamp jaw (vertical piece)
    jaw = kit.primitive_object(f"{ASSET_ID}-clamp-jaw", "cube", chrome,
                               size=(0.010, 0.024, 0.010),
                               location=(0.06, 0.0, 0.128))

    # Wingnut (small detail)
    wingnut = kit.primitive_object(f"{ASSET_ID}-wingnut", "cylinder", iron,
                                    size=(0.012, 0.012, 0.004),
                                    location=(0.06, 0.012, 0.14))

    return [base, rod, clamp, jaw, wingnut]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_stand()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
