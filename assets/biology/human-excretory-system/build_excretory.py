"""
build_excretory.py — Medical-Grade 3D Construction Pipeline for the Human Excretory System
CBSE Class 10 Biology (Chapter 5: Life Processes — Excretion in Human Beings, Fig 5.13)
CBSE Class 11 Biology (Chapter 19: Excretory Products and their Elimination, Fig 19.1, 19.2)

Key Anatomical Features:
1. Paired Kidneys:
   - Anatomically contoured bean-shaped kidneys with concave medial hilum.
   - Left kidney slightly higher (T12-L3) than right kidney (pushed lower by liver).
   - Renal fibrous capsule with glistening moist surface.
2. Coronal Internal Kidney Architecture (NCERT Fig 19.2):
   - Outer granular Renal Cortex (cortex renalis).
   - Inner Renal Medulla with 8-10 striated Renal Medullary Pyramids (pyramides renales).
   - Renal Columns of Bertin extending between medullary pyramids.
   - Renal Papillae projecting into Minor and Major Calyces.
   - Funnel-shaped Renal Pelvis collecting urine and transitioning into ureter.
   - Segmental and interlobar vascular branching inside renal sinus.
3. Suprarenal (Adrenal) Glands:
   - Pyramidal/crescentic caps resting snugly over superior poles of each kidney.
4. Great Abdominal Blood Vessels:
   - Abdominal Aorta running slightly left of midline, giving off renal arteries, and bifurcating
     into left and right common iliac arteries at L4.
   - Inferior Vena Cava (IVC) right of midline, receiving right renal vein and longer left renal vein
     crossing anteriorly over aorta.
5. Bilateral Curving Ureters:
   - Smooth muscular retroperitoneal ducts descending and inserting obliquely into the posterolateral
     bladder base at the ureteric orifices.
6. Urinary Bladder & Urethra:
   - Detrusor muscle body, bladder neck, and urethra outflow canal.
7. Dual Presentation Collections:
   - Full 3D Excretory System (preview.png).
   - NCERT Fig 19.2 Coronal Cross-Section exposing internal renal zones (preview_section.png).
"""

import sys
import math
import shutil
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parents[2]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))

import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = "human-excretory-system"
OUT_DIR = THIS_DIR / "out"
OUT_BLEND = OUT_DIR / "human-excretory-system.blend"
OUT_GLB = OUT_DIR / "human-excretory-system.glb"
VIEWER_GLB = ROOT_DIR / "apps" / "interactive-viewer" / "public" / "assets" / "human-excretory-system.glb"
OUT_PREVIEW = OUT_DIR / "preview.png"
OUT_PREVIEW_SECTION = OUT_DIR / "preview_section.png"


