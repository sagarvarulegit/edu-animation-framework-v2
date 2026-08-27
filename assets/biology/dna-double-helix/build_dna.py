import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = "dna-double-helix"


def build_dna():
    # Materials
    backbone = kit.add_material("dna-backbone", (0.85, 0.55, 0.20), metallic=0.0, roughness=0.5)
    # Base pair colors: A=Red, T=Yellow, G=Blue, C=Green
    at_a = kit.add_material("dna-adenine", (0.85, 0.20, 0.20), metallic=0.0, roughness=0.5)
    at_t = kit.add_material("dna-thymine", (0.90, 0.85, 0.20), metallic=0.0, roughness=0.5)
    gc_g = kit.add_material("dna-guanine", (0.20, 0.45, 0.80), metallic=0.0, roughness=0.5)
    gc_c = kit.add_material("dna-cytosine", (0.20, 0.70, 0.35), metallic=0.0, roughness=0.5)

    radius = 0.012
    height = 0.10
    turns = 2.0
    steps = 40

    # Create continuous helical backbone using bmesh tube
    for strand in range(2):
        bm = bmesh.new()
        prev_vert = None
        for i in range(steps + 1):
            t = i / steps
            angle = t * turns * 2 * math.pi + strand * math.pi  # offset 180°
            y = -height / 2 + t * height
            x = radius * math.cos(angle)
            z = radius * math.sin(angle)
            vert = bm.verts.new((x, y, z))
            if prev_vert is not None:
                bm.edges.new([prev_vert, vert])
            prev_vert = vert

        # Convert edges to tube mesh
        mesh = bpy.data.meshes.new(f"{ASSET_ID}-backbone-{strand}")
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(f"{ASSET_ID}-backbone-{strand}", mesh)
        bpy.context.collection.objects.link(obj)
        # Add skin modifier for tube thickness
        skin = obj.modifiers.new(name="skin", type='SKIN')
        # Set skin radius for each vertex
        for v in obj.data.skin_vertices[0].data:
            v.radius = (0.0015, 0.0015)
        obj.data.materials.append(backbone)

    # Base pairs connecting the two strands
    pair_mats = [(at_a, at_t), (gc_g, gc_c)]
    for i in range(0, steps, 3):  # every 3rd step
        t = i / steps
        angle1 = t * turns * 2 * math.pi
        angle2 = angle1 + math.pi
        y = -height / 2 + t * height

        x1 = radius * math.cos(angle1)
        z1 = radius * math.sin(angle1)
        x2 = radius * math.cos(angle2)
        z2 = radius * math.sin(angle2)

        # Direction vector between strands
        dx = x2 - x1
        dz = z2 - z1
        length = math.sqrt(dx*dx + dz*dz)
        angle = math.atan2(dz, dx)

        mat_pair = pair_mats[(i // 3) % 2]

        # Two half-rungs with different colors (complementary bases)
        mx = (x1 + x2) / 2
        mz = (z1 + z2) / 2

        kit.primitive_object(f"{ASSET_ID}-pair-{i}-a", "cylinder", mat_pair[0],
                              size=(0.0015, 0.0015, length / 2),
                              location=(mx - dx/4, y, mz - dz/4),
                              rotation_euler=(0.0, 0.0, angle))

        kit.primitive_object(f"{ASSET_ID}-pair-{i}-b", "cylinder", mat_pair[1],
                              size=(0.0015, 0.0015, length / 2),
                              location=(mx + dx/4, y, mz + dz/4),
                              rotation_euler=(0.0, 0.0, angle))

    return []


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
