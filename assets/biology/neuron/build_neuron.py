import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "neuron"


def build_neuron():
    # Cell body (soma): pale yellow
    soma = kit.add_material("neuron-soma", (0.92, 0.85, 0.55), metallic=0.0, roughness=0.6)
    # Axon: light blue
    axon = kit.add_material("neuron-axon", (0.55, 0.70, 0.85), metallic=0.0, roughness=0.5)
    # Myelin sheath: white
    myelin = kit.add_material("neuron-myelin", (0.95, 0.95, 0.92), metallic=0.0, roughness=0.4)
    # Dendrites: green
    dendrite = kit.add_material("neuron-dendrite", (0.45, 0.72, 0.45), metallic=0.0, roughness=0.5)
    # Nucleus: dark purple
    nucleus = kit.add_material("neuron-nucleus", (0.50, 0.25, 0.55), metallic=0.0, roughness=0.6)

    # Cell body (soma) - round, horizontal
    soma_obj = kit.primitive_object(f"{ASSET_ID}-soma", "cylinder", soma,
                                     size=(0.025, 0.025, 0.02),
                                     location=(0.0, 0.0, 0.0))

    # Nucleus inside soma
    nucleus_obj = kit.primitive_object(f"{ASSET_ID}-nucleus", "cylinder", nucleus,
                                        size=(0.012, 0.012, 0.012),
                                        location=(0.0, 0.0, 0.0))

    # Axon (long cable extending RIGHT along X-axis)
    axon_obj = kit.primitive_object(f"{ASSET_ID}-axon", "cylinder", axon,
                                     size=(0.005, 0.005, 0.10),
                                     location=(0.06, 0.0, 0.0),
                                     rotation_euler=(0.0, 1.57, 0.0))  # Horizontal

    # Myelin sheath segments (white beads along axon, horizontal)
    for i in range(5):
        x = 0.02 + i * 0.02
        kit.primitive_object(f"{ASSET_ID}-myelin-{i}", "cylinder", myelin,
                              size=(0.008, 0.008, 0.012),
                              location=(x, 0.0, 0.0),
                              rotation_euler=(0.0, 1.57, 0.0))

    # Dendrites (branching from soma, extending LEFT and radially)
    import math
    for i, angle in enumerate([0.3, 0.0, -0.3, 0.6, -0.6]):
        kit.primitive_object(f"{ASSET_ID}-dendrite-{i}", "cylinder", dendrite,
                              size=(0.003, 0.003, 0.025),
                              location=(-0.02, 0.0, 0.0),
                              rotation_euler=(0.0, 1.57, angle))

    # Axon terminal (right end, branching)
    kit.primitive_object(f"{ASSET_ID}-terminal-1", "cylinder", soma,
                          size=(0.005, 0.005, 0.008),
                          location=(0.11, 0.0, 0.003))
    kit.primitive_object(f"{ASSET_ID}-terminal-2", "cylinder", soma,
                          size=(0.005, 0.005, 0.008),
                          location=(0.11, 0.0, -0.003))

    return [soma_obj, nucleus_obj, axon_obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_neuron()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