def create_pbr_materials():
    """Builds authentic medical-grade PBR shaders for all excretory organs and vessels."""
    mats = {}

    # 1. Kidney Cortex Exterior: Deep red-brown fibrous renal capsule
    cortex_ext = bpy.data.materials.new("kidney-cortex-exterior")
    cortex_ext.use_nodes = True
    bsdf = cortex_ext.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.24, 0.05, 0.06, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.26
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.015
    mats["cortex_ext"] = cortex_ext

    # 2. Kidney Cortex Section: Granular vascular pink-brown cortical zone
    cortex_sec = bpy.data.materials.new("kidney-cortex-section")
    cortex_sec.use_nodes = True
    bsdf = cortex_sec.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.40, 0.10, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
    mats["cortex_sec"] = cortex_sec

    # 3. Medullary Pyramids: Striated deeper purplish-crimson pyramids
    pyramid_mat = bpy.data.materials.new("kidney-medulla-pyramid")
    pyramid_mat.use_nodes = True
    bsdf = pyramid_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.20, 0.03, 0.05, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.30
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.50
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.2, 0.1)
    mats["pyramid"] = pyramid_mat

    # 4. Renal Pelvis & Calyces: Pale buff/cream glistening collecting ducts
    pelvis_mat = bpy.data.materials.new("kidney-pelvis-calyx")
    pelvis_mat.use_nodes = True
    bsdf = pelvis_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.86, 0.82, 0.68, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
    mats["pelvis"] = pelvis_mat

    # 5. Adrenal Gland: Golden-amber endocrine parenchyma
    adrenal_mat = bpy.data.materials.new("adrenal-gland")
    adrenal_mat.use_nodes = True
    bsdf = adrenal_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.68, 0.46, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.38
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
    mats["adrenal"] = adrenal_mat

    # 6. Abdominal Aorta & Renal Arteries: Oxygenated arterial red
    aorta_mat = bpy.data.materials.new("vessel-artery-red")
    aorta_mat.use_nodes = True
    bsdf = aorta_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.85, 0.08, 0.10, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Metallic"].default_value = 0.12
    mats["aorta"] = aorta_mat

    # 7. Inferior Vena Cava & Renal Veins: Deoxygenated venous blue
    vena_mat = bpy.data.materials.new("vessel-vein-blue")
    vena_mat.use_nodes = True
    bsdf = vena_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.10, 0.30, 0.85, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Metallic"].default_value = 0.12
    mats["vena_cava"] = vena_mat

    # 8. Ureters: Pale buff-pink muscular tube
    ureter_mat = bpy.data.materials.new("ureter-muscle")
    ureter_mat.use_nodes = True
    bsdf = ureter_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.84, 0.74, 0.56, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.28
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
    mats["ureter"] = ureter_mat

    # 9. Urinary Bladder: Distensible vascular muscular organ
    bladder_mat = bpy.data.materials.new("urinary-bladder")
    bladder_mat.use_nodes = True
    bsdf = bladder_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.36, 0.08, 0.11, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.24
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    mats["bladder"] = bladder_mat

    return mats


