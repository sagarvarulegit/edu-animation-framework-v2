import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bunsen-burner"


def build_burner():
    cast_iron = kit.add_material("burner-cast-iron", (0.10, 0.10, 0.11),
                                 metallic=0.8, roughness=0.45)
    brass = kit.add_material("burner-brass", (0.70, 0.52, 0.20),
                             metallic=1.0, roughness=0.30)
    base_z = 0.005
    stem_height = 0.105
    stem_center_z = 0.010 + stem_height / 2
    collar_center_z = 0.010 + 0.014
    nozzle_height = 0.018
    nozzle_center_z = 0.010 + stem_height + nozzle_height / 2

    base = kit.primitive_object(f"{ASSET_ID}-base", "cylinder", cast_iron,
                                size=(0.09, 0.09, 0.010), location=(0.0, 0.0, base_z))
    collar = kit.primitive_object(f"{ASSET_ID}-air-collar", "cylinder", cast_iron,
                                  size=(0.020, 0.020, 0.028), location=(0.0, 0.0, collar_center_z))
    stem = kit.primitive_object(f"{ASSET_ID}-stem", "cylinder", cast_iron,
                                size=(0.013, 0.013, stem_height), location=(0.0, 0.0, stem_center_z))
    nozzle = kit.primitive_object(f"{ASSET_ID}-nozzle", "cone", brass,
                                  size=(0.013, 0.007, nozzle_height),
                                  location=(0.0, 0.0, nozzle_center_z))
    return [base, collar, stem, nozzle]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_burner()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
