"""
build_magnesium_ribbon.py — NCERT Class 10 Chemistry Activity 1.1 High-Fidelity Magnesium Ribbon
Dual collections:
  - Magnesium_Ribbon_Full: Realistic coiled elemental ribbon showing shiny cleaned zone vs dull tarnished zone, with sandpaper sheet on studio plinth
  - Magnesium_Ribbon_Detail: Micro-structural cross-section showing pure Mg core, surface oxide passivation layer, abrasive cleaning mechanics, and annotated plaque
"""

import sys
import math
import shutil
from pathlib import Path
from mathutils import Vector, Euler

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy
import bmesh

ASSET_ID = "magnesium-ribbon"

# Calibrated NCERT Laboratory Palette
COLOR_MG_SHINY      = (0.94, 0.96, 0.98)     # Freshly cleaned elemental Mg metal (mirror luster)
COLOR_MG_TARNISH    = (0.32, 0.35, 0.38)     # Protective dark-grey MgO/MgCO3 passivation layer
COLOR_SANDPAPER     = (0.28, 0.22, 0.18)     # Coarse dark silicon carbide sandpaper
COLOR_SANDPAPER_BACK= (0.75, 0.65, 0.45)     # Kraft paper backing
COLOR_PLINTH        = (0.12, 0.13, 0.16)     # Dark slate pedestal
COLOR_GOLD          = (0.90, 0.75, 0.22)     # Plaque frame
COLOR_CYAN_DIM      = (0.20, 0.85, 1.00)     # Dimension caliper
COLOR_SCRATCH_ARR   = (0.95, 0.70, 0.15)     # Mechanical abrasion vectors


