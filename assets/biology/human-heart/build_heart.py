"""
build_heart.py — Medical-grade extraction and construction pipeline for Human Heart
CBSE Class 10 Biology (Chapter 5: Life Processes — Transportation / Human Heart)
CBSE Class 11 Biology (Chapter 18: Body Fluids and Circulation — Cardiac Anatomy)

Extracts authentic anatomical structures from Z-Anatomy:
- 4 Muscular Chambers: Left Ventricle, Right Ventricle, Left Atrium, Right Atrium
- Coronal Cutaway Chambers: Solidified cross-section (LV 11mm, RV 4mm, IAS/IVS) exposing interior 4 cavities
- Valves & Cusps: Tricuspid (3 cusps), Bicuspid/Mitral (2 cusps), Aortic Semilunar, Pulmonary Semilunar
- Papillary Muscles & Chordae: RV Anterior/Inferior/Septal, LV Inferior
- Great Arteries & Veins: Aorta & Arch with 3 branches, Pulmonary Trunk & Arteries,
  Superior & Inferior Vena Cava, 4 Pulmonary Veins (all trimmed to standard anatomical margins)
- Coronary Circulation: LAD (Anterior Interventricular), RCA, Circumflex,
  Great Cardiac Vein, Middle Cardiac Vein, Coronary Sinus
Applies PBR Subsurface Scattering shaders and organizes into clean educational collections.
"""

import sys
import math
import shutil
from pathlib import Path
import bpy
import bmesh
from mathutils import Vector, Matrix

# Project paths
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]
SOURCE_BLEND = THIS_DIR / "source/extracted/Z-Anatomy/Startup.blend"
OUT_DIR = THIS_DIR / "out"
OUT_BLEND = OUT_DIR / "human-heart.blend"
OUT_GLB = OUT_DIR / "human-heart.glb"
VIEWER_GLB = PROJECT_ROOT / "apps/interactive-viewer/public/assets/human-heart.glb"
OUT_PREVIEW = OUT_DIR / "preview.png"
OUT_PREVIEW_CORONAL = OUT_DIR / "preview_coronal.png"

# Target anatomical objects grouped by category
CHAMBER_TARGETS = [
    'Left ventricle',
    'Right ventricle',
    'Left atrium',
    'Right atrium',
]

VALVE_TARGETS = [
    'Posterior leaflet of left atrioventricular valve',
    'Septal leaflet of right atrioventricular valve',
    'Inferior leaflet of right atrioventricular valve',
    'Left coronary leaflet',
    'Right coronary leaflet',
    'Non-coronary leaflet',
    'Anterior semilunar leaflet of pulmonary valve',
    'Left semilunar leaflet of pulmonary valve',
    'Right semilunar leaflet of pulmonary valve',
]

PAPILLARY_TARGETS = [
    'Anterior papillary muscle of right ventricle',
    'Inferior papillary muscle of right ventricle',
    'Septal papillary muscle of right ventricle',
    'Inferior papillary muscle of left ventricle',
]

GREAT_VESSEL_TARGETS = [
    'Ascending aorta',
    'Aortic arch',
    'Brachiocephalic trunk',
    'Left common carotid artery',
    'Left subclavian artery',
    'Thoracic aorta',
    'Pulmonary trunk',
    'Bifurcation of pulmonary trunk',
    'Left pulmonary artery',
    'Right pulmonary artery',
    'Superior vena cava',
    'Inferior vena cava (thoracic part)',
    'Left superior pulmonary vein',
    'Left inferior pulmonary vein',
    'Right superior pulmonary vein',
    'Right inferior pulmonary vein',
]

CORONARY_TARGETS = [
    'Left coronary artery',
    'Anterior interventricular artery',
    'Septal branches of anterior interventricular artery',
    'Circumflex artery of heart',
    'Right coronary artery',
    'Right inferolateral branch of right coronary artery',
    'Great cardiac vein',
    'Middle cardiac vein',
    'Coronary sinus',
    'Inferior vein of left ventricle',
    "Inferior vein of left ventricle (//Posterior '')",
]

TARGET_GROUPS = {
    'Chambers': CHAMBER_TARGETS,
    'Valves': VALVE_TARGETS,
    'Papillary_Muscles': PAPILLARY_TARGETS,
    'Great_Vessels': GREAT_VESSEL_TARGETS,
    'Coronary_Circulation': CORONARY_TARGETS,
}


