import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "beaker"


def build_beaker():
    # Warm green glass (Pyrex style)
    glass = kit.add_material("beaker-glass", (0.75, 0.85, 0.78), metallic=0.0, roughness=0.08)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.52

    # Blue CuSO₄ liquid
    liquid = kit.add_material("beaker-liquid", (0.15, 0.35, 0.80), metallic=0.0, roughness=0.2)

    # Graduation marks: white tick marks (NOT 360° rings!)
    mark = kit.add_material("beaker-mark", (0.85, 0.85, 0.80), metallic=0.0, roughness=0.4)

    # Beaker body
    kit.primitive_object(f"{ASSET_ID}-body", "cylinder", glass,
                          size=(0.035, 0.035, 0.06),
                          location=(0.0, 0.0, 0.03))

    # Pour spout (small wedge at rim)
    kit.primitive_object(f"{ASSET_ID}-spout", "cube", glass,
                          size=(0.01, 0.005, 0.005),
                          location=(0.03, 0.0, 0.06))

    # Liquid inside (partial fill)
    kit.primitive_object(f"{ASSET_ID}-liquid", "cylinder", liquid,
                          size=(0.032, 0.032, 0.035),
                          location=(0.0, 0.0, 0.018))

    # Graduation marks: thin horizontal rings at different heights
    for i, h in enumerate([0.01, 0.02, 0.03, 0.04, 0.05]):
        kit.primitive_object(f"{ASSET_ID}-mark-{i}", "cylinder", mark,
                              size=(0.036, 0.036, 0.0008),
                              location=(0.0, 0.0, h))

    return []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_beaker()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
