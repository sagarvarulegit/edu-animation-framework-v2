"""
build_bunsen_burner.py — NCERT Class 9-12 High-Fidelity Laboratory Bunsen Burner
Dual collections:
  - Burner_Full: Complete authentic burner with cast base, gas inlet, air collar, chimney & dual-zone flame
  - Burner_Section: Longitudinal cutaway revealing internal gas orifice nozzle, Venturi mixing chamber & flame thermometry
"""

import sys
from pathlib import Path
import math
import shutil
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bunsen-burner"

# Authentic Laboratory Color Palette
COLOR_CAST_IRON = (0.10, 0.11, 0.13)
COLOR_BRASS     = (0.86, 0.68, 0.22)
COLOR_NICKEL    = (0.85, 0.86, 0.88)
COLOR_HOSE      = (0.85, 0.38, 0.12)
COLOR_STEEL_CLIP= (0.75, 0.76, 0.78)
COLOR_PLINTH    = (0.16, 0.18, 0.22)
COLOR_GOLD      = (0.85, 0.68, 0.22)
COLOR_CYAN_DIM  = (0.20, 0.80, 0.95)

# Flame Colors & Emission Strengths
COLOR_FLAME_OUTER = (0.35, 0.62, 0.98) # 1400°C Oxidizing Mantle
COLOR_FLAME_INNER = (0.20, 0.78, 0.98) # 900-1000°C Reducing Core
COLOR_FLAME_HOT   = (0.95, 0.92, 0.70) # 1540°C Hottest Zone Tip
COLOR_FLAME_COOL  = (0.15, 0.25, 0.40) # 300°C Unburnt gas


def link_strictly(obj, target_collection):
    for col in list(obj.users_collection):
        col.objects.unlink(obj)
    target_collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def create_cylinder_segment(name, p1, p2, radius, material, collection):
    p1 = Vector(p1)
    p2 = Vector(p2)
    disp = p2 - p1
    length = disp.length
    if length < 1e-6:
        return None
    mid = (p1 + p2) / 2.0
    rot = Vector((0, 0, 1)).rotation_difference(disp).to_euler()
    obj = kit.primitive_object(
        name, "cylinder", material,
        size=(radius * 2, radius * 2, length),
        location=mid, rotation_euler=rot
    )
    link_strictly(obj, collection)
    return obj