def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_emissive_mat(name, color, strength=8.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    diff = p2 - p1
    length = diff.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = diff.to_track_quat("Z", "Y").to_euler()

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = mid
    obj.rotation_euler = rot
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# BUILD MAGNESIUM RIBBON FULL
# -----------------------------------------------------------------------------
def build_ribbon_full(collection):
    shiny_mat    = kit.add_machined_metal_material("mg-shiny", COLOR_MG_SHINY, metallic=0.98, roughness=0.18)
    tarnish_mat  = kit.add_material("mg-tarnish", COLOR_MG_TARNISH, metallic=0.30, roughness=0.75)
    sandpaper_mat= kit.add_material("mg-sandpaper", COLOR_SANDPAPER, metallic=0.05, roughness=0.95)
    sp_back_mat  = kit.add_material("mg-sandpaper-back", COLOR_SANDPAPER_BACK, metallic=0.0, roughness=0.70)
    plinth_mat   = kit.add_material("mg-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.240, 0.160, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Curled Magnesium Ribbon Strip (L = 130mm, W = 8mm, Thickness = 0.8mm)
    # The ribbon has natural curled/wavy bends. Left half (s < 0.45) is shiny cleaned, right half is tarnished.
    num_stations = 80
    ribbon_w = 0.008
    ribbon_th = 0.0008
    half_w = ribbon_w / 2.0
    half_th = ribbon_th / 2.0

    bm = bmesh.new()
    verts_grid = []

    # Path spine: gentle natural coil bend across X axis
    for i in range(num_stations):
        t = i / (num_stations - 1)
        x = (t - 0.5) * 0.130
        y = 0.012 * math.sin(2.5 * math.pi * t)
        z = 0.004 + 0.005 * math.cos(3.0 * math.pi * t) + 0.003

        # Tangent vector for spine
        dt = 0.001
        t_next = min(1.0, t + dt)
        x_n = (t_next - 0.5) * 0.130
        y_n = 0.012 * math.sin(2.5 * math.pi * t_next)
        z_n = 0.004 + 0.005 * math.cos(3.0 * math.pi * t_next) + 0.003
        tangent = Vector((x_n - x, y_n - y, z_n - z_n)).normalized() if False else Vector((1.0, 0.0, 0.0))
        
        # Cross vector (along ribbon width) and normal vector (along thickness)
        normal = Vector((0.0, 0.0, 1.0))
        binormal = Vector((0.0, 1.0, 0.0))

        ring = [
            bm.verts.new(Vector((x, y, z)) + binormal * half_w + normal * half_th),
            bm.verts.new(Vector((x, y, z)) - binormal * half_w + normal * half_th),
            bm.verts.new(Vector((x, y, z)) - binormal * half_w - normal * half_th),
            bm.verts.new(Vector((x, y, z)) + binormal * half_w - normal * half_th)
        ]
        verts_grid.append(ring)

    # Faces and material assignment: index 0 = shiny, index 1 = tarnish
    split_index = int(num_stations * 0.48)
    for i in range(num_stations - 1):
        mat_idx = 0 if i < split_index else 1
        f1 = bm.faces.new([verts_grid[i][0], verts_grid[i+1][0], verts_grid[i+1][1], verts_grid[i][1]])
        f2 = bm.faces.new([verts_grid[i][1], verts_grid[i+1][1], verts_grid[i+1][2], verts_grid[i][2]])
        f3 = bm.faces.new([verts_grid[i][2], verts_grid[i+1][2], verts_grid[i+1][3], verts_grid[i][3]])
        f4 = bm.faces.new([verts_grid[i][3], verts_grid[i+1][3], verts_grid[i+1][0], verts_grid[i][0]])
        for f in [f1, f2, f3, f4]:
            f.material_index = mat_idx

    # End caps
    f_start = bm.faces.new([verts_grid[0][0], verts_grid[0][1], verts_grid[0][2], verts_grid[0][3]])
    f_start.material_index = 0
    f_end = bm.faces.new([verts_grid[-1][3], verts_grid[-1][2], verts_grid[-1][1], verts_grid[-1][0]])
    f_end.material_index = 1

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{ASSET_ID}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    ribbon_obj = bpy.data.objects.new(f"{ASSET_ID}_Ribbon", mesh)
    bpy.context.collection.objects.link(ribbon_obj)
    ribbon_obj.data.materials.append(shiny_mat)
    ribbon_obj.data.materials.append(tarnish_mat)
    link_strictly(ribbon_obj, collection)

    # 3. Sandpaper Sheet (Curled slightly, resting beside the ribbon)
    sp_w = 0.050
    sp_l = 0.038
    sp_th = 0.0006
    sandpaper = kit.primitive_object(
        f"{ASSET_ID}_Sandpaper", "cube", sandpaper_mat,
        size=(sp_w, sp_l, sp_th),
        location=(-0.035, -0.040, sp_th / 2.0),
        rotation_euler=(0.0, 0.0, math.radians(15.0))
    )
    link_strictly(sandpaper, collection)

    # Sandpaper folded edge showing kraft paper backing
    sp_backing = kit.primitive_object(
        f"{ASSET_ID}_Sandpaper_Back", "cube", sp_back_mat,
        size=(0.016, sp_l, sp_th),
        location=(-0.052, -0.045, sp_th + 0.0006),
        rotation_euler=(0.0, math.radians(25.0), math.radians(15.0))
    )
    link_strictly(sp_backing, collection)


# -----------------------------------------------------------------------------
# BUILD MAGNESIUM RIBBON DETAIL / SECTION
# -----------------------------------------------------------------------------
def build_ribbon_detail(collection):
    shiny_mat    = kit.add_machined_metal_material("mg-sec-shiny", COLOR_MG_SHINY, metallic=0.98, roughness=0.18)
    tarnish_mat  = kit.add_material("mg-sec-tarnish", COLOR_MG_TARNISH, metallic=0.30, roughness=0.75)
    sandpaper_mat= kit.add_material("mg-sec-sandpaper", COLOR_SANDPAPER, metallic=0.05, roughness=0.95)
    plinth_mat   = kit.add_material("mg-sec-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat     = kit.add_machined_metal_material("mg-sec-gold", COLOR_GOLD, metallic=0.92, roughness=0.22)
    dim_mat      = create_emissive_mat("mg-sec-dim", COLOR_CYAN_DIM, strength=10.0)
    arrow_mat    = create_emissive_mat("mg-sec-arr", COLOR_SCRATCH_ARR, strength=12.0)

    # 1. Studio Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Sec_Plinth", "cube", plinth_mat,
        size=(0.260, 0.180, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Magnified Ribbon Cross-Section Block
    # Dimensions: Length = 60mm, Width = 30mm, Core Thickness = 8mm (magnified 10x for pedagogical clarity)
    z_elev = 0.006
    x_offset = 0.030
    y_offset = -0.005

    core_w = 0.040
    core_l = 0.060
    core_h = 0.008

    # Elemental Mg Core
    core = kit.primitive_object(
        f"{ASSET_ID}_Sec_Core", "cube", shiny_mat,
        size=(core_w, core_l, core_h),
        location=(x_offset, y_offset, z_elev + core_h / 2.0)
    )
    link_strictly(core, collection)

    # Surface Passivation Layer (Top & Bottom grey tarnish film)
    film_th = 0.0012
    top_film = kit.primitive_object(
        f"{ASSET_ID}_Sec_TopFilm", "cube", tarnish_mat,
        size=(core_w, core_l, film_th),
        location=(x_offset, y_offset, z_elev + core_h + film_th / 2.0)
    )
    link_strictly(top_film, collection)

    bot_film = kit.primitive_object(
        f"{ASSET_ID}_Sec_BotFilm", "cube", tarnish_mat,
        size=(core_w, core_l, film_th),
        location=(x_offset, y_offset, z_elev - film_th / 2.0)
    )
    link_strictly(bot_film, collection)

    # Sandpaper Abrasive Block actively removing the oxide film from the front section
    sp_block_w = 0.024
    sp_block_l = 0.035
    sp_block_h = 0.006
    sp_block = kit.primitive_object(
        f"{ASSET_ID}_Sec_Sandpaper_Block", "cube", sandpaper_mat,
        size=(sp_block_w, sp_block_l, sp_block_h),
        location=(x_offset + 0.008, y_offset - 0.015, z_elev + core_h + film_th + sp_block_h / 2.0),
        rotation_euler=(0.0, 0.0, math.radians(-15.0))
    )
    link_strictly(sp_block, collection)

    # Directional Mechanical Rubbing Arrows
    create_cylinder_segment(f"{ASSET_ID}_Arr_Rub_1", (x_offset - 0.005, y_offset - 0.010, z_elev + core_h + 0.015),
                            (x_offset + 0.020, y_offset - 0.010, z_elev + core_h + 0.015), 0.0005, arrow_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Arr_Rub_2", (x_offset + 0.020, y_offset - 0.010, z_elev + core_h + 0.015),
                            (x_offset + 0.015, y_offset - 0.006, z_elev + core_h + 0.015), 0.0005, arrow_mat, collection)

    # 3. Dimension Caliper Lines
    # Width caliper (40mm visual)
    create_cylinder_segment(f"{ASSET_ID}_Dim_W", (x_offset - core_w / 2.0, y_offset + core_l / 2.0 + 0.008, z_elev + core_h / 2.0),
                            (x_offset + core_w / 2.0, y_offset + core_l / 2.0 + 0.008, z_elev + core_h / 2.0), 0.0003, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_W_L", (x_offset - core_w / 2.0, y_offset + core_l / 2.0 + 0.004, z_elev + core_h / 2.0),
                            (x_offset - core_w / 2.0, y_offset + core_l / 2.0 + 0.012, z_elev + core_h / 2.0), 0.0004, dim_mat, collection)
    create_cylinder_segment(f"{ASSET_ID}_Dim_W_R", (x_offset + core_w / 2.0, y_offset + core_l / 2.0 + 0.004, z_elev + core_h / 2.0),
                            (x_offset + core_w / 2.0, y_offset + core_l / 2.0 + 0.012, z_elev + core_h / 2.0), 0.0004, dim_mat, collection)

    # Thickness caliper
    create_cylinder_segment(f"{ASSET_ID}_Dim_Thick", (x_offset + core_w / 2.0 + 0.008, y_offset, z_elev),
                            (x_offset + core_w / 2.0 + 0.008, y_offset, z_elev + core_h), 0.0003, dim_mat, collection)

    # 4. Educational Plaque
    plq_x = -0.065
    plq_y = 0.000
    plq_rot = (math.radians(12.0), 0.0, math.radians(35.0))
    plq_norm_x = 0.005 * math.sin(math.radians(35.0))
    plq_norm_y = -0.005 * math.cos(math.radians(35.0))

    plaque_base = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Base", "cube", plinth_mat,
        size=(0.095, 0.010, 0.052),
        location=(plq_x, plq_y, 0.030),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_base, collection)

    plaque_border = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Border", "cube", gold_mat,
        size=(0.091, 0.002, 0.048),
        location=(plq_x + plq_norm_x, plq_y + plq_norm_y, 0.030),
        rotation_euler=plq_rot
    )
    link_strictly(plaque_border, collection)

    txt_mat = create_emissive_mat("mg-sec-txt", (0.95, 0.95, 0.98), strength=6.0)
    title_bar = kit.primitive_object(
        f"{ASSET_ID}_Plaque_TitleBar", "cube", txt_mat,
        size=(0.075, 0.002, 0.004),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.042),
        rotation_euler=plq_rot
    )
    link_strictly(title_bar, collection)

    line_1 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line1", "cube", dim_mat,
        size=(0.065, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.032),
        rotation_euler=plq_rot
    )
    link_strictly(line_1, collection)

    line_2 = kit.primitive_object(
        f"{ASSET_ID}_Plaque_Line2", "cube", arrow_mat,
        size=(0.055, 0.002, 0.0025),
        location=(plq_x + plq_norm_x * 1.2, plq_y + plq_norm_y * 1.2, 0.022),
        rotation_euler=plq_rot
    )
    link_strictly(line_2, collection)


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING SETUP
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 45.0
    cam = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    cam.location = (0.16, -0.24, 0.14)
    cam_target = Vector((0.0, 0.0, 0.015))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Studio Lighting
    key_light_data = bpy.data.lights.new("Key_Light", type="AREA")
    key_light_data.energy = 40.0
    key_light_data.size = 0.35
    key_light_data.color = (1.0, 0.98, 0.95)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.22, -0.18, 0.28)
    key_light.rotation_euler = (math.radians(35), math.radians(20), math.radians(-30))
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new("Fill_Light", type="AREA")
    fill_light_data.energy = 18.0
    fill_light_data.size = 0.40
    fill_light_data.color = (0.90, 0.95, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.22, -0.16, 0.22)
    fill_light.rotation_euler = (math.radians(40), math.radians(-25), math.radians(30))
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new("Rim_Light", type="POINT")
    rim_light_data.energy = 30.0
    rim_light_data.shadow_soft_size = 0.05
    rim_light_data.color = (0.85, 0.92, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (0.0, 0.25, 0.22)
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Magnesium_Ribbon_Full")
    sec_col  = bpy.data.collections.new("Magnesium_Ribbon_Detail")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_ribbon_full(full_col)
    build_ribbon_detail(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB only
    bpy.ops.object.select_all(action='DESELECT')
    for obj in full_col.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = full_col.objects[0]

    bpy.ops.export_scene.gltf(
        filepath=str(out_dir / f"{ASSET_ID}.glb"),
        use_selection=True,
        export_format='GLB'
    )

    viewer_dest = Path("/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets") / f"{ASSET_ID}.glb"
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f"{ASSET_ID}.glb", viewer_dest)
        print(f"Synced GLB to: {viewer_dest}")

    # Render Preview 1: Magnesium_Ribbon_Full
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False

    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Magnesium_Ribbon_Detail
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False

    cam = bpy.context.scene.camera
    cam.location = (0.16, -0.22, 0.14)
    cam_target = Vector((0.0, 0.0, 0.025))
    cam_dir = cam_target - cam.location
    cam.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
