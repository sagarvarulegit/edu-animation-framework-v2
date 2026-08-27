import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "test-tube"


def build_test_tube():
    # Warm green glass
    glass = kit.add_material("tube-glass", (0.75, 0.85, 0.78), metallic=0.0, roughness=0.08)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.52

    # Orange iodine liquid
    liquid = kit.add_material("tube-liquid", (0.85, 0.45, 0.10), metallic=0.0, roughness=0.2)

    # Rim (slightly wider than body)
    rim = kit.add_material("tube-rim", (0.70, 0.80, 0.73), metallic=0.0, roughness=0.1)

    # Tube body (cylindrical)
    kit.primitive_object(f"{ASSET_ID}-body", "cylinder", glass,
                          size=(0.008, 0.008, 0.08),
                          location=(0.0, 0.0, 0.04))

    # Smooth hemispherical bottom (using a sphere cut in half)
    kit.primitive_object(f"{ASSET_ID}-bottom", "cylinder", glass,
                          size=(0.008, 0.008, 0.008),
                          location=(0.0, 0.0, 0.0))

    # Rim at top (slightly wider)
    kit.primitive_object(f"{ASSET_ID}-rim", "cylinder", rim,
                          size=(0.009, 0.009, 0.003),
                          location=(0.0, 0.0, 0.082))

    # Liquid inside (partial fill)
    kit.primitive_object(f"{ASSET_ID}-liquid", "cylinder", liquid,
                          size=(0.006, 0.006, 0.035),
                          location=(0.0, 0.0, 0.018))

    return []


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
