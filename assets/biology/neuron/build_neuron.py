import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "neuron"


def build_neuron():
    # Materials
    soma = kit.add_material("neuron-soma", (0.92, 0.85, 0.55), metallic=0.0, roughness=0.6)
    axon = kit.add_material("neuron-axon", (0.55, 0.70, 0.85), metallic=0.0, roughness=0.5)
    myelin = kit.add_material("neuron-myelin", (0.95, 0.95, 0.92), metallic=0.0, roughness=0.4)
    dendrite = kit.add_material("neuron-dendrite", (0.45, 0.72, 0.45), metallic=0.0, roughness=0.5)
    nucleus = kit.add_material("neuron-nucleus", (0.50, 0.25, 0.55), metallic=0.0, roughness=0.6)
    terminal = kit.add_material("neuron-terminal", (0.80, 0.50, 0.30), metallic=0.0, roughness=0.5)

    # Cell body (soma) — star-shaped with organic contour
    soma_obj = kit.primitive_object(f"{ASSET_ID}-soma", "cylinder", soma,
                                     size=(0.022, 0.022, 0.015),
                                     location=(0.0, 0.0, 0.0))

    # Nucleus (visible, slightly protruding)
    nucleus_obj = kit.primitive_object(f"{ASSET_ID}-nucleus", "cylinder", nucleus,
                                        size=(0.010, 0.010, 0.008),
                                        location=(0.0, 0.0, 0.005))

    # Nucleolus (dark spot inside nucleus)
    kit.primitive_object(f"{ASSET_ID}-nucleolus", "cylinder", terminal,
                          size=(0.004, 0.004, 0.004),
                          location=(0.0, 0.0, 0.006))

    # Axon (long cable extending RIGHT along X-axis)
    axon_obj = kit.primitive_object(f"{ASSET_ID}-axon", "cylinder", axon,
                                     size=(0.004, 0.004, 0.10),
                                     location=(0.06, 0.0, 0.0),
                                     rotation_euler=(0.0, 1.57, 0.0))

    # Myelin sheath segments with Nodes of Ranvier (gaps)
    for i in range(6):
        x = 0.02 + i * 0.015
        kit.primitive_object(f"{ASSET_ID}-myelin-{i}", "cylinder", myelin,
                              size=(0.007, 0.007, 0.010),
                              location=(x, 0.0, 0.0),
                              rotation_euler=(0.0, 1.57, 0.0))

    # Dendrites — PRIMARY branches (thick, from soma)
    primary_angles = [0.4, 0.0, -0.4, 0.8, -0.8, 1.2, -1.2]
    for i, angle in enumerate(primary_angles):
        kit.primitive_object(f"{ASSET_ID}-dendrite-{i}", "cylinder", dendrite,
                              size=(0.003, 0.003, 0.020),
                              location=(-0.018, 0.0, 0.0),
                              rotation_euler=(0.0, 1.57, math.pi + angle))

    # Dendrites — SECONDARY branches (thinner, offshoots)
    secondary_positions = [
        (-0.025, 0.003, 0.4), (-0.030, -0.003, -0.3),
        (-0.028, 0.002, 0.6), (-0.032, -0.002, -0.5),
    ]
    for i, (x, z_off, angle) in enumerate(secondary_positions):
        kit.primitive_object(f"{ASSET_ID}-dendrite-sec-{i}", "cylinder", dendrite,
                              size=(0.002, 0.002, 0.012),
                              location=(x, 0.0, z_off),
                              rotation_euler=(0.0, 1.57, math.pi + angle))

    # Axon terminals (branching at right end)
    kit.primitive_object(f"{ASSET_ID}-terminal-1", "cylinder", terminal,
                          size=(0.004, 0.004, 0.008),
                          location=(0.105, 0.0, 0.005))
    kit.primitive_object(f"{ASSET_ID}-terminal-2", "cylinder", terminal,
                          size=(0.004, 0.004, 0.008),
                          location=(0.105, 0.0, -0.005))
    kit.primitive_object(f"{ASSET_ID}-terminal-3", "cylinder", terminal,
                          size=(0.004, 0.004, 0.006),
                          location=(0.108, 0.0, 0.0))

    # Synaptic knobs (small spheres at terminals)
    kit.primitive_object(f"{ASSET_ID}-synapse-1", "cylinder", terminal,
                          size=(0.003, 0.003, 0.003),
                          location=(0.110, 0.0, 0.005))
    kit.primitive_object(f"{ASSET_ID}-synapse-2", "cylinder", terminal,
                          size=(0.003, 0.003, 0.003),
                          location=(0.110, 0.0, -0.005))

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
