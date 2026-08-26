import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "beaker"


def build_beaker():
    # Glass: warm neutral tone, slightly yellow-green like real lab glass
    glass = kit.add_material("beaker-glass", (0.82, 0.88, 0.82),
                             metallic=0.0, roughness=0.08)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    bsdf.inputs["IOR"].default_value = 1.52

    # Liquid: bright blue (copper sulphate solution - common in CBSE labs)
    liquid = kit.add_material("beaker-liquid", (0.15, 0.45, 0.85),
                              metallic=0.0, roughness=0.2)
    liquid.use_nodes = True
    bsdf_l = liquid.node_tree.nodes["Principled BSDF"]
    bsdf_l.inputs["Transmission Weight"].default_value = 0.6

    # Graduation marks: dark green (like real Pyrex beakers)
    mark_mat = kit.add_material("beaker-marks", (0.15, 0.35, 0.15), roughness=0.5)

    # Glass body (open top cylinder, slight taper)
    body = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", glass,
                                size=(0.07, 0.065, 0.10),
                                location=(0.0, 0.0, 0.05))

    # Liquid inside (slightly smaller, lower)
    liquid_level = kit.primitive_object(f"{ASSET_ID}-liquid", "cylinder", liquid,
                                         size=(0.062, 0.058, 0.06),
                                         location=(0.0, 0.0, 0.032))

    # Pour spout (triangular wedge on rim)
    spout = kit.primitive_object(f"{ASSET_ID}-spout", "cube", glass,
                                 size=(0.015, 0.03, 0.01),
                                 location=(0.035, 0.0, 0.102))

    # Graduation marks (3 visible lines at 50ml, 100ml, 150ml)
    marks = []
    for i, h in enumerate([0.035, 0.055, 0.075]):
        mark = kit.primitive_object(f"{ASSET_ID}-mark-{i}", "cylinder", mark_mat,
                                     size=(0.072, 0.067, 0.001),
                                     location=(0.0, 0.0, h))
        marks.append(mark)

    # Label text indicator (small white rectangle)
    label_bg = kit.primitive_object(f"{ASSET_ID}-label-bg", "cube",
                                     kit.add_material("label-white", (0.95, 0.95, 0.95), roughness=0.4),
                                     size=(0.025, 0.001, 0.015),
                                     location=(0.035, 0.0, 0.055))

    return [body, liquid_level, spout, label_bg] + marks


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
