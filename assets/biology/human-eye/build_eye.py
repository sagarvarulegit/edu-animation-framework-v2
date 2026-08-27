import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh

ASSET_ID = "human-eye"


def build_eye():
    # Materials
    sclera = kit.add_material("eye-sclera", (0.92, 0.90, 0.85), metallic=0.0, roughness=0.4)
    choroid = kit.add_material("eye-choroid", (0.40, 0.20, 0.15), metallic=0.0, roughness=0.6)
    iris = kit.add_material("eye-iris", (0.25, 0.45, 0.75), metallic=0.0, roughness=0.5)
    pupil = kit.add_material("eye-pupil", (0.02, 0.02, 0.02), metallic=0.0, roughness=0.8)
    lens_mat = kit.add_material("eye-lens", (0.90, 0.92, 0.95), metallic=0.0, roughness=0.05)
    lens_mat.use_nodes = True
    bsdf = lens_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    retina = kit.add_material("eye-retina", (0.80, 0.40, 0.35), metallic=0.0, roughness=0.6)
    cornea_mat = kit.add_material("eye-cornea", (0.88, 0.92, 0.96), metallic=0.0, roughness=0.02)
    cornea_mat.use_nodes = True
    bsdf2 = cornea_mat.node_tree.nodes["Principled BSDF"]
    bsdf2.inputs["Transmission Weight"].default_value = 0.90
    nerve = kit.add_material("eye-nerve", (0.85, 0.80, 0.35), metallic=0.0, roughness=0.5)
    vitreous = kit.add_material("eye-vitreous", (0.85, 0.88, 0.92), metallic=0.0, roughness=0.1)
    vitreous.use_nodes = True
    bsdf3 = vitreous.node_tree.nodes["Principled BSDF"]
    bsdf3.inputs["Transmission Weight"].default_value = 0.70

    # 3/4 CUTAWAY SPHERE — sagittal section showing internal structures
    bm = bmesh.new()
    segments = 32
    radius = 0.04

    # Create a 3/4 sphere (remove one quadrant for cutaway view)
    for i in range(segments + 1):
        theta = math.pi * i / segments  # 0 to pi
        for j in range(segments + 1):
            phi = 2 * math.pi * j / segments  # 0 to 2pi
            x = radius * math.sin(theta) * math.cos(phi)
            y = radius * math.sin(theta) * math.sin(phi)
            z = radius * math.cos(theta)
            # Cutaway: remove front-right quadrant
            if not (x > 0 and y > 0 and z > 0):
                bm.verts.new((x, y, z))

    bm.verts.ensure_lookup_table()
    for i in range(segments):
        for j in range(segments):
            idx = i * (segments + 1) + j
            if idx < len(bm.verts) and (idx + 1) < len(bm.verts):
                v1 = bm.verts[idx]
                v2 = bm.verts[idx + 1]
                v3_idx = (i + 1) * (segments + 1) + j + 1
                v4_idx = v3_idx - 1
                if v3_idx < len(bm.verts) and v4_idx < len(bm.verts):
                    v3 = bm.verts[v3_idx]
                    v4 = bm.verts[v4_idx]
                    try:
                        bm.faces.new([v1, v2, v3, v4])
                    except:
                        pass

    mesh = bpy.data.meshes.new(f"{ASSET_ID}-sclera")
    bm.to_mesh(mesh)
    bm.free()
    sclera_obj = bpy.data.objects.new(f"{ASSET_ID}-sclera", mesh)
    bpy.context.collection.objects.link(sclera_obj)
    sclera_obj.data.materials.append(sclera)

    # Retina layer (slightly smaller sphere, back half only)
    bm2 = bmesh.new()
    for i in range(segments + 1):
        theta = math.pi * i / segments
        for j in range(segments + 1):
            phi = 2 * math.pi * j / segments
            r = radius * 0.95
            x = r * math.sin(theta) * math.cos(phi)
            y = r * math.sin(theta) * math.sin(phi)
            z = r * math.cos(theta)
            # Only back half
            if z < 0.01:
                bm2.verts.new((x, y, z))

    bm2.verts.ensure_lookup_table()
    for i in range(segments):
        for j in range(segments):
            idx = i * (segments + 1) + j
            if idx < len(bm2.verts) and (idx + 1) < len(bm2.verts):
                v1 = bm2.verts[idx]
                v2 = bm2.verts[idx + 1]
                v3_idx = (i + 1) * (segments + 1) + j + 1
                v4_idx = v3_idx - 1
                if v3_idx < len(bm2.verts) and v4_idx < len(bm2.verts):
                    v3 = bm2.verts[v3_idx]
                    v4 = bm2.verts[v4_idx]
                    try:
                        bm2.faces.new([v1, v2, v3, v4])
                    except:
                        pass

    mesh2 = bpy.data.meshes.new(f"{ASSET_ID}-retina")
    bm2.to_mesh(mesh2)
    bm2.free()
    retina_obj = bpy.data.objects.new(f"{ASSET_ID}-retina", mesh2)
    bpy.context.collection.objects.link(retina_obj)
    retina_obj.data.materials.append(retina)

    # Cornea (bulging transparent dome at front)
    kit.primitive_object(f"{ASSET_ID}-cornea", "cylinder", cornea_mat,
                          size=(0.018, 0.018, 0.008),
                          location=(0.0, 0.0, 0.038))

    # Iris (colored disc behind cornea)
    kit.primitive_object(f"{ASSET_ID}-iris", "cylinder", iris,
                          size=(0.022, 0.022, 0.002),
                          location=(0.0, 0.0, 0.032))

    # Pupil (black center of iris)
    kit.primitive_object(f"{ASSET_ID}-pupil", "cylinder", pupil,
                          size=(0.008, 0.008, 0.003),
                          location=(0.0, 0.0, 0.033))

    # Crystalline lens (biconvex, behind iris)
    kit.primitive_object(f"{ASSET_ID}-lens", "cylinder", lens_mat,
                          size=(0.015, 0.015, 0.006),
                          location=(0.0, 0.0, 0.025))

    # Vitreous humor (filling main chamber)
    kit.primitive_object(f"{ASSET_ID}-vitreous", "cylinder", vitreous,
                          size=(0.035, 0.035, 0.03),
                          location=(0.0, 0.0, -0.005))

    # Optic nerve (exits back)
    kit.primitive_object(f"{ASSET_ID}-optic-nerve", "cylinder", nerve,
                          size=(0.006, 0.006, 0.025),
                          location=(0.0, 0.0, -0.05))

    # Blind spot (optic disc)
    kit.primitive_object(f"{ASSET_ID}-blind-spot", "cylinder", pupil,
                          size=(0.004, 0.004, 0.002),
                          location=(0.0, 0.0, -0.038))

    return [sclera_obj, retina_obj]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_eye()
    kit.setup_world_and_light()
    kit.configure_render()
    kit.frame_camera(objects)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")


if __name__ == "__main__":
    main()
