"""
extract_z_anatomy_heart.py — Complete, Isolated Human Heart Asset Extraction via Appending to Fresh Scene
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

# Import edu_asset_kit
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))
import edu_asset_kit as kit

ASSET_ID = "human-heart"
STANDARD_HEIGHT = 0.14  # 14 cm world scale

# Explicit whitelist of heart anatomical structures
HEART_CHAMBERS_AND_VALVES = [
    "Right atrium",
    "Right ventricle",
    "Left atrium",
    "Left ventricle",
    "Inferior papillary muscle of right ventricle",
    "Anterior papillary muscle of right ventricle",
    "Septal papillary muscle of right ventricle",
    "Inferior papillary muscle of left ventricle",
    "Inferior leaflet of right atrioventricular valve",
    "Septal leaflet of right atrioventricular valve",
    "Posterior leaflet of left atrioventricular valve",
    "Left coronary leaflet",
    "Non-coronary leaflet",
    "Right coronary leaflet",
    "Anterior semilunar leaflet of pulmonary valve",
    "Left semilunar leaflet of pulmonary valve",
    "Right semilunar leaflet of pulmonary valve",
    "Pulmonary trunk"
]

HEART_GREAT_VESSELS = [
    "Ascending aorta",
    "Aortic arch",
    "Brachiocephalic trunk",
    "Thoracic aorta",
    "Bifurcation of pulmonary trunk",
    "Left pulmonary artery",
    "Right pulmonary artery",
    "Superior vena cava",
    "Inferior vena cava (thoracic part)",
    "Left superior pulmonary vein",
    "Left inferior pulmonary vein",
    "Right superior pulmonary vein",
    "Right inferior pulmonary vein",
    "Right coronary artery",
    "Left coronary artery",
    "Right inferolateral branch of right coronary artery",
    "Coronary sinus"
]


def setup_standard_materials():
    mats = {}
    # Anatomical textbook color palette:
    # Right heart / Deoxygenated: Medical Blue
    mats["heart-right-ventricle"] = kit.add_material("heart-right-ventricle", (0.20, 0.40, 0.78), metallic=0.0, roughness=0.45)
    mats["heart-right-atrium"] = kit.add_material("heart-right-atrium", (0.24, 0.46, 0.82), metallic=0.0, roughness=0.45)
    mats["heart-deoxy-vessel"] = kit.add_material("heart-deoxy-vessel", (0.16, 0.36, 0.75), metallic=0.0, roughness=0.45)

    # Left heart / Oxygenated: Vibrant Crimson / Red
    mats["heart-left-ventricle"] = kit.add_material("heart-left-ventricle", (0.80, 0.18, 0.16), metallic=0.0, roughness=0.45)
    mats["heart-left-atrium"] = kit.add_material("heart-left-atrium", (0.85, 0.22, 0.18), metallic=0.0, roughness=0.45)
    mats["heart-aorta"] = kit.add_material("heart-aorta", (0.88, 0.14, 0.12), metallic=0.0, roughness=0.45)
    mats["heart-oxy-vessel"] = kit.add_material("heart-oxy-vessel", (0.84, 0.20, 0.16), metallic=0.0, roughness=0.45)

    # Coronary arteries & veins: Bright red / orange
    mats["heart-coronary"] = kit.add_material("heart-coronary", (0.95, 0.25, 0.18), metallic=0.0, roughness=0.35)

    # Valves & Papillary: Off-white ivory
    mats["heart-valve"] = kit.add_material("heart-valve", (0.92, 0.90, 0.82), metallic=0.0, roughness=0.35)
    return mats


def get_material_for_object(name, mats):
    nl = name.lower()
    if "aorta" in nl or "aortic" in nl or "brachiocephalic" in nl:
        return mats["heart-aorta"]
    if "right ventricle" in nl:
        return mats["heart-right-ventricle"]
    if "right atrium" in nl:
        return mats["heart-right-atrium"]
    if "left ventricle" in nl:
        return mats["heart-left-ventricle"]
    if "left atrium" in nl:
        return mats["heart-left-atrium"]
    if "pulmonary artery" in nl or "pulmonary trunk" in nl or "cava" in nl:
        return mats["heart-deoxy-vessel"]
    if "pulmonary vein" in nl:
        return mats["heart-oxy-vessel"]
    if "valve" in nl or "leaflet" in nl or "papillary" in nl:
        return mats["heart-valve"]
    if "coronary" in nl or "sinus" in nl:
        return mats["heart-coronary"]
    return mats["heart-left-ventricle"]


def extract_heart():
    out_dir = Path(ROOT_DIR / "assets" / "biology" / "human-heart" / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    source_blend = ROOT_DIR / "assets" / "biology" / "human-heart" / "source" / "extracted" / "Z-Anatomy" / "Startup.blend"

    # 1. Open source file to extract raw mesh vertex and polygon data
    bpy.ops.wm.open_mainfile(filepath=str(source_blend))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    target_names = set(HEART_CHAMBERS_AND_VALVES + HEART_GREAT_VESSELS)
    matched_objs = [obj for obj in bpy.data.objects if obj.name in target_names]
    print(f"[INFO] Found {len(matched_objs)} target heart objects in source.")

    mesh_data_list = []
    for orig_obj in matched_objs:
        mw = orig_obj.matrix_world.copy()
        if orig_obj.type == 'CURVE':
            eval_obj = orig_obj.evaluated_get(depsgraph)
            temp_mesh = bpy.data.meshes.new_from_object(eval_obj)
        else:
            temp_mesh = orig_obj.data

        # Extract vertex coordinates transformed by matrix_world
        verts = [(mw @ v.co)[:] for v in temp_mesh.vertices]
        polys = [list(p.vertices) for p in temp_mesh.polygons]
        edges = [list(e.vertices) for e in temp_mesh.edges]

        mesh_data_list.append((orig_obj.name, verts, edges, polys))

    # 2. Reset to a fresh clean Blender scene
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

        clean_name = obj.name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace("'", "")
        obj.name = f"{ASSET_ID}-{clean_name}"

    bpy.context.view_layer.update()

    # 4. Standard Studio Lighting & Camera (Front-facing educational angle)
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
    extract_heart()
