"""
extract_z_anatomy_eye.py — Clean, High-Fidelity Human Eye Asset Extraction
"""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

# Import edu_asset_kit
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))
import edu_asset_kit as kit

ASSET_ID = "human-eye"
STANDARD_HEIGHT = 0.08  # 8 cm world scale for eyeball visualization

# Eye anatomical structures (Right Eye + Optic pathway)
EYE_STRUCTURES = [
    "Cornea.r",
    "Sclera.r",
    "Iris.r",
    "Lens.r",
    "Retina.r",
    "Vitreous body.r",
    "Optic nerve (II).r",
    "Central retinal artery.r"
]


def setup_standard_materials():
    mats = {}
    # Cornea: Clear transparent refractive
    mats["eye-cornea"] = kit.add_material("eye-cornea", (0.85, 0.95, 1.0), metallic=0.0, roughness=0.05)
    # Sclera: Clean anatomical off-white
    mats["eye-sclera"] = kit.add_material("eye-sclera", (0.94, 0.94, 0.92), metallic=0.0, roughness=0.3)
    # Iris: Medical hazel / amber brown
    mats["eye-iris"] = kit.add_material("eye-iris", (0.35, 0.55, 0.75), metallic=0.0, roughness=0.4)
    # Lens: Clear transparent biconvex optical element
    mats["eye-lens"] = kit.add_material("eye-lens", (0.90, 0.96, 1.0), metallic=0.0, roughness=0.08)
    # Retina: Warm orange-red neural sensory layer
    mats["eye-retina"] = kit.add_material("eye-retina", (0.88, 0.42, 0.30), metallic=0.0, roughness=0.5)
    # Vitreous body: Semi-transparent gel
    mats["eye-vitreous"] = kit.add_material("eye-vitreous", (0.88, 0.94, 0.98), metallic=0.0, roughness=0.1)
    # Optic Nerve: Pale yellow-cream cranial nerve
    mats["eye-optic-nerve"] = kit.add_material("eye-optic-nerve", (0.92, 0.88, 0.65), metallic=0.0, roughness=0.4)
    # Retinal Artery: Bright red
    mats["eye-artery"] = kit.add_material("eye-artery", (0.90, 0.15, 0.12), metallic=0.0, roughness=0.35)

    return mats


def get_material_for_object(name, mats):
    nl = name.lower()
    if "cornea" in nl:
        return mats["eye-cornea"]
    if "sclera" in nl:
        return mats["eye-sclera"]
    if "iris" in nl:
        return mats["eye-iris"]
    if "lens" in nl:
        return mats["eye-lens"]
    if "retina" in nl:
        return mats["eye-retina"]
    if "vitreous" in nl:
        return mats["eye-vitreous"]
    if "optic nerve" in nl:
        return mats["eye-optic-nerve"]
    if "artery" in nl:
        return mats["eye-artery"]
    return mats["eye-sclera"]


def extract_eye():
    out_dir = Path(ROOT_DIR / "assets" / "biology" / "human-eye" / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    source_blend = ROOT_DIR / "assets" / "biology" / "human-heart" / "source" / "extracted" / "Z-Anatomy" / "Startup.blend"

    # 1. Open source file to extract raw mesh data
    bpy.ops.wm.open_mainfile(filepath=str(source_blend))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    target_names = set(EYE_STRUCTURES)
    matched_objs = [obj for obj in bpy.data.objects if obj.name in target_names]
    print(f"[INFO] Found {len(matched_objs)} target eye anatomical objects in source.")

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

    # 4. Standard Studio Lighting & Camera (Front-angled anatomical framing)
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
    extract_eye()
