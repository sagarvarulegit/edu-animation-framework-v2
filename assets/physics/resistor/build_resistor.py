import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "resistor"


def build_resistor():
    # Tan/beige ceramic body (real resistors)
    body_mat = kit.add_material("resistor-body", (0.82, 0.72, 0.55),
                                metallic=0.0, roughness=0.65)
    # Silver wire leads
    wire_mat = kit.add_material("resistor-wire", (0.72, 0.72, 0.74),
                                metallic=0.95, roughness=0.2)

    # Color bands (standard resistor code: Brown-Black-Red-Gold = 1kΩ ±5%)
    band_colors = [
        (0.60, 0.30, 0.10, "Brown"),    # 1
        (0.05, 0.05, 0.05, "Black"),    # 0
        (0.85, 0.10, 0.10, "Red"),      # ×100
        (0.80, 0.65, 0.15, "Gold"),     # ±5%
    ]

    # Body (larger for visibility: 8mm x 3mm)
    body = kit.primitive_object(f"{ASSET_ID}-body", "cylinder", body_mat,
                                size=(0.008, 0.008, 0.003),
                                location=(0.0, 0.0, 0.0))

    # Color bands (visible rings on body)
    bands = []
    offsets = [-0.0009, -0.0003, 0.0003, 0.0009]
    for i, (off, (r, g, b, name)) in enumerate(zip(offsets, band_colors)):
        mat = kit.add_material(f"band-{name}", (r, g, b), roughness=0.5)
        band = kit.primitive_object(f"{ASSET_ID}-band-{i}", "cylinder", mat,
                                     size=(0.0085, 0.0085, 0.0004),
                                     location=(0.0, 0.0, off))
        bands.append(band)

    # Wire leads (thicker, longer for visibility)
    lead_l = kit.primitive_object(f"{ASSET_ID}-lead-left", "cylinder", wire_mat,
                                   size=(0.0012, 0.0012, 0.012),
                                   location=(0.0, 0.0, -0.0075))
    lead_r = kit.primitive_object(f"{ASSET_ID}-lead-right", "cylinder", wire_mat,
                                   size=(0.0012, 0.0012, 0.012),
                                   location=(0.0, 0.0, 0.0075))

    return [body] + bands + [lead_l, lead_r]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_resistor()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects, lens=100.0)  # Macro view
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
