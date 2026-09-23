"""
build_brain.py — High-Detail Anatomical Human Brain Model
CBSE Class 10 Biology, Chapter 6: Control and Coordination (NCERT Fig 6.3)
CBSE Class 11 Biology, Chapter 21: Neural Control and Coordination — Central Nervous System (Brain)

Anatomical Structures & Coverage:
- Cerebrum: Complete bilateral cerebral hemispheres (Left & Right) with genuine anatomical gyri and sulci
  * Frontal Lobe: Superior, middle, inferior frontal gyri (opercular, triangular, orbital parts), precentral gyrus
  * Parietal Lobe: Postcentral gyrus, superior parietal lobule, supramarginal & angular gyri, central sulcus
  * Temporal Lobe: Superior, middle, inferior temporal gyri, temporal pole, lateral sulcus (Sylvian fissure), insula
  * Occipital Lobe: Superior & lateral occipital gyri, cuneus, lingual gyrus, calcarine sulcus, occipital pole
- Diencephalon & Internal Medial Anatomy (Exposed in Sagittal Cross-Section):
  * Corpus Callosum: Authentic C-shaped commissural arch (rostrum, genu, body, and splenium)
  * Thalamus: Large paired ovoid sensory relay center
  * Hypothalamus: Autonomic and neuroendocrine control center
  * Pituitary Gland (Hypophysis): Adenohypophysis and neurohypophysis
  * Optic Chiasm & Tracts: White matter visual pathways
  * Pineal Gland: Epithalamic neuroendocrine body
  * Ventricular System: Lateral ventricles, third ventricle, fourth ventricle, cerebral aqueduct with CSF fluid shader
- Brainstem:
  * Midbrain (Mesencephalon): Cerebral peduncles and tectal colliculi (superior & inferior colliculi)
  * Pons: Prominent rounded anterior basilar bulge
  * Medulla Oblongata: Pyramids and olivary bodies
  * Spinal Cord: Seamless continuous downward cervical extension
- Hindbrain:
  * Cerebellum: Complete cerebellar hemispheres and vermis with fine horizontal folia striations
"""

import sys
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))
import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector, Matrix

ASSET_ID = "brain"
STANDARD_HEIGHT = 0.14  # 14 cm world scale (standard anatomical adult brain)

SOURCE_BLEND = ROOT_DIR / "assets" / "biology" / "human-heart" / "source" / "extracted" / "Z-Anatomy" / "Startup.blend"
OUT_DIR = Path(__file__).resolve().parent / "out"


