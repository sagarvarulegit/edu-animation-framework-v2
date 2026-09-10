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
    mg_mat = kit.add_material("MgCationMat", (0.02, 0.71, 0.83), metallic=0.6, roughness=0.15)
    o_mat = kit.add_material("OAnionMat", (0.97, 0.44, 0.44), metallic=0.4, roughness=0.2)
    bond_mat = kit.add_material("IonicBondMat", (0.85, 0.88, 0.95), metallic=0.8, roughness=0.3)

    # 3x3x3 Cubic Lattice of alternating Mg²⁺ (smaller) and O²⁻ (larger)
    all_objs = []
    spacing = 0.055

    for x in range(-1, 2):
        for y in range(-1, 2):
            for z in range(-1, 2):
                is_mg = (x + y + z) % 2 == 0
                pos = (x * spacing, y * spacing, z * spacing)
                mat = mg_mat if is_mg else o_mat
                radius = 0.012 if is_mg else 0.018 // 2 * 2.2 * 0.012 # Mg2+ is smaller, O2- is larger
                ion_radius = 0.013 if is_mg else 0.021

                ion = kit.primitive_object(
                    f"ion_{x}_{y}_{z}",
                    "uv_sphere",
                    mat,
                    size=(ion_radius * 2, ion_radius * 2, ion_radius * 2),
                    location=pos
                )
                all_objs.append(ion)

                # Connect bonds along positive axes
                if x < 1:
                    b_pos = ((x + 0.5) * spacing, y * spacing, z * spacing)
                    b = kit.primitive_object(f"bond_x_{x}_{y}_{z}", "cylinder", bond_mat, size=(0.003, 0.003, spacing), location=b_pos, rotation_euler=(0, math.pi / 2, 0))
                    all_objs.append(b)
                if y < 1:
                    b_pos = (x * spacing, (y + 0.5) * spacing, z * spacing)
                    b = kit.primitive_object(f"bond_y_{x}_{y}_{z}", "cylinder", bond_mat, size=(0.003, 0.003, spacing), location=b_pos, rotation_euler=(math.pi / 2, 0, 0))
                    all_objs.append(b)
                if z < 1:
                    b_pos = (x * spacing, y * spacing, (z + 0.5) * spacing)
                    b = kit.primitive_object(f"bond_z_{x}_{y}_{z}", "cylinder", bond_mat, size=(0.003, 0.003, spacing), location=b_pos)
                    all_objs.append(b)

    kit.frame_camera(all_objs, lens=50.0)
    kit.configure_render(width=1280, height=720, samples=24)

    kit.save_blend(out / "magnesium-oxide-lattice.blend")
    kit.export_glb(out / "magnesium-oxide-lattice.glb")
    kit.render_preview(out / "preview.png")
    print("[OK] High-fidelity magnesium-oxide-lattice built and rendered.")


if __name__ == "__main__":
    main()
