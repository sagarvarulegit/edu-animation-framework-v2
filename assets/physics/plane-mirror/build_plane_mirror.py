import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "plane-mirror"


def build_mirror():
    # Mirror: bright silver (like real mirror coating)
    mirror_mat = kit.add_material("mirror-surface", (0.88, 0.90, 0.93),
                                  metallic=1.0, roughness=0.01)
    # Frame: warm wood tone (light oak)
    frame_mat = kit.add_material("mirror-frame", (0.55, 0.38, 0.22),
                                 metallic=0.0, roughness=0.6)

    # Reflective surface (slightly recessed)
    surface = kit.primitive_object(f"{ASSET_ID}-surface", "cube", mirror_mat,
                                   size=(0.12, 0.08, 0.004),
                                   location=(0.0, 0.0, 0.0))

    # Frame strips (4 sides, visible contrast)
    fw, fd = 0.008, 0.010
    frame_parts = [
        kit.primitive_object(f"{ASSET_ID}-frame-top", "cube", frame_mat,
                             size=(0.12 + 2*fw, fw, fd),
                             location=(0.0, 0.04 + fw/2, 0.0)),
        kit.primitive_object(f"{ASSET_ID}-frame-bottom", "cube", frame_mat,
                             size=(0.12 + 2*fw, fw, fd),
                             location=(0.0, -0.04 - fw/2, 0.0)),
        kit.primitive_object(f"{ASSET_ID}-frame-left", "cube", frame_mat,
                             size=(fw, 0.08, fd),
                             location=(-0.06 - fw/2, 0.0, 0.0)),
        kit.primitive_object(f"{ASSET_ID}-frame-right", "cube", frame_mat,
                             size=(fw, 0.08, fd),
                             location=(0.06 + fw/2, 0.0, 0.0)),
    ]

    # Backing (dark cardboard)
    backing_mat = kit.add_material("mirror-back", (0.15, 0.12, 0.10),
                                   metallic=0.0, roughness=0.8)
    backing = kit.primitive_object(f"{ASSET_ID}-backing", "cube", backing_mat,
                                   size=(0.13, 0.09, 0.003),
                                   location=(0.0, 0.0, -0.004))

    return [surface, backing] + frame_parts


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_mirror()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
