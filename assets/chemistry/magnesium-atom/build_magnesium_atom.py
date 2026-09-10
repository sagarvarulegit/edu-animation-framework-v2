import math
import sys
from pathlib import Path

# Add shared python asset kit to path
KIT_PATH = Path(__file__).resolve().parent.parent.parent / "python"
if str(KIT_PATH) not in sys.path:
    sys.path.insert(0, str(KIT_PATH))

import edu_asset_kit as kit
import bpy


def make_torus_ring(name, radius, tube_r=0.0009, segments=64, material=None):
    sub = 12
    profile = []
    for j in range(sub + 1):
        ang = 2.0 * math.pi * j / sub
        profile.append((radius + tube_r * math.cos(ang), tube_r * math.sin(ang)))
    return kit.lathe_object(name, profile, segments=segments, material=material)


def main():
    out = kit.output_dir(Path(__file__).parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    # Materials with authentic emission
    proton_mat = kit.add_material("ProtonMat", (0.95, 0.22, 0.22), metallic=0.1, roughness=0.2)
    bsdf_p = proton_mat.node_tree.nodes["Principled BSDF"]
    bsdf_p.inputs["Emission Color"].default_value = (0.95, 0.22, 0.22, 1.0)
    bsdf_p.inputs["Emission Strength"].default_value = 1.2

    neutron_mat = kit.add_material("NeutronMat", (0.45, 0.50, 0.60), metallic=0.3, roughness=0.4)

    # Unified electron styling synchronized to design token (particle_electron / cyan #38bdf8)
    electron_mat = kit.add_material_from_token("ElectronMat", "particle_electron")
    bsdf_e = electron_mat.node_tree.nodes["Principled BSDF"]
    bsdf_e.inputs["Emission Color"].default_value = (0.15, 0.78, 1.0, 1.0)
    bsdf_e.inputs["Emission Strength"].default_value = 3.0

    ring_mat = kit.add_material("RingMat", (0.25, 0.40, 0.60), metallic=0.6, roughness=0.3)

    # 1. Nucleons in tightly-packed spherical nucleus (12 protons, 12 neutrons)
    all_objs = []
    golden_ratio = (1 + math.sqrt(5)) / 2
    for i in range(24):
        theta = 2 * math.pi * i / golden_ratio
        phi = math.acos(1 - 2 * (i + 0.5) / 24)
        r = 0.016 * math.pow((i + 1) / 24, 1 / 3)
        x = r * math.sin(phi) * math.cos(theta)
        y = r * math.sin(phi) * math.sin(theta)
        z = r * math.cos(phi)
        mat = proton_mat if i < 12 else neutron_mat
        nuc = kit.primitive_object(f"nucleon_{i}", "uv_sphere", mat, size=(0.009, 0.009, 0.009), location=(x, y, z))
        all_objs.append(nuc)

    # 2. Concentric Electron Shells [2, 8, 2] (K, L, M)
    shells = [
        {"radius": 0.042, "count": 2},
        {"radius": 0.076, "count": 8},
        {"radius": 0.112, "count": 2},
    ]

    for s_idx, shell in enumerate(shells):
        r = shell["radius"]
        count = shell["count"]
        ring = make_torus_ring(f"shell_ring_{s_idx}", r, tube_r=0.0008, material=ring_mat)
        all_objs.append(ring)

        for e_idx in range(count):
            angle = (2 * math.pi * e_idx) / count
            ex = r * math.cos(angle)
            ey = r * math.sin(angle)
            elec = kit.primitive_object(
                f"electron_{s_idx}_{e_idx}",
                "uv_sphere",
                electron_mat,
                size=(0.008, 0.008, 0.008),
                location=(ex, ey, 0.0)
            )
            all_objs.append(elec)

    kit.frame_camera(all_objs, lens=50.0)
    kit.configure_render(width=1280, height=720, samples=24)

    kit.save_blend(out / "magnesium-atom.blend")
    kit.export_glb(out / "magnesium-atom.glb")
    kit.render_preview(out / "preview.png")
    print("[OK] High-fidelity magnesium-atom built and rendered.")


if __name__ == "__main__":
    main()
