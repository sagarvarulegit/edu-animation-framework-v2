import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "human-heart"


def build_heart():
    # Muscle tissue: deep reddish-brown (realistic)
    muscle = kit.add_material("heart-muscle", (0.55, 0.12, 0.10),
                              metallic=0.0, roughness=0.75)
    # Oxygenated blood: bright red
    oxygenated = kit.add_material("heart-oxy", (0.90, 0.18, 0.12),
                                  metallic=0.0, roughness=0.6)
    # Deoxygenated blood: deep blue-purple
    deoxygenated = kit.add_material("heart-deoxy", (0.18, 0.22, 0.60),
                                    metallic=0.0, roughness=0.6)
    # Valve tissue: pale pink
    valve = kit.add_material("heart-valve", (0.88, 0.72, 0.62),
                             metallic=0.0, roughness=0.5)
    # Label background
    label_bg = kit.add_material("label-white", (0.95, 0.95, 0.95), roughness=0.4)

    # === CHAMBERS (organic shapes using scaled cylinders) ===

    # Right atrium (upper right, rounded)
    ra = kit.primitive_object(f"{ASSET_ID}-right-atrium", "cylinder", deoxygenated,
                              size=(0.025, 0.022, 0.020),
                              location=(0.014, 0.0, 0.032))

    # Left atrium (upper left, slightly smaller)
    la = kit.primitive_object(f"{ASSET_ID}-left-atrium", "cylinder", oxygenated,
                              size=(0.022, 0.020, 0.020),
                              location=(-0.012, 0.0, 0.034))

    # Right ventricle (lower right, thicker walls)
    rv = kit.primitive_object(f"{ASSET_ID}-right-ventricle", "cone", deoxygenated,
                              size=(0.030, 0.015, 0.038),
                              location=(0.010, 0.0, 0.008))

    # Left ventricle (lower left, thickest walls - pumps to body)
    lv = kit.primitive_object(f"{ASSET_ID}-left-ventricle", "cone", oxygenated,
                              size=(0.028, 0.012, 0.042),
                              location=(-0.008, 0.0, 0.006))

    # Septum (thick dividing wall)
    septum = kit.primitive_object(f"{ASSET_ID}-septum", "cube", muscle,
                                  size=(0.004, 0.022, 0.055),
                                  location=(0.0, 0.0, 0.022))

    # === VESSELS (color-coded for oxygenation) ===

    # Aorta (large, from left ventricle, arching over)
    aorta = kit.primitive_object(f"{ASSET_ID}-aorta", "cylinder", oxygenated,
                                  size=(0.014, 0.014, 0.025),
                                  location=(-0.006, 0.0, 0.060))

    # Superior vena cava (into right atrium, blue)
    svc = kit.primitive_object(f"{ASSET_ID}-svc", "cylinder", deoxygenated,
                               size=(0.010, 0.010, 0.022),
                               location=(0.016, 0.0, 0.055))

    # Pulmonary artery (from right ventricle, blue - goes to lungs)
    pa = kit.primitive_object(f"{ASSET_ID}-pulmonary-artery", "cylinder", deoxygenated,
                              size=(0.011, 0.011, 0.020),
                              location=(0.006, 0.0, 0.055))

    # Pulmonary veins (into left atrium, red - from lungs)
    pv = kit.primitive_object(f"{ASSET_ID}-pulmonary-veins", "cylinder", oxygenated,
                              size=(0.008, 0.008, 0.015),
                              location=(-0.014, 0.0, 0.050))

    return [ra, la, rv, lv, septum, aorta, svc, pa, pv]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_heart()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