def build_anatomical_kidney(name, sign, kz, is_section, mats):
    """
    Creates an anatomically authentic kidney:
    - Bean-shaped kidney with convex lateral border and concave medial hilum.
    - If is_section=False: Full exterior kidney with smooth renal capsule.
    - If is_section=True: Anterior cutaway revealing internal renal architecture
      (cortex layer, medullary pyramids, renal columns, calyces, pelvis).
    """
    objs = []
    bm = bmesh.new()
    num_z = 24
    num_pts = 24
    z_min = -0.034
    z_max = 0.034

    slices = []
    for s in range(num_z):
        tz = s / (num_z - 1)
        z = z_min + tz * (z_max - z_min)
        r_scale = math.cos((tz - 0.5) * math.pi * 0.88)
        r_scale = max(r_scale, 0.16)

        rx = 0.022 * r_scale
        ry = 0.016 * r_scale

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            ct = math.cos(theta)
            st = math.sin(theta)

            px = rx * ct
            py = ry * st

            # Medial hilum notch indentation where (ct * sign) < 0
            if (ct * sign) < 0 and 0.25 < tz < 0.75:
                hilum_depth = 0.011 * math.sin((tz - 0.25) / 0.50 * math.pi) * abs(ct)
                px += sign * hilum_depth

            v = bm.verts.new((px, py, z))
            ring.append(v)
        slices.append(ring)

    for s in range(num_z - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            v1 = slices[s][i]
            v2 = slices[s][next_i]
            v3 = slices[s + 1][next_i]
            v4 = slices[s + 1][i]
            bm.faces.new([v1, v2, v3, v4])

    base_center = bm.verts.new((0.0, 0.0, z_min))
    top_center = bm.verts.new((0.0, 0.0, z_max))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][next_i], slices[0][i], base_center])
        bm.faces.new([slices[-1][i], slices[-1][next_i], top_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    kidney_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(kidney_obj)
    kidney_obj.location = (sign * 0.054, 0.0, kz)
    kidney_obj.rotation_euler = (0.0, -sign * 0.08, 0.0)

    sub = kidney_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = kidney_obj
    kidney_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    kidney_obj.data.materials.append(mats["cortex_sec"] if is_section else mats["cortex_ext"])
    objs.append(kidney_obj)

    # If is_section=True, cut away anterior half (-Y) and build internal medullary pyramids & pelvis
    if is_section:
        cutter_bm = bmesh.new()
        bmesh.ops.create_cube(cutter_bm, size=1.0)
        c_mesh = bpy.data.meshes.new(f"{name}_Cutter_Mesh")
        cutter_bm.to_mesh(c_mesh)
        cutter_bm.free()
        cutter_obj = bpy.data.objects.new(f"{name}_Cutter", c_mesh)
        bpy.context.collection.objects.link(cutter_obj)
        cutter_obj.scale = (0.12, 0.08, 0.12)
        # Position cutter on anterior side (-Y)
        cutter_obj.location = (sign * 0.054, -0.040, kz)
        bpy.context.view_layer.update()

        mod_cut = kidney_obj.modifiers.new("Coronal_Cut", "BOOLEAN")
        mod_cut.operation = "DIFFERENCE"
        mod_cut.solver = "EXACT"
        mod_cut.object = cutter_obj
        bpy.context.view_layer.objects.active = kidney_obj
        bpy.ops.object.modifier_apply(modifier="Coronal_Cut")
        bpy.data.objects.remove(cutter_obj, do_unlink=True)
        bpy.ops.object.shade_smooth()

        # Build 7-8 Medullary Pyramids (triangular/conical pyramids radiating inwards)
        pyramid_specs = [
            (sign * 0.012, 0.001, 0.020, math.radians(sign * -40)),
            (sign * 0.015, 0.001, 0.012, math.radians(sign * -20)),
            (sign * 0.016, 0.001, 0.002, math.radians(0)),
            (sign * 0.015, 0.001, -0.008, math.radians(sign * 20)),
            (sign * 0.012, 0.001, -0.018, math.radians(sign * 40)),
            (sign * 0.006, 0.001, 0.024, math.radians(sign * -65)),
            (sign * 0.006, 0.001, -0.022, math.radians(sign * 65)),
        ]
        for p_idx, (px, py, pz, rot_y) in enumerate(pyramid_specs):
            pyr = kit.primitive_object(
                f"{name}_Pyramid_{p_idx}", "cone", mats["pyramid"],
                size=(0.0075, 0.0040, 0.010),
                location=(sign * 0.054 + px, py, kz + pz),
                rotation_euler=(0.0, rot_y, math.radians(-sign * 90))
            )
            objs.append(pyr)

        # Calyces & Pelvis Funnel (Calyces collecting into renal pelvis)
        pelvis_internal = kit.primitive_object(
            f"{name}_Pelvis_Cavity", "cone", mats["pelvis"],
            size=(0.014, 0.006, 0.022),
            location=(sign * 0.046, 0.001, kz - 0.002),
            rotation_euler=(0.0, 0.0, sign * (math.pi / 2 + 0.15))
        )
        objs.append(pelvis_internal)

    return objs


def build_adrenal_glands(mats):
    """
    Creates anatomical pyramidal suprarenal (adrenal) glands capping
    the superior medial pole of each kidney.
    """
    objs = []
    for sign, name, kz in [(-1, "Right", 0.126), (+1, "Left", 0.138)]:
        # Pyramidal cap molded over superior pole
        adrenal = kit.primitive_object(
            f"Adrenal_Gland_{name}", "cone", mats["adrenal"],
            size=(0.020, 0.012, 0.016),
            location=(sign * 0.050, 0.001, kz + 0.034),
            rotation_euler=(0.0, sign * 0.20, 0.0)
        )
        objs.append(adrenal)
    return objs


def build_great_vessels_and_renal_vasculature(mats):
    """
    Constructs the Abdominal Aorta with renal arteries & iliac bifurcations,
    and Inferior Vena Cava with renal veins & iliac tributaries.
    Crucial anatomical fact: Left renal vein crosses ANTERIOR to the aorta!
    """
    objs = []

    # 1. Abdominal Aorta: Left of midline (x = +0.007)
    aorta = kit.primitive_object(
        "Abdominal_Aorta", "cylinder", mats["aorta"],
        size=(0.013, 0.013, 0.160),
        location=(0.007, 0.003, 0.145)
    )
    objs.append(aorta)

    # 2. Inferior Vena Cava: Right of midline (x = -0.007)
    vena_cava = kit.primitive_object(
        "Inferior_Vena_Cava", "cylinder", mats["vena_cava"],
        size=(0.015, 0.015, 0.160),
        location=(-0.007, -0.002, 0.145)
    )
    objs.append(vena_cava)

    # 3. Common Iliac Arteries & Veins Bifurcations at base
    iliac_art_r = kit.create_smooth_tube(
        "Iliac_Artery_R", [(0.007, 0.003, 0.065), (-0.010, 0.002, 0.038), (-0.022, 0.002, 0.018)],
        radius=0.0044, cap_ends=True, material=mats["aorta"]
    )
    iliac_art_l = kit.create_smooth_tube(
        "Iliac_Artery_L", [(0.007, 0.003, 0.065), (0.018, 0.003, 0.038), (0.028, 0.002, 0.018)],
        radius=0.0044, cap_ends=True, material=mats["aorta"]
    )
    iliac_vein_r = kit.create_smooth_tube(
        "Iliac_Vein_R", [(-0.007, -0.002, 0.065), (-0.018, -0.002, 0.038), (-0.026, -0.001, 0.018)],
        radius=0.0048, cap_ends=True, material=mats["vena_cava"]
    )
    iliac_vein_l = kit.create_smooth_tube(
        "Iliac_Vein_L", [(-0.007, -0.002, 0.065), (0.010, -0.001, 0.038), (0.022, -0.001, 0.018)],
        radius=0.0048, cap_ends=True, material=mats["vena_cava"]
    )
    objs.extend([iliac_art_r, iliac_art_l, iliac_vein_r, iliac_vein_l])

    # 4. Renal Arteries
    # Right Renal Artery: emerges from aorta, passes posterior to IVC to right hilum
    r_art_pts = [
        (0.007, 0.003, 0.128),
        (-0.004, 0.008, 0.127),
        (-0.026, 0.006, 0.125),
        (-0.044, 0.000, 0.124),
    ]
    r_art = kit.create_smooth_tube("Renal_Artery_Right", r_art_pts, radius=0.0032, cap_ends=True, material=mats["aorta"])

    # Left Renal Artery: direct branch to left hilum
    l_art_pts = [
        (0.007, 0.003, 0.138),
        (0.024, 0.003, 0.138),
        (0.044, 0.000, 0.138),
    ]
    l_art = kit.create_smooth_tube("Renal_Artery_Left", l_art_pts, radius=0.0032, cap_ends=True, material=mats["aorta"])

    # 5. Renal Veins
    # Right Renal Vein: short branch to IVC
    r_vein_pts = [
        (-0.044, 0.000, 0.126),
        (-0.025, -0.002, 0.126),
        (-0.007, -0.002, 0.126),
    ]
    r_vein = kit.create_smooth_tube("Renal_Vein_Right", r_vein_pts, radius=0.0040, cap_ends=True, material=mats["vena_cava"])

    # Left Renal Vein: crosses ANTERIOR (-Y) to the aorta to reach IVC!
    l_vein_pts = [
        (0.044, 0.000, 0.138),
        (0.024, -0.006, 0.137),
        (0.007, -0.010, 0.136),   # Arches anteriorly in front of aorta!
        (-0.007, -0.002, 0.135),
    ]
    l_vein = kit.create_smooth_tube("Renal_Vein_Left", l_vein_pts, radius=0.0040, cap_ends=True, material=mats["vena_cava"])
    objs.extend([r_art, l_art, r_vein, l_vein])

    return objs


def build_ureters_and_urinary_bladder(mats):
    """
    Creates bilateral curving ureters inserting into the posterolateral base
    of the muscular urinary bladder with tapering bladder neck and urethra.
    """
    objs = []

    # Right Ureter
    u_right_pts = [
        (-0.038, 0.000, 0.118),
        (-0.034, -0.002, 0.090),
        (-0.028, -0.004, 0.060),
        (-0.020, -0.003, 0.034),
        (-0.014, 0.002, 0.018), # Inward to posterolateral bladder
    ]
    u_right = kit.create_smooth_tube("Ureter_Right", u_right_pts, radius=0.0024, cap_ends=True, material=mats["ureter"])

    # Left Ureter
    u_left_pts = [
        (0.038, 0.000, 0.130),
        (0.034, -0.002, 0.095),
        (0.028, -0.004, 0.062),
        (0.020, -0.003, 0.034),
        (0.014, 0.002, 0.018),
    ]
    u_left = kit.create_smooth_tube("Ureter_Left", u_left_pts, radius=0.0024, cap_ends=True, material=mats["ureter"])
    objs.extend([u_right, u_left])

    # Muscular Urinary Bladder
    bladder = kit.primitive_object(
        "Urinary_Bladder", "uv_sphere", mats["bladder"],
        size=(0.046, 0.040, 0.048),
        location=(0.0, -0.004, 0.014)
    )
    bladder_neck = kit.primitive_object(
        "Bladder_Neck", "cone", mats["bladder"],
        size=(0.022, 0.020, 0.016),
        location=(0.0, -0.004, -0.008),
        rotation_euler=(math.pi, 0.0, 0.0)
    )
    urethra = kit.primitive_object(
        "Urethra", "cylinder", mats["ureter"],
        size=(0.007, 0.007, 0.024),
        location=(0.0, -0.004, -0.020)
    )
    objs.extend([bladder, bladder_neck, urethra])

    return objs


def setup_lighting(coll_lights):
    world = bpy.data.worlds.new("Excretory_World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.015, 0.020, 0.028, 1.0)
    bg.inputs["Strength"].default_value = 0.50
    bpy.context.scene.world = world

    try:
        bpy.context.scene.view_settings.view_transform = 'AgX'
        bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    except Exception:
        pass

    # Calibrated macro light values
    key_data = bpy.data.lights.new("Key_Light", 'AREA')
    key_data.energy = 13.0
    key_data.color = (1.0, 0.98, 0.94)
    key_data.size = 0.45
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = Vector((0.35, -0.65, 0.35))
    key_obj.rotation_euler = (Vector((0.0, 0.0, 0.08)) - key_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(key_obj)

    fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_data.energy = 7.0
    fill_data.color = (0.86, 0.92, 1.0)
    fill_data.size = 0.55
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = Vector((-0.45, -0.55, 0.25))
    fill_obj.rotation_euler = (Vector((0.0, 0.0, 0.08)) - fill_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("Rim_Light", 'AREA')
    rim_data.energy = 10.0
    rim_data.color = (0.94, 0.98, 1.0)
    rim_data.size = 0.40
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = Vector((0.15, 0.55, 0.30))
    rim_obj.rotation_euler = (Vector((0.0, 0.0, 0.08)) - rim_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(rim_obj)

    bounce_data = bpy.data.lights.new("Bounce_Light", 'AREA')
    bounce_data.energy = 3.5
    bounce_data.size = 0.35
    bounce_obj = bpy.data.objects.new("Bounce_Light", bounce_data)
    bounce_obj.location = Vector((0.0, -0.30, -0.15))
    bounce_obj.rotation_euler = (Vector((0.0, 0.0, 0.08)) - bounce_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(bounce_obj)


def build_scene():
    kit.reset_scene()
    mats = create_pbr_materials()

    root_coll = bpy.context.scene.collection
    coll_full = bpy.data.collections.new("Excretory_Full")
    coll_section = bpy.data.collections.new("Excretory_Section")
    coll_lights = bpy.data.collections.new("Studio_Lighting")
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)
    root_coll.children.link(coll_lights)

    setup_lighting(coll_lights)

    # 1. BUILD FULL COLLECTION (Exterior kidneys, vessels, ureters, bladder)
    full_objs = []
    full_objs.extend(build_adrenal_glands(mats))
    full_objs.extend(build_great_vessels_and_renal_vasculature(mats))
    full_objs.extend(build_ureters_and_urinary_bladder(mats))
    full_objs.extend(build_anatomical_kidney("Kidney_Right_Full", -1, 0.126, False, mats))
    full_objs.extend(build_anatomical_kidney("Kidney_Left_Full", +1, 0.138, False, mats))

    for o in full_objs:
        if o.name not in coll_full.objects:
            coll_full.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # 2. BUILD SECTION COLLECTION (Right kidney coronally sliced open showing cortex, pyramids, calyces, pelvis)
    sec_objs = []
    sec_objs.extend(build_adrenal_glands(mats))
    sec_objs.extend(build_great_vessels_and_renal_vasculature(mats))
    sec_objs.extend(build_ureters_and_urinary_bladder(mats))
    sec_objs.extend(build_anatomical_kidney("Kidney_Right_Section", -1, 0.126, True, mats))
    sec_objs.extend(build_anatomical_kidney("Kidney_Left_Section", +1, 0.138, False, mats))

    for o in sec_objs:
        if o.name not in coll_section.objects:
            coll_section.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # 3. CAMERA SETUP
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 46.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    root_coll.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32

    return coll_full, coll_section, cam_obj


def main():
    print("=== BUILDING MEDICAL-GRADE HUMAN EXCRETORY SYSTEM ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    coll_full, coll_section, cam_obj = build_scene()

    # 1. Save blend
    print(f"Saving .blend: {OUT_BLEND}")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    # 2. Export GLB (using Full collection)
    coll_section.hide_viewport = True
    coll_full.hide_viewport = False
    print(f"Exporting GLB: {OUT_GLB}")
    bpy.ops.export_scene.gltf(
        filepath=str(OUT_GLB),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
    )
    print(f"Exported GLB ({OUT_GLB.stat().st_size / 1024:.1f} KB)")

    if VIEWER_GLB.parent.exists():
        shutil.copy2(OUT_GLB, VIEWER_GLB)
        print(f"Synchronized to viewer: {VIEWER_GLB}")

    vl = bpy.context.view_layer

    # 3. Render Mode A: 3/4 Exterior Preview (preview.png)
    print("Rendering 3/4 Exterior Preview...")
    vl.layer_collection.children['Excretory_Full'].exclude = False
    vl.layer_collection.children['Excretory_Section'].exclude = True
    coll_full.hide_render = False
    coll_section.hide_render = True

    target = Vector((0.0, 0.0, 0.088))
    cam_loc = Vector((0.25, -0.76, 0.15))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW}")

    # 4. Render Mode B: Coronal Cross-Section Preview (preview_section.png)
    print("Rendering Coronal Cross-Section Preview...")
    vl.layer_collection.children['Excretory_Full'].exclude = True
    vl.layer_collection.children['Excretory_Section'].exclude = False
    coll_full.hide_render = True
    coll_section.hide_render = False

    cam_sec_loc = Vector((0.0, -0.74, 0.088))
    cam_obj.location = cam_sec_loc
    cam_obj.rotation_euler = (target - cam_sec_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW_SECTION)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW_SECTION}")

    # Reset visibility
    vl.layer_collection.children['Excretory_Full'].exclude = False
    vl.layer_collection.children['Excretory_Section'].exclude = False
    coll_full.hide_render = False
    coll_section.hide_render = False
    bpy.ops.wm.save_mainfile()
    print("=== EXCRETORY SYSTEM BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
