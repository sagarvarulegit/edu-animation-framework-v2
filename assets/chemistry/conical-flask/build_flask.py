import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh

ASSET_ID = "conical-flask"


def build_flask():
    # Warm green glass
    glass = kit.add_material("flask-glass", (0.75, 0.85, 0.78), metallic=0.0, roughness=0.1)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.52

    # Liquid: pale yellow (dilute acid)
    liquid = kit.add_material("flask-liquid", (0.92, 0.88, 0.45), metallic=0.0, roughness=0.2)

    # Graduation marks: white tick marks (not 360° rings)
    mark = kit.add_material("flask-mark", (0.85, 0.85, 0.80), metallic=0.0, roughness=0.4)

    # Flask body: wide cone base → narrow cylindrical neck
    # Base cone
    cone = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", glass,
                                 size=(0.04, 0.03, 0.05),
                                 location=(0.0, 0.0, 0.025))

    # Neck (narrow cylinder on top)
    neck = kit.primitive_object(f"{ASSET_ID}-neck", "cylinder", glass,
                                 size=(0.012, 0.012, 0.03),
                                 location=(0.0, 0.0, 0.07))

    # Rim at top
    rim = kit.primitive_object(f"{ASSET_ID}-rim", "cylinder", glass,
                                size=(0.015, 0.015, 0.003),
                                location=(0.0, 0.0, 0.086))

    # Liquid inside (partial fill)
    liquid_obj = kit.primitive_object(f"{ASSET_ID}-liquid", "cylinder", liquid,
                                       size=(0.035, 0.028, 0.035),
                                       location=(0.0, 0.0, 0.018))

    # Graduation marks: thin horizontal rings at different heights (1-sided look)
    for i, h in enumerate([0.01, 0.02, 0.03, 0.04]):
        kit.primitive_object(f"{ASSET_ID}-mark-{i}", "cylinder", mark,
                              size=(0.035 - i * 0.003, 0.035 - i * 0.003, 0.001),
                              location=(0.0, 0.0, h))

    return [cone, neck, rim, liquid_obj]


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
