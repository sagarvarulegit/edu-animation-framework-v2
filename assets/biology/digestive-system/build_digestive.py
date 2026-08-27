import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "digestive-system"


def build_digestive():
    # Materials
    esophagus_mat = kit.add_material("digest-esophagus", (0.78, 0.55, 0.50), metallic=0.0, roughness=0.6)
    stomach_mat = kit.add_material("digest-stomach", (0.75, 0.45, 0.40), metallic=0.0, roughness=0.65)
    small_int = kit.add_material("digest-small-int", (0.80, 0.60, 0.55), metallic=0.0, roughness=0.6)
    large_int = kit.add_material("digest-large-int", (0.72, 0.50, 0.45), metallic=0.0, roughness=0.65)
    liver_mat = kit.add_material("digest-liver", (0.55, 0.25, 0.20), metallic=0.0, roughness=0.6)
    gallbladder = kit.add_material("digest-gall", (0.45, 0.55, 0.25), metallic=0.0, roughness=0.5)
    pancreas_mat = kit.add_material("digest-pancreas", (0.85, 0.70, 0.50), metallic=0.0, roughness=0.55)
    mouth_mat = kit.add_material("digest-mouth", (0.80, 0.55, 0.50), metallic=0.0, roughness=0.5)
    rectum_mat = kit.add_material("digest-rectum", (0.65, 0.42, 0.38), metallic=0.0, roughness=0.65)

    # Continuous alimentary canal from mouth to anus (vertical layout)
    # Mouth (top)
    kit.primitive_object(f"{ASSET_ID}-mouth", "cube", mouth_mat,
                          size=(0.025, 0.015, 0.01),
                          location=(0.0, 0.0, 0.12))

    # Pharynx
    kit.primitive_object(f"{ASSET_ID}-pharynx", "cylinder", esophagus_mat,
                          size=(0.008, 0.008, 0.008),
                          location=(0.0, 0.0, 0.11))

    # Esophagus (tube down to stomach)
    kit.primitive_object(f"{ASSET_ID}-esophagus", "cylinder", esophagus_mat,
                          size=(0.006, 0.006, 0.035),
                          location=(0.0, 0.0, 0.088))

    # Stomach (J-shaped, wider)
    kit.primitive_object(f"{ASSET_ID}-stomach-body", "cylinder", stomach_mat,
                          size=(0.020, 0.015, 0.025),
                          location=(0.01, 0.0, 0.065))
    # Stomach fundus (upper curve)
    kit.primitive_object(f"{ASSET_ID}-stomach-fundus", "cylinder", stomach_mat,
                          size=(0.015, 0.012, 0.01),
                          location=(0.015, 0.0, 0.078))

    # Liver (triangular, above stomach on right)
    kit.primitive_object(f"{ASSET_ID}-liver", "cube", liver_mat,
                          size=(0.035, 0.012, 0.015),
                          location=(-0.005, 0.0, 0.085))

    # Gallbladder (small pear shape under liver)
    kit.primitive_object(f"{ASSET_ID}-gallbladder", "cylinder", gallbladder,
                          size=(0.005, 0.005, 0.008),
                          location=(0.01, 0.0, 0.075))

    # Pancreas (leaf-shaped, behind stomach)
    kit.primitive_object(f"{ASSET_ID}-pancreas", "cube", pancreas_mat,
                          size=(0.030, 0.008, 0.006),
                          location=(0.0, 0.0, 0.058))

    # Duodenum (C-shaped curve from stomach)
    kit.primitive_object(f"{ASSET_ID}-duodenum", "cylinder", small_int,
                          size=(0.006, 0.006, 0.012),
                          location=(0.0, 0.0, 0.052))

    # Small intestine (coiled tubes — multiple loops)
    coil_positions = [
        (0.005, 0.035), (-0.005, 0.030), (0.008, 0.025),
        (-0.008, 0.020), (0.003, 0.015), (-0.003, 0.010),
        (0.006, 0.005), (-0.006, 0.000),
    ]
    for i, (x_off, z_pos) in enumerate(coil_positions):
        kit.primitive_object(f"{ASSET_ID}-small-int-{i}", "cylinder", small_int,
                              size=(0.005, 0.005, 0.008),
                              location=(x_off, 0.0, z_pos))

    # Large intestine (framing the small intestine)
    # Ascending colon (right side, going up)
    kit.primitive_object(f"{ASSET_ID}-ascending-colon", "cylinder", large_int,
                          size=(0.008, 0.008, 0.04),
                          location=(0.02, 0.0, 0.02),
                          rotation_euler=(0.0, 0.0, 0.0))

    # Transverse colon (across top)
    kit.primitive_object(f"{ASSET_ID}-transverse-colon", "cylinder", large_int,
                          size=(0.008, 0.008, 0.035),
                          location=(0.0, 0.0, 0.045),
                          rotation_euler=(0.0, 1.57, 0.0))

    # Descending colon (left side, going down)
    kit.primitive_object(f"{ASSET_ID}-descending-colon", "cylinder", large_int,
                          size=(0.008, 0.008, 0.035),
                          location=(-0.02, 0.0, 0.025))

    # Sigmoid colon (curved at bottom)
    kit.primitive_object(f"{ASSET_ID}-sigmoid", "cylinder", large_int,
                          size=(0.007, 0.007, 0.01),
                          location=(-0.01, 0.0, 0.005))

    # Rectum
    kit.primitive_object(f"{ASSET_ID}-rectum", "cylinder", rectum_mat,
                          size=(0.008, 0.008, 0.012),
                          location=(0.0, 0.0, -0.005))

    # Anus
    kit.primitive_object(f"{ASSET_ID}-anus", "cylinder", rectum_mat,
                          size=(0.005, 0.005, 0.003),
                          location=(0.0, 0.0, -0.012))

    # Appendix (small tube at caecum)
    kit.primitive_object(f"{ASSET_ID}-appendix", "cylinder", large_int,
                          size=(0.002, 0.002, 0.008),
                          location=(0.018, 0.0, 0.002),
                          rotation_euler=(0.0, 0.0, 0.5))

    return []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_digestive()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
