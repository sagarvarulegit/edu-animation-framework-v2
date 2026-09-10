"""
build_heart.py — Museum-Grade Anatomical Human Heart (Coronal Cutaway & Double Circulation)
CBSE Class 10 Biology, Chapter 5: Life Processes — Circulation in Human Beings
CBSE Class 11 Biology, Chapter 18: Body Fluids and Circulation — Human Circulatory System

Anatomical Features:
- 4 distinct chambers: Right Atrium (RA), Right Ventricle (RV), Left Atrium (LA), Left Ventricle (LV)
- True coronal section revealing interior cavities and thick muscular myocardium walls
- Left Ventricle wall (LV_WALL_THICKNESS = 0.012 m / 12 mm) ~3x thicker than Right Ventricle wall (RV_WALL_THICKNESS = 0.004 m / 4 mm)
- Interventricular septum (IVS) and interatrial septum (IAS)
- Atrioventricular valves: Tricuspid valve (3 cusps) & Bicuspid/Mitral valve (2 cusps) with chordae tendineae and papillary muscles
- Semilunar valves: Aortic semilunar valve and Pulmonary semilunar valve
- Great vessels with clean manifold capped ends (ZERO non-manifold edges):
  * Superior Vena Cava (SVC) and Inferior Vena Cava (IVC) into RA
  * Pulmonary Trunk & Left/Right Pulmonary Arteries from RV
  * 4 Pulmonary Veins into LA
  * Aorta with Aortic Arch and 3 systemic branches (brachiocephalic, left common carotid, left subclavian) from LV
- Coronary arteries (LAD, RCA) and cardiac vein with epicardial fat cushions
- Realistic Subsurface Scattering (SSS) biological tissue myocardium materials
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector

ASSET_ID = "human-heart"

# Anatomical myocardial wall thicknesses (Class 11 Ch 18 benchmark: LV ~3x RV)
LV_WALL_THICKNESS = 0.012     # 12 mm systemic pressure myocardium wall
RV_WALL_THICKNESS = 0.004     # 4 mm pulmonary circuit myocardium wall
SEPTUM_WALL_THICKNESS = 0.009 # 9 mm muscular interventricular septum


def create_coronal_ventricles(name, myo_mat):
    """
    Builds the ventricular cone with coronal cutaway exposing the 4-chamber internal anatomy.
    Anterior is -Y in Blender (facing camera in frontal view).
    Anatomical Right is -X (Viewer's Left, Right Ventricle).
    Anatomical Left is +X (Viewer's Right, Left Ventricle and Apex).
    """
    # 1. Exterior anatomical ventricular cone
    bm_outer = bmesh.new()
    num_rings = 22
    num_pts = 36
    ring_verts = []

    for r in range(num_rings):
        t = r / (num_rings - 1)  # 0 at base (Z=0.035), 1 at apex (Z=-0.048)
        z = 0.035 * (1.0 - t) - 0.048 * t

        if t < 0.20:
            scale = 0.036 + (t / 0.20) * 0.008
        else:
            scale = 0.044 * math.cos((t - 0.20) / 0.80 * (math.pi * 0.46))

        # Apex tilts toward anatomical left (+X) and slightly anterior (-Y)
        offset_x = 0.015 * (t ** 1.3)
        offset_y = -0.006 * (1.0 - t) - 0.005 * (t ** 2)

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            rx = scale * (1.04 - 0.10 * math.cos(theta + 0.3))
            ry = scale * (0.88 + 0.14 * math.sin(theta + 0.2))

            # Anterior sulcus groove
            if 4.2 < theta < 5.4:
                indent = math.sin((theta - 4.2) / 1.2 * math.pi) * (0.0035 * (1.0 - t * 0.6))
                rx -= indent * 0.5
                ry += indent

            x = offset_x + rx * math.cos(theta)
            y = offset_y + ry * math.sin(theta)
            v = bm_outer.verts.new((x, y, z))
            ring.append(v)
        ring_verts.append(ring)

    for r in range(num_rings - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            bm_outer.faces.new([ring_verts[r][i], ring_verts[r][next_i],
                                ring_verts[r + 1][next_i], ring_verts[r + 1][i]])

    # Apex cap
    apex_center = bm_outer.verts.new((offset_x, offset_y, -0.049))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm_outer.faces.new([ring_verts[-1][i], apex_center, ring_verts[-1][next_i]])

    # Base cap
    base_center = bm_outer.verts.new((0.0, -0.006, 0.035))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm_outer.faces.new([ring_verts[0][i], ring_verts[0][next_i], base_center])

    bmesh.ops.recalc_face_normals(bm_outer, faces=bm_outer.faces)
    outer_mesh = bpy.data.meshes.new(f"{name}-outer")
    bm_outer.to_mesh(outer_mesh)
    bm_outer.free()

    heart_obj = bpy.data.objects.new(name, outer_mesh)
    bpy.context.collection.objects.link(heart_obj)

    # 2. Left Ventricle (LV) Chamber Cavity (Thick muscular wall surrounding it)
    # Cavity dimensions and lateral placement are governed by LV_WALL_THICKNESS:
    # Outer lateral wall is at X ~ +0.043 m; septum is at X ~ -0.001 m.
    # Lateral cavity edge: X_outer_lv - LV_WALL_THICKNESS.
    lv_radius_base = (0.044 - LV_WALL_THICKNESS) / 2.0  # 0.016 m for nominal 0.012 m wall
    lv_radius_apex = lv_radius_base * 0.25               # 0.004 m for nominal 0.012 m wall
    lv_pos_x = -0.001 + lv_radius_base                  # +0.015 m for nominal 0.012 m wall

    bm_lv = bmesh.new()
    bmesh.ops.create_cone(bm_lv, cap_ends=True, cap_tris=False, segments=32,
                          radius1=lv_radius_base, radius2=lv_radius_apex, depth=0.062)
    lv_mesh = bpy.data.meshes.new("lv_void")
    bm_lv.to_mesh(lv_mesh)
    bm_lv.free()
    lv_void = bpy.data.objects.new("lv_void", lv_mesh)
    bpy.context.collection.objects.link(lv_void)
    lv_void.location = (lv_pos_x, 0.002, -0.008)
    lv_void.rotation_euler = (0.05, -0.15, 0.0)

    # 3. Right Ventricle (RV) Chamber Cavity (Crescentic, thinner wall)
    # Cavity dimensions and lateral placement are governed by RV_WALL_THICKNESS:
    # Outer lateral wall is at X ~ -0.035 m; crescentic alignment offset is -0.002 m.
    # Thinner myocardium expands cavity laterally toward the pulmonary circuit wall.
    rv_radius_base = (0.034 - RV_WALL_THICKNESS) / 2.0  # 0.015 m for nominal 0.004 m wall
    rv_radius_apex = rv_radius_base * 0.40               # 0.006 m for nominal 0.004 m wall
    rv_pos_x = -0.002 - rv_radius_base                  # -0.017 m for nominal 0.004 m wall

    bm_rv = bmesh.new()
    bmesh.ops.create_cone(bm_rv, cap_ends=True, cap_tris=False, segments=32,
                          radius1=rv_radius_base, radius2=rv_radius_apex, depth=0.056)
    rv_mesh = bpy.data.meshes.new("rv_void")
    bm_rv.to_mesh(rv_mesh)
    bm_rv.free()
    rv_void = bpy.data.objects.new("rv_void", rv_mesh)
    bpy.context.collection.objects.link(rv_void)
    rv_void.location = (rv_pos_x, -0.001, -0.010)
    rv_void.rotation_euler = (-0.05, 0.12, 0.0)

    # 4. Coronal Cutaway Box: Removes anterior half (Y < -0.003) to reveal interior
    bm_cut = bmesh.new()
    bmesh.ops.create_cube(bm_cut, size=1.0)
    cut_mesh = bpy.data.meshes.new("coronal_cut")
    bm_cut.to_mesh(cut_mesh)
    bm_cut.free()
    coronal_cut = bpy.data.objects.new("coronal_cut", cut_mesh)
    bpy.context.collection.objects.link(coronal_cut)
    coronal_cut.scale = (0.16, 0.06, 0.16)
    coronal_cut.location = (0.0, -0.033, -0.010)

    bpy.context.view_layer.update()

    # Apply booleans sequentially
    for cutter in [lv_void, rv_void, coronal_cut]:
        mod = heart_obj.modifiers.new("CoronalCut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = cutter
        bpy.context.view_layer.objects.active = heart_obj
        bpy.ops.object.modifier_apply(modifier="CoronalCut")
        bpy.data.objects.remove(cutter, do_unlink=True)

    # Polish and smooth
    for poly in heart_obj.data.polygons:
        poly.use_smooth = True

    if myo_mat:
        heart_obj.data.materials.append(myo_mat)

    return heart_obj


def create_interventricular_septum(name, myo_mat):
    """
    Creates the muscular interventricular septum dividing RV and LV.
    Positioned in the midline sagittal plane between the two ventricles.
    """
    bm = bmesh.new()
    # High-relief muscular wall extending from apex to fibrous skeleton
    bmesh.ops.create_cube(bm, size=1.0)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.scale = (SEPTUM_WALL_THICKNESS, 0.018, 0.058)
    obj.location = (-0.001, 0.007, -0.010)
    obj.rotation_euler = (0.0, -0.08, 0.0)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    if myo_mat:
        obj.data.materials.append(myo_mat)
    return obj


def create_papillary_and_chordae(name, root_loc, valve_locs, valve_mat, myo_mat):
    """
    Creates a conical papillary muscle arising from ventricular wall with
    delicate fibrous chordae tendineae extending to valve cusps.
    """
    objects = []
    # Papillary muscle body
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                          radius1=0.0035, radius2=0.0018, depth=0.014)
    pm_mesh = bpy.data.meshes.new(f"{name}-pm-mesh")
    bm.to_mesh(pm_mesh)
    bm.free()

    pm_obj = bpy.data.objects.new(f"{name}-papillary", pm_mesh)
    bpy.context.collection.objects.link(pm_obj)
    pm_obj.location = root_loc
    dir_vec = (valve_locs[0] - root_loc).normalized()
    pm_obj.rotation_euler = dir_vec.to_track_quat('Z', 'Y').to_euler()
    for poly in pm_obj.data.polygons:
        poly.use_smooth = True
    if myo_mat:
        pm_obj.data.materials.append(myo_mat)
    objects.append(pm_obj)

    # Chordae tendineae fibers
    pm_tip = root_loc + dir_vec * 0.007
    for i, v_pt in enumerate(valve_locs):
        mid_pt = (pm_tip + v_pt) * 0.5 + Vector((0.0005, 0.0005, 0.0))
        chorda = kit.create_smooth_tube(
            f"{name}-chorda-{i}",
            [pm_tip, mid_pt, v_pt],
            radius=0.0006,
            resolution=12,
            material=valve_mat,
            cap_ends=True
        )
        objects.append(chorda)

    return objects


def create_valve_cusps(name, center, normal, radius, num_cusps, valve_mat):
    """
    Creates delicate fibrous valve cusps (3 for tricuspid/semilunar, 2 for bicuspid/mitral).
    """
    objects = []
    for c in range(num_cusps):
        start_ang = 2.0 * math.pi * c / num_cusps
        end_ang = 2.0 * math.pi * (c + 1) / num_cusps
        mid_ang = (start_ang + end_ang) / 2.0

        pts = [
            center,
            center + Vector((radius * math.cos(start_ang), radius * math.sin(start_ang), -0.0015)),
            center + Vector((radius * 1.15 * math.cos(mid_ang), radius * 1.15 * math.sin(mid_ang), -0.0035)),
            center + Vector((radius * math.cos(end_ang), radius * math.sin(end_ang), -0.0015)),
        ]
        cusp = kit.create_smooth_tube(
            f"{name}-cusp-{c}",
            pts,
            radius=0.0010,
            resolution=12,
            material=valve_mat,
            cap_ends=True
        )
        objects.append(cusp)
    return objects


def build_heart():
    """Builds a complete, authentic 4-chamber human heart with coronal section and great vessels."""
    # === PBR MATERIALS with Biological Subsurface Scattering (SSS) ===
    myo_mat = kit.add_tissue_material(
        "heart-myocardium",
        base_color=(0.55, 0.09, 0.11, 1.0),
        roughness=0.35,
        subsurface_weight=0.35,
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_scale=0.02
    )
    atrium_mat = kit.add_tissue_material(
        "heart-atrium",
        base_color=(0.48, 0.10, 0.12, 1.0),
        roughness=0.38,
        subsurface_weight=0.30,
        subsurface_radius=(1.0, 0.2, 0.1),
        subsurface_scale=0.018
    )
    valve_mat = kit.add_material("heart-valve", (0.92, 0.90, 0.84), metallic=0.02, roughness=0.30)
    aorta_mat = kit.add_material("heart-aorta", (0.84, 0.03, 0.03), metallic=0.08, roughness=0.24)
    pulmonary_mat = kit.add_material("heart-pulmonary", (0.015, 0.18, 0.88), metallic=0.08, roughness=0.24)
    vena_cava_mat = kit.add_material("heart-vena-cava", (0.015, 0.16, 0.80), metallic=0.06, roughness=0.28)
    pulm_vein_mat = kit.add_material("heart-pulm-vein", (0.80, 0.03, 0.03), metallic=0.06, roughness=0.24)
    fat_mat = kit.add_material_from_token("heart-fat", "tissueFat")
    coronary_mat = kit.add_material("heart-coronary", (0.95, 0.02, 0.02), metallic=0.10, roughness=0.18)
    coronary_vein_mat = kit.add_material("heart-coronary-vein", (0.08, 0.24, 0.92), metallic=0.10, roughness=0.18)

    objects = []

    # 1. Ventricular Myocardium with Coronal Cutaway (LV & RV Chambers)
    ventricles = create_coronal_ventricles(f"{ASSET_ID}-ventricles", myo_mat)
    septum = create_interventricular_septum(f"{ASSET_ID}-interventricular-septum", myo_mat)
    objects.extend([ventricles, septum])

    # 2. Right Atrium (RA) with Coronal Window (Viewer's Left, -X)
    ra = kit.primitive_object(
        f"{ASSET_ID}-right-atrium", "uv_sphere", atrium_mat,
        size=(0.036, 0.032, 0.034),
        location=(-0.024, 0.004, 0.040),
        rotation_euler=(0.2, 0.1, -0.3)
    )
    ra_auricle = kit.primitive_object(
        f"{ASSET_ID}-right-auricle", "uv_sphere", atrium_mat,
        size=(0.018, 0.015, 0.017),
        location=(-0.016, -0.018, 0.034),
        rotation_euler=(-0.4, -0.2, -0.5)
    )
    # Cut anterior half of RA to reveal chamber interior
    bm_ra_cut = bmesh.new()
    bmesh.ops.create_cube(bm_ra_cut, size=1.0)
    ra_cut_mesh = bpy.data.meshes.new("ra_cut")
    bm_ra_cut.to_mesh(ra_cut_mesh)
    bm_ra_cut.free()
    ra_cut_box = bpy.data.objects.new("ra_cut_box", ra_cut_mesh)
    bpy.context.collection.objects.link(ra_cut_box)
    ra_cut_box.scale = (0.05, 0.03, 0.05)
    ra_cut_box.location = (-0.024, -0.015, 0.040)
    bpy.context.view_layer.update()
    mod_ra = ra.modifiers.new("RACut", "BOOLEAN")
    mod_ra.operation = "DIFFERENCE"
    mod_ra.solver = "EXACT"
    mod_ra.object = ra_cut_box
    bpy.context.view_layer.objects.active = ra
    bpy.ops.object.modifier_apply(modifier="RACut")
    bpy.data.objects.remove(ra_cut_box, do_unlink=True)
    objects.extend([ra, ra_auricle])

    # 3. Left Atrium (LA) with Coronal Window (Viewer's Right, +X)
    la = kit.primitive_object(
        f"{ASSET_ID}-left-atrium", "uv_sphere", atrium_mat,
        size=(0.032, 0.030, 0.032),
        location=(0.020, 0.010, 0.042),
        rotation_euler=(-0.1, -0.2, 0.4)
    )
    la_auricle = kit.primitive_object(
        f"{ASSET_ID}-left-auricle", "uv_sphere", atrium_mat,
        size=(0.016, 0.014, 0.015),
        location=(0.017, -0.014, 0.036),
        rotation_euler=(-0.3, 0.3, 0.6)
    )
    # Cut anterior half of LA to reveal chamber interior
    bm_la_cut = bmesh.new()
    bmesh.ops.create_cube(bm_la_cut, size=1.0)
    la_cut_mesh = bpy.data.meshes.new("la_cut")
    bm_la_cut.to_mesh(la_cut_mesh)
    bm_la_cut.free()
    la_cut_box = bpy.data.objects.new("la_cut_box", la_cut_mesh)
    bpy.context.collection.objects.link(la_cut_box)
    la_cut_box.scale = (0.05, 0.03, 0.05)
    la_cut_box.location = (0.020, -0.010, 0.042)
    bpy.context.view_layer.update()
    mod_la = la.modifiers.new("LACut", "BOOLEAN")
    mod_la.operation = "DIFFERENCE"
    mod_la.solver = "EXACT"
    mod_la.object = la_cut_box
    bpy.context.view_layer.objects.active = la
    bpy.ops.object.modifier_apply(modifier="LACut")
    bpy.data.objects.remove(la_cut_box, do_unlink=True)
    objects.extend([la, la_auricle])

    # Interatrial Septum
    ias = kit.primitive_object(
        f"{ASSET_ID}-interatrial-septum", "cube", myo_mat,
        size=(0.005, 0.024, 0.032),
        location=(-0.002, 0.008, 0.041)
    )
    objects.append(ias)

    # 4. Atrioventricular Valves (Tricuspid and Bicuspid/Mitral)
    # Tricuspid Valve in Right AV Orifice (3 cusps)
    tri_center = Vector((-0.018, 0.004, 0.026))
    tri_cusps = create_valve_cusps(f"{ASSET_ID}-tricuspid", tri_center, Vector((0, 0, 1)), radius=0.007, num_cusps=3, valve_mat=valve_mat)
    objects.extend(tri_cusps)

    # RV Papillary Muscle and Chordae Tendineae
    rv_pm_root = Vector((-0.022, 0.006, -0.016))
    rv_chordae_targets = [
        tri_center + Vector((0.004, 0.002, -0.002)),
        tri_center + Vector((-0.003, 0.004, -0.002)),
        tri_center + Vector((0.000, -0.004, -0.002)),
    ]
    rv_pm_objects = create_papillary_and_chordae(
        f"{ASSET_ID}-rv", rv_pm_root, rv_chordae_targets, valve_mat, myo_mat
    )
    objects.extend(rv_pm_objects)

    # Bicuspid (Mitral) Valve in Left AV Orifice (2 cusps)
    bi_center = Vector((0.016, 0.005, 0.028))
    bi_cusps = create_valve_cusps(f"{ASSET_ID}-mitral", bi_center, Vector((0, 0, 1)), radius=0.0075, num_cusps=2, valve_mat=valve_mat)
    objects.extend(bi_cusps)

    # LV Prominent Papillary Muscles and Chordae Tendineae (anchored to thick LV wall)
    lv_pm_root_ant = Vector((0.024, 0.004, -0.018))
    lv_pm_root_post = Vector((0.014, 0.012, -0.020))
    lv_chordae_ant = [
        bi_center + Vector((0.004, 0.001, -0.002)),
        bi_center + Vector((0.001, -0.004, -0.002)),
    ]
    lv_chordae_post = [
        bi_center + Vector((-0.004, 0.002, -0.002)),
        bi_center + Vector((0.002, 0.005, -0.002)),
    ]
    lv_pm_ant = create_papillary_and_chordae(f"{ASSET_ID}-lv-ant", lv_pm_root_ant, lv_chordae_ant, valve_mat, myo_mat)
    lv_pm_post = create_papillary_and_chordae(f"{ASSET_ID}-lv-post", lv_pm_root_post, lv_chordae_post, valve_mat, myo_mat)
    objects.extend(lv_pm_ant + lv_pm_post)

    # 5. Semilunar Valves
    # Pulmonary Semilunar Valve (at RV conus arteriosus)
    pulm_valve_cusps = create_valve_cusps(
        f"{ASSET_ID}-pulmonary-valve", Vector((-0.005, -0.020, 0.028)),
        Vector((0, 0.4, 0.9)), radius=0.0055, num_cusps=3, valve_mat=valve_mat
    )
    objects.extend(pulm_valve_cusps)

    # Aortic Semilunar Valve (at aortic vestibule behind pulmonary trunk)
    aortic_valve_cusps = create_valve_cusps(
        f"{ASSET_ID}-aortic-valve", Vector((0.004, -0.010, 0.032)),
        Vector((0, 0.2, 0.9)), radius=0.006, num_cusps=3, valve_mat=valve_mat
    )
    objects.extend(aortic_valve_cusps)

    # 6. Pulmonary Trunk & Arteries (Crosses ANTERIOR to aorta from RV)
    pulm_trunk_pts = [
        Vector((-0.008, -0.024, 0.024)),
        Vector((-0.004, -0.022, 0.040)),
        Vector((0.001, -0.016, 0.054)),
        Vector((0.002, -0.008, 0.062)),
    ]
    pulm_trunk = kit.create_smooth_tube(
        f"{ASSET_ID}-pulmonary-trunk", pulm_trunk_pts, radius=0.0075,
        resolution=24, material=pulmonary_mat, cap_ends=True
    )
    l_pulm_art = kit.create_smooth_tube(
        f"{ASSET_ID}-pulmonary-art-left",
        [Vector((0.002, -0.008, 0.062)), Vector((0.016, -0.002, 0.061)), Vector((0.030, 0.006, 0.058))],
        radius=0.0048, resolution=16, material=pulmonary_mat, cap_ends=True
    )
    r_pulm_art = kit.create_smooth_tube(
        f"{ASSET_ID}-pulmonary-art-right",
        [Vector((0.002, -0.008, 0.062)), Vector((-0.014, -0.002, 0.060)), Vector((-0.028, 0.006, 0.056))],
        radius=0.0048, resolution=16, material=pulmonary_mat, cap_ends=True
    )
    objects.extend([pulm_trunk, l_pulm_art, r_pulm_art])

    # 7. Aorta with Aortic Arch and 3 Systemic Branches
    aorta_arch_pts = [
        Vector((0.004, -0.012, 0.030)),
        Vector((0.003, -0.008, 0.046)),
        Vector((0.000, 0.000, 0.066)),
        Vector((0.008, 0.012, 0.071)),
        Vector((0.016, 0.020, 0.062)),
        Vector((0.018, 0.022, 0.036)),
    ]
    aorta_arch = kit.create_smooth_tube(
        f"{ASSET_ID}-aorta-arch", aorta_arch_pts, radius=0.0078,
        resolution=28, material=aorta_mat, cap_ends=True
    )
    branch_1 = kit.create_smooth_tube(
        f"{ASSET_ID}-brachiocephalic",
        [Vector((-0.004, 0.003, 0.069)), Vector((-0.010, 0.002, 0.084))],
        radius=0.0035, resolution=14, material=aorta_mat, cap_ends=True
    )
    branch_2 = kit.create_smooth_tube(
        f"{ASSET_ID}-left-carotid",
        [Vector((0.003, 0.007, 0.072)), Vector((0.004, 0.007, 0.086))],
        radius=0.0028, resolution=14, material=aorta_mat, cap_ends=True
    )
    branch_3 = kit.create_smooth_tube(
        f"{ASSET_ID}-left-subclavian",
        [Vector((0.010, 0.012, 0.070)), Vector((0.015, 0.013, 0.084))],
        radius=0.0028, resolution=14, material=aorta_mat, cap_ends=True
    )
    objects.extend([aorta_arch, branch_1, branch_2, branch_3])

    # 8. Vena Cava System (SVC and IVC into RA)
    svc = kit.create_smooth_tube(
        f"{ASSET_ID}-svc",
        [Vector((-0.026, 0.004, 0.080)), Vector((-0.025, 0.003, 0.062)), Vector((-0.024, 0.002, 0.046))],
        radius=0.0068, resolution=18, material=vena_cava_mat, cap_ends=True
    )
    ivc = kit.create_smooth_tube(
        f"{ASSET_ID}-ivc",
        [Vector((-0.022, 0.006, -0.024)), Vector((-0.022, 0.005, 0.008)), Vector((-0.023, 0.004, 0.024))],
        radius=0.0065, resolution=18, material=vena_cava_mat, cap_ends=True
    )
    objects.extend([svc, ivc])

    # 9. Four Pulmonary Veins into LA
    lpv_sup = kit.create_smooth_tube(
        f"{ASSET_ID}-pulm-vein-ls",
        [Vector((0.035, 0.016, 0.045)), Vector((0.022, 0.014, 0.043))],
        radius=0.0035, resolution=12, material=pulm_vein_mat, cap_ends=True
    )
    lpv_inf = kit.create_smooth_tube(
        f"{ASSET_ID}-pulm-vein-li",
        [Vector((0.034, 0.018, 0.035)), Vector((0.022, 0.016, 0.035))],
        radius=0.0035, resolution=12, material=pulm_vein_mat, cap_ends=True
    )
    rpv_sup = kit.create_smooth_tube(
        f"{ASSET_ID}-pulm-vein-rs",
        [Vector((-0.032, 0.018, 0.044)), Vector((-0.015, 0.016, 0.042)), Vector((0.006, 0.014, 0.041))],
        radius=0.0035, resolution=14, material=pulm_vein_mat, cap_ends=True
    )
    rpv_inf = kit.create_smooth_tube(
        f"{ASSET_ID}-pulm-vein-ri",
        [Vector((-0.031, 0.020, 0.034)), Vector((-0.015, 0.018, 0.034)), Vector((0.006, 0.016, 0.034))],
        radius=0.0035, resolution=14, material=pulm_vein_mat, cap_ends=True
    )
    objects.extend([lpv_sup, lpv_inf, rpv_sup, rpv_inf])

    # 10. Coronary Blood Vessels & Epicardial Fat
    lad_pts = [
        Vector((-0.002, -0.024, 0.024)),
        Vector((0.002, -0.022, 0.012)),
        Vector((0.006, -0.018, -0.002)),
        Vector((0.010, -0.015, -0.018)),
        Vector((0.014, -0.011, -0.032)),
        Vector((0.016, -0.008, -0.042)),
    ]
    lad_artery = kit.create_smooth_tube(
        f"{ASSET_ID}-lad-artery", lad_pts, radius=0.0016,
        resolution=18, material=coronary_mat, cap_ends=True
    )
    gcv_pts = [
        Vector((0.001, -0.023, 0.022)),
        Vector((0.005, -0.021, 0.010)),
        Vector((0.009, -0.017, -0.004)),
        Vector((0.013, -0.014, -0.020)),
        Vector((0.016, -0.010, -0.033)),
    ]
    great_cardiac_vein = kit.create_smooth_tube(
        f"{ASSET_ID}-cardiac-vein", gcv_pts, radius=0.0014,
        resolution=16, material=coronary_vein_mat, cap_ends=True
    )
    rca_pts = [
        Vector((-0.008, -0.020, 0.026)),
        Vector((-0.016, -0.018, 0.022)),
        Vector((-0.022, -0.013, 0.016)),
        Vector((-0.025, -0.005, 0.008)),
        Vector((-0.024, 0.004, 0.000)),
    ]
    rca_artery = kit.create_smooth_tube(
        f"{ASSET_ID}-rca-artery", rca_pts, radius=0.0015,
        resolution=16, material=coronary_mat, cap_ends=True
    )
    fat_sulcus = kit.primitive_object(
        f"{ASSET_ID}-fat-sulcus", "uv_sphere", fat_mat,
        size=(0.026, 0.010, 0.006),
        location=(-0.012, -0.018, 0.026),
        rotation_euler=(-0.2, -0.3, -0.4)
    )
    fat_apex = kit.primitive_object(
        f"{ASSET_ID}-fat-apex", "uv_sphere", fat_mat,
        size=(0.012, 0.008, 0.005),
        location=(0.015, -0.008, -0.038),
        rotation_euler=(-0.3, -0.2, -0.2)
    )
    objects.extend([lad_artery, great_cardiac_vein, rca_artery, fat_sulcus, fat_apex])

    # Smooth shading across all mesh components
    for obj in objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.shade_smooth()

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_heart()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] Museum-grade anatomical {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
