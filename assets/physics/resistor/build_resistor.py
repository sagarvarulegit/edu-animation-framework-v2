import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "resistor"


def build_resistor():
    # Body: tan/beige
    body_mat = kit.add_material("resistor-body", (0.82, 0.75, 0.55), metallic=0.0, roughness=0.6)
    # Color bands: Brown, Black, Red, Gold (1kΩ)
    brown = kit.add_material("band-brown", (0.45, 0.22, 0.08), metallic=0.0, roughness=0.4)
    black = kit.add_material("band-black", (0.05, 0.05, 0.05), metallic=0.0, roughness=0.4)
    red = kit.add_material("band-red", (0.80, 0.12, 0.10), metallic=0.0, roughness=0.4)
    gold = kit.add_material("band-gold", (0.85, 0.72, 0.20), metallic=0.8, roughness=0.25)
    # Wire leads: silver
    lead = kit.add_material("resistor-lead", (0.75, 0.75, 0.78), metallic=0.9, roughness=0.3)

    # Axial horizontal body (correct proportions: 7mm long, 2.5mm diameter)
    body = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", body_mat,
                                 size=(0.0025, 0.0025, 0.007),
                                 location=(0.0, 0.0, 0.0),
                                 rotation_euler=(0.0, 1.57, 0.0))  # Horizontal along X

    # Color bands (thin coaxial rings along the body)
    band_positions = [-0.002, -0.0005, 0.001, 0.0025]
    band_mats = [brown, black, red, gold]
    for i, (pos, mat) in enumerate(zip(band_positions, band_mats)):
        kit.primitive_object(f"{ASSET_ID}-band-{i}", "cylinder", mat,
                              size=(0.0028, 0.0028, 0.0005),
                              location=(pos, 0.0, 0.0),
                              rotation_euler=(0.0, 1.57, 0.0))

    # Wire leads extending horizontally from both ends
    kit.primitive_object(f"{ASSET_ID}-lead-left", "cylinder", lead,
                          size=(0.0005, 0.0005, 0.015),
                          location=(-0.011, 0.0, 0.0),
                          rotation_euler=(0.0, 1.57, 0.0))

    kit.primitive_object(f"{ASSET_ID}-lead-right", "cylinder", lead,
                          size=(0.0005, 0.0005, 0.015),
                          location=(0.011, 0.0, 0.0),
                          rotation_euler=(0.0, 1.57, 0.0))

    return [body]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_resistor()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
