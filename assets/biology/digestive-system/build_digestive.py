import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "digestive-system"


def build_digestive():
    # Mouth/oral cavity: pink
    mouth_mat = kit.add_material("mouth-pink", (0.85, 0.55, 0.50),
                                 metallic=0.0, roughness=0.6)
    # Esophagus: pale pink tube
    esophagus_mat = kit.add_material("esophagus", (0.88, 0.65, 0.58),
                                     metallic=0.0, roughness=0.55)
    # Stomach: darker pink-red (muscular organ)
    stomach_mat = kit.add_material("stomach", (0.75, 0.35, 0.30),
                                   metallic=0.0, roughness=0.5)
    # Small intestine: pale pink, coiled
    small_int_mat = kit.add_material("small-intestine", (0.90, 0.72, 0.65),
                                     metallic=0.0, roughness=0.55)
    # Large intestine: darker, wider
    large_int_mat = kit.add_material("large-intestine", (0.82, 0.58, 0.50),
                                     metallic=0.0, roughness=0.6)
    # Liver: dark reddish-brown (accessory organ)
    liver_mat = kit.add_material("liver", (0.55, 0.20, 0.15),
                                 metallic=0.0, roughness=0.7)

    # === MOUTH (top) ===
    mouth = kit.primitive_object(f"{ASSET_ID}-mouth", "cube", mouth_mat,
                                 size=(0.022, 0.018, 0.014),
                                 location=(0.0, 0.0, 0.155))

    # === ESOPHAGUS (tube going down) ===
    esophagus = kit.primitive_object(f"{ASSET_ID}-esophagus", "cylinder", esophagus_mat,
                                      size=(0.009, 0.009, 0.045),
                                      location=(0.0, 0.0, 0.125))

    # === STOMACH (bean-shaped, larger) ===
    stomach = kit.primitive_object(f"{ASSET_ID}-stomach", "cylinder", stomach_mat,
                                   size=(0.040, 0.028, 0.035),
                                   location=(0.012, 0.0, 0.095))

    # === LIVER (above stomach, right side) ===
    liver = kit.primitive_object(f"{ASSET_ID}-liver", "cube", liver_mat,
                                 size=(0.045, 0.020, 0.018),
                                 location=(-0.015, 0.0, 0.115))

    # === SMALL INTESTINE (coiled tube, center) ===
    small_parts = []
    # Create a spiral-like arrangement
    for i in range(8):
        angle = i * 0.8
        x = 0.005 + 0.010 * (i % 3) - 0.010
        z = 0.055 - 0.006 * (i // 3)
        si = kit.primitive_object(f"{ASSET_ID}-small-int-{i}", "cylinder", small_int_mat,
                                   size=(0.007, 0.007, 0.028),
                                   location=(x, 0.0, z),
                                   rotation_euler=(0.0, 0.0, 0.4 * ((-1) ** i)))
        small_parts.append(si)

    # === LARGE INTESTINE (wider tube, frames the small intestine) ===
    large_parts = []
    # Ascending colon (right side, going up)
    large_parts.append(kit.primitive_object(f"{ASSET_ID}-large-asc", "cylinder", large_int_mat,
                                             size=(0.012, 0.012, 0.040),
                                             location=(0.025, 0.0, 0.055)))
    # Transverse colon (top, going across)
    large_parts.append(kit.primitive_object(f"{ASSET_ID}-large-trans", "cylinder", large_int_mat,
                                             size=(0.012, 0.012, 0.050),
                                             location=(0.0, 0.0, 0.078),
                                             rotation_euler=(0.0, 1.57, 0.0)))
    # Descending colon (left side, going down)
    large_parts.append(kit.primitive_object(f"{ASSET_ID}-large-desc", "cylinder", large_int_mat,
                                             size=(0.012, 0.012, 0.040),
                                             location=(-0.025, 0.0, 0.055)))

    # === RECTUM (bottom) ===
    rectum = kit.primitive_object(f"{ASSET_ID}-rectum", "cylinder", large_int_mat,
                                   size=(0.009, 0.009, 0.018),
                                   location=(0.0, 0.0, 0.009))

    return [mouth, esophagus, stomach, liver] + small_parts + large_parts + [rectum]


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
