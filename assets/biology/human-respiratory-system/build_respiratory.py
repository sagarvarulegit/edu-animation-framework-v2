"""
build_respiratory.py — Medical-Grade 3D Construction Pipeline for the Human Respiratory System
CBSE Class 10 Biology (Chapter 5: Life Processes — Respiration in Human Beings, Fig 5.9)
CBSE Class 11 Biology (Chapter 17: Breathing and Exchange of Gases, Fig 17.1)

Key Anatomical Features:
1. Larynx (Voice Box):
   - Hyoid bone anchor arch.
   - Thyroid cartilage with V-shaped Adam's apple (laryngeal prominence), superior notch, and horns.
   - Cricoid cartilage signet ring beneath thyroid.
   - Epiglottis flexible fibrocartilage stalk guarding the laryngeal inlet.
2. Trachea & Carina:
   - 16 authentic C-shaped hyaline cartilaginous rings, open posteriorly (<360 deg arc).
   - Smooth trachealis muscle band bridging dorsal open gap where trachea abuts esophagus.
   - Carina ridge at bifurcation level (T4/T5).
3. Bronchial Arborization:
   - Right primary bronchus: shorter, wider, more vertical (~25 deg).
   - Left primary bronchus: longer, narrower, more horizontal (~45 deg) passing below aortic arch.
   - Lobar (secondary) bronchi: 3 on right (superior, middle, inferior), 2 on left (superior, inferior).
   - Segmental (tertiary) bronchioles arborizing through bronchopulmonary segments.
4. Bilateral Lungs:
   - Right Lung (3 Lobes): Superior, Middle, Inferior separated by oblique and horizontal fissures.
   - Left Lung (2 Lobes): Superior, Inferior with cardiac notch indentation and lingula.
   - Pleural surfaces contoured to thoracic cavity and concave diaphragmatic base.
5. Muscular Diaphragm:
   - Upward convex dome with right dome slightly higher than left dome.
   - Glistening central aponeurotic tendon with radiating peripheral muscle fibers.
6. Magnified Alveolar Cluster & Microvasculature:
   - Terminal bronchiole branching into alveolar ducts and grape-like clusters of spherical alveoli sacs.
   - Pulmonary microvascular capillary meshwork: deoxygenated blue pulmonary arteriole, dense
     anastomosing capillary bed wrapping alveoli, and oxygenated red pulmonary venule.
7. Dual Presentation Collections:
   - Full 3D Respiratory System with translucent pleural surfaces revealing the internal arborization.
   - Coronal cross-section (NCERT Fig 5.9) exposing internal airway branching and lung parenchymal interior.
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

ASSET_ID = "human-respiratory-system"
OUT_DIR = THIS_DIR / "out"
OUT_BLEND = OUT_DIR / "human-respiratory-system.blend"
OUT_GLB = OUT_DIR / "human-respiratory-system.glb"
VIEWER_GLB = ROOT_DIR / "apps" / "interactive-viewer" / "public" / "assets" / "human-respiratory-system.glb"
OUT_PREVIEW = OUT_DIR / "preview.png"
OUT_PREVIEW_SECTION = OUT_DIR / "preview_section.png"


def create_pbr_materials():
    """Builds authentic medical-grade PBR shaders for all respiratory tissues."""
    mats = {}

    # 1. Hyaline Cartilage (trachea C-rings, cricoid)
    cartilage = bpy.data.materials.new("respiratory-cartilage")
    cartilage.use_nodes = True
    bsdf = cartilage.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.78, 0.88, 0.92, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
        bsdf.inputs["Subsurface Radius"].default_value = (0.6, 0.8, 1.0)
        bsdf.inputs["Subsurface Scale"].default_value = 0.015
    mats["cartilage"] = cartilage

    # 2. Thyroid Cartilage (slightly warmer amber-cream cartilage)
    thyroid_mat = bpy.data.materials.new("respiratory-thyroid-cartilage")
    thyroid_mat.use_nodes = True
    bsdf = thyroid_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.58, 0.42, 0.32, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.32
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
        bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.6, 0.4)
    mats["thyroid"] = thyroid_mat

    # 3. Epiglottis (elastic cartilage, yellowish elastic fibrocartilage)
    epiglottis_mat = bpy.data.materials.new("respiratory-epiglottis")
    epiglottis_mat.use_nodes = True
    bsdf = epiglottis_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.78, 0.62, 0.28, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.30
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
        bsdf.inputs["Subsurface Radius"].default_value = (0.9, 0.7, 0.3)
    mats["epiglottis"] = epiglottis_mat

    # 4. Trachealis & Airway Lining (reddish-pink smooth muscle / mucosa)
    airway_mat = bpy.data.materials.new("respiratory-airway-mucosa")
    airway_mat.use_nodes = True
    bsdf = airway_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.62, 0.22, 0.24, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.28
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    mats["airway"] = airway_mat

    # 5. Bronchial Tree (pale salmon pink conducting tubules)
    bronchus_mat = bpy.data.materials.new("respiratory-bronchus")
    bronchus_mat.use_nodes = True
    bsdf = bronchus_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.70, 0.22, 0.25, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.26
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
    mats["bronchus"] = bronchus_mat

    # 6. Lung Parenchyma Exterior (Translucent salmon-pink with subtle SSS & transmission to reveal interior bronchial tree)
    lung_ext_mat = bpy.data.materials.new("respiratory-lung-exterior")
    lung_ext_mat.use_nodes = True
    bsdf = lung_ext_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.84, 0.42, 0.46, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.72
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.72
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.34
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.3)
    mats["lung_exterior"] = lung_ext_mat

    # 7. Lung Parenchyma Cutaway Section (spongy, porous vascular lung tissue)
    lung_sec_mat = bpy.data.materials.new("respiratory-lung-interior")
    lung_sec_mat.use_nodes = True
    bsdf = lung_sec_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.72, 0.28, 0.32, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    mats["lung_section"] = lung_sec_mat

    # 8. Diaphragm Muscle (deep striated reddish-brown muscle)
    diaphragm_mat = bpy.data.materials.new("respiratory-diaphragm")
    diaphragm_mat.use_nodes = True
    bsdf = diaphragm_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.26, 0.07, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.38
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
    mats["diaphragm"] = diaphragm_mat

    # 9. Central Tendon of Diaphragm (pearly white fibrous aponeurosis)
    tendon_mat = bpy.data.materials.new("respiratory-central-tendon")
    tendon_mat.use_nodes = True
    bsdf = tendon_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.90, 0.92, 0.88, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.26
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
    mats["tendon"] = tendon_mat

    # 10. Alveolar Sacs (microscopic thin epithelial vesicles)
    alveolus_mat = bpy.data.materials.new("respiratory-alveolus")
    alveolus_mat.use_nodes = True
    bsdf = alveolus_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.68, 0.70, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.50
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.3)
    mats["alveolus"] = alveolus_mat

    # 11. Capillaries: Oxygenated Red (Pulmonary venules)
    cap_oxy = bpy.data.materials.new("respiratory-capillary-oxy")
    cap_oxy.use_nodes = True
    bsdf = cap_oxy.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.88, 0.08, 0.10, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Metallic"].default_value = 0.10
    mats["cap_oxy"] = cap_oxy

    # 12. Capillaries: Deoxygenated Blue (Pulmonary arterioles)
    cap_deoxy = bpy.data.materials.new("respiratory-capillary-deoxy")
    cap_deoxy.use_nodes = True
    bsdf = cap_deoxy.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.12, 0.32, 0.88, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Metallic"].default_value = 0.10
    mats["cap_deoxy"] = cap_deoxy

    return mats


def build_anatomical_larynx(prefix, mats):
    objs = []

    # 1. Thyroid Cartilage
    bm = bmesh.new()
    num_steps = 16
    slices = []
    for s in range(num_steps):
        t = s / (num_steps - 1)
        z = 0.176 + t * 0.026
        ring = []
        for a in range(-8, 9):
            deg = a * 12.0
            rad = math.radians(deg)
            # Anterior is -Y (deg = 0 => cos = 1 => py is negative)
            v_factor = 1.0 - 0.45 * abs(math.sin(rad * 0.5))
            r = 0.014 * (0.85 + 0.3 * (1.0 - t))
            px = r * math.sin(rad) * 1.15
            py = - (r * math.cos(rad) * v_factor) + 0.002
            # Superior thyroid notch indentation at antero-superior border
            if t > 0.75 and abs(deg) < 25:
                py += 0.004 * (t - 0.75) / 0.25 * (1.0 - abs(deg) / 25)
            # Adam's apple laryngeal prominence pointing anteriorly (-Y)
            if 0.40 < t < 0.75 and abs(deg) < 30:
                py -= 0.0040 * math.sin((t - 0.40) / 0.35 * math.pi) * (1.0 - abs(deg) / 30)
            v = bm.verts.new((px, py, z))
            ring.append(v)
        slices.append(ring)

    for s in range(num_steps - 1):
        for i in range(len(slices[s]) - 1):
            v1 = slices[s][i]
            v2 = slices[s][i + 1]
            v3 = slices[s + 1][i + 1]
            v4 = slices[s + 1][i]
            bm.faces.new([v1, v2, v3, v4])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{prefix}_Thyroid_Cartilage")
    bm.to_mesh(mesh)
    bm.free()

    thyroid_obj = bpy.data.objects.new(f"{prefix}_Thyroid_Cartilage", mesh)
    bpy.context.collection.objects.link(thyroid_obj)
    thyroid_obj.data.materials.append(mats["thyroid"])

    sol = thyroid_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0022
    sub = thyroid_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = thyroid_obj
    thyroid_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()

    objs.append(thyroid_obj)
    # Thyroid cornua (superior and inferior horns)
    sh_r = kit.create_smooth_tube(f"{prefix}_Thyroid_Sup_Horn_R", [(0.014, 0.006, 0.200), (0.014, 0.004, 0.214)], radius=0.0014, cap_ends=True, material=mats["thyroid"])
    sh_l = kit.create_smooth_tube(f"{prefix}_Thyroid_Sup_Horn_L", [(-0.014, 0.006, 0.200), (-0.014, 0.004, 0.214)], radius=0.0014, cap_ends=True, material=mats["thyroid"])
    ih_r = kit.create_smooth_tube(f"{prefix}_Thyroid_Inf_Horn_R", [(0.013, 0.006, 0.178), (0.012, 0.005, 0.168)], radius=0.0013, cap_ends=True, material=mats["thyroid"])
    ih_l = kit.create_smooth_tube(f"{prefix}_Thyroid_Inf_Horn_L", [(-0.013, 0.006, 0.178), (-0.012, 0.005, 0.168)], radius=0.0013, cap_ends=True, material=mats["thyroid"])
    objs.extend([sh_r, sh_l, ih_r, ih_l])

    # 2. Cricoid Cartilage
    bm = bmesh.new()
    num_cric_pts = 24
    num_cric_z = 8
    cric_slices = []
    for s in range(num_cric_z):
        t = s / (num_cric_z - 1)
        ring = []
        for i in range(num_cric_pts):
            theta = 2.0 * math.pi * i / num_cric_pts
            ct = math.cos(theta)
            st = math.sin(theta)
            z_base = 0.166
            height = 0.006 + 0.008 * max(0.0, st)
            z = z_base + t * height
            rx = 0.010
            ry = 0.0105
            v = bm.verts.new((rx * ct, ry * st + 0.003, z))
            ring.append(v)
        cric_slices.append(ring)

    for s in range(num_cric_z - 1):
        for i in range(num_cric_pts):
            next_i = (i + 1) % num_cric_pts
            bm.faces.new([cric_slices[s][i], cric_slices[s][next_i], cric_slices[s + 1][next_i], cric_slices[s + 1][i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{prefix}_Cricoid_Cartilage")
    bm.to_mesh(mesh)
    bm.free()
    cricoid_obj = bpy.data.objects.new(f"{prefix}_Cricoid_Cartilage", mesh)
    bpy.context.collection.objects.link(cricoid_obj)
    cricoid_obj.data.materials.append(mats["cartilage"])
    sol = cricoid_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0020
    sub = cricoid_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = cricoid_obj
    cricoid_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    objs.append(cricoid_obj)

    # 3. Epiglottis
    bm = bmesh.new()
    num_epi_steps = 14
    num_epi_width = 12
    epi_slices = []
    for s in range(num_epi_steps):
        t = s / (num_epi_steps - 1)
        z = 0.190 + t * 0.022
        y = 0.004 + 0.008 * math.sin(t * 0.8 * math.pi)
        w = 0.0085 * math.sin(t * math.pi * 0.85 + 0.15)
        ring = []
        for i in range(num_epi_width):
            u = (i / (num_epi_width - 1) - 0.5) * 2.0
            x = u * w
            cy = y - 0.0025 * (1.0 - u * u)
            ring.append(bm.verts.new((x, cy, z)))
        epi_slices.append(ring)

    for s in range(num_epi_steps - 1):
        for i in range(num_epi_width - 1):
            bm.faces.new([epi_slices[s][i], epi_slices[s][i + 1], epi_slices[s + 1][i + 1], epi_slices[s + 1][i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{prefix}_Epiglottis")
    bm.to_mesh(mesh)
    bm.free()
    epiglottis_obj = bpy.data.objects.new(f"{prefix}_Epiglottis", mesh)
    bpy.context.collection.objects.link(epiglottis_obj)
    epiglottis_obj.data.materials.append(mats["epiglottis"])
    sol = epiglottis_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0016
    sub = epiglottis_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = epiglottis_obj
    epiglottis_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    objs.append(epiglottis_obj)

    # 4. Hyoid Bone Arch
    hyoid_pts = [
        (-0.018, -0.014, 0.216),
        (-0.016, -0.002, 0.218),
        (-0.011, 0.012, 0.219),
        (0.000, 0.016, 0.220),
        (0.011, 0.012, 0.219),
        (0.016, -0.002, 0.218),
        (0.018, -0.014, 0.216),
    ]
    hyoid_obj = kit.create_smooth_tube(f"{prefix}_Hyoid_Bone", hyoid_pts, radius=0.0022, cap_ends=True, material=mats["cartilage"])
    objs.append(hyoid_obj)

    return objs


def build_trachea_and_c_rings(prefix, mats):
    objs = []

    # 1. Trachea Mucosa / Lumen Wall Tube
    trachea_tube = kit.primitive_object(
        f"{prefix}_Trachea_Lumen", "cylinder", mats["airway"],
        size=(0.018, 0.018, 0.068),
        location=(0.0, 0.002, 0.132)
    )
    objs.append(trachea_tube)

    # 2. Posterior Trachealis Muscle
    trachealis = kit.primitive_object(
        f"{prefix}_Trachealis_Muscle", "cube", mats["airway"],
        size=(0.012, 0.0028, 0.068),
        location=(0.0, -0.0065, 0.132)
    )
    objs.append(trachealis)

    # 3. 14 Authentic C-Shaped Hyaline Cartilage Rings
    ring_radius = 0.0102
    num_rings = 14
    z_start = 0.100
    z_step = 0.0045
    for i in range(num_rings):
        rz = z_start + i * z_step
        c_ring_pts = []
        for deg in range(45, 316, 15):
            rad = math.radians(deg)
            rx = ring_radius * math.sin(rad)
            ry = ring_radius * math.cos(rad) + 0.002
            c_ring_pts.append((rx, ry, rz))

        c_ring = kit.create_smooth_tube(
            f"{prefix}_Trachea_C_Ring_{i:02d}", c_ring_pts, radius=0.0013, cap_ends=True, material=mats["cartilage"]
        )
        objs.append(c_ring)

    return objs


def build_bronchial_tree(prefix, mats):
    objs = []

    # 1. Carina bifurcation point at T4/T5 level (z = 0.098)
    r_main_pts = [
        (0.000, 0.002, 0.098),
        (0.008, 0.001, 0.088),
        (0.018, -0.001, 0.076),
        (0.026, -0.002, 0.064),
    ]
    r_main = kit.create_smooth_tube(f"{prefix}_Bronchus_Right_Main", r_main_pts, radius=0.0050, cap_ends=True, material=mats["bronchus"])
    objs.append(r_main)

    l_main_pts = [
        (0.000, 0.002, 0.098),
        (-0.012, 0.001, 0.088),
        (-0.026, -0.001, 0.076),
        (-0.038, -0.003, 0.062),
    ]
    l_main = kit.create_smooth_tube(f"{prefix}_Bronchus_Left_Main", l_main_pts, radius=0.0044, cap_ends=True, material=mats["bronchus"])
    objs.append(l_main)

    # 2. Right Lobar Bronchi (Superior, Middle, Inferior)
    r_sup_pts = [
        (0.018, -0.001, 0.076),
        (0.028, 0.005, 0.088),
        (0.038, 0.008, 0.102),
    ]
    r_sup = kit.create_smooth_tube(f"{prefix}_Bronchus_Right_Superior", r_sup_pts, radius=0.0034, cap_ends=True, material=mats["bronchus"])
    objs.append(r_sup)

    r_mid_pts = [
        (0.026, -0.002, 0.064),
        (0.038, 0.010, 0.054),
        (0.052, 0.009, 0.044),
    ]
    r_mid = kit.create_smooth_tube(f"{prefix}_Bronchus_Right_Middle", r_mid_pts, radius=0.0030, cap_ends=True, material=mats["bronchus"])
    objs.append(r_mid)

    r_inf_pts = [
        (0.026, -0.002, 0.064),
        (0.034, -0.008, 0.046),
        (0.040, -0.006, 0.024),
    ]
    r_inf = kit.create_smooth_tube(f"{prefix}_Bronchus_Right_Inferior", r_inf_pts, radius=0.0032, cap_ends=True, material=mats["bronchus"])
    objs.append(r_inf)

    # 3. Left Lobar Bronchi (Superior and Inferior)
    l_sup_pts = [
        (-0.038, -0.003, 0.062),
        (-0.044, 0.004, 0.078),
        (-0.048, 0.006, 0.096),
    ]
    l_sup = kit.create_smooth_tube(f"{prefix}_Bronchus_Left_Superior", l_sup_pts, radius=0.0034, cap_ends=True, material=mats["bronchus"])
    objs.append(l_sup)

    l_inf_pts = [
        (-0.038, -0.003, 0.062),
        (-0.044, -0.008, 0.046),
        (-0.048, -0.006, 0.022),
    ]
    l_inf = kit.create_smooth_tube(f"{prefix}_Bronchus_Left_Inferior", l_inf_pts, radius=0.0032, cap_ends=True, material=mats["bronchus"])
    objs.append(l_inf)

    # 4. Tertiary Segmental Bronchioles
    segmental_branches = [
        ([(0.038, 0.008, 0.102), (0.036, 0.004, 0.118)], "R_Apical"),
        ([(0.038, 0.008, 0.102), (0.048, 0.014, 0.108)], "R_Anterior"),
        ([(0.038, 0.008, 0.102), (0.046, -0.008, 0.104)], "R_Posterior"),
        ([(0.052, 0.009, 0.044), (0.064, 0.012, 0.042)], "R_Lateral"),
        ([(0.052, 0.009, 0.044), (0.048, 0.018, 0.036)], "R_Medial"),
        ([(0.040, -0.006, 0.024), (0.054, -0.010, 0.018)], "R_Lat_Basal"),
        ([(0.040, -0.006, 0.024), (0.034, 0.008, 0.012)], "R_Med_Basal"),
        ([(0.040, -0.006, 0.024), (0.056, 0.004, 0.028)], "R_Sup_Basal"),
        ([(-0.048, 0.006, 0.096), (-0.044, 0.003, 0.116)], "L_Apicoposterior"),
        ([(-0.048, 0.006, 0.096), (-0.058, 0.012, 0.098)], "L_Anterior"),
        ([(-0.048, 0.006, 0.096), (-0.048, 0.014, 0.068)], "L_Lingular"),
        ([(-0.048, -0.006, 0.022), (-0.060, -0.008, 0.016)], "L_Lat_Basal"),
        ([(-0.048, -0.006, 0.022), (-0.038, 0.008, 0.010)], "L_Med_Basal"),
        ([(-0.048, -0.006, 0.022), (-0.058, 0.004, 0.026)], "L_Sup_Basal"),
    ]
    for pts, tag in segmental_branches:
        b = kit.create_smooth_tube(f"{prefix}_Bronchiole_{tag}", pts, radius=0.0016, cap_ends=True, material=mats["bronchus"])
        objs.append(b)

    return objs


def build_anatomical_lung(name, sign, is_section, mat):
    bm = bmesh.new()
    num_z = 28
    num_pts = 28
    z_min = 0.008
    z_max = 0.126

    slices = []
    for s in range(num_z):
        tz = s / (num_z - 1)
        z = z_min + tz * (z_max - z_min)

        if tz < 0.20:
            wf = 0.90 + tz * 0.80
        elif tz < 0.65:
            wf = 1.06 + 0.14 * math.sin(tz * math.pi)
        else:
            wf = 1.20 * math.cos((tz - 0.65) * (math.pi / 0.80))
        wf = max(wf, 0.16)

        rx = 0.026 * wf
        ry = 0.030 * wf

        center_x = sign * (0.044 - 0.006 * tz)
        center_y = -0.002 * tz

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            ct = math.cos(theta)
            st = math.sin(theta)

            px = rx * ct
            py = ry * st

            if (ct * sign) < 0:
                px *= 0.66

            if sign == -1 and 0.22 < tz < 0.62:
                cardiac_t = math.sin((tz - 0.22) / 0.40 * math.pi)
                if ct > -0.1 and st > -0.2:
                    px -= 0.013 * cardiac_t * 0.75
                    py -= 0.013 * cardiac_t * 0.60

            vz = z
            if s == 0:
                vz = z_min + 0.005 * (1.0 - math.sqrt(ct * ct + st * st))

            v = bm.verts.new((center_x + px, center_y + py, vz))
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

    base_center = bm.verts.new((sign * 0.044, 0.0, z_min + 0.005))
    apex_center = bm.verts.new((sign * 0.038, 0.0, z_max))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][next_i], slices[0][i], base_center])
        bm.faces.new([slices[-1][i], slices[-1][next_i], apex_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(mat)

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    if is_section:
        # Perform clean coronal cutaway: remove anterior half (y > -0.004) to expose internal bronchial tree
        cutter_bm = bmesh.new()
        bmesh.ops.create_cube(cutter_bm, size=1.0)
        c_mesh = bpy.data.meshes.new(f"{name}_Cutter_Mesh")
        cutter_bm.to_mesh(c_mesh)
        cutter_bm.free()
        cutter_obj = bpy.data.objects.new(f"{name}_Cutter", c_mesh)
        bpy.context.collection.objects.link(cutter_obj)
        cutter_obj.scale = (0.20, 0.15, 0.20)
        cutter_obj.location = (sign * 0.044, -0.055, 0.065)
        bpy.context.view_layer.update()

        mod_cut = obj.modifiers.new("Coronal_Cut", "BOOLEAN")
        mod_cut.operation = "DIFFERENCE"
        mod_cut.solver = "EXACT"
        mod_cut.object = cutter_obj
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Coronal_Cut")
        bpy.data.objects.remove(cutter_obj, do_unlink=True)

        # Solidify the cut rim
        mod_sol = obj.modifiers.new("Pleura_Wall", "SOLIDIFY")
        mod_sol.thickness = 0.0022
        bpy.ops.object.modifier_apply(modifier="Pleura_Wall")
        bpy.ops.object.shade_smooth()

    fissure_objs = []
    fissure_mat = bpy.data.materials.get("respiratory-airway-mucosa") or mat
    if sign == 1:
        obl_pts = [
            (0.024, -0.020, 0.094),
            (0.048, -0.014, 0.072),
            (0.068, 0.004, 0.046),
            (0.046, 0.016, 0.028),
        ]
        hor_pts = [
            (0.028, 0.006, 0.060),
            (0.052, 0.016, 0.060),
            (0.068, 0.008, 0.058),
            (0.064, -0.010, 0.056),
        ]
        f1 = kit.create_smooth_tube(f"{name}_Oblique_Fissure", obl_pts, radius=0.0016, cap_ends=True, material=fissure_mat)
        f2 = kit.create_smooth_tube(f"{name}_Horizontal_Fissure", hor_pts, radius=0.0016, cap_ends=True, material=fissure_mat)
        fissure_objs.extend([f1, f2])
    else:
        obl_pts = [
            (-0.022, -0.020, 0.092),
            (-0.046, -0.014, 0.070),
            (-0.066, 0.004, 0.044),
            (-0.044, 0.014, 0.024),
        ]
        f = kit.create_smooth_tube(f"{name}_Oblique_Fissure", obl_pts, radius=0.0016, cap_ends=True, material=fissure_mat)
        fissure_objs.append(f)

    return obj, fissure_objs


def build_anatomical_diaphragm(prefix, mats):
    objs = []
    bm = bmesh.new()

    num_r = 16
    num_phi = 32

    verts_grid = []
    for r_idx in range(num_r):
        tr = r_idx / (num_r - 1)
        ring = []
        for p_idx in range(num_phi):
            phi = 2.0 * math.pi * p_idx / num_phi
            rx = 0.090 * tr
            ry = 0.070 * tr

            px = rx * math.cos(phi)
            py = ry * math.sin(phi)

            r_dist = math.sqrt((px - 0.042)**2 + py**2)
            l_dist = math.sqrt((px + 0.042)**2 + py**2)
            r_dome = math.exp(- (r_dist / 0.045)**2) * 0.022
            l_dome = math.exp(- (l_dist / 0.045)**2) * 0.018

            pz = r_dome + l_dome - 0.012 * (tr**1.6)

            v = bm.verts.new((px, py, pz))
            ring.append(v)
        verts_grid.append(ring)

    for r_idx in range(num_r - 1):
        for p_idx in range(num_phi):
            next_p = (p_idx + 1) % num_phi
            v1 = verts_grid[r_idx][p_idx]
            v2 = verts_grid[r_idx][next_p]
            v3 = verts_grid[r_idx + 1][next_p]
            v4 = verts_grid[r_idx + 1][p_idx]
            bm.faces.new([v1, v2, v3, v4])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{prefix}_Diaphragm_Muscle")
    bm.to_mesh(mesh)
    bm.free()

    dia_obj = bpy.data.objects.new(f"{prefix}_Diaphragm_Muscle", mesh)
    bpy.context.collection.objects.link(dia_obj)
    dia_obj.data.materials.append(mats["diaphragm"])

    sol = dia_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0032
    sub = dia_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = dia_obj
    dia_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    objs.append(dia_obj)

    tendon_obj = kit.primitive_object(
        f"{prefix}_Diaphragm_Central_Tendon", "cylinder", mats["tendon"],
        size=(0.048, 0.038, 0.0035),
        location=(0.0, 0.004, 0.014),
        rotation_euler=(0.08, 0.0, 0.0)
    )
    objs.append(tendon_obj)

    return objs


def build_magnified_alveoli(prefix, mats):
    objs = []
    origin = Vector((0.082, 0.038, 0.024))

    b_pts = [
        (origin.x + 0.004, origin.y - 0.022, origin.z - 0.010),
        (origin.x + 0.002, origin.y - 0.012, origin.z - 0.004),
        (origin.x, origin.y, origin.z),
    ]
    term_b = kit.create_smooth_tube(f"{prefix}_Alveolar_Terminal_Bronchiole", b_pts, radius=0.0032, cap_ends=True, material=mats["bronchus"])
    objs.append(term_b)

    sac_offsets = [
        (0.000, 0.000, 0.000, 0.0085),
        (0.011, 0.005, 0.004, 0.0080),
        (-0.009, 0.006, 0.005, 0.0078),
        (0.004, -0.009, 0.006, 0.0082),
        (-0.007, -0.008, 0.012, 0.0080),
        (0.009, -0.004, 0.014, 0.0084),
        (-0.003, 0.008, 0.016, 0.0082),
        (0.008, 0.007, 0.018, 0.0076),
        (0.002, 0.002, 0.022, 0.0080),
        (-0.010, -0.002, 0.020, 0.0075),
        (0.012, 0.002, 0.012, 0.0078),
        (-0.005, 0.012, 0.010, 0.0076),
    ]
    for idx, (ox, oy, oz, sr) in enumerate(sac_offsets):
        sac = kit.primitive_object(
            f"{prefix}_Alveolus_Sac_{idx:02d}", "uv_sphere", mats["alveolus"],
            size=(sr * 2.0, sr * 2.0, sr * 2.0),
            location=(origin.x + ox, origin.y + oy, origin.z + oz)
        )
        objs.append(sac)

    art_pts = [
        (origin.x - 0.012, origin.y - 0.018, origin.z - 0.006),
        (origin.x - 0.008, origin.y - 0.008, origin.z + 0.002),
        (origin.x - 0.006, origin.y + 0.002, origin.z + 0.010),
    ]
    art = kit.create_smooth_tube(f"{prefix}_Pulmonary_Arteriole_Deoxy", art_pts, radius=0.0016, cap_ends=True, material=mats["cap_deoxy"])
    objs.append(art)

    ven_pts = [
        (origin.x + 0.012, origin.y - 0.018, origin.z - 0.006),
        (origin.x + 0.009, origin.y - 0.006, origin.z + 0.004),
        (origin.x + 0.007, origin.y + 0.004, origin.z + 0.012),
    ]
    ven = kit.create_smooth_tube(f"{prefix}_Pulmonary_Venule_Oxy", ven_pts, radius=0.0016, cap_ends=True, material=mats["cap_oxy"])
    objs.append(ven)

    cap_loops = [
        ([
            (origin.x - 0.006, origin.y + 0.002, origin.z + 0.010),
            (origin.x - 0.012, origin.y + 0.008, origin.z + 0.016),
            (origin.x - 0.006, origin.y + 0.014, origin.z + 0.022),
            (origin.x + 0.002, origin.y + 0.012, origin.z + 0.024),
            (origin.x + 0.007, origin.y + 0.004, origin.z + 0.012),
        ], mats["cap_oxy"], f"{prefix}_Capillary_Loop_1"),
        ([
            (origin.x - 0.006, origin.y + 0.002, origin.z + 0.010),
            (origin.x - 0.002, origin.y - 0.010, origin.z + 0.014),
            (origin.x + 0.012, origin.y - 0.006, origin.z + 0.018),
            (origin.x + 0.014, origin.y + 0.006, origin.z + 0.016),
            (origin.x + 0.007, origin.y + 0.004, origin.z + 0.012),
        ], mats["cap_deoxy"], f"{prefix}_Capillary_Loop_2"),
        ([
            (origin.x + 0.002, origin.y - 0.008, origin.z + 0.002),
            (origin.x + 0.012, origin.y + 0.002, origin.z + 0.006),
            (origin.x + 0.008, origin.y + 0.012, origin.z + 0.010),
            (origin.x - 0.004, origin.y + 0.006, origin.z + 0.006),
        ], mats["cap_oxy"], f"{prefix}_Capillary_Loop_3"),
    ]
    for pts, m, tag in cap_loops:
        c = kit.create_smooth_tube(tag, pts, radius=0.0011, cap_ends=True, material=m)
        objs.append(c)

    return objs


def setup_lighting(coll_lights):
    world = bpy.data.worlds.new("Respiratory_World")
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

    # Calibrated macro light values (Watts in Cycles/EEVEE for 0.25m scale)
    # Key light: Warm main high-angle light
    key_data = bpy.data.lights.new("Key_Light", 'AREA')
    key_data.energy = 14.0
    key_data.color = (1.0, 0.98, 0.94)
    key_data.size = 0.45
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = Vector((0.35, -0.65, 0.40))
    key_obj.rotation_euler = (Vector((0.0, 0.0, 0.11)) - key_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(key_obj)

    # Fill light: Cool soft fill
    fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_data.energy = 7.5
    fill_data.color = (0.86, 0.92, 1.0)
    fill_data.size = 0.55
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = Vector((-0.45, -0.55, 0.30))
    fill_obj.rotation_euler = (Vector((0.0, 0.0, 0.11)) - fill_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(fill_obj)

    # Rim light: Separation edge light from behind
    rim_data = bpy.data.lights.new("Rim_Light", 'AREA')
    rim_data.energy = 11.0
    rim_data.color = (0.94, 0.98, 1.0)
    rim_data.size = 0.40
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = Vector((0.15, 0.55, 0.35))
    rim_obj.rotation_euler = (Vector((0.0, 0.0, 0.11)) - rim_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(rim_obj)

    # Internal cavity / Bottom bounce light
    bounce_data = bpy.data.lights.new("Bounce_Light", 'AREA')
    bounce_data.energy = 4.0
    bounce_data.color = (1.0, 0.88, 0.84)
    bounce_data.size = 0.35
    bounce_obj = bpy.data.objects.new("Bounce_Light", bounce_data)
    bounce_obj.location = Vector((0.0, -0.30, -0.15))
    bounce_obj.rotation_euler = (Vector((0.0, 0.0, 0.10)) - bounce_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(bounce_obj)


def build_scene():
    kit.reset_scene()
    mats = create_pbr_materials()

    root_coll = bpy.context.scene.collection
    coll_full = bpy.data.collections.new("Respiratory_Full")
    coll_section = bpy.data.collections.new("Respiratory_Section")
    coll_lights = bpy.data.collections.new("Studio_Lighting")
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)
    root_coll.children.link(coll_lights)

    setup_lighting(coll_lights)

    # 1. BUILD FULL COLLECTION
    full_objs = []
    full_objs.extend(build_anatomical_larynx("Full", mats))
    full_objs.extend(build_trachea_and_c_rings("Full", mats))
    full_objs.extend(build_bronchial_tree("Full", mats))
    full_objs.extend(build_anatomical_diaphragm("Full", mats))
    full_objs.extend(build_magnified_alveoli("Full", mats))
    r_lung, r_fiss = build_anatomical_lung("Lung_Right_Full", +1, False, mats["lung_exterior"])
    l_lung, l_fiss = build_anatomical_lung("Lung_Left_Full", -1, False, mats["lung_exterior"])
    full_objs.extend([r_lung, *r_fiss, l_lung, *l_fiss])

    for o in full_objs:
        if o.name not in coll_full.objects:
            coll_full.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # 2. BUILD SECTION COLLECTION (Anterior cutaway exposing internal bronchial tree & parenchyma)
    sec_objs = []
    sec_objs.extend(build_anatomical_larynx("Sec", mats))
    sec_objs.extend(build_trachea_and_c_rings("Sec", mats))
    sec_objs.extend(build_bronchial_tree("Sec", mats))
    sec_objs.extend(build_anatomical_diaphragm("Sec", mats))
    sec_objs.extend(build_magnified_alveoli("Sec", mats))
    r_lung_sec, r_fiss_sec = build_anatomical_lung("Lung_Right_Section", +1, True, mats["lung_section"])
    l_lung_sec, l_fiss_sec = build_anatomical_lung("Lung_Left_Section", -1, True, mats["lung_section"])
    sec_objs.extend([r_lung_sec, *r_fiss_sec, l_lung_sec, *l_fiss_sec])

    for o in sec_objs:
        if o.name not in coll_section.objects:
            coll_section.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # 3. CAMERA SETUP
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 52.0
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
    print("=== BUILDING MEDICAL-GRADE HUMAN RESPIRATORY SYSTEM ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    coll_full, coll_section, cam_obj = build_scene()

    # 1. Save blend file
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
    vl.layer_collection.children['Respiratory_Full'].exclude = False
    vl.layer_collection.children['Respiratory_Section'].exclude = True
    coll_full.hide_render = False
    coll_section.hide_render = True

    # Camera location framed to fill 85% of frame
    target = Vector((0.0, 0.0, 0.115))
    cam_loc = Vector((0.26, -0.75, 0.20))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW}")

    # 4. Render Mode B: Coronal Cross-Section Preview (preview_section.png)
    print("Rendering Coronal Cross-Section Preview...")
    vl.layer_collection.children['Respiratory_Full'].exclude = True
    vl.layer_collection.children['Respiratory_Section'].exclude = False
    coll_full.hide_render = True
    coll_section.hide_render = False

    cam_sec_loc = Vector((0.0, -0.72, 0.115))
    cam_obj.location = cam_sec_loc
    cam_obj.rotation_euler = (target - cam_sec_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW_SECTION)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW_SECTION}")

    # Reset visibility
    vl.layer_collection.children['Respiratory_Full'].exclude = False
    vl.layer_collection.children['Respiratory_Section'].exclude = False
    coll_full.hide_render = False
    coll_section.hide_render = False
    bpy.ops.wm.save_mainfile()
    print("=== RESPIRATORY SYSTEM BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
