import sys
from pathlib import Path
from math import cos, sin, tau

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "magnesium-ribbon"
LENGTH = 0.15
WIDTH = 0.012
THICKNESS = 0.0015
AMPLITUDE = 0.008
WAVELENGTH = 0.05
STATIONS = 140


def build_ribbon():
    material = kit.add_material("magnesium-metal", (0.82, 0.84, 0.87),
                                metallic=1.0, roughness=0.35)
    verts = []
    half_width = WIDTH / 2
    half_thickness = THICKNESS / 2
    for i in range(STATIONS):
        t = i / (STATIONS - 1)
        x = (t - 0.5) * LENGTH
        z = AMPLITUDE * sin(tau * x / WAVELENGTH)
        slope = AMPLITUDE * (tau / WAVELENGTH) * cos(tau * x / WAVELENGTH)
        inv_len = (1.0 + slope ** 2) ** -0.5
        normal = (-slope * inv_len, 0.0, inv_len)
        binormal = (0.0, 1.0, 0.0)
        for sign_b in (+1, -1):
            for sign_n in (+1, -1):
                verts.append((
                    x + binormal[0] * half_width * sign_b + normal[0] * half_thickness * sign_n,
                    binormal[1] * half_width * sign_b,
                    z + binormal[2] * half_width * sign_b + normal[2] * half_thickness * sign_n,
                ))
    faces = []
    for i in range(STATIONS - 1):
        a = i * 4
        b = a + 4
        faces.append((a, a + 1, b + 1, b))
        faces.append((a + 1, a + 2, b + 2, b + 1))
        faces.append((a + 2, a + 3, b + 3, b + 2))
        faces.append((a + 3, a, b, b + 3))
    first = 0
    last = (STATIONS - 1) * 4
    faces.append((first, first + 1, first + 2, first + 3))
    faces.append((last + 3, last + 2, last + 1, last))
    return [kit.mesh_object(ASSET_ID, verts, faces, material)]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_ribbon()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
