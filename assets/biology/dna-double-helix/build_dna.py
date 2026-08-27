import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "dna-double-helix"


def build_dna():
    # Sugar-phosphate backbone: warm orange
    backbone = kit.add_material("dna-backbone", (0.85, 0.55, 0.20), metallic=0.0, roughness=0.5)
    # Base pairs: 4 colors (A-T, G-C)
    at_color = kit.add_material("dna-AT", (0.85, 0.20, 0.20), metallic=0.0, roughness=0.5)
    gc_color = kit.add_material("dna-GC", (0.20, 0.55, 0.80), metallic=0.0, roughness=0.5)

    radius = 0.015
    height = 0.12
    turns = 2.5
    steps = 30

    backbone_parts = []
    pair_parts = []

    for i in range(steps):
        t = i / steps
        angle = t * turns * 2 * math.pi
        y = -height / 2 + t * height

        # Strand 1
        x1 = radius * math.cos(angle)
        z1 = radius * math.sin(angle)
        kit.primitive_object(f"{ASSET_ID}-backbone-{i}-a", "cylinder", backbone,
                              size=(0.003, 0.003, 0.005),
                              location=(x1, y, z1))

        # Strand 2 (opposite side)
        x2 = radius * math.cos(angle + math.pi)
        z2 = radius * math.sin(angle + math.pi)
        kit.primitive_object(f"{ASSET_ID}-backbone-{i}-b", "cylinder", backbone,
                              size=(0.003, 0.003, 0.005),
                              location=(x2, y, z2))

        # Base pair connecting strands (every 3rd step)
        if i % 3 == 0:
            color = at_color if (i // 3) % 2 == 0 else gc_color
            # Calculate midpoint and direction
            mx = (x1 + x2) / 2
            mz = (z1 + z2) / 2
            length = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)
            kit.primitive_object(f"{ASSET_ID}-pair-{i}", "cylinder", color,
                                  size=(0.002, 0.002, length),
                                  location=(mx, y, mz),
                                  rotation_euler=(0.0, 0.0, angle))

    # Return objects for camera framing (collect all backbone parts)
    import bpy
    objects = [o for o in bpy.context.collection.objects if o.name.startswith(ASSET_ID)]
    return objects if objects else []


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_dna()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects, lens=80.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
