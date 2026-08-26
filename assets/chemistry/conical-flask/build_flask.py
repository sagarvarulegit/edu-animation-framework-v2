import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "conical-flask"


def build_flask():
    glass = kit.add_material("flask-glass", (0.82, 0.88, 0.82),
                             metallic=0.0, roughness=0.06)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    bsdf.inputs["IOR"].default_value = 1.52

    # Liquid: pale yellow (acid solution)
    liquid = kit.add_material("flask-liquid", (0.95, 0.90, 0.50),
                              metallic=0.0, roughness=0.15)
    liquid.use_nodes = True
    bsdf_l = liquid.node_tree.nodes["Principled BSDF"]
    bsdf_l.inputs["Transmission Weight"].default_value = 0.65

    mark_mat = kit.add_material("flask-marks", (0.15, 0.35, 0.15), roughness=0.5)

    # Wide cone base (real Erlenmeyer proportions)
    cone = kit.primitive_object(f"{ASSET_ID}-cone", "cone", glass,
                                size=(0.09, 0.03, 0.055),
                                location=(0.0, 0.0, 0.0275))

    # Liquid in cone
    liquid_cone = kit.primitive_object(f"{ASSET_ID}-liquid-cone", "cone", liquid,
                                        size=(0.07, 0.02, 0.035),
                                        location=(0.0, 0.0, 0.0175))

    # Narrow cylindrical neck (longer, more realistic)
    neck = kit.primitive_object(f"{ASSET_ID}-neck", "cylinder", glass,
                                size=(0.028, 0.028, 0.05),
                                location=(0.0, 0.0, 0.08))

    # Flat bottom
    base = kit.primitive_object(f"{ASSET_ID}-base", "cylinder", glass,
                                size=(0.09, 0.09, 0.005),
                                location=(0.0, 0.0, 0.0025))

    # Rim (thickened lip)
    rim = kit.primitive_object(f"{ASSET_ID}-rim", "cylinder", glass,
                               size=(0.032, 0.032, 0.005),
                               location=(0.0, 0.0, 0.105))

    # Graduation mark
    mark = kit.primitive_object(f"{ASSET_ID}-mark", "cylinder", mark_mat,
                                size=(0.092, 0.075, 0.001),
                                location=(0.0, 0.0, 0.04))

    return [cone, liquid_cone, neck, base, rim, mark]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_flask()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
