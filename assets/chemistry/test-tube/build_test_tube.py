import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "test-tube"


def build_test_tube():
    # Glass: warmer tone like real borosilicate
    glass = kit.add_material("test-tube-glass", (0.80, 0.87, 0.82),
                             metallic=0.0, roughness=0.06)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.52

    # Liquid: bright orange (iodine solution - common CBSE experiment)
    liquid = kit.add_material("test-tube-liquid", (0.90, 0.45, 0.10),
                              metallic=0.0, roughness=0.15)
    liquid.use_nodes = True
    bsdf_l = liquid.node_tree.nodes["Principled BSDF"]
    bsdf_l.inputs["Transmission Weight"].default_value = 0.7

    # Glass cylinder body (wider for visibility)
    body = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", glass,
                                size=(0.024, 0.024, 0.14),
                                location=(0.0, 0.0, 0.07))

    # Liquid inside (partial fill)
    liquid_level = kit.primitive_object(f"{ASSET_ID}-liquid", "cylinder", liquid,
                                         size=(0.020, 0.020, 0.08),
                                         location=(0.0, 0.0, 0.042))

    # Rounded bottom (hemisphere approximation)
    bottom = kit.primitive_object(f"{ASSET_ID}-bottom", "cone", glass,
                                  size=(0.024, 0.005, 0.018),
                                  location=(0.0, 0.0, 0.009))

    # Rim (thickened top edge)
    rim = kit.primitive_object(f"{ASSET_ID}-rim", "cylinder", glass,
                               size=(0.028, 0.028, 0.006),
                               location=(0.0, 0.0, 0.143))

    return [body, liquid_level, bottom, rim]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_test_tube()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
