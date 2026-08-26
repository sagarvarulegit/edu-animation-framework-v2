import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bulb"


def build_bulb():
    # Glass globe: warm clear glass
    glass = kit.add_material("bulb-glass", (0.92, 0.93, 0.88),
                             metallic=0.0, roughness=0.04)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.52

    # Metal base: dark threaded aluminum
    metal = kit.add_material("bulb-aluminum", (0.45, 0.45, 0.48),
                             metallic=0.92, roughness=0.35)

    # Filament: bright tungsten (visible when lit)
    filament_mat = kit.add_material("bulb-filament", (0.95, 0.80, 0.30),
                                    metallic=0.85, roughness=0.3)

    # Contact point: brass
    contact_mat = kit.add_material("bulb-contact", (0.75, 0.55, 0.20),
                                   metallic=0.9, roughness=0.25)

    # Glass globe (sphere approximation using cylinder with equal dimensions)
    globe = kit.primitive_object(f"{ASSET_ID}-globe", "cylinder", glass,
                                  size=(0.035, 0.035, 0.035),
                                  location=(0.0, 0.0, 0.035))

    # Neck (narrow section connecting globe to base)
    neck = kit.primitive_object(f"{ASSET_ID}-neck", "cylinder", glass,
                                size=(0.012, 0.012, 0.008),
                                location=(0.0, 0.0, 0.016))

    # Metal screw base (threaded section)
    base = kit.primitive_object(f"{ASSET_ID}-base", "cylinder", metal,
                                size=(0.016, 0.016, 0.012),
                                location=(0.0, 0.0, 0.008))

    # Thread rings (3 visible grooves)
    for i in range(3):
        ring = kit.primitive_object(f"{ASSET_ID}-ring-{i}", "cylinder", metal,
                                     size=(0.017, 0.017, 0.002),
                                     location=(0.0, 0.0, 0.004 + i * 0.004))

    # Contact point at bottom
    contact = kit.primitive_object(f"{ASSET_ID}-contact", "cylinder", contact_mat,
                                    size=(0.006, 0.006, 0.003),
                                    location=(0.0, 0.0, 0.0015))

    # Filament (thin wire inside globe)
    filament = kit.primitive_object(f"{ASSET_ID}-filament", "cylinder", filament_mat,
                                    size=(0.0015, 0.0015, 0.018),
                                    location=(0.0, 0.0, 0.035))

    return [globe, neck, base, contact, filament]


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
