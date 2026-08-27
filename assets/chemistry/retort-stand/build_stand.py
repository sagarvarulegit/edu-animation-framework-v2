import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "retort-stand"


def build_stand():
    # Brighter iron
    iron = kit.add_material("stand-iron", (0.30, 0.30, 0.32), metallic=0.8, roughness=0.45)
    # Chrome rod
    chrome = kit.add_material("stand-chrome", (0.72, 0.72, 0.74), metallic=0.95, roughness=0.1)
    # Clamp
    clamp = kit.add_material("stand-clamp", (0.65, 0.65, 0.68), metallic=0.85, roughness=0.3)

    # Heavy base plate — rod at REAR CENTER (not middle)
    kit.primitive_object(f"{ASSET_ID}-base", "cube", iron,
                          size=(0.08, 0.005, 0.05),
                          location=(0.0, 0.0, 0.0))

    # Vertical rod — positioned at rear edge of base
    kit.primitive_object(f"{ASSET_ID}-rod", "cylinder", chrome,
                          size=(0.004, 0.004, 0.10),
                          location=(0.0, 0.02, 0.05))

    # Bosshead (clamp connector sleeve)
    kit.primitive_object(f"{ASSET_ID}-bosshead", "cube", clamp,
                          size=(0.008, 0.008, 0.008),
                          location=(0.0, 0.016, 0.06))

    # Clamp arm (horizontal)
    kit.primitive_object(f"{ASSET_ID}-clamp-arm", "cube", clamp,
                          size=(0.03, 0.004, 0.004),
                          location=(-0.015, 0.012, 0.06))

    # Clamp jaws (3-prong style)
    kit.primitive_object(f"{ASSET_ID}-jaw-top", "cube", clamp,
                          size=(0.015, 0.003, 0.003),
                          location=(-0.025, 0.012, 0.063))
    kit.primitive_object(f"{ASSET_ID}-jaw-bottom", "cube", clamp,
                          size=(0.015, 0.003, 0.003),
                          location=(-0.025, 0.012, 0.057))

    # Thumbscrew
    kit.primitive_object(f"{ASSET_ID}-thumbscrew", "cylinder", chrome,
                          size=(0.005, 0.005, 0.005),
                          location=(0.0, 0.010, 0.06))

    return []


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
