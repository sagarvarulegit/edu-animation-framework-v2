"""Build a stylized, granular magnesium oxide powder heap for experiment outcomes."""
import sys
from pathlib import Path
import math
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "magnesium-oxide"


def build_magnesium_oxide():
    powder = kit.add_material("magnesium-oxide-powder", (0.94, 0.94, 0.91), 0.0, 0.92)
    objects = [kit.primitive_object(f"{ASSET_ID}-heap", "cone", powder, size=(0.034, 0.008, 0.010), location=(0, 0, 0.005))]
    # A few grains make the product read as powder, rather than a white geometric cone.
    for index in range(22):
        angle = index * 2.39996
        radius = 0.006 + (index % 5) * 0.004
        grain = kit.primitive_object(f"{ASSET_ID}-grain-{index:02d}", "uv_sphere", powder, size=(0.0035, 0.0035, 0.0035),
                                     location=(math.cos(angle) * radius, math.sin(angle) * radius, 0.008 + (index % 3) * 0.001))
        objects.append(grain)
    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene(); objects = build_magnesium_oxide(); kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=48); kit.frame_camera(objects, lens=55.0)
    kit.save_blend(out / f"{ASSET_ID}.blend"); kit.export_glb(out / f"{ASSET_ID}.glb"); kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
