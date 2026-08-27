import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "rheostat"


def build_rheostat():
    # Ceramic base
    base_mat = kit.add_material("rheostat-base", (0.85, 0.82, 0.75), metallic=0.0, roughness=0.7)
    # Resistance wire coil: copper
    coil = kit.add_material("rheostat-coil", (0.75, 0.45, 0.18), metallic=0.9, roughness=0.35)
    # Slider contact: brass
    slider = kit.add_material("rheostat-slider", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)
    # Terminal posts: brass
    terminal = kit.add_material("rheostat-terminal", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)

    # Base plate
    base_obj = kit.primitive_object(f"{ASSET_ID}-base", "cube", base_mat,
                                     size=(0.08, 0.015, 0.04),
                                     location=(0.0, 0.0, 0.0))

    # Coil (series of cylinders along length)
    for i in range(8):
        x = -0.03 + i * 0.008
        kit.primitive_object(f"{ASSET_ID}-coil-{i}", "cylinder", coil,
                              size=(0.004, 0.004, 0.03),
                              location=(x, 0.01, 0.0),
                              rotation_euler=(1.57, 0.0, 0.0))

    # Slider bar (top rail)
    kit.primitive_object(f"{ASSET_ID}-slider-bar", "cube", slider,
                          size=(0.07, 0.003, 0.004),
                          location=(0.0, 0.02, 0.0))

    # Slider contact (moveable point)
    kit.primitive_object(f"{ASSET_ID}-slider-contact", "cylinder", slider,
                          size=(0.006, 0.006, 0.005),
                          location=(0.01, 0.018, 0.0))

    # Terminal posts (2)
    kit.primitive_object(f"{ASSET_ID}-terminal-1", "cylinder", terminal,
                          size=(0.005, 0.005, 0.01),
                          location=(-0.035, 0.01, 0.0))
    kit.primitive_object(f"{ASSET_ID}-terminal-2", "cylinder", terminal,
                          size=(0.005, 0.005, 0.01),
                          location=(0.035, 0.01, 0.0))

    dummy = kit.primitive_object(f"{ASSET_ID}-frame-helper", "cube",
                                  kit.add_material("_helper", (0, 0, 0)),
                                  size=(0.10, 0.03, 0.05),
                                  location=(0.0, 0.0, 0.0))
    return [dummy]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_rheostat()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
