"""
extract_z_anatomy_digestive.py — Clean, High-Fidelity Human Digestive System Extraction
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

# Import edu_asset_kit
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))
import edu_asset_kit as kit

ASSET_ID = "digestive-system"
STANDARD_HEIGHT = 0.50  # 50 cm standard anatomical torso scale

# Core anatomical organs of the human gastrointestinal tract for CBSE Class 10
GI_STRUCTURES = [
    "Oesophagus",
    "Stomach",
    "Liver",
    "Gallbladder",
    "Pancreas",
    "Jejunum",
    "Transverse colon",
    "Sigmoid colon",
    "Vermiform appendix"
]


def setup_standard_materials():
    mats = {}
    # Esophagus: Soft pinkish tube
    mats["gi-esophagus"] = kit.add_material("gi-esophagus", (0.85, 0.65, 0.62), metallic=0.0, roughness=0.5)
    # Stomach: Warm coral muscular pouch
    mats["gi-stomach"] = kit.add_material("gi-stomach", (0.86, 0.48, 0.44), metallic=0.0, roughness=0.45)
    # Liver: Rich reddish-brown hepatic tissue
    mats["gi-liver"] = kit.add_material("gi-liver", (0.60, 0.22, 0.18), metallic=0.0, roughness=0.45)
    # Gallbladder: Distinct olive/emerald green bile reservoir
    mats["gi-gallbladder"] = kit.add_material("gi-gallbladder", (0.22, 0.55, 0.32), metallic=0.0, roughness=0.35)
    # Pancreas: Soft golden-amber glandular organ
    mats["gi-pancreas"] = kit.add_material("gi-pancreas", (0.90, 0.72, 0.38), metallic=0.0, roughness=0.55)
    # Small Intestine (Jejunum): Soft warm pink/orange coiled loops
    mats["gi-small-intestine"] = kit.add_material("gi-small-intestine", (0.88, 0.58, 0.52), metallic=0.0, roughness=0.5)
    # Large Intestine (Colon & Appendix): Soft beige/tan segmented colon
    mats["gi-large-intestine"] = kit.add_material("gi-large-intestine", (0.80, 0.68, 0.58), metallic=0.0, roughness=0.5)

    return mats


def get_material_for_object(name, mats):
    nl = name.lower()
    if "oesophagus" in nl or "esophagus" in nl:
        return mats["gi-esophagus"]
    if "stomach" in nl:
        return mats["gi-stomach"]
    if "liver" in nl:
        return mats["gi-liver"]
    if "gallbladder" in nl:
        return mats["gi-gallbladder"]
    if "pancreas" in nl:
        return mats["gi-pancreas"]
    if "jejunum" in nl or "ileum" in nl:
        return mats["gi-small-intestine"]
    if "colon" in nl or "appendix" in nl or "caecum" in nl:
        return mats["gi-large-intestine"]
    return mats["gi-stomach"]


def extract_digestive_system():
    out_dir = Path(ROOT_DIR / "assets" / "biology" / "digestive-system" / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    source_blend = ROOT_DIR / "assets" / "biology" / "human-heart" / "source" / "extracted" / "Z-Anatomy" / "Startup.blend"

    # 1. Open source file to extract raw mesh data
    bpy.ops.wm.open_mainfile(filepath=str(source_blend))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    target_names = set(GI_STRUCTURES)
    matched_objs = [obj for obj in bpy.data.objects if obj.name in target_names]
    print(f"[INFO] Found {len(matched_objs)} target GI anatomical objects in source.")

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

    # 4. Standard Studio Lighting & Camera
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
    extract_digestive_system()
