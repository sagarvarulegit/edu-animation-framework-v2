import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "glass-slab"


def build_slab():
    glass = kit.add_material("slab-glass", (0.88, 0.92, 0.96), metallic=0.0, roughness=0.02)
    glass.use_nodes = True
    bsdf = glass.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.90
    bsdf.inputs["IOR"].default_value = 1.52

    # Rectangular glass slab
    slab = kit.primitive_object(f"{ASSET_ID}-slab", "cube", glass,
                                 size=(0.10, 0.06, 0.02),
                                 location=(0.0, 0.0, 0.0))

    return [slab]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_slab()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