def create_pbr_materials():
    mats = {}

    # 1. Cerebral Cortex (Gray matter, gyri & sulci)
    cortex_mat = bpy.data.materials.new("brain-cortex")
    cortex_mat.use_nodes = True
    nt = cortex_mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]

    ao_node = nt.nodes.new("ShaderNodeAmbientOcclusion")
    ao_node.inputs["Distance"].default_value = 0.015

    mix_ao = nt.nodes.new("ShaderNodeMix")
    mix_ao.data_type = 'RGBA'
    mix_ao.blend_type = 'MULTIPLY'
    mix_ao.inputs[0].default_value = 0.65
    mix_ao.inputs[6].default_value = (0.75, 0.52, 0.48, 1.0)  # Ridge tone
    mix_ao.inputs[7].default_value = (0.44, 0.26, 0.24, 1.0)  # Sulcal crevice tone
    nt.links.new(ao_node.outputs["AO"], mix_ao.inputs[0])
    nt.links.new(mix_ao.outputs[2], bsdf.inputs["Base Color"])

    bsdf.inputs["Roughness"].default_value = 0.42
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.36
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.38, 0.22)
        bsdf.inputs["Subsurface Scale"].default_value = 0.012
        if "Subsurface IOR" in bsdf.inputs:
            bsdf.inputs["Subsurface IOR"].default_value = 1.40

    noise_tex = nt.nodes.new("ShaderNodeTexNoise")
    noise_tex.inputs["Scale"].default_value = 500.0
    noise_tex.inputs["Detail"].default_value = 4.0
    noise_tex.inputs["Roughness"].default_value = 0.6
    bump_node = nt.nodes.new("ShaderNodeBump")
    bump_node.inputs["Strength"].default_value = 0.06
    bump_node.inputs["Distance"].default_value = 0.0015
    nt.links.new(noise_tex.outputs["Fac"], bump_node.inputs["Height"])
    nt.links.new(bump_node.outputs["Normal"], bsdf.inputs["Normal"])
    mats["cortex"] = cortex_mat

    # 2. Cerebellar Cortex (Horizontal folia, warm terra-cotta tone with fine folial striations)
    cb_mat = bpy.data.materials.new("brain-cerebellum")
    cb_mat.use_nodes = True
    nt_cb = cb_mat.node_tree
    bsdf_cb = nt_cb.nodes["Principled BSDF"]

    ao_cb = nt_cb.nodes.new("ShaderNodeAmbientOcclusion")
    ao_cb.inputs["Distance"].default_value = 0.012

    mix_cb = nt_cb.nodes.new("ShaderNodeMix")
    mix_cb.data_type = 'RGBA'
    mix_cb.blend_type = 'MULTIPLY'
    mix_cb.inputs[0].default_value = 0.70
    mix_cb.inputs[6].default_value = (0.68, 0.40, 0.34, 1.0)
    mix_cb.inputs[7].default_value = (0.36, 0.18, 0.16, 1.0)
    nt_cb.links.new(ao_cb.outputs["AO"], mix_cb.inputs[0])
    nt_cb.links.new(mix_cb.outputs[2], bsdf_cb.inputs["Base Color"])

    bsdf_cb.inputs["Roughness"].default_value = 0.48
    if "Subsurface Weight" in bsdf_cb.inputs:
        bsdf_cb.inputs["Subsurface Weight"].default_value = 0.32
        bsdf_cb.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.20)
        bsdf_cb.inputs["Subsurface Scale"].default_value = 0.012

    wave_tex = nt_cb.nodes.new("ShaderNodeTexWave")
    wave_tex.wave_type = 'BANDS'
    wave_tex.bands_direction = 'Z'
    wave_tex.inputs["Scale"].default_value = 220.0
    wave_tex.inputs["Distortion"].default_value = 1.2
    bump_cb = nt_cb.nodes.new("ShaderNodeBump")
    bump_cb.inputs["Strength"].default_value = 0.18
    bump_cb.inputs["Distance"].default_value = 0.002
    nt_cb.links.new(wave_tex.outputs["Color"], bump_cb.inputs["Height"])
    nt_cb.links.new(bump_cb.outputs["Normal"], bsdf_cb.inputs["Normal"])
    mats["cerebellum"] = cb_mat

    # 3. Brainstem (Midbrain, Pons, Medulla, Spinal Cord - creamy white matter nerve tracts)
    stem_mat = bpy.data.materials.new("brain-stem")
    stem_mat.use_nodes = True
    nt_s = stem_mat.node_tree
    bsdf_s = nt_s.nodes["Principled BSDF"]
    bsdf_s.inputs["Base Color"].default_value = (0.86, 0.80, 0.70, 1.0)
    bsdf_s.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf_s.inputs:
        bsdf_s.inputs["Subsurface Weight"].default_value = 0.38
        bsdf_s.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.3)
        bsdf_s.inputs["Subsurface Scale"].default_value = 0.014
    mats["stem"] = stem_mat

    # 4. Corpus Callosum (White matter commissure - bright ivory-white)
    cc_mat = bpy.data.materials.new("brain-corpus-callosum")
    cc_mat.use_nodes = True
    nt_cc = cc_mat.node_tree
    bsdf_cc = nt_cc.nodes["Principled BSDF"]
    bsdf_cc.inputs["Base Color"].default_value = (0.92, 0.88, 0.80, 1.0)
    bsdf_cc.inputs["Roughness"].default_value = 0.36
    if "Subsurface Weight" in bsdf_cc.inputs:
        bsdf_cc.inputs["Subsurface Weight"].default_value = 0.45
        bsdf_cc.inputs["Subsurface Radius"].default_value = (1.0, 0.6, 0.4)
        bsdf_cc.inputs["Subsurface Scale"].default_value = 0.015
    mats["corpus_callosum"] = cc_mat

    # 5. Thalamus (Sensory relay nucleus - soft amber-pink)
    th_mat = bpy.data.materials.new("brain-thalamus")
    th_mat.use_nodes = True
    nt_th = th_mat.node_tree
    bsdf_th = nt_th.nodes["Principled BSDF"]
    bsdf_th.inputs["Base Color"].default_value = (0.82, 0.56, 0.48, 1.0)
    bsdf_th.inputs["Roughness"].default_value = 0.44
    if "Subsurface Weight" in bsdf_th.inputs:
        bsdf_th.inputs["Subsurface Weight"].default_value = 0.30
        bsdf_th.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
        bsdf_th.inputs["Subsurface Scale"].default_value = 0.012
    mats["thalamus"] = th_mat

    # 6. Hypothalamus (Autonomic / neuroendocrine center)
    hypo_mat = bpy.data.materials.new("brain-hypothalamus")
    hypo_mat.use_nodes = True
    nt_hy = hypo_mat.node_tree
    bsdf_hy = nt_hy.nodes["Principled BSDF"]
    bsdf_hy.inputs["Base Color"].default_value = (0.84, 0.52, 0.46, 1.0)
    bsdf_hy.inputs["Roughness"].default_value = 0.42
    if "Subsurface Weight" in bsdf_hy.inputs:
        bsdf_hy.inputs["Subsurface Weight"].default_value = 0.30
        bsdf_hy.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
        bsdf_hy.inputs["Subsurface Scale"].default_value = 0.012
    mats["hypothalamus"] = hypo_mat

    # 7. Pituitary Gland (Hypophysis - vascular master gland, rich crimson/pink)
    pit_mat = bpy.data.materials.new("brain-pituitary")
    pit_mat.use_nodes = True
    nt_pit = pit_mat.node_tree
    bsdf_pit = nt_pit.nodes["Principled BSDF"]
    bsdf_pit.inputs["Base Color"].default_value = (0.80, 0.22, 0.24, 1.0)
    bsdf_pit.inputs["Roughness"].default_value = 0.28
    if "Subsurface Weight" in bsdf_pit.inputs:
        bsdf_pit.inputs["Subsurface Weight"].default_value = 0.45
        bsdf_pit.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.15)
        bsdf_pit.inputs["Subsurface Scale"].default_value = 0.010
    mats["pituitary"] = pit_mat

    # 8. Optic Chiasm & Tracts (White matter sensory pathway)
    opt_mat = bpy.data.materials.new("brain-optic")
    opt_mat.use_nodes = True
    nt_opt = opt_mat.node_tree
    bsdf_opt = nt_opt.nodes["Principled BSDF"]
    bsdf_opt.inputs["Base Color"].default_value = (0.89, 0.84, 0.76, 1.0)
    bsdf_opt.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf_opt.inputs:
        bsdf_opt.inputs["Subsurface Weight"].default_value = 0.35
        bsdf_opt.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.3)
        bsdf_opt.inputs["Subsurface Scale"].default_value = 0.012
    mats["optic"] = opt_mat

    # 9. Pineal Gland (Neuroendocrine body)
    pin_mat = bpy.data.materials.new("brain-pineal")
    pin_mat.use_nodes = True
    nt_pin = pin_mat.node_tree
    bsdf_pin = nt_pin.nodes["Principled BSDF"]
    bsdf_pin.inputs["Base Color"].default_value = (0.76, 0.38, 0.36, 1.0)
    bsdf_pin.inputs["Roughness"].default_value = 0.36
    if "Subsurface Weight" in bsdf_pin.inputs:
        bsdf_pin.inputs["Subsurface Weight"].default_value = 0.40
        bsdf_pin.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.15)
        bsdf_pin.inputs["Subsurface Scale"].default_value = 0.010
    mats["pineal"] = pin_mat

    # 10. Ventricles / CSF fluid chambers (Subtle transparent blue glass)
    ven_mat = bpy.data.materials.new("brain-ventricles")
    ven_mat.use_nodes = True
    nt_ven = ven_mat.node_tree
    bsdf_ven = nt_ven.nodes["Principled BSDF"]
    bsdf_ven.inputs["Base Color"].default_value = (0.70, 0.88, 0.96, 1.0)
    bsdf_ven.inputs["Roughness"].default_value = 0.15
    bsdf_ven.inputs["IOR"].default_value = 1.34
    if "Transmission Weight" in bsdf_ven.inputs:
        bsdf_ven.inputs["Transmission Weight"].default_value = 0.80
    if "Specular IOR Level" in bsdf_ven.inputs:
        bsdf_ven.inputs["Specular IOR Level"].default_value = 0.5
    mats["ventricles"] = ven_mat

    return mats


