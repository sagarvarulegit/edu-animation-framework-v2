import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "human-eye"


def build_eye():
    # Sclera: off-white
    sclera = kit.add_material("eye-sclera", (0.92, 0.90, 0.85), metallic=0.0, roughness=0.4)
    # Iris: blue (common)
    iris = kit.add_material("eye-iris", (0.25, 0.45, 0.75), metallic=0.0, roughness=0.5)
    # Pupil: black
    pupil = kit.add_material("eye-pupil", (0.02, 0.02, 0.02), metallic=0.0, roughness=0.8)
    # Lens: transparent
    lens_mat = kit.add_material("eye-lens", (0.90, 0.92, 0.95), metallic=0.0, roughness=0.05)
    lens_mat.use_nodes = True
    bsdf = lens_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    # Retina: pinkish-red
    retina = kit.add_material("eye-retina", (0.80, 0.40, 0.35), metallic=0.0, roughness=0.6)
    # Optic nerve: yellow
    nerve = kit.add_material("eye-nerve", (0.85, 0.80, 0.35), metallic=0.0, roughness=0.5)

    # Outer eyeball (sclera)
    eyeball = kit.primitive_object(f"{ASSET_ID}-eyeball", "cylinder", sclera,
                                    size=(0.05, 0.05, 0.05),
                                    location=(0.0, 0.0, 0.0))

    # Iris (front disc)
    iris_obj = kit.primitive_object(f"{ASSET_ID}-iris", "cylinder", iris,
                                     size=(0.025, 0.025, 0.003),
                                     location=(0.0, -0.024, 0.0))

    # Pupil (center of iris)
    pupil_obj = kit.primitive_object(f"{ASSET_ID}-pupil", "cylinder", pupil,
                                      size=(0.010, 0.010, 0.004),
                                      location=(0.0, -0.026, 0.0))

    # Lens (behind pupil)
    lens = kit.primitive_object(f"{ASSET_ID}-lens", "cylinder", lens_mat,
                                 size=(0.020, 0.020, 0.008),
                                 location=(0.0, -0.018, 0.0))

    # Retina (back inner surface)
    retina_obj = kit.primitive_object(f"{ASSET_ID}-retina", "cylinder", retina,
                                       size=(0.048, 0.048, 0.005),
                                       location=(0.0, 0.022, 0.0))

    # Optic nerve (exits back)
    nerve_obj = kit.primitive_object(f"{ASSET_ID}-optic-nerve", "cylinder", nerve,
                                      size=(0.008, 0.008, 0.02),
                                      location=(0.0, 0.035, 0.0))

    return [eyeball, iris_obj, pupil_obj, lens, retina_obj, nerve_obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_eye()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
