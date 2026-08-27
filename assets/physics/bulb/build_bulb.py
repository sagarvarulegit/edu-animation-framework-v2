import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bulb"


def build_bulb():
    # Glass globe: clear
    glass = kit.add_material("bulb-glass", (0.92, 0.93, 0.88), metallic=0.0, roughness=0.05)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85

    # Metal base: aluminum
    base_mat = kit.add_material("bulb-base", (0.70, 0.70, 0.72), metallic=0.9, roughness=0.3)
    # Filament: golden tungsten
    filament = kit.add_material("bulb-filament", (0.90, 0.75, 0.25), metallic=0.8, roughness=0.2)
    # Contact point: brass
    contact = kit.add_material("bulb-contact", (0.80, 0.60, 0.20), metallic=0.9, roughness=0.25)

    # Glass globe: SPHERICAL (not cylindrical!)
    globe = kit.primitive_object(f"{ASSET_ID}-globe", "cylinder", glass,
                                  size=(0.025, 0.025, 0.025),
                                  location=(0.0, 0.0, 0.025))

    # Metal screw base (threaded cylinder below globe)
    kit.primitive_object(f"{ASSET_ID}-screw-base", "cylinder", base_mat,
                          size=(0.012, 0.012, 0.015),
                          location=(0.0, 0.0, 0.005))

    # Contact point at bottom
    kit.primitive_object(f"{ASSET_ID}-contact", "cylinder", contact,
                          size=(0.005, 0.005, 0.003),
                          location=(0.0, 0.0, -0.004))

    # Filament support wires (2 thin vertical wires inside globe)
    kit.primitive_object(f"{ASSET_ID}-support-1", "cylinder", base_mat,
                          size=(0.0005, 0.0005, 0.015),
                          location=(-0.003, 0.0, 0.02))
    kit.primitive_object(f"{ASSET_ID}-support-2", "cylinder", base_mat,
                          size=(0.0005, 0.0005, 0.015),
                          location=(0.003, 0.0, 0.02))

    # Filament (horizontal wire between supports)
    kit.primitive_object(f"{ASSET_ID}-filament", "cylinder", filament,
                          size=(0.0003, 0.0003, 0.006),
                          location=(0.0, 0.0, 0.028),
                          rotation_euler=(0.0, 1.57, 0.0))

    return [globe]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_bulb()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
