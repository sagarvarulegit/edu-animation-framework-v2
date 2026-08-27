import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh

ASSET_ID = "brain"


def build_brain():
    # Materials
    cerebrum_mat = kit.add_material("brain-cerebrum", (0.82, 0.65, 0.58), metallic=0.0, roughness=0.7)
    cerebellum_mat = kit.add_material("brain-cerebellum", (0.75, 0.55, 0.48), metallic=0.0, roughness=0.75)
    stem_mat = kit.add_material("brain-stem", (0.65, 0.45, 0.38), metallic=0.0, roughness=0.7)
    gray_matter = kit.add_material("brain-gray", (0.60, 0.50, 0.45), metallic=0.0, roughness=0.8)
    white_matter = kit.add_material("brain-white", (0.85, 0.78, 0.70), metallic=0.0, roughness=0.6)

    # SAGITTAL CROSS-SECTION view (cutaway showing internal structures)
    # Outer cerebrum shell (left hemisphere, cut in half)
    bm = bmesh.new()
    # Create a half-ellipsoid for sagittal view
    segments_u = 32
    segments_v = 24
    rx, ry, rz = 0.04, 0.035, 0.03  # radii

    for i in range(segments_u + 1):
        u = math.pi * i / segments_u  # 0 to pi (half sphere)
        for j in range(segments_v + 1):
            v = 2 * math.pi * j / segments_v  # full circle
            x = rx * math.sin(u) * math.cos(v)
            y = ry * math.sin(u) * math.sin(v)
            z = rz * math.cos(u)
            # Only keep front half for cross-section view
            if y >= 0:
                bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    # Create faces between adjacent vertices (safe bounds check)
    for i in range(segments_u):
        for j in range(segments_v):
            v1_idx = i * (segments_v + 1) + j
            v2_idx = v1_idx + 1
            v3_idx = (i + 1) * (segments_v + 1) + j + 1
            v4_idx = v3_idx - 1
            if v1_idx < len(bm.verts) and v2_idx < len(bm.verts) and v3_idx < len(bm.verts) and v4_idx < len(bm.verts):
                try:
                    bm.faces.new([bm.verts[v1_idx], bm.verts[v2_idx], bm.verts[v3_idx], bm.verts[v4_idx]])
                except:
                    pass

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-cerebrum")
    bm.to_mesh(mesh)
    bm.free()
    cerebrum = bpy.data.objects.new(f"{ASSET_ID}-cerebrum", mesh)
    bpy.context.collection.objects.link(cerebrum)
    cerebrum.data.materials.append(cerebrum_mat)

    # Cerebellum (posterior-inferior, with folia ridges)
    bm2 = bmesh.new()
    seg = 24
    for i in range(seg + 1):
        u = math.pi * i / seg
        for j in range(seg + 1):
            v = 2 * math.pi * j / seg
            x = 0.02 * math.sin(u) * math.cos(v)
            y = 0.015 * math.sin(u) * math.sin(v) - 0.03
            z = 0.015 * math.cos(u) - 0.015
            if y >= -0.03:
                bm2.verts.new((x, y, z))

    bm2.verts.ensure_lookup_table()
    for i in range(seg):
        for j in range(seg):
            v1 = i * (seg + 1) + j
            v2 = v1 + 1
            v3 = (i + 1) * (seg + 1) + j + 1
            v4 = v3 - 1
            try:
                bm2.faces.new([bm2.verts[v1], bm2.verts[v2], bm2.verts[v3], bm2.verts[v4]])
            except:
                pass

    mesh2 = bpy.data.meshes.new(f"{ASSET_ID}-cerebellum")
    bm2.to_mesh(mesh2)
    bm2.free()
    cerebellum = bpy.data.objects.new(f"{ASSET_ID}-cerebellum", mesh2)
    bpy.context.collection.objects.link(cerebellum)
    cerebellum.data.materials.append(cerebellum_mat)

    # Brain stem (pons + medulla)
    kit.primitive_object(f"{ASSET_ID}-pons", "cylinder", stem_mat,
                          size=(0.008, 0.008, 0.015),
                          location=(0.0, -0.015, -0.025))
    kit.primitive_object(f"{ASSET_ID}-medulla", "cylinder", stem_mat,
                          size=(0.006, 0.006, 0.02),
                          location=(0.0, -0.02, -0.04))

    # Spinal cord extension
    kit.primitive_object(f"{ASSET_ID}-spinal-cord", "cylinder", stem_mat,
                          size=(0.004, 0.004, 0.025),
                          location=(0.0, -0.025, -0.055))

    # Corpus callosum (white matter arch)
    kit.primitive_object(f"{ASSET_ID}-corpus-callosum", "cube", white_matter,
                          size=(0.03, 0.005, 0.005),
                          location=(0.0, 0.005, 0.005))

    # Thalamus (center)
    kit.primitive_object(f"{ASSET_ID}-thalamus", "cylinder", gray_matter,
                          size=(0.01, 0.01, 0.01),
                          location=(0.0, 0.005, -0.005))

    return [cerebrum, cerebellum]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_brain()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
