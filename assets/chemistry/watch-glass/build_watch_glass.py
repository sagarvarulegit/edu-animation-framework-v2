"""Build a reusable 80 mm borosilicate watch glass."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "watch-glass"


def build_watch_glass():
    glass = kit.add_glass_material("watch-glass-borosilicate", tint=(0.92, 0.97, 1.0), roughness=0.012)
    profile = [(0.0, 0.003), (0.016, 0.0035), (0.030, 0.006), (0.040, 0.011), (0.041, 0.012),
               (0.040, 0.013), (0.030, 0.008), (0.016, 0.0055), (0.0, 0.005)]
    return [kit.lathe_object(ASSET_ID, profile, segments=64, material=glass)]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene(); objects = build_watch_glass(); kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=48); kit.frame_camera(objects, lens=55.0)
    kit.save_blend(out / f"{ASSET_ID}.blend"); kit.export_glb(out / f"{ASSET_ID}.glb"); kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