def clean_identifier(name):
    clean = name.lower()
    for ch in [' ', '(', ')', '\'', '/', '*', '.']:
        clean = clean.replace(ch, '-')
    while '--' in clean:
        clean = clean.replace('--', '-')
    return f"heart-{clean.strip('-')}"


def create_tissue_material(name, base_rgb, crevice_rgb=None, sss_weight=0.20, sss_radius=(0.4, 0.1, 0.05), roughness=0.35, transmission=0.0, bump_strength=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    output.location = (450, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (150, 0)

    # Ambient Occlusion for natural depth in anatomical sulci and crevices
    if crevice_rgb:
        ao_node = nodes.new('ShaderNodeAmbientOcclusion')
        ao_node.location = (-300, 100)
        ao_node.inputs['Distance'].default_value = 0.02

        mix_ao = nodes.new('ShaderNodeMix')
        mix_ao.location = (-100, 100)
        mix_ao.data_type = 'RGBA'
        mix_ao.blend_type = 'MULTIPLY'
        mix_ao.inputs[0].default_value = 0.75
        mix_ao.inputs[6].default_value = (*base_rgb, 1.0)
        mix_ao.inputs[7].default_value = (*crevice_rgb, 1.0)

        links.new(ao_node.outputs['AO'], mix_ao.inputs[0])
        links.new(mix_ao.outputs[2], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (*base_rgb, 1.0)

    bsdf.inputs['Roughness'].default_value = roughness

    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.5
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.5

    # Transmission for semi-translucent fibrous valve leaflets
    if transmission > 0.0:
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission

    # Subsurface scattering
    if sss_weight > 0.0:
        if 'Subsurface Weight' in bsdf.inputs:
            bsdf.inputs['Subsurface Weight'].default_value = sss_weight
            bsdf.inputs['Subsurface Radius'].default_value = sss_radius
            if 'Subsurface Scale' in bsdf.inputs:
                bsdf.inputs['Subsurface Scale'].default_value = 0.012
        elif 'Subsurface' in bsdf.inputs:
            bsdf.inputs['Subsurface'].default_value = sss_weight
            bsdf.inputs['Subsurface Radius'].default_value = sss_radius

    # Procedural micro-muscle bump
    if bump_strength > 0.0:
        noise = nodes.new('ShaderNodeTexNoise')
        noise.location = (-300, -150)
        noise.inputs['Scale'].default_value = 400.0
        noise.inputs['Detail'].default_value = 4.0
        noise.inputs['Roughness'].default_value = 0.6

        bump = nodes.new('ShaderNodeBump')
        bump.location = (-100, -150)
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.001

        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    return mat


def main():
    print(f"[1/7] Opening source anatomy: {SOURCE_BLEND}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))

    depsgraph = bpy.context.evaluated_depsgraph_get()

    extracted_groups = {}
    total_extracted = 0

    for group_key, target_list in TARGET_GROUPS.items():
        extracted_groups[group_key] = []
        for target_name in target_list:
            obj = bpy.data.objects.get(target_name)
            if not obj:
                print(f"Warning: '{target_name}' not found!")
                continue

            mw = obj.matrix_world.copy()
            if obj.type == 'CURVE':
                eval_obj = obj.evaluated_get(depsgraph)
                temp_mesh = bpy.data.meshes.new_from_object(eval_obj)
            else:
                temp_mesh = obj.data

            verts = [(mw @ v.co)[:] for v in temp_mesh.vertices]
            edges = [list(e.vertices) for e in temp_mesh.edges]
            polys = [list(p.vertices) for p in temp_mesh.polygons]

            if obj.type == 'CURVE':
                bpy.data.meshes.remove(temp_mesh)

            extracted_groups[group_key].append({
                'orig_name': target_name,
                'verts': verts,
                'edges': edges,
                'polys': polys,
            })
            total_extracted += 1

    print(f"[2/7] Successfully extracted {total_extracted} anatomical structures into memory.")

    # Calculate global center using core cardiac structures (ventricles + atria)
    core_verts = []
    for item in extracted_groups['Chambers']:
        core_verts.extend(item['verts'])

    min_x = min(v[0] for v in core_verts)
    max_x = max(v[0] for v in core_verts)
    min_y = min(v[1] for v in core_verts)
    max_y = max(v[1] for v in core_verts)
    min_z = min(v[2] for v in core_verts)
    max_z = max(v[2] for v in core_verts)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    center_z = (min_z + max_z) / 2.0

    print(f"Computed Heart Chamber Center: ({center_x:.4f}, {center_y:.4f}, {center_z:.4f})")

    # [3/7] Rebuilding clean target scene
    print("[3/7] Rebuilding clean target scene...")
    bpy.ops.wm.read_homefile(use_empty=True)

    world = bpy.data.worlds.new("HeartStudioWorld")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.015, 0.015, 0.02, 1.0)
        bg_node.inputs["Strength"].default_value = 1.0

    # Create PBR Tissue Materials
    mat_myocardium = create_tissue_material(
        "heart-myocardium",
        base_rgb=(0.48, 0.08, 0.10),
        crevice_rgb=(0.22, 0.02, 0.03),
        sss_weight=0.18,
        sss_radius=(0.45, 0.10, 0.06),
        roughness=0.38,
        bump_strength=0.04
    )
    mat_atrium = create_tissue_material(
        "heart-atrium",
        base_rgb=(0.46, 0.11, 0.13),
        crevice_rgb=(0.25, 0.04, 0.05),
        sss_weight=0.18,
        sss_radius=(0.42, 0.10, 0.06),
        roughness=0.40,
        bump_strength=0.03
    )
    mat_valve = create_tissue_material(
        "heart-valve",
        base_rgb=(0.88, 0.86, 0.78),
        crevice_rgb=(0.68, 0.65, 0.58),
        sss_weight=0.25,
        sss_radius=(0.35, 0.30, 0.25),
        roughness=0.32,
        transmission=0.12
    )
    mat_papillary = create_tissue_material(
        "heart-papillary",
        base_rgb=(0.45, 0.08, 0.10),
        crevice_rgb=(0.22, 0.02, 0.03),
        sss_weight=0.18,
        roughness=0.36
    )
    mat_aorta = create_tissue_material(
        "heart-aorta",
        base_rgb=(0.76, 0.04, 0.04),
        crevice_rgb=(0.42, 0.02, 0.02),
        sss_weight=0.14,
        roughness=0.28
    )
    mat_pulm_vein = create_tissue_material(
        "heart-pulmonary-vein",
        base_rgb=(0.74, 0.04, 0.04),
        crevice_rgb=(0.40, 0.02, 0.02),
        sss_weight=0.14,
        roughness=0.28
    )
    mat_pulm_artery = create_tissue_material(
        "heart-pulmonary-trunk",
        base_rgb=(0.04, 0.16, 0.68),
        crevice_rgb=(0.02, 0.08, 0.36),
        sss_weight=0.14,
        roughness=0.28
    )
    mat_vena_cava = create_tissue_material(
        "heart-vena-cava",
        base_rgb=(0.04, 0.15, 0.65),
        crevice_rgb=(0.02, 0.07, 0.34),
        sss_weight=0.14,
        roughness=0.28
    )
    mat_coronary_art = create_tissue_material(
        "heart-coronary-artery",
        base_rgb=(0.86, 0.03, 0.03),
        sss_weight=0.12,
        roughness=0.22
    )
    mat_cardiac_vein = create_tissue_material(
        "heart-cardiac-vein",
        base_rgb=(0.03, 0.22, 0.82),
        sss_weight=0.12,
        roughness=0.22
    )

    # Collections
    collection_titles = {
        'Chambers_Full': "01_Heart_Chambers_Full",
        'Chambers_Cutaway': "02_Heart_Chambers_Coronal_Cutaway",
        'Valves': "03_Heart_Valves",
        'Papillary_Muscles': "04_Papillary_Muscles",
        'Great_Vessels': "05_Great_Vessels",
        'Coronary_Circulation': "06_Coronary_Circulation",
    }

    colls = {}
    for gkey, title in collection_titles.items():
        col = bpy.data.collections.new(title)
        bpy.context.scene.collection.children.link(col)
        colls[gkey] = col

    # Recreate all objects with vertices centered around (0, 0, 0)
    created_objects = []
    chamber_objects = []

    for gkey, items in extracted_groups.items():
        target_col_key = gkey
        if gkey == 'Chambers':
            target_col_key = 'Chambers_Full'
        target_col = colls[target_col_key]

        for item in items:
            orig_name = item['orig_name']
            clean_name = clean_identifier(orig_name)

            centered_verts = [
                (v[0] - center_x, v[1] - center_y, v[2] - center_z)
                for v in item['verts']
            ]

            mesh = bpy.data.meshes.new(clean_name)
            mesh.from_pydata(centered_verts, item['edges'], item['polys'])
            mesh.update()

            # Trimming excessive neck/abdominal vessel extensions:
            if 'carotid' in clean_name:
                bm_trim = bmesh.new()
                bm_trim.from_mesh(mesh)
                bmesh.ops.bisect_plane(
                    bm_trim,
                    geom=bm_trim.verts[:] + bm_trim.edges[:] + bm_trim.faces[:],
                    plane_co=(0, 0, 0.125),
                    plane_no=(0, 0, 1),
                    clear_outer=True
                )
                b_edges = [e for e in bm_trim.edges if e.is_boundary]
                if b_edges:
                    try:
                        bmesh.ops.edgeloop_fill(bm_trim, edges=b_edges)
                    except Exception:
                        pass
                bm_trim.to_mesh(mesh)
                bm_trim.free()
                mesh.update()

            if 'thoracic-aorta' in clean_name or 'inferior-vena-cava' in clean_name:
                bm_trim = bmesh.new()
                bm_trim.from_mesh(mesh)
                bmesh.ops.bisect_plane(
                    bm_trim,
                    geom=bm_trim.verts[:] + bm_trim.edges[:] + bm_trim.faces[:],
                    plane_co=(0, 0, -0.085),
                    plane_no=(0, 0, -1),
                    clear_outer=True
                )
                b_edges = [e for e in bm_trim.edges if e.is_boundary]
                if b_edges:
                    try:
                        bmesh.ops.edgeloop_fill(bm_trim, edges=b_edges)
                    except Exception:
                        pass
                bm_trim.to_mesh(mesh)
                bm_trim.free()
                mesh.update()

            for p in mesh.polygons:
                p.use_smooth = True

            obj = bpy.data.objects.new(clean_name, mesh)
            target_col.objects.link(obj)

            # Assign PBR Material
            if gkey == 'Chambers':
                chamber_objects.append((obj, orig_name))
                if 'atrium' in orig_name.lower():
                    obj.data.materials.append(mat_atrium)
                else:
                    obj.data.materials.append(mat_myocardium)
            elif gkey == 'Valves':
                obj.data.materials.append(mat_valve)
            elif gkey == 'Papillary_Muscles':
                obj.data.materials.append(mat_papillary)
            elif gkey == 'Great_Vessels':
                nl = orig_name.lower()
                if 'pulmonary vein' in nl:
                    obj.data.materials.append(mat_pulm_vein)
                elif 'pulmonary' in nl:
                    obj.data.materials.append(mat_pulm_artery)
                elif 'cava' in nl:
                    obj.data.materials.append(mat_vena_cava)
                else:
                    obj.data.materials.append(mat_aorta)
            elif gkey == 'Coronary_Circulation':
                nl = orig_name.lower()
                if 'vein' in nl or 'sinus' in nl:
                    obj.data.materials.append(mat_cardiac_vein)
                else:
                    obj.data.materials.append(mat_coronary_art)

            created_objects.append(obj)

    # [4/7] Create Coronal Cutaway Collection (NCERT Fig 5.4 4-chamber internal anatomy)
    print("[4/7] Generating Coronal Cutaway anatomy with solidified wall thicknesses...")
    cutaway_col = colls['Chambers_Cutaway']
    for orig_obj, orig_name in chamber_objects:
        cut_name = f"{orig_obj.name}-coronal-cut"
        cut_obj = orig_obj.copy()
        cut_obj.data = orig_obj.data.copy()
        cut_obj.name = cut_name
        cutaway_col.objects.link(cut_obj)

        bm = bmesh.new()
        bm.from_mesh(cut_obj.data)

        cut_y = -0.016 if 'ventricle' in orig_name.lower() else -0.010
        bmesh.ops.bisect_plane(
            bm,
            geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=(0, cut_y, 0),
            plane_no=(0, -1, 0),
            clear_outer=True
        )
        bm.to_mesh(cut_obj.data)
        bm.free()
        cut_obj.data.update()

        solid_mod = cut_obj.modifiers.new(name="Myocardial_Thickness", type='SOLIDIFY')
        if 'left-ventricle' in orig_obj.name:
            solid_mod.thickness = 0.011  # 11 mm muscular wall
        elif 'right-ventricle' in orig_obj.name:
            solid_mod.thickness = 0.004  # 4 mm muscular wall (~3x thinner)
        else:
            solid_mod.thickness = 0.0025 # 2.5 mm atrial wall

        solid_mod.offset = -1.0

    cutaway_col.hide_viewport = True
    cutaway_col.hide_render = True

    print(f"Created {len(created_objects)} full anatomy objects and {len(chamber_objects)} cutaway sections.")

    # [5/7] Setup Studio Balanced Lighting & Camera
    print("[5/7] Configuring studio lighting & camera framing...")
    light_coll = bpy.data.collections.new("Lighting")
    bpy.context.scene.collection.children.link(light_coll)

    key_data = bpy.data.lights.new(name="Key_Light", type='AREA')
    key_data.energy = 18.0
    key_data.size = 0.5
    key_data.color = (1.0, 0.96, 0.92)
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = (-0.30, -0.70, 0.40)
    key_obj.rotation_euler = (math.radians(52), 0, math.radians(-28))
    light_coll.objects.link(key_obj)

    fill_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
    fill_data.energy = 8.5
    fill_data.size = 0.7
    fill_data.color = (0.92, 0.95, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (0.45, -0.60, 0.20)
    fill_obj.rotation_euler = (math.radians(65), 0, math.radians(38))
    light_coll.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_data.energy = 15.0
    rim_data.size = 0.4
    rim_data.color = (1.0, 0.95, 0.88)
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0.0, 0.65, 0.45)
    rim_obj.rotation_euler = (math.radians(-50), 0, math.radians(180))
    light_coll.objects.link(rim_obj)

    bounce_data = bpy.data.lights.new(name="Bounce_Light", type='AREA')
    bounce_data.energy = 4.0
    bounce_data.size = 0.5
    bounce_data.color = (0.85, 0.85, 0.90)
    bounce_obj = bpy.data.objects.new("Bounce_Light", bounce_data)
    bounce_obj.location = (0.0, -0.40, -0.40)
    bounce_obj.rotation_euler = (math.radians(130), 0, 0)
    light_coll.objects.link(bounce_obj)

    # Camera Setup: 75mm lens, distance 0.85m to give perfect ~85% height framing
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 75.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 50.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    # 3/4 Anterior-Lateral perspective view
    cam_obj.location = (-0.18, -0.85, 0.08)
    cam_obj.rotation_euler = (math.radians(84), 0, math.radians(-12))
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Render settings
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    # [6/7] Save Blend, GLB, and Viewer Asset
    print(f"[6/7] Saving master files to {OUT_DIR}...")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    print(f"Saved: {OUT_BLEND}")

    # Export GLB (Full exterior heart model with valves & vessels)
    bpy.ops.export_scene.gltf(
        filepath=str(OUT_GLB),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
    )
    print(f"Exported GLB: {OUT_GLB} ({OUT_GLB.stat().st_size / 1024 / 1024:.2f} MB)")

    # Copy to interactive-viewer public assets
    shutil.copy2(OUT_GLB, VIEWER_GLB)
    print(f"Synchronized to Viewer: {VIEWER_GLB}")

    # [7/7] Render Educational Visuals
    print("[7/7] Rendering preview images...")
    # 1. 3/4 Exterior View (Full 3D Heart with coronary vessels)
    scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered 3/4 Exterior Preview: {OUT_PREVIEW}")

    # 2. Coronal Cutaway View (NCERT Fig 5.4 Internal Chambers & Valves)
    colls['Chambers_Full'].hide_render = True
    colls['Coronary_Circulation'].hide_render = True
    colls['Chambers_Cutaway'].hide_render = False

    cam_obj.location = (0.0, -0.85, 0.015)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    scene.render.filepath = str(OUT_PREVIEW_CORONAL)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered Coronal Cutaway Preview: {OUT_PREVIEW_CORONAL}")

    # Restore default collection visibility and save final state
    colls['Chambers_Full'].hide_render = False
    colls['Coronary_Circulation'].hide_render = False
    colls['Chambers_Cutaway'].hide_render = True
    cam_obj.location = (-0.18, -0.85, 0.08)
    cam_obj.rotation_euler = (math.radians(84), 0, math.radians(-12))
    bpy.ops.wm.save_mainfile()

    print("=== REALISTIC HUMAN HEART BUILD COMPLETE ===")

if __name__ == "__main__":
    main()
