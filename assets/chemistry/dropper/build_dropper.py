"""Build a reusable glass Pasteur dropper with a compressible rubber bulb."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
ASSET_ID = "dropper"


def build_dropper():
    glass = kit.add_glass_material("dropper-glass", tint=(0.90, 0.97, 1.0), roughness=0.015)
    rubber = kit.add_material("dropper-rubber", (0.16, 0.25, 0.52), 0.0, 0.36)
    liquid = kit.add_glass_material("dropper-liquid", tint=(0.82, 0.18, 0.30), ior=1.333, roughness=0.02)
    bulb = kit.primitive_object(f"{ASSET_ID}-rubber-bulb", "uv_sphere", rubber, size=(0.044, 0.044, 0.044), location=(0.052, 0.0, 0.0))
    bulb.scale = (1.25, 1.0, 1.0)
    neck = kit.primitive_object(f"{ASSET_ID}-bulb-neck", "cylinder", rubber, size=(0.017, 0.017, 0.026), location=(0.019, 0.0, 0.0), rotation_euler=(0.0, 1.5708, 0.0))
    pipette = kit.lathe_object(f"{ASSET_ID}-glass-pipette", [(0.0032, 0.0), (0.0040, 0.008), (0.0040, 0.125), (0.0010, 0.165), (0.00045, 0.181)], segments=48, material=glass, rotation_euler=(0.0, 1.5708, 0.0), location=(0.008, 0.0, 0.0))
    solution = kit.lathe_object(f"{ASSET_ID}-solution", [(0.0, 0.004), (0.0024, 0.009), (0.0024, 0.095), (0.0008, 0.135), (0.0, 0.139)], segments=48, material=liquid, rotation_euler=(0.0, 1.5708, 0.0), location=(0.008, 0.0, 0.0))
    return [bulb, neck, pipette, solution]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene(); objects = build_dropper(); kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=48); kit.frame_camera(objects, lens=58.0)
    kit.save_blend(out / f"{ASSET_ID}.blend"); kit.export_glb(out / f"{ASSET_ID}.glb"); kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