# -----------------------------------------------------------------------------
# BUILD BURNER FULL
# -----------------------------------------------------------------------------
def build_burner_full(collection):
    iron_mat   = kit.add_material("bf-iron", COLOR_CAST_IRON, metallic=0.78, roughness=0.52)
    brass_mat  = kit.add_machined_metal_material("bf-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    nickel_mat = kit.add_machined_metal_material("bf-nickel", COLOR_NICKEL, metallic=0.95, roughness=0.18)
    hose_mat   = kit.add_material("bf-hose", COLOR_HOSE, metallic=0.02, roughness=0.65)
    clip_mat   = kit.add_machined_metal_material("bf-clip", COLOR_STEEL_CLIP, metallic=0.92, roughness=0.25)
    plinth_mat = kit.add_material("bf-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)

    # 1. Base Pedestal Plinth (Studio slate)
    plinth = kit.primitive_object(
        f"{ASSET_ID}_Plinth", "cube", plinth_mat,
        size=(0.220, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Heavy Cast-Iron Base (Flanged circular footprint with stepped rim)
    base_profile = [
        (0.000, 0.000),
        (0.045, 0.000),      # 90mm diameter base
        (0.045, 0.004),      # Vertical foot rim
        (0.042, 0.007),      # Chamfered shoulder
        (0.038, 0.009),      # Stepped plateau
        (0.016, 0.013),      # Sloped central boss transition
        (0.013, 0.022),      # Central threaded boss column
        (0.000, 0.022)       # Top center of boss
    ]
    base_obj = kit.lathe_object(f"{ASSET_ID}_Base", base_profile, segments=64, material=iron_mat)
    link_strictly(base_obj, collection)

    # 3. Gas Inlet Barb (Machined brass side nipple with 3 ribbed barbs)
    barb_profile = [
        (0.000, 0.000),
        (0.0055, 0.000),     # Mounting hex flange
        (0.0055, 0.005),
        (0.0040, 0.005),     # Nipple neck
        (0.0048, 0.010),     # Barb 1 crest
        (0.0038, 0.011),     # Barb 1 drop
        (0.0048, 0.016),     # Barb 2 crest
        (0.0038, 0.017),     # Barb 2 drop
        (0.0048, 0.022),     # Barb 3 crest
        (0.0036, 0.028),     # Tapered tip
        (0.0022, 0.028),     # Inner gas bore
        (0.0022, 0.000)
    ]
    barb_obj = kit.lathe_object(f"{ASSET_ID}_Hose_Barb", barb_profile, segments=32, material=brass_mat)
    barb_obj.rotation_euler = (0.0, math.radians(90), 0.0)
    barb_obj.location = (-0.013, 0.0, 0.014)
    link_strictly(barb_obj, collection)

    # 4. Rubber Gas Tubing Section with Steel Hose Clamp
    hose_len = 0.075
    hose = kit.primitive_object(
        f"{ASSET_ID}_Hose", "cylinder", hose_mat,
        size=(0.011, 0.011, hose_len),
        location=(-0.013 - 0.015 - hose_len / 2, 0.0, 0.014),
        rotation_euler=(0.0, math.radians(90), 0.0)
    )
    link_strictly(hose, collection)

    clip = kit.primitive_object(
        f"{ASSET_ID}_Hose_Clip", "cylinder", clip_mat,
        size=(0.0125, 0.0125, 0.005),
        location=(-0.034, 0.0, 0.014),
        rotation_euler=(0.0, math.radians(90), 0.0)
    )
    link_strictly(clip, collection)

    # 5. Rotatable Brass Air Collar with Dual Intake Ports
    collar_profile = [
        (0.0080, 0.021),
        (0.0112, 0.021),
        (0.0118, 0.023),     # Lower knurl rim
        (0.0118, 0.039),     # Main sleeve
        (0.0112, 0.041),     # Upper knurl rim
        (0.0080, 0.041),
        (0.0080, 0.021)
    ]
    collar_obj = kit.lathe_object(f"{ASSET_ID}_Air_Collar", collar_profile, segments=48, material=brass_mat)
    link_strictly(collar_obj, collection)

    # Air intake slots (Diametric horizontal holes)
    for sign in [-1, 1]:
        air_slot = kit.primitive_object(
            f"{ASSET_ID}_Air_Slot_{sign}", "cylinder", iron_mat,
            size=(0.007, 0.007, 0.025),
            location=(0.0, 0.0, 0.031),
            rotation_euler=(math.radians(90), 0.0, 0.0)
        )
        air_slot.scale = (0.7, 1.0, 1.2)
        link_strictly(air_slot, collection)

    # 6. Nickel-Plated Mixing Chimney (Barrel)
    barrel_h = 0.128
    barrel_profile = [
        (0.0066, 0.038),
        (0.0072, 0.044),     # Bottom flare onto collar
        (0.0068, 0.048),
        (0.0068, barrel_h - 0.005), # Main cylindrical barrel
        (0.0078, barrel_h - 0.001), # Flame stabilizer crown flare
        (0.0080, barrel_h),         # Top rim
        (0.0070, barrel_h + 0.0006),# Inner beaded lip
        (0.0054, barrel_h - 0.002), # Hollow inner bore
        (0.0054, 0.038),
        (0.0066, 0.038)
    ]
    barrel_obj = kit.lathe_object(f"{ASSET_ID}_Chimney", barrel_profile, segments=64, material=nickel_mat)
    link_strictly(barrel_obj, collection)

    # 7. Dual-Zone Emissive Blue Flame
    # Outer Oxidizing Mantle Cone (Pale blue, 1400-1540°C)
    outer_flame_mat = bpy.data.materials.new("bf-flame-outer")
    outer_flame_mat.use_nodes = True
    b_fo = outer_flame_mat.node_tree.nodes["Principled BSDF"]
    b_fo.inputs["Base Color"].default_value = (0.04, 0.30, 0.90, 1.0)
    b_fo.inputs["Emission Color"].default_value = (0.04, 0.30, 0.90, 1.0)
    b_fo.inputs["Emission Strength"].default_value = 1.4
    b_fo.inputs["Roughness"].default_value = 0.2

    flame_out_h = 0.052
    flame_out = kit.primitive_object(
        f"{ASSET_ID}_Flame_Outer", "cone", outer_flame_mat,
        size=(0.015, 0.015, flame_out_h),
        location=(0.0, 0.0, barrel_h + flame_out_h / 2)
    )
    link_strictly(flame_out, collection)

    # Inner Cyan Reducing Core Cone (900-1000°C)
    inner_flame_mat = bpy.data.materials.new("bf-flame-inner")
    inner_flame_mat.use_nodes = True
    b_fi = inner_flame_mat.node_tree.nodes["Principled BSDF"]
    b_fi.inputs["Base Color"].default_value = (0.02, 0.75, 0.95, 1.0)
    b_fi.inputs["Emission Color"].default_value = (0.02, 0.75, 0.95, 1.0)
    b_fi.inputs["Emission Strength"].default_value = 2.4
    b_fi.inputs["Roughness"].default_value = 0.2

    flame_in_h = 0.026
    flame_in = kit.primitive_object(
        f"{ASSET_ID}_Flame_Inner", "cone", inner_flame_mat,
        size=(0.010, 0.010, flame_in_h),
        location=(0.0, 0.0, barrel_h + flame_in_h / 2)
    )
    link_strictly(flame_in, collection)

    print("Built Burner_Full successfully.")


# -----------------------------------------------------------------------------
# BUILD BURNER SECTION (Longitudinal Cutaway & Flame Thermometry)
# -----------------------------------------------------------------------------
def build_burner_section(collection):
    iron_mat   = kit.add_material("sec-b-iron", COLOR_CAST_IRON, metallic=0.78, roughness=0.52)
    brass_mat  = kit.add_machined_metal_material("sec-b-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    nickel_mat = kit.add_machined_metal_material("sec-b-nickel", COLOR_NICKEL, metallic=0.95, roughness=0.18)
    plinth_mat = kit.add_material("sec-b-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.70)
    gold_mat   = kit.add_machined_metal_material("sec-b-gold", COLOR_GOLD, metallic=0.92, roughness=0.20)
    plaque_bg  = kit.add_material("sec-b-plaque", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)
    dim_mat    = kit.add_material("sec-b-dim", COLOR_CYAN_DIM, metallic=0.1, roughness=0.3)

    # 1. Base Pedestal Plinth
    plinth = kit.primitive_object(
        "Sec_Plinth", "cube", plinth_mat,
        size=(0.220, 0.220, 0.012),
        location=(0.0, 0.0, -0.006)
    )
    link_strictly(plinth, collection)

    # 2. Revolve 180° Cutaway Base
    # Base with internal gas plenum chamber
    base_cut_profile = [
        (0.0030, 0.000),     # Inner central gas passage
        (0.0450, 0.000),
        (0.0450, 0.004),
        (0.0420, 0.007),
        (0.0380, 0.009),
        (0.0160, 0.013),
        (0.0130, 0.022),
        (0.0040, 0.022),     # Threaded internal boss
        (0.0040, 0.010),     # Internal gas plenum chamber
        (0.0030, 0.010),
        (0.0030, 0.000)
    ]
    bm_base = bmesh.new()
    segments = 32
    rings = []
    for r_pt, z_pt in base_cut_profile:
        ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            ring.append(bm_base.verts.new((x, y, z_pt)))
        rings.append(ring)

    for i in range(len(rings) - 1):
        for s in range(segments):
            bm_base.faces.new([rings[i][s], rings[i+1][s], rings[i+1][s+1], rings[i][s+1]])

    bm_base.faces.new([rings[i][0] for i in range(len(rings))])
    bm_base.faces.new([rings[i][segments] for i in range(len(rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_base, faces=bm_base.faces)
    mesh_base = bpy.data.meshes.new("Sec_Base_Mesh")
    bm_base.to_mesh(mesh_base)
    bm_base.free()

    obj_base = bpy.data.objects.new("Sec_Base_Cutaway", mesh_base)
    bpy.context.collection.objects.link(obj_base)
    obj_base.data.materials.append(iron_mat)
    link_strictly(obj_base, collection)

    # 3. Gas Jet Nozzle Spud (Internal brass orifice spud at z = 0.020 to 0.030)
    spud_profile = [
        (0.0008, 0.020),     # Gas jet orifice 0.8mm bore
        (0.0038, 0.020),
        (0.0038, 0.026),
        (0.0022, 0.029),     # Nozzle taper
        (0.0010, 0.030),     # Orifice tip (0.5mm - 1.0mm)
        (0.0004, 0.030),     # Critical jet orifice
        (0.0004, 0.024),
        (0.0008, 0.020)
    ]
    bm_spud = bmesh.new()
    s_rings = []
    for r_pt, z_pt in spud_profile:
        s_ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            s_ring.append(bm_spud.verts.new((x, y, z_pt)))
        s_rings.append(s_ring)

    for i in range(len(s_rings) - 1):
        for s in range(segments):
            bm_spud.faces.new([s_rings[i][s], s_rings[i+1][s], s_rings[i+1][s+1], s_rings[i][s+1]])

    bm_spud.faces.new([s_rings[i][0] for i in range(len(s_rings))])
    bm_spud.faces.new([s_rings[i][segments] for i in range(len(s_rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_spud, faces=bm_spud.faces)
    mesh_spud = bpy.data.meshes.new("Sec_Spud_Mesh")
    bm_spud.to_mesh(mesh_spud)
    bm_spud.free()

    obj_spud = bpy.data.objects.new("Sec_Gas_Orifice_Nozzle", mesh_spud)
    bpy.context.collection.objects.link(obj_spud)
    obj_spud.data.materials.append(brass_mat)
    link_strictly(obj_spud, collection)

    # 4. Half Air Collar (180°)
    collar_cut_profile = [
        (0.0080, 0.021),
        (0.0112, 0.021),
        (0.0118, 0.023),
        (0.0118, 0.039),
        (0.0112, 0.041),
        (0.0080, 0.041),
        (0.0080, 0.021)
    ]
    bm_col = bmesh.new()
    c_rings = []
    for r_pt, z_pt in collar_cut_profile:
        c_ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            c_ring.append(bm_col.verts.new((x, y, z_pt)))
        c_rings.append(c_ring)

    for i in range(len(c_rings) - 1):
        for s in range(segments):
            bm_col.faces.new([c_rings[i][s], c_rings[i+1][s], c_rings[i+1][s+1], c_rings[i][s+1]])

    bm_col.faces.new([c_rings[i][0] for i in range(len(c_rings))])
    bm_col.faces.new([c_rings[i][segments] for i in range(len(c_rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_col, faces=bm_col.faces)
    mesh_col = bpy.data.meshes.new("Sec_Collar_Mesh")
    bm_col.to_mesh(mesh_col)
    bm_col.free()

    obj_col = bpy.data.objects.new("Sec_Air_Collar_Cutaway", mesh_col)
    bpy.context.collection.objects.link(obj_col)
    obj_col.data.materials.append(brass_mat)
    link_strictly(obj_col, collection)

    # 5. Half Chimney (Mixing Barrel Cutaway)
    barrel_h = 0.128
    barrel_cut_profile = [
        (0.0066, 0.038),
        (0.0072, 0.044),
        (0.0068, 0.048),
        (0.0068, barrel_h - 0.005),
        (0.0078, barrel_h - 0.001),
        (0.0080, barrel_h),
        (0.0070, barrel_h + 0.0006),
        (0.0054, barrel_h - 0.002),
        (0.0054, 0.038),
        (0.0066, 0.038)
    ]
    bm_bar = bmesh.new()
    b_rings = []
    for r_pt, z_pt in barrel_cut_profile:
        b_ring = []
        for s in range(segments + 1):
            theta = math.pi * s / segments
            x = r_pt * math.cos(theta)
            y = r_pt * math.sin(theta)
            b_ring.append(bm_bar.verts.new((x, y, z_pt)))
        b_rings.append(b_ring)

    for i in range(len(b_rings) - 1):
        for s in range(segments):
            bm_bar.faces.new([b_rings[i][s], b_rings[i+1][s], b_rings[i+1][s+1], b_rings[i][s+1]])

    bm_bar.faces.new([b_rings[i][0] for i in range(len(b_rings))])
    bm_bar.faces.new([b_rings[i][segments] for i in range(len(b_rings))][::-1])

    bmesh.ops.recalc_face_normals(bm_bar, faces=bm_bar.faces)
    mesh_bar = bpy.data.meshes.new("Sec_Barrel_Mesh")
    bm_bar.to_mesh(mesh_bar)
    bm_bar.free()

    obj_bar = bpy.data.objects.new("Sec_Chimney_Cutaway", mesh_bar)
    bpy.context.collection.objects.link(obj_bar)
    obj_bar.data.materials.append(nickel_mat)
    link_strictly(obj_bar, collection)

    # 6. Flame Thermometry Cross-Section (Color-Coded Isotherms)
    # Zone 1: Unburnt gas / preheating core (300°C)
    z1_mat = kit.add_material("sec-flame-300", COLOR_FLAME_COOL, metallic=0.0, roughness=0.3)
    z1_cone = kit.primitive_object("Sec_Zone_300C", "cone", z1_mat, size=(0.008, 0.004, 0.014), location=(0.0, 0.002, barrel_h + 0.007))
    link_strictly(z1_cone, collection)

    # Zone 2: Reducing Zone (900-1000°C, cyan emission)
    z2_mat = bpy.data.materials.new("sec-flame-900")
    z2_mat.use_nodes = True
    b_z2 = z2_mat.node_tree.nodes["Principled BSDF"]
    b_z2.inputs["Base Color"].default_value = (0.05, 0.85, 0.98, 1.0)
    b_z2.inputs["Emission Color"].default_value = (0.05, 0.85, 0.98, 1.0)
    b_z2.inputs["Emission Strength"].default_value = 4.5
    z2_cone = kit.primitive_object("Sec_Zone_900C", "cone", z2_mat, size=(0.010, 0.005, 0.026), location=(0.0, 0.0025, barrel_h + 0.013))
    link_strictly(z2_cone, collection)

    # Zone 3: Hottest Point Indicator (1540°C tip of inner core)
    z3_mat = bpy.data.materials.new("sec-flame-1540")
    z3_mat.use_nodes = True
    b_z3 = z3_mat.node_tree.nodes["Principled BSDF"]
    b_z3.inputs["Base Color"].default_value = (1.0, 0.92, 0.65, 1.0)
    b_z3.inputs["Emission Color"].default_value = (1.0, 0.92, 0.65, 1.0)
    b_z3.inputs["Emission Strength"].default_value = 6.0
    z3_sph = kit.primitive_object("Sec_Zone_1540C_Tip", "uv_sphere", z3_mat, size=(0.004, 0.004, 0.004), location=(0.0, 0.001, barrel_h + 0.026))
    link_strictly(z3_sph, collection)

    # Zone 4: Oxidizing Mantle (1400°C outer blue sheath)
    z4_mat = bpy.data.materials.new("sec-flame-1400")
    z4_mat.use_nodes = True
    b_z4 = z4_mat.node_tree.nodes["Principled BSDF"]
    b_z4.inputs["Base Color"].default_value = (0.10, 0.40, 0.95, 1.0)
    b_z4.inputs["Emission Color"].default_value = (0.10, 0.40, 0.95, 1.0)
    b_z4.inputs["Emission Strength"].default_value = 2.8
    z4_cone = kit.primitive_object("Sec_Zone_1400C", "cone", z4_mat, size=(0.015, 0.0075, 0.052), location=(0.0, 0.0035, barrel_h + 0.026))
    link_strictly(z4_cone, collection)

    # 7. Dimension Calipers & Gas Flow Pointers
    create_cylinder_segment("Sec_Caliper_H", (0.050, 0.0, 0.0), (0.050, 0.0, barrel_h), 0.0006, dim_mat, collection)
    create_cylinder_segment("Sec_Caliper_Flame", (0.030, 0.0, barrel_h), (0.030, 0.0, barrel_h + 0.052), 0.0006, dim_mat, collection)

    # 8. Educational Plaque
    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.180, 0.006, 0.054),
        location=(0.0, -0.058, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", gold_mat,
        size=(0.184, 0.004, 0.058),
        location=(0.0, -0.058, 0.024),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    for dx in [-0.065, 0.065]:
        leg = kit.primitive_object(
            f"Sec_Plaque_Leg_{dx}", "cylinder", gold_mat,
            size=(0.003, 0.003, 0.024),
            location=(dx, -0.052, 0.012)
        )
        link_strictly(leg, collection)

    title_strip = kit.primitive_object(
        "Sec_Plaque_Title", "cube", gold_mat,
        size=(0.150, 0.001, 0.008),
        location=(0.0, -0.060, 0.038),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(title_strip, collection)

    sub1 = kit.primitive_object(
        "Sec_Plaque_Bar_1", "cube", dim_mat,
        size=(0.120, 0.001, 0.004),
        location=(0.0, -0.059, 0.026),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub1, collection)

    sub2 = kit.primitive_object(
        "Sec_Plaque_Bar_2", "cube", gold_mat,
        size=(0.140, 0.001, 0.004),
        location=(0.0, -0.058, 0.014),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(sub2, collection)

    print("Built Burner_Section successfully.")


# -----------------------------------------------------------------------------
# CAMERA & LIGHTING RIG
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("Burner_Camera")
    cam_data.lens = 36.0
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("Burner_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # 3/4 Studio angle capturing entire burner, hose and flame apex
    cam_obj.location = (0.28, -0.32, 0.20)
    cam_target = Vector((0.0, 0.0, 0.100))
    cam_dir = cam_target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    # Three-Point Lighting Setup
    key_light_data = bpy.data.lights.new(name="Key_Light", type="AREA")
    key_light_data.energy = 4.5
    key_light_data.size = 0.35
    key_light_data.color = (1.0, 0.96, 0.92)
    key_light = bpy.data.objects.new("Key_Light", key_light_data)
    key_light.location = (0.24, -0.24, 0.30)
    key_dir = cam_target - key_light.location
    key_light.rotation_euler = key_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(key_light)

    fill_light_data = bpy.data.lights.new(name="Fill_Light", type="AREA")
    fill_light_data.energy = 2.0
    fill_light_data.size = 0.40
    fill_light_data.color = (0.85, 0.92, 1.0)
    fill_light = bpy.data.objects.new("Fill_Light", fill_light_data)
    fill_light.location = (-0.24, -0.20, 0.20)
    fill_dir = cam_target - fill_light.location
    fill_light.rotation_euler = fill_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(fill_light)

    rim_light_data = bpy.data.lights.new(name="Rim_Light", type="AREA")
    rim_light_data.energy = 3.5
    rim_light_data.size = 0.30
    rim_light_data.color = (0.80, 0.90, 1.0)
    rim_light = bpy.data.objects.new("Rim_Light", rim_light_data)
    rim_light.location = (-0.15, 0.28, 0.26)
    rim_dir = cam_target - rim_light.location
    rim_light.rotation_euler = rim_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.collection.objects.link(rim_light)


# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Burner_Full")
    sec_col  = bpy.data.collections.new("Burner_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_burner_full(full_col)
    build_burner_section(sec_col)
    setup_camera_and_lighting()

    kit.save_blend(out_dir / f"{ASSET_ID}.blend")

    # Export Full GLB
    sec_col.hide_viewport = True
    sec_col.hide_render = True
    full_col.hide_viewport = False
    full_col.hide_render = False
    kit.export_glb(out_dir / f"{ASSET_ID}.glb")

    viewer_dest = Path("/home/sagarv/Projects/edu-animation-framework-v2/apps/interactive-viewer/public/assets") / f"{ASSET_ID}.glb"
    if viewer_dest.parent.exists():
        shutil.copyfile(out_dir / f"{ASSET_ID}.glb", viewer_dest)
        print(f"Synced GLB to: {viewer_dest}")

    # Render Preview 1: Burner_Full
    kit.configure_render(width=1280, height=720, samples=16)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Burner_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
