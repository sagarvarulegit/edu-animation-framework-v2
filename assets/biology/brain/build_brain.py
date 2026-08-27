import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "brain"


def build_brain():
    # Cerebrum: pinkish-grey (real brain color)
    cerebrum = kit.add_material("brain-cerebrum", (0.82, 0.65, 0.58), metallic=0.0, roughness=0.7)
    # Cerebellum: slightly darker
    cerebellum = kit.add_material("brain-cerebellum", (0.75, 0.55, 0.48), metallic=0.0, roughness=0.75)
    # Brain stem: darker brown
    stem_mat = kit.add_material("brain-stem", (0.65, 0.45, 0.38), metallic=0.0, roughness=0.7)
    # Label
    label_bg = kit.add_material("label-white", (0.95, 0.95, 0.95), roughness=0.4)

    # Cerebrum (large, two hemispheres)
    cerebrum_l = kit.primitive_object(f"{ASSET_ID}-cerebrum-left", "cylinder", cerebrum,
                                       size=(0.04, 0.035, 0.045),
                                       location=(-0.015, 0.0, 0.04))
    cerebrum_r = kit.primitive_object(f"{ASSET_ID}-cerebrum-right", "cylinder", cerebrum,
                                       size=(0.04, 0.035, 0.045),
                                       location=(0.015, 0.0, 0.04))

    # Cerebellum (back, smaller, bumpy)
    cerebellum_obj = kit.primitive_object(f"{ASSET_ID}-cerebellum", "cylinder", cerebellum,
                                           size=(0.03, 0.025, 0.025),
                                           location=(0.0, 0.02, 0.02))

    # Brain stem
    stem = kit.primitive_object(f"{ASSET_ID}-stem", "cylinder", stem_mat,
                                size=(0.012, 0.012, 0.03),
                                location=(0.0, 0.025, 0.01))

    return [cerebrum_l, cerebrum_r, cerebellum_obj, stem]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_brain()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
