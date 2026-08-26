import sys
from pathlib import Path
from math import cos, pi, radians, sin

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "laboratory-tongs"
HINGE = (0.03, 0.0, 0.0)
ARM_LENGTH = 0.22
HINGE_TO_CENTER = 0.03
ARM_TILT = radians(6.0)


def build_tongs():
    steel = kit.add_material("tongs-steel", (0.55, 0.57, 0.60),
                             metallic=1.0, roughness=0.35)
    objects = []
    for side in (+1, -1):
        tilt = ARM_TILT * side
        location = (
            HINGE[0] - HINGE_TO_CENTER * cos(tilt),
            0.009 * side,
            HINGE[2] + HINGE_TO_CENTER * sin(tilt),
        )
        name = f"{ASSET_ID}-arm-{'+' if side > 0 else '-'}"
        objects.append(kit.primitive_object(
            name,
            "cube",
            steel,
            size=(ARM_LENGTH, 0.012, 0.006),
            location=location,
            rotation_euler=(0.0, tilt, 0.0),
        ))
    objects.append(kit.primitive_object(
        f"{ASSET_ID}-hinge",
        "cylinder",
        steel,
        size=(0.014, 0.014, 0.026),
        location=HINGE,
        rotation_euler=(pi / 2, 0.0, 0.0),
    ))
    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_tongs()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
