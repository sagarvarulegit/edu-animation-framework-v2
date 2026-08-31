import math
import sys
from pathlib import Path

KIT_PATH = Path(__file__).resolve().parent.parent.parent / "python"
if str(KIT_PATH) not in sys.path:
    sys.path.insert(0, str(KIT_PATH))

import edu_asset_kit as kit
import bpy


def main():
    out = kit.output_dir(Path(__file__).parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    # Materials
    core_mat = kit.add_material("OxygenCoreMat", (0.97, 0.44, 0.44), metallic=0.3, roughness=0.2)
    proton_mat = kit.add_material("ProtonMat", (0.94, 0.27, 0.27), metallic=0.1, roughness=0.3)
    neutron_mat = kit.add_material("NeutronMat", (0.39, 0.45, 0.55), metallic=0.1, roughness=0.5)
    electron_mat = kit.add_material("OxygenElectronMat", (0.98, 0.44, 0.52), metallic=0.8, roughness=0.1)
    ring_mat = kit.add_material("RingMat", (0.38, 0.20, 0.25), metallic=0.5, roughness=0.4)

    # 1. Central Nucleus Sphere
    core = kit.primitive_object("oxygen_nucleus", "uv_sphere", core_mat, size=(0.044, 0.044, 0.044))

    # Nucleons (8 protons, 8 neutrons)
    nucleons = []
    golden_ratio = (1 + math.sqrt(5)) / 2
    for i in range(16):
        theta = 2 * math.pi * i / golden_ratio
        phi = math.acos(1 - 2 * (i + 0.5) / 16)
        r = 0.018 * math.pow((i + 1) / 16, 1 / 3)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        mat = proton_mat if i < 8 else neutron_mat
        nuc = kit.primitive_object(f"nucleon_{i}", "uv_sphere", mat, size=(0.010, 0.010, 0.010), location=(x, y, z))
        nucleons.append(nuc)

    # 2. Concentric Electron Shells [2, 6]
    shells = [
        {"radius": 0.055, "count": 2},
        {"radius": 0.095, "count": 6},
    ]

    all_objs = [core, *nucleons]

    for s_idx, shell in enumerate(shells):
        r = shell["radius"]
        count = shell["count"]
        ring = kit.primitive_object(f"shell_ring_{s_idx}", "cylinder", ring_mat, size=(r * 2, r * 2, 0.0016))
        all_objs.append(ring)

        for e_idx in range(count):
            angle = (2 * math.pi * e_idx) / count
            ex = r * math.cos(angle)
            ey = r * math.sin(angle)
            elec = kit.primitive_object(
                f"electron_{s_idx}_{e_idx}",
                "uv_sphere",
                electron_mat,
                size=(0.010, 0.010, 0.010),
                location=(ex, ey, 0.0)
            )
            all_objs.append(elec)

    kit.frame_camera(all_objs, lens=50.0)
    kit.configure_render(width=1280, height=720, samples=32)

    kit.save_blend(out / "oxygen-atom.blend")
    kit.export_glb(out / "oxygen-atom.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
