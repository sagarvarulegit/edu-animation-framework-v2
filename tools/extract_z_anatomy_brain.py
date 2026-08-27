"""
extract_z_anatomy_brain.py — Clean, High-Fidelity Human Brain Asset Extraction
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

# Import edu_asset_kit
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))
import edu_asset_kit as kit

ASSET_ID = "brain"
STANDARD_HEIGHT = 0.14  # 14 cm world scale

# Curated anatomical structures representing the complete human brain for CBSE STEM curriculum
BRAIN_STRUCTURES = [
    # Cerebrum Cortical Gyri (Left & Right)
    "Precentral gyrus.l",
    "Precentral gyrus.r",
    "Postcentral gyrus.l",
    "Postcentral gyrus.r",
    "Superior frontal gyrus.l",
    "Superior frontal gyrus.r",
    "Middle frontal gyrus.l",
    "Middle frontal gyrus.r",
    "Superior parietal lobule.l",
    "Superior parietal lobule.r",
    "Supramarginal gyrus.l",
    "Supramarginal gyrus.r",
    "Angular gyrus.l",
    "Angular gyrus.r",
    "Superior temporal gyrus (Lateral part).l",
    "Superior temporal gyrus (Lateral part).r",
    "Middle temporal gyrus.l",
    "Middle temporal gyrus.r",
    "Inferior temporal gyrus.l",
    "Inferior temporal gyrus.r",
    "Superior occipital gyri.l",
    "Superior occipital gyri.r",
    "Lateral occipital gyrus (Middle occipital gyrus*).l",
    "Lateral occipital gyrus (Middle occipital gyrus*).r",
    "Cuneus.l",
    "Cuneus.r",
    "Lingual gyrus.l",
    "Lingual gyrus.r",
    "Temporal pole.l",
    "Temporal pole.r",
    "Occipital pole.l",
    "Occipital pole.r",

    # Midbrain & Deep Structures
    "Corpus callosum",
    "Thalamus.l",
    "Thalamus.r",

    # Hindbrain: Cerebellar Lobules (Complete Cerebellum)
    "Anterior quadrangular lobule.l",
    "Anterior quadrangular lobule.r",
    "Posterior quadrangular lobule.l",
    "Posterior quadrangular lobule.r",
    "Superior semilunar lobule.l",
    "Superior semilunar lobule.r",
    "Inferior semilunar lobule.l",
    "Inferior semilunar lobule.r",
    "Biventral lobule.l",
    "Biventral lobule.r",
    "Tonsil of cerebellum.l",
    "Tonsil of cerebellum.r",
    "Flocculus.l",
    "Flocculus.r",
    "Culmen",
    "Declive",
    "Folium of vermis",
    "Tuber of vermis",
    "Pyramis of vermis",
    "Uvula of vermis",

    # Hindbrain: Brainstem (Pons & Medulla)
    "Pons.l",
    "Pons.r",
    "Medulla oblongata.l",
    "Medulla oblongata.r",
    "Pyramid of medulla oblongata.l",
    "Pyramid of medulla oblongata.r"
]


def setup_standard_materials():
    mats = {}
    # Cerebrum: Soft grey/pink organic cortex
    mats["brain-cerebrum"] = kit.add_material("brain-cerebrum", (0.84, 0.65, 0.62), metallic=0.0, roughness=0.55)
    mats["brain-frontal"] = kit.add_material("brain-frontal", (0.86, 0.60, 0.54), metallic=0.0, roughness=0.55)
    mats["brain-parietal"] = kit.add_material("brain-parietal", (0.82, 0.62, 0.60), metallic=0.0, roughness=0.55)
    mats["brain-temporal"] = kit.add_material("brain-temporal", (0.88, 0.66, 0.58), metallic=0.0, roughness=0.55)
    mats["brain-occipital"] = kit.add_material("brain-occipital", (0.80, 0.58, 0.58), metallic=0.0, roughness=0.55)

    # Cerebellum: Richer terra-cotta brown/pink
    mats["brain-cerebellum"] = kit.add_material("brain-cerebellum", (0.75, 0.48, 0.42), metallic=0.0, roughness=0.6)

    # Brainstem: Ivory / soft beige
    mats["brain-stem"] = kit.add_material("brain-stem", (0.88, 0.82, 0.72), metallic=0.0, roughness=0.45)

    # Deep Structures: Warm light ivory
    mats["brain-deep"] = kit.add_material("brain-deep", (0.92, 0.80, 0.65), metallic=0.0, roughness=0.4)

    return mats


def get_material_for_object(name, mats):
    nl = name.lower()
    if any(k in nl for k in ["cerebell", "lobule", "vermis", "culmen", "declive", "flocculus", "tonsil"]):
        return mats["brain-cerebellum"]
    if any(k in nl for k in ["pons", "medulla", "pyramid"]):
        return mats["brain-stem"]
    if any(k in nl for k in ["corpus callosum", "thalamus"]):
        return mats["brain-deep"]
    if any(k in nl for k in ["frontal", "precentral"]):
        return mats["brain-frontal"]
    if any(k in nl for k in ["parietal", "postcentral", "supramarginal", "angular"]):
        return mats["brain-parietal"]
    if "temporal" in nl:
        return mats["brain-temporal"]
    if any(k in nl for k in ["occipital", "cuneus", "lingual"]):
        return mats["brain-occipital"]
    return mats["brain-cerebrum"]


def extract_brain():
    out_dir = Path(ROOT_DIR / "assets" / "biology" / "brain" / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    source_blend = ROOT_DIR / "assets" / "biology" / "human-heart" / "source" / "extracted" / "Z-Anatomy" / "Startup.blend"

    # 1. Open source file to extract raw mesh data
    bpy.ops.wm.open_mainfile(filepath=str(source_blend))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    target_names = set(BRAIN_STRUCTURES)
    matched_objs = [obj for obj in bpy.data.objects if obj.name in target_names]
    print(f"[INFO] Found {len(matched_objs)} target brain anatomical objects in source.")

    mesh_data_list = []
    for orig_obj in matched_objs:
        mw = orig_obj.matrix_world.copy()
        if orig_obj.type == 'CURVE':
            eval_obj = orig_obj.evaluated_get(depsgraph)
            temp_mesh = bpy.data.meshes.new_from_object(eval_obj)
        else:
            temp_mesh = orig_obj.data

        # Bake true global world coordinates
        verts = [(mw @ v.co)[:] for v in temp_mesh.vertices]
        polys = [list(p.vertices) for p in temp_mesh.polygons]
        edges = [list(e.vertices) for e in temp_mesh.edges]

        mesh_data_list.append((orig_obj.name, verts, edges, polys))

    # 2. Reset to a fresh empty Blender scene
    bpy.ops.wm.read_homefile(use_empty=True)

    materials = setup_standard_materials()
    extracted_objs = []

    for name, verts, edges, polys in mesh_data_list:
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, edges, polys)
        mesh.update()

        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        extracted_objs.append(obj)

    bpy.context.view_layer.update()

    # 3. Calculate unified bounding box and scale to standard height
    all_points = []
    for obj in extracted_objs:
        for vert in obj.data.vertices:
            all_points.append(vert.co)

    center = sum(all_points, Vector()) / len(all_points)
    min_z = min(p.z for p in all_points)
    max_z = max(p.z for p in all_points)
    current_height = max(max_z - min_z, 0.001)
    scale_factor = STANDARD_HEIGHT / current_height

    for obj in extracted_objs:
        for vert in obj.data.vertices:
            vert.co = (vert.co - center) * scale_factor
        obj.data.update()

        mat = get_material_for_object(obj.name, materials)
        obj.data.materials.clear()
        obj.data.materials.append(mat)

        clean_name = obj.name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("'", "").replace("*", "")
        obj.name = f"{ASSET_ID}-{clean_name}"

    bpy.context.view_layer.update()

    # 4. Standard Studio Lighting & Camera (3/4 anatomical perspective)
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=32)
    cam = kit.frame_camera(extracted_objs, lens=50.0)

    # 5. Save master .blend
    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"[OK] Saved clean master: {blend_path}")

    # 6. Export Web GLB
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"[OK] Exported GLB: {glb_path}")

    # 7. Render Preview
    preview_path = out_dir / "preview.png"
    kit.render_preview(preview_path)
    print(f"[OK] Rendered preview: {preview_path}")


if __name__ == "__main__":
    extract_brain()