def get_material_for_structure(name, mats):
    nl = name.lower()
    if any(k in nl for k in ["pituitary", "adenohypophysis", "neurohypophysis"]):
        return mats["pituitary"]
    if any(k in nl for k in ["optic chiasm", "optic tract"]):
        return mats["optic"]
    if "pineal" in nl:
        return mats["pineal"]
    if "callosum" in nl or "fornix" in nl:
        return mats["corpus_callosum"]
    if "thalamus" in nl:
        return mats["thalamus"]
    if "hypothalamus" in nl:
        return mats["hypothalamus"]
    if any(k in nl for k in ["ventricle", "aqueduct"]):
        return mats["ventricles"]
    if any(k in nl for k in ["cerebell", "lobule", "vermis", "culmen", "declive", "flocculus", "tonsil", "lingula of cerebell"]):
        return mats["cerebellum"]
    if any(k in nl for k in ["pons", "medulla", "midbrain", "colliculus", "olive", "pyramid", "spinal"]):
        return mats["stem"]
    return mats["cortex"]


def setup_lighting():
    world = bpy.data.worlds.new("edu_world")
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    bg = nt.nodes.new(type="ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.02, 0.025, 0.035, 1.0)
    bg.inputs["Strength"].default_value = 0.35
    out = nt.nodes.new(type="ShaderNodeOutputWorld")
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bpy.context.scene.world = world

    try:
        bpy.context.scene.view_settings.view_transform = 'AgX'
    except Exception:
        try:
            bpy.context.scene.view_settings.view_transform = 'Filmic'
        except Exception:
            pass
    try:
        bpy.context.scene.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass

    # Key light: Warm 4800K light at 45 degrees
    key_data = bpy.data.lights.new("brain_key_light", type="AREA")
    key_data.energy = 25.0
    key_data.color = (1.0, 0.94, 0.88)
    key_data.size = 0.25
    key = bpy.data.objects.new("brain_key_light", key_data)
    bpy.context.scene.collection.objects.link(key)
    key.location = Vector((0.20, -0.25, 0.18))
    key.rotation_euler = (Vector((0, 0, 0)) - key.location).to_track_quat("-Z", "Y").to_euler()

    # Fill light: Cool 6500K soft wrap fill
    fill_data = bpy.data.lights.new("brain_fill_light", type="AREA")
    fill_data.energy = 12.0
    fill_data.color = (0.88, 0.94, 1.0)
    fill_data.size = 0.35
    fill = bpy.data.objects.new("brain_fill_light", fill_data)
    bpy.context.scene.collection.objects.link(fill)
    fill.location = Vector((-0.24, -0.18, 0.10))
    fill.rotation_euler = (Vector((0, 0, 0)) - fill.location).to_track_quat("-Z", "Y").to_euler()

    # Rim light: Accentuate gyri and cerebellum contours
    rim_data = bpy.data.lights.new("brain_rim_light", type="AREA")
    rim_data.energy = 18.0
    rim_data.color = (0.95, 0.98, 1.0)
    rim_data.size = 0.22
    rim = bpy.data.objects.new("brain_rim_light", rim_data)
    bpy.context.scene.collection.objects.link(rim)
    rim.location = Vector((0.12, 0.28, 0.16))
    rim.rotation_euler = (Vector((0, 0, 0)) - rim.location).to_track_quat("-Z", "Y").to_euler()

    # Bottom bounce: subtle soft upward bounce
    bounce_data = bpy.data.lights.new("brain_bounce_light", type="AREA")
    bounce_data.energy = 6.0
    bounce_data.color = (0.85, 0.80, 0.75)
    bounce_data.size = 0.30
    bounce = bpy.data.objects.new("brain_bounce_light", bounce_data)
    bpy.context.scene.collection.objects.link(bounce)
    bounce.location = Vector((0.0, -0.12, -0.20))
    bounce.rotation_euler = (Vector((0, 0, 0)) - bounce.location).to_track_quat("-Z", "Y").to_euler()


def build_brain():
    print(f"[1/6] Loading source dataset: {SOURCE_BLEND}")
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE_BLEND))
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()

    target_groups = {
        "Cerebrum_Left": [],
        "Cerebrum_Right": [],
        "Cerebellum": [],
        "Brainstem": [],
        "Diencephalon_Deep": []
    }

    def is_valid_mesh(o):
        return o and o.type == 'MESH' and len(o.data.vertices) >= 10

    # 1. Left Cerebral Hemisphere
    left_col = bpy.data.collections.get('Left cerebral hemisphere')
    if left_col:
        for o in left_col.objects:
            if is_valid_mesh(o) and not o.name.startswith('White matter'):
                target_groups["Cerebrum_Left"].append(o)

    # 2. Right Cerebral Hemisphere ('Right cerebal hemisphere' in source)
    right_col = bpy.data.collections.get('Right cerebal hemisphere') or bpy.data.collections.get('Right cerebral hemisphere')
    if right_col:
        for o in right_col.objects:
            if is_valid_mesh(o) and not o.name.startswith('White matter'):
                target_groups["Cerebrum_Right"].append(o)

    # 3. Cerebellum
    cb_col = bpy.data.collections.get('Cerebellum')
    if cb_col:
        for o in cb_col.objects:
            if is_valid_mesh(o):
                target_groups["Cerebellum"].append(o)

    # 4. Brainstem
    bs_col = bpy.data.collections.get('Brainstem')
    if bs_col:
        for o in bs_col.objects:
            if is_valid_mesh(o) and not any(k in o.name.lower() for k in ["ventricle", "aqueduct", "nucleus of", "nerve"]):
                target_groups["Brainstem"].append(o)

    # 5. Diencephalon, Endocrine & Deep structures
    deep_names = [
        "Corpus callosum",
        "Thalamus.l", "Thalamus.r",
        "Hypothalamus",
        "Adenohypophysis", "Neurohypophysis",
        "Optic chiasm.l", "Optic chiasm.r",
        "Optic tract.l", "Optic tract.r",
        "Pineal gland",
        "Fornix.l", "Fornix.r",
        "Hippocampus.l", "Hippocampus.r",
        "Lateral ventricle.l", "Lateral ventricle.r",
        "Third ventricle", "Fourth ventricle", "Aqueduct of midbrain"
    ]
    for dname in deep_names:
        obj = bpy.data.objects.get(dname)
        if obj and is_valid_mesh(obj):
            target_groups["Diencephalon_Deep"].append(obj)

    print("[2/6] Structure counts identified:")
    total_count = sum(len(v) for v in target_groups.values())
    for gname, objs in target_groups.items():
        print(f"  - {gname}: {len(objs)} objects")
    print(f"Total target objects: {total_count}")

    # Extract mesh pydata with world matrix baked
    extracted_data = {}
    for gname, objs in target_groups.items():
        extracted_data[gname] = []
        for orig_obj in objs:
            mw = orig_obj.matrix_world.copy()
            if orig_obj.type == 'CURVE':
                eval_obj = orig_obj.evaluated_get(depsgraph)
                temp_mesh = bpy.data.meshes.new_from_object(eval_obj)
            else:
                temp_mesh = orig_obj.data

            verts = [(mw @ v.co)[:] for v in temp_mesh.vertices]
            edges = [list(e.vertices) for e in temp_mesh.edges]
            polys = [list(p.vertices) for p in temp_mesh.polygons]
            extracted_data[gname].append((orig_obj.name, verts, edges, polys))

    # [3/6] Switch to clean new scene
    print("[3/6] Rebuilding clean target scene...")
    bpy.ops.wm.read_homefile(use_empty=True)

    materials = create_pbr_materials()

    main_col = bpy.context.scene.collection
    created_objects = []

    collection_names = {
        "Cerebrum_Left": "Cerebrum (Left Hemisphere)",
        "Cerebrum_Right": "Cerebrum (Right Hemisphere)",
        "Cerebellum": "Cerebellum",
        "Brainstem": "Brainstem",
        "Diencephalon_Deep": "Diencephalon & Internal Structures"
    }

    for gname, items in extracted_data.items():
        col_title = collection_names.get(gname, f"Brain-{gname}")
        col = bpy.data.collections.new(col_title)
        main_col.children.link(col)

        for name, verts, edges, polys in items:
            clean_name = f"brain-{name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace('*', '').replace('\'', '')}"
            mesh = bpy.data.meshes.new(clean_name)
            mesh.from_pydata(verts, edges, polys)
            mesh.update()

            for p in mesh.polygons:
                p.use_smooth = True

            obj = bpy.data.objects.new(clean_name, mesh)
            col.objects.link(obj)

            mat = get_material_for_structure(name, materials)
            obj.data.materials.append(mat)
            created_objects.append(obj)

    # Compute medulla oblongata bottom rim and continuous trajectory for spinal cord
    medulla_objs = [o for o in created_objects if "medulla-oblongata" in o.name]
    if medulla_objs:
        all_med_verts = [v.co for mo in medulla_objs for v in mo.data.vertices]
        min_med_z = min(v.z for v in all_med_verts)

        bottom_verts = [v for v in all_med_verts if v.z <= min_med_z + 0.003]
        bot_cx = sum(v.x for v in bottom_verts) / len(bottom_verts)
        bot_cy = sum(v.y for v in bottom_verts) / len(bottom_verts)

        slice_high = [v for v in all_med_verts if min_med_z + 0.008 <= v.z <= min_med_z + 0.012]
        high_cx = sum(v.x for v in slice_high) / len(slice_high)
        high_cy = sum(v.y for v in slice_high) / len(slice_high)

        dz = 0.010
        dy = bot_cy - high_cy
        dx = bot_cx - high_cx
        pitch_angle = math.atan2(dy, dz)

        bm = bmesh.new()
        cord_depth = 0.022
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=32,
            radius1=0.0055, radius2=0.0048, depth=cord_depth
        )
        bmesh.ops.rotate(bm, cent=Vector((0, 0, 0)), matrix=Matrix.Rotation(pitch_angle, 3, 'X'), verts=bm.verts)

        cord_mesh = bpy.data.meshes.new("brain-spinal-cord")
        bm.to_mesh(cord_mesh)
        bm.free()
        for p in cord_mesh.polygons:
            p.use_smooth = True

        overlap = 0.0025
        center_z = min_med_z - (cord_depth / 2.0) * math.cos(pitch_angle) + overlap
        center_y = bot_cy + (cord_depth / 2.0) * math.sin(pitch_angle)
        for v in cord_mesh.vertices:
            v.co += Vector((bot_cx, center_y, center_z))

        cord_obj = bpy.data.objects.new("brain-spinal-cord", cord_mesh)
        stem_col = bpy.data.collections.get("Brainstem") or main_col
        stem_col.objects.link(cord_obj)
        cord_obj.location = Vector((0.0, 0.0, 0.0))
        cord_obj.data.materials.append(materials["stem"])
        created_objects.append(cord_obj)

    bpy.context.view_layer.update()

    # [4/6] Normalize bounding box & scale to real-world anatomical standard
    print("[4/6] Centering and scaling model to anatomical standard...")
    all_verts = []
    for obj in created_objects:
        for v in obj.data.vertices:
            all_verts.append(v.co)

    if all_verts:
        center = sum(all_verts, Vector()) / len(all_verts)
        min_z = min(p.z for p in all_verts)
        max_z = max(p.z for p in all_verts)
        height = max(max_z - min_z, 0.001)
        scale_factor = STANDARD_HEIGHT / height

        for obj in created_objects:
            for v in obj.data.vertices:
                v.co = (v.co - center) * scale_factor
            obj.location = Vector((0.0, 0.0, 0.0))
            obj.data.update()

    bpy.context.view_layer.update()

    # [5/6] Setup 3-Point Educational Studio Lighting & Camera
    print("[5/6] Setting up studio environment, lighting & camera...")
    setup_lighting()

    cam_data = bpy.data.cameras.new("edu_camera")
    cam_data.lens = 72.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 10.0
    cam_obj = bpy.data.objects.new("edu_camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    cam_dist = 0.17
    cam_elev = 0.015
    cam_angle = math.radians(45.0)
    cam_x = cam_dist * math.sin(cam_angle)
    cam_y = -cam_dist * math.cos(cam_angle)
    cam_z = cam_elev
    cam_obj.location = Vector((cam_x, cam_y, cam_z))
    target = Vector((0.0, 0.0, 0.008))
    direction = target - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items else 'BLENDER_EEVEE'

    return created_objects


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    build_brain()

    # [6/6] Save outputs
    print("[6/6] Saving outputs (.blend, .glb, preview.png)...")
    blend_path = OUT_DIR / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"  [OK] Saved blend: {blend_path}")

    glb_path = OUT_DIR / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"  [OK] Exported GLB: {glb_path}")

    preview_path = OUT_DIR / "preview.png"
    kit.render_preview(preview_path)
    print(f"  [OK] Rendered preview: {preview_path}")

    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
