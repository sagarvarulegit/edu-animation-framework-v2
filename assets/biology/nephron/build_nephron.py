"""
build_nephron.py — Medical-Grade 3D Construction Pipeline for the Nephron
CBSE Class 10 Biology (Chapter 5: Life Processes — Excretion in Human Beings, Fig 5.14)
CBSE Class 11 Biology (Chapter 19: Excretory Products and their Elimination, Fig 19.3)

Key Anatomical Features:
1. Malpighian Body (Renal Corpuscle):
   - Bowman's Capsule: Double-walled cup with open cutaway hemisphere revealing internal capsular space.
   - Glomerulus: Dense anastomosing capillary knot nestled inside the cup.
   - Afferent Arteriole: Wider diameter inflow arteriole carrying high-pressure blood.
   - Efferent Arteriole: Narrower diameter outflow arteriole creating glomerular hydrostatic pressure.
2. Proximal Convoluted Tubule (PCT):
   - Dense convolutions and loops in renal cortex lined with brush-border microvilli epithelium.
3. Hairpin Loop of Henle:
   - Thin descending limb entering renal medulla (permeable to water).
   - Medullary hairpin U-turn bend.
   - Thick ascending limb (TAL) ascending back to cortex (active ion transport, impermeable to water).
4. Juxtaglomerular Contact (Macula Densa):
   - Thick ascending limb curves intimately between afferent and efferent arterioles at vascular pole.
5. Distal Convoluted Tubule (DCT):
   - Cortical tortuous convolutions connecting to collecting duct.
6. Collecting Duct:
   - Robust vertical collecting trunk receiving tributary branches from multiple nephrons.
7. Peritubular Capillary Network & Vasa Recta:
   - Extensive microvascular capillary meshwork entwining PCT and DCT.
   - Slender hairpin Vasa Recta loops running parallel to Henle's loop.
   - Continuous color transition: arterial red -> purple capillary mesh -> venous blue drainage.
8. Corticomedullary Boundary:
   - Clear demarcation line dividing Renal Cortex (z > 0) from Renal Medulla (z < 0).
9. Dual Presentation Collections:
   - Full Nephron Unit with rich capillary network (preview.png).
   - Section / Corpuscle Closeup showcasing ultrafiltration in the glomerulus (preview_section.png).
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

ASSET_ID = "nephron"
OUT_DIR = THIS_DIR / "out"
OUT_BLEND = OUT_DIR / "nephron.blend"
OUT_GLB = OUT_DIR / "nephron.glb"
VIEWER_GLB = ROOT_DIR / "apps" / "interactive-viewer" / "public" / "assets" / "nephron.glb"
OUT_PREVIEW = OUT_DIR / "preview.png"
OUT_PREVIEW_SECTION = OUT_DIR / "preview_section.png"


def create_pbr_materials():
    """Builds authentic medical-grade PBR shaders for nephron tissues and microvasculature."""
    mats = {}

    # 1. Bowman's Capsule: Double-walled translucent epithelial cup
    capsule_mat = bpy.data.materials.new("nephron-bowman-capsule")
    capsule_mat.use_nodes = True
    bsdf = capsule_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.78, 0.72, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.28
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.2)
    mats["capsule"] = capsule_mat

    # 2. Glomerulus Capillary Tuft: Dense arterial crimson red
    glom_mat = bpy.data.materials.new("nephron-glomerulus")
    glom_mat.use_nodes = True
    bsdf = glom_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.88, 0.08, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.18
    bsdf.inputs["Metallic"].default_value = 0.10
    mats["glomerulus"] = glom_mat

    # 3. Afferent / Efferent Arteriole & Arterial Vasculature
    artery_mat = bpy.data.materials.new("nephron-artery-red")
    artery_mat.use_nodes = True
    bsdf = artery_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.85, 0.06, 0.10, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    bsdf.inputs["Metallic"].default_value = 0.08
    mats["artery"] = artery_mat

    # 4. Venous Drainage & Interlobular Vein
    vein_mat = bpy.data.materials.new("nephron-vein-blue")
    vein_mat.use_nodes = True
    bsdf = vein_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.12, 0.32, 0.85, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    bsdf.inputs["Metallic"].default_value = 0.08
    mats["vein"] = vein_mat

    # 5. Peritubular Capillaries (Anastomosing violet/purple reabsorption network)
    cap_mat = bpy.data.materials.new("nephron-peritubular-capillary")
    cap_mat.use_nodes = True
    bsdf = cap_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.68, 0.14, 0.48, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Metallic"].default_value = 0.08
    mats["capillary"] = cap_mat

    # 6. Proximal Convoluted Tubule (PCT): Warm cream/amber reabsorptive tubule
    pct_mat = bpy.data.materials.new("nephron-pct")
    pct_mat.use_nodes = True
    bsdf = pct_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.82, 0.55, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
    mats["pct"] = pct_mat

    # 7. Loop of Henle - Thin Descending Limb: Slender pale amber tubule
    henle_thin_mat = bpy.data.materials.new("nephron-henle-thin")
    henle_thin_mat.use_nodes = True
    bsdf = henle_thin_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.86, 0.76, 0.50, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.32
    mats["henle_thin"] = henle_thin_mat

    # 8. Loop of Henle - Thick Ascending Limb (TAL) & DCT: Warm golden-cream tubule
    tal_mat = bpy.data.materials.new("nephron-tal-dct")
    tal_mat.use_nodes = True
    bsdf = tal_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.90, 0.80, 0.52, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.35
    mats["tal"] = tal_mat

    # 9. Collecting Duct: Prominent pale golden-yellow trunk
    duct_mat = bpy.data.materials.new("nephron-collecting-duct")
    duct_mat.use_nodes = True
    bsdf = duct_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.72, 0.30, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.30
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.25
    mats["duct"] = duct_mat

    # 10. Corticomedullary Boundary Plane: Subtle frosted glass dividing plane
    boundary_mat = bpy.data.materials.new("nephron-cortex-medulla-boundary")
    boundary_mat.use_nodes = True
    bsdf = boundary_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.75, 0.80, 0.88, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.15
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.82
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.82
    mats["boundary"] = boundary_mat

    return mats


def build_malpighian_body(prefix, mats, is_section=False):
    """
    Constructs the Renal Corpuscle (Bowman's capsule + Glomerular tuft + arterioles).
    Bowman's cup is open anteriorly so the glomerulus is directly visible!
    """
    objs = []
    glom_center = Vector((-0.052, 0.000, 0.088))
    cup_radius = 0.016

    # 1. Bowman's Capsule: Double-walled cup open anteriorly (-Y) and superiorly (+Z)
    bm = bmesh.new()
    num_lat = 18
    num_lon = 28
    for i in range(num_lat):
        lat = (i / (num_lat - 1)) * (math.pi * 0.75) # 0 to 135 deg cup
        for j in range(num_lon):
            lon = (j / num_lon) * 2.0 * math.pi
            # Anterior cutaway: open the anterior quadrant so internal tuft is visible
            clamped_lat = lat
            px = cup_radius * math.sin(clamped_lat) * math.cos(lon)
            py = cup_radius * math.sin(clamped_lat) * math.sin(lon)
            pz = - cup_radius * math.cos(clamped_lat)

            # In section view, remove front quadrant (-Y)
            if is_section or py < -0.002:
                if py < -0.002:
                    py = -0.002

            bm.verts.new((glom_center.x + px, glom_center.y + py, glom_center.z + pz))

    bm.verts.ensure_lookup_table()
    for i in range(num_lat - 1):
        for j in range(num_lon):
            next_j = (j + 1) % num_lon
            v1 = bm.verts[i * num_lon + j]
            v2 = bm.verts[i * num_lon + next_j]
            v3 = bm.verts[(i + 1) * num_lon + next_j]
            v4 = bm.verts[(i + 1) * num_lon + j]
            bm.faces.new([v1, v2, v3, v4])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    cup_mesh = bpy.data.meshes.new(f"{prefix}_Bowman_Capsule_Mesh")
    bm.to_mesh(cup_mesh)
    bm.free()

    capsule_obj = bpy.data.objects.new(f"{prefix}_Bowman_Capsule", cup_mesh)
    bpy.context.collection.objects.link(capsule_obj)
    capsule_obj.data.materials.append(mats["capsule"])

    sol = capsule_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0022
    sub = capsule_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = capsule_obj
    capsule_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    objs.append(capsule_obj)

    # 2. Glomerulus: Intricate knot of convoluted capillary loops nestled inside Bowman's cup
    num_loops = 5
    for loop_idx in range(num_loops):
        pts = []
        phase = loop_idx * (2.0 * math.pi / num_loops)
        num_pts = 24
        for p in range(num_pts):
            t = p / (num_pts - 1)
            angle = phase + t * math.pi * 3.5
            r = 0.0085 * math.sin(t * math.pi)
            gx = glom_center.x + r * math.cos(angle) * 0.95
            gy = glom_center.y + r * math.sin(angle) * 0.95 - 0.002
            gz = glom_center.z + (t - 0.5) * 0.012 + 0.002 * math.cos(angle * 2.0)
            pts.append((gx, gy, gz))
        g_loop = kit.create_smooth_tube(f"{prefix}_Glomerulus_Loop_{loop_idx}", pts, radius=0.0014, cap_ends=True, material=mats["glomerulus"])
        objs.append(g_loop)

    # Central glomerulus core tuft
    glom_core = kit.primitive_object(
        f"{prefix}_Glomerulus_Core", "uv_sphere", mats["glomerulus"],
        size=(0.015, 0.015, 0.015),
        location=(glom_center.x, glom_center.y - 0.002, glom_center.z)
    )
    objs.append(glom_core)

    # 3. Afferent Arteriole (Inflow: wider diameter, entering vascular pole from left)
    aff_pts = [
        (-0.082, -0.008, 0.126),
        (-0.070, -0.005, 0.110),
        (-0.058, -0.003, 0.098),
        (glom_center.x, glom_center.y - 0.003, glom_center.z + 0.006),
    ]
    aff_art = kit.create_smooth_tube(f"{prefix}_Afferent_Arteriole", aff_pts, radius=0.0032, cap_ends=True, material=mats["artery"])
    objs.append(aff_art)

    # 4. Efferent Arteriole (Outflow: distinctly narrower diameter creating pressure gradient)
    eff_pts = [
        (glom_center.x, glom_center.y + 0.004, glom_center.z + 0.006),
        (-0.046, 0.005, 0.100),
        (-0.038, 0.006, 0.112),
        (-0.032, 0.004, 0.120),
    ]
    eff_art = kit.create_smooth_tube(f"{prefix}_Efferent_Arteriole", eff_pts, radius=0.0022, cap_ends=True, material=mats["artery"])
    objs.append(eff_art)

    return objs


def build_renal_tubules_and_collecting_duct(prefix, mats):
    """
    Constructs PCT, Loop of Henle (thin descending, hairpin, thick ascending),
    DCT with macula densa contact, and vertical Collecting Duct.
    """
    objs = []
    glom_center = Vector((-0.052, 0.000, 0.088))

    # 1. Proximal Convoluted Tubule (PCT): Tortuous winding loops emerging from urinary pole of capsule
    pct_pts = [
        (glom_center.x, 0.000, glom_center.z - 0.016), # Urinary pole
        (-0.050, 0.008, 0.065),
        (-0.042, 0.014, 0.062),
        (-0.036, 0.006, 0.068),
        (-0.038, -0.010, 0.074),
        (-0.048, -0.012, 0.078),
        (-0.054, -0.004, 0.072),
        (-0.046, 0.008, 0.054),
        (-0.036, 0.010, 0.042),
        (-0.028, 0.004, 0.032),
        (-0.024, 0.000, 0.015), # Transitions into descending limb at corticomedullary boundary
    ]
    pct = kit.create_smooth_tube(f"{prefix}_PCT", pct_pts, radius=0.0034, cap_ends=True, material=mats["pct"])
    objs.append(pct)

    # 2. Loop of Henle:
    # A. Thin Descending Limb: Slender tube descending deep into renal medulla (z < 0)
    des_pts = [
        (-0.024, 0.000, 0.015),
        (-0.022, -0.002, -0.020),
        (-0.020, -0.004, -0.055),
        (-0.018, -0.004, -0.085),
    ]
    henle_desc = kit.create_smooth_tube(f"{prefix}_Henle_Thin_Descending", des_pts, radius=0.0020, cap_ends=True, material=mats["henle_thin"])

    # B. Hairpin U-Turn Bend
    bend_pts = [
        (-0.018, -0.004, -0.085),
        (-0.016, -0.003, -0.096),
        (-0.011, 0.000, -0.098),
        (-0.006, 0.003, -0.095),
        (-0.004, 0.003, -0.085),
    ]
    henle_bend = kit.create_smooth_tube(f"{prefix}_Henle_Hairpin_Bend", bend_pts, radius=0.0022, cap_ends=True, material=mats["henle_thin"])

    # C. Thick Ascending Limb (TAL): Wider diameter active transport tubule ascending to cortex
    asc_pts = [
        (-0.004, 0.003, -0.085),
        (-0.005, 0.003, -0.055),
        (-0.006, 0.002, -0.020),
        (-0.008, 0.000, 0.015), # Enters cortex
        (-0.012, -0.002, 0.045),
        (-0.020, -0.004, 0.072),
        (-0.034, -0.002, 0.088), # Reaches Macula Densa between afferent and efferent arterioles!
    ]
    henle_asc = kit.create_smooth_tube(f"{prefix}_Henle_Thick_Ascending", asc_pts, radius=0.0032, cap_ends=True, material=mats["tal"])
    objs.extend([henle_desc, henle_bend, henle_asc])

    # 3. Distal Convoluted Tubule (DCT): Cortical winding loops leading to collecting duct
    dct_pts = [
        (-0.034, -0.002, 0.088), # Macula densa site
        (-0.026, 0.008, 0.096),
        (-0.016, 0.012, 0.092),
        (-0.008, 0.006, 0.086),
        (-0.006, -0.008, 0.080),
        (0.004, -0.008, 0.075),
        (0.014, 0.002, 0.072),
        (0.024, 0.006, 0.068),
        (0.036, 0.004, 0.062), # Joins collecting duct
    ]
    dct = kit.create_smooth_tube(f"{prefix}_DCT", dct_pts, radius=0.0032, cap_ends=True, material=mats["tal"])
    objs.append(dct)

    # 4. Collecting Duct: Robust vertical collecting trunk receiving multiple tributary branches
    cd_pts = [
        (0.040, 0.002, 0.120),
        (0.040, 0.002, 0.075),
        (0.038, 0.001, 0.020),
        (0.036, 0.000, -0.035),
        (0.034, -0.001, -0.080),
        (0.032, -0.002, -0.115), # Drains at renal papilla
    ]
    collecting_duct = kit.create_smooth_tube(f"{prefix}_Collecting_Duct", cd_pts, radius=0.0052, cap_ends=True, material=mats["duct"])
    objs.append(collecting_duct)

    # Tributary branches from adjacent nephrons entering collecting duct
    tributaries = [
        ([(0.054, 0.008, 0.095), (0.046, 0.004, 0.090), (0.040, 0.002, 0.085)], "Trib_Sup_R"),
        ([(0.026, -0.008, 0.105), (0.034, -0.004, 0.100), (0.040, 0.002, 0.098)], "Trib_Sup_L"),
        ([(0.052, 0.006, 0.048), (0.044, 0.003, 0.044), (0.038, 0.001, 0.040)], "Trib_Mid_R"),
        ([(0.048, -0.006, -0.015), (0.042, -0.003, -0.018), (0.036, 0.000, -0.020)], "Trib_Inf_R"),
    ]
    for pts, tag in tributaries:
        tr = kit.create_smooth_tube(f"{prefix}_{tag}", pts, radius=0.0026, cap_ends=True, material=mats["tal"])
        objs.append(tr)

    return objs


def build_peritubular_capillaries_and_vasa_recta(prefix, mats):
    """
    Creates the rich microvascular network:
    - Peritubular capillary net entwining cortical tubules (PCT/DCT).
    - Hairpin Vasa Recta vessels descending alongside the Loop of Henle into the medulla.
    - Continuous color progression from arterial red to capillary purple to venous blue.
    """
    objs = []

    # 1. Peritubular Capillary Loops around PCT and DCT in cortex
    cortical_loops = [
        # Loop wrapping around PCT loops
        ([
            (-0.032, 0.004, 0.120), # From efferent arteriole
            (-0.024, 0.014, 0.105),
            (-0.020, 0.016, 0.080),
            (-0.028, 0.014, 0.065),
            (-0.036, 0.006, 0.055),
        ], mats["artery"], "Cap_PCT_1"),
        ([
            (-0.036, 0.006, 0.055),
            (-0.044, -0.006, 0.058),
            (-0.040, -0.016, 0.072),
            (-0.032, -0.014, 0.080),
            (-0.022, -0.010, 0.085),
        ], mats["capillary"], "Cap_PCT_2"),
        # Loops wrapping DCT
        ([
            (-0.022, -0.010, 0.085),
            (-0.010, -0.012, 0.088),
            (0.002, -0.010, 0.082),
            (0.012, -0.004, 0.076),
            (0.022, -0.002, 0.072),
        ], mats["capillary"], "Cap_DCT_1"),
        ([
            (0.022, -0.002, 0.072),
            (0.016, 0.012, 0.078),
            (0.006, 0.014, 0.086),
            (-0.004, 0.012, 0.094),
        ], mats["vein"], "Cap_DCT_2"),
    ]
    for pts, m, tag in cortical_loops:
        c = kit.create_smooth_tube(f"{prefix}_{tag}", pts, radius=0.0014, cap_ends=True, material=m)
        objs.append(c)

    # 2. Vasa Recta: Slender hairpin microvessels descending parallel to Henle's loop into medulla
    vasa_loops = [
        # Descending arterial vasa recta
        ([
            (-0.022, -0.010, 0.035),
            (-0.020, -0.008, 0.000),
            (-0.018, -0.006, -0.045),
            (-0.016, -0.006, -0.080),
        ], mats["artery"], "Vasa_Recta_Desc_1"),
        # Hairpin U-turn at deep medulla
        ([
            (-0.016, -0.006, -0.080),
            (-0.014, -0.004, -0.090),
            (-0.008, 0.000, -0.090),
            (-0.006, 0.002, -0.080),
        ], mats["capillary"], "Vasa_Recta_Hairpin_1"),
        # Ascending venous vasa recta
        ([
            (-0.006, 0.002, -0.080),
            (-0.008, 0.004, -0.045),
            (-0.010, 0.006, 0.000),
            (-0.014, 0.008, 0.035),
            (-0.020, 0.010, 0.060), # Drains into interlobular vein
        ], mats["vein"], "Vasa_Recta_Asc_1"),
    ]
    for pts, m, tag in vasa_loops:
        v = kit.create_smooth_tube(f"{prefix}_{tag}", pts, radius=0.0013, cap_ends=True, material=m)
        objs.append(v)

    # 3. Interlobular Artery and Vein (running vertically in cortex)
    int_art_pts = [
        (-0.082, -0.008, 0.020),
        (-0.082, -0.008, 0.075),
        (-0.082, -0.008, 0.130),
    ]
    int_art = kit.create_smooth_tube(f"{prefix}_Interlobular_Artery", int_art_pts, radius=0.0036, cap_ends=True, material=mats["artery"])

    int_vein_pts = [
        (-0.082, 0.008, 0.020),
        (-0.082, 0.008, 0.075),
        (-0.082, 0.008, 0.130),
    ]
    int_vein = kit.create_smooth_tube(f"{prefix}_Interlobular_Vein", int_vein_pts, radius=0.0040, cap_ends=True, material=mats["vein"])
    objs.extend([int_art, int_vein])

    return objs


def build_corticomedullary_boundary(prefix, mats):
    """
    Creates a frosted, semi-transparent horizontal boundary plane at z = 0.015
    distinguishing the Renal Cortex above from the Renal Medulla below.
    """
    objs = []
    plane = kit.primitive_object(
        f"{prefix}_Corticomedullary_Boundary", "cube", mats["boundary"],
        size=(0.18, 0.09, 0.0018),
        location=(-0.015, 0.001, 0.015)
    )
    objs.append(plane)
    return objs


def setup_lighting(coll_lights):
    world = bpy.data.worlds.new("Nephron_World")
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

    # Calibrated macro studio lighting
    key_data = bpy.data.lights.new("Key_Light", 'AREA')
    key_data.energy = 12.0
    key_data.color = (1.0, 0.98, 0.94)
    key_data.size = 0.40
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = Vector((0.25, -0.60, 0.30))
    key_obj.rotation_euler = (Vector((-0.02, 0.0, 0.0)) - key_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(key_obj)

    fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_data.energy = 6.5
    fill_data.color = (0.86, 0.92, 1.0)
    fill_data.size = 0.50
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = Vector((-0.40, -0.50, 0.20))
    fill_obj.rotation_euler = (Vector((-0.02, 0.0, 0.0)) - fill_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(fill_obj)

    rim_data = bpy.data.lights.new("Rim_Light", 'AREA')
    rim_data.energy = 9.5
    rim_data.color = (0.94, 0.98, 1.0)
    rim_data.size = 0.35
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = Vector((0.10, 0.50, 0.25))
    rim_obj.rotation_euler = (Vector((-0.02, 0.0, 0.0)) - rim_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(rim_obj)

    bounce_data = bpy.data.lights.new("Bounce_Light", 'AREA')
    bounce_data.energy = 3.0
    bounce_data.size = 0.30
    bounce_obj = bpy.data.objects.new("Bounce_Light", bounce_data)
    bounce_obj.location = Vector((0.0, -0.25, -0.15))
    bounce_obj.rotation_euler = (Vector((-0.02, 0.0, 0.0)) - bounce_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(bounce_obj)


def build_scene():
    kit.reset_scene()
    mats = create_pbr_materials()

    root_coll = bpy.context.scene.collection
    coll_full = bpy.data.collections.new("Nephron_Full")
    coll_section = bpy.data.collections.new("Nephron_Section")
    coll_lights = bpy.data.collections.new("Studio_Lighting")
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)
    root_coll.children.link(coll_lights)

    setup_lighting(coll_lights)

    # 1. BUILD FULL COLLECTION (Complete nephron unit with capillaries and vasa recta)
    full_objs = []
    full_objs.extend(build_malpighian_body("Full", mats, is_section=False))
    full_objs.extend(build_renal_tubules_and_collecting_duct("Full", mats))
    full_objs.extend(build_peritubular_capillaries_and_vasa_recta("Full", mats))
    full_objs.extend(build_corticomedullary_boundary("Full", mats))

    for o in full_objs:
        if o.name not in coll_full.objects:
            coll_full.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # 2. BUILD SECTION COLLECTION (Ultrafiltration focus: cutaway Bowman's capsule and clear tubules)
    sec_objs = []
    sec_objs.extend(build_malpighian_body("Sec", mats, is_section=True))
    sec_objs.extend(build_renal_tubules_and_collecting_duct("Sec", mats))
    sec_objs.extend(build_corticomedullary_boundary("Sec", mats))

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
    print("=== BUILDING MEDICAL-GRADE NEPHRON ASSET ===")
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
    vl.layer_collection.children['Nephron_Full'].exclude = False
    vl.layer_collection.children['Nephron_Section'].exclude = True
    coll_full.hide_render = False
    coll_section.hide_render = True

    target = Vector((-0.018, 0.0, 0.010))
    cam_loc = Vector((0.20, -0.62, 0.16))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW}")

    # 4. Render Mode B: Section / Ultrafiltration Focus (preview_section.png)
    print("Rendering Section Preview...")
    vl.layer_collection.children['Nephron_Full'].exclude = True
    vl.layer_collection.children['Nephron_Section'].exclude = False
    coll_full.hide_render = True
    coll_section.hide_render = False

    cam_sec_loc = Vector((-0.02, -0.58, 0.020))
    cam_obj.location = cam_sec_loc
    cam_obj.rotation_euler = (target - cam_sec_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW_SECTION)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW_SECTION}")

    # Reset visibility
    vl.layer_collection.children['Nephron_Full'].exclude = False
    vl.layer_collection.children['Nephron_Section'].exclude = False
    coll_full.hide_render = False
    coll_section.hide_render = False
    bpy.ops.wm.save_mainfile()
    print("=== NEPHRON BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
