"""Build a reusable glass Pasteur dropper with a compressible rubber bulb."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
ASSET_ID = "dropper"


def build_dropper():
    glass = kit.add_glass_material("dropper-glass", tint=(0.90, 0.97, 1.0), ior=1.52, roughness=0.015)
    rubber = kit.add_material("dropper-rubber", (0.16, 0.25, 0.52), 0.0, 0.36)
    liquid = kit.add_glass_material("dropper-liquid", tint=(0.82, 0.18, 0.30), ior=1.333, roughness=0.02)

    # Compressible rubber squeeze bulb with neck collar (closed manifold primitives)
    bulb = kit.primitive_object(f"{ASSET_ID}-rubber-bulb", "uv_sphere", rubber, size=(0.044, 0.044, 0.044), location=(0.052, 0.0, 0.0))
    bulb.scale = (1.25, 1.0, 1.0)
    neck = kit.primitive_object(f"{ASSET_ID}-bulb-neck", "cylinder", rubber, size=(0.017, 0.017, 0.026), location=(0.019, 0.0, 0.0), rotation_euler=(0.0, 1.5708, 0.0))

    # Closed 2D lathe profile for glass pipette with inner and outer wall thickness (wall thickness >= 1.0 mm)
    # Forms a completely closed solid manifold shell (0 non-manifold edges)
    pipette_profile = [
        # Top rim (connecting inner and outer walls)
        (0.0032, 0.000),
        (0.0044, 0.000),
        # Outer wall
        (0.0044, 0.008),
        (0.0040, 0.016),
        (0.0040, 0.125),
        (0.0018, 0.165),
        (0.0015, 0.181),
        # Bottom tip rim
        (0.0005, 0.181),
        # Inner wall bore (physical wall thickness >= 1.0 mm throughout)
        (0.0008, 0.165),
        (0.0028, 0.125),
        (0.0028, 0.016),
        (0.0032, 0.008),
        (0.0032, 0.000)  # Closes back to top rim
    ]
    pipette = kit.lathe_object(f"{ASSET_ID}-glass-pipette", pipette_profile, segments=48, material=glass, rotation_euler=(0.0, 1.5708, 0.0), location=(0.008, 0.0, 0.0))

    # Liquid reagent column inside pipette bore (closed manifold solid)
    solution_profile = [
        (0.0, 0.004),
        (0.0026, 0.008),
        (0.0026, 0.095),
        (0.0007, 0.135),
        (0.0, 0.139)
    ]
    solution = kit.lathe_object(f"{ASSET_ID}-solution", solution_profile, segments=48, material=liquid, rotation_euler=(0.0, 1.5708, 0.0), location=(0.008, 0.0, 0.0))
    return [bulb, neck, pipette, solution]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene(); objects = build_dropper(); kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24); kit.frame_camera(objects, lens=58.0)
    kit.save_blend(out / f"{ASSET_ID}.blend"); kit.export_glb(out / f"{ASSET_ID}.glb"); kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
