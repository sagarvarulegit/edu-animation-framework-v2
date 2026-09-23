"""
build_digestive.py — Human Alimentary Canal & Digestive System (NCERT Class 10 Fig 6.6)
High-fidelity medical-grade 3D model with dual collections:
- Digestive_Full: Complete alimentary canal with intact organs
- Digestive_Section: Cutaway exposing gastric rugae inside stomach and duodenal junction

Standard Anatomical Orientation (Anterior View):
- Patient's Right (Viewer's Left, X < 0): Liver, Gallbladder, Bile Duct, Duodenum, Ascending Colon, Caecum, Appendix
- Patient's Left (Viewer's Right, X > 0): Stomach Fundus/Body, Pancreas Tail, Descending Colon
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'digestive-system'

# Colors based on medical anatomical palettes
COLOR_BUCCAL = (0.85, 0.50, 0.52)
COLOR_SALIVARY = (0.90, 0.82, 0.70)
COLOR_ESOPHAGUS = (0.88, 0.62, 0.60)
COLOR_STOMACH = (0.84, 0.38, 0.34)
COLOR_RUGAE = (0.70, 0.22, 0.20)
COLOR_LIVER = (0.42, 0.12, 0.08)       # Deep rich reddish-brown
COLOR_GALLBLADDER = (0.15, 0.55, 0.22)  # Vivid bile green
COLOR_BILE_DUCT = (0.35, 0.68, 0.28)
COLOR_PANCREAS = (0.92, 0.84, 0.48)    # Pale yellowish cream
COLOR_DUODENUM = (0.88, 0.65, 0.58)
COLOR_SMALL_INT = (0.86, 0.58, 0.52)
COLOR_LARGE_INT = (0.78, 0.52, 0.48)
COLOR_APPENDIX = (0.75, 0.45, 0.42)

def create_pbr_mat(name, base_color, roughness=0.35, sss=0.0):
    mat = kit.add_material(name, base_color[:3], metallic=0.04, roughness=roughness)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = sss
        elif "Subsurface" in bsdf.inputs:
            bsdf.inputs["Subsurface"].default_value = sss
    return mat

def create_curved_tube(name, points, radius, mat, collection, resolution=16):
    curve_data = bpy.data.curves.new(name=f"{name}_data", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 12
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = resolution
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)

    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj.select_set(False)
    return obj

def build_stomach_mesh(name, mat, collection, is_section=False):
    """
    Creates an anatomically accurate J-shaped stomach.
    Anterior view: Cardiac sphincter near midline, fundus curving up and right (X > 0),
    greater curvature swinging down on the right lateral side,
    pyloric antrum swinging back towards midline into duodenum on the left (X < 0).
    """
    stomach_pts = [
        Vector((0.002, 0.005, 0.082)),   # Cardiac orifice
        Vector((0.015, 0.000, 0.090)),   # Fundus top apex
        Vector((0.038, -0.005, 0.075)),  # Upper greater curvature (viewer's right)
        Vector((0.042, -0.008, 0.050)),  # Mid greater curvature
        Vector((0.032, -0.006, 0.028)),  # Lower greater curvature
        Vector((0.012, -0.004, 0.020)),  # Pyloric antrum bottom swing
        Vector((-0.006, -0.002, 0.026)), # Pyloric canal
        Vector((-0.018, 0.000, 0.024)),  # Pylorus sphincter entering duodenum
    ]
    
    radii = [0.009, 0.022, 0.026, 0.025, 0.020, 0.015, 0.011, 0.008]

    curve_data = bpy.data.curves.new(name=f"{name}_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 16
    curve_data.bevel_depth = 0.01
    curve_data.bevel_resolution = 16
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(stomach_pts) - 1)

    for i, pt in enumerate(stomach_pts):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.radius = radii[i] / 0.01
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')

    if is_section:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(
            bm,
            geom=geom,
            plane_co=(0.0, -0.004, 0.0),
            plane_no=(0.0, -1.0, 0.0),
            clear_outer=True,
            clear_inner=False
        )
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        mod_sol = obj.modifiers.new(name='WallThickness', type='SOLIDIFY')
        mod_sol.thickness = 0.0025
        mod_sol.offset = -1.0
        bpy.ops.object.modifier_apply(modifier='WallThickness')

        rugae_mat = create_pbr_mat(f"{name}_rugae_mat", COLOR_RUGAE, roughness=0.3)
        rugae_tracks = [
            [Vector((0.012, 0.005, 0.078)), Vector((0.024, 0.004, 0.065)), Vector((0.028, 0.003, 0.045)), Vector((0.018, 0.003, 0.028))],
            [Vector((0.018, 0.005, 0.072)), Vector((0.032, 0.004, 0.056)), Vector((0.032, 0.003, 0.038)), Vector((0.010, 0.003, 0.025))],
            [Vector((0.006, 0.005, 0.075)), Vector((0.012, 0.004, 0.052)), Vector((0.005, 0.003, 0.032)), Vector((-0.005, 0.003, 0.025))],
        ]
        for r_idx, r_pts in enumerate(rugae_tracks):
            create_curved_tube(f"{name}_rugae_{r_idx}", r_pts, 0.0014, rugae_mat, collection)

    obj.select_set(False)
    return obj

def build_liver(name, mat, collection):
    """
    Creates anatomical dual-lobed liver on patient's right (viewer's left: X < 0).
    """
    bm = bmesh.new()

    # Right Lobe (large wedge on anatomical right, viewer's left: X < 0)
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=0.032)
    for v in bm.verts:
        v.co.x = v.co.x * 1.35 - 0.028
        v.co.y = v.co.y * 0.75 + 0.005
        v.co.z = v.co.z * 0.90 + 0.072
        if v.co.x < -0.03:
            v.co.z -= (-0.03 - v.co.x) * 0.5
        if v.co.z < 0.065:
            v.co.y *= 0.65

    # Left Lobe (thinner triangular flap extending over stomach towards X = +0.015)
    bm_left = bmesh.new()
    bmesh.ops.create_uvsphere(bm_left, u_segments=20, v_segments=12, radius=0.020)
    for v in bm_left.verts:
        v.co.x = v.co.x * 1.2 + 0.005
        v.co.y = v.co.y * 0.55 + 0.003
        v.co.z = v.co.z * 0.75 + 0.076
        if v.co.x > 0.01:
            v.co.z -= (v.co.x - 0.01) * 0.4
    
    left_mesh = bpy.data.meshes.new("temp_left")
    bm_left.to_mesh(left_mesh)
    bm_left.free()

    bm.from_mesh(left_mesh)
    bpy.data.meshes.remove(left_mesh)

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    for poly in obj.data.polygons:
        poly.use_smooth = True

    return obj

def build_pancreas(name, mat, collection):
    """
    Creates elongated lobulated pancreas:
    Head nested in duodenal C-loop on viewer's left (X = -0.016),
    body and tail extending across behind stomach to viewer's right (X = +0.028).
    """
    bm = bmesh.new()
    lobule_coords = [
        (-0.016, 0.002, 0.018, 0.008),   # Head (in duodenal C-loop)
        (-0.008, 0.003, 0.022, 0.007),   # Neck
        (0.004, 0.005, 0.026, 0.0065),   # Body
        (0.016, 0.006, 0.030, 0.006),    # Body
        (0.028, 0.008, 0.034, 0.005),    # Tail
    ]

    for lx, ly, lz, lr in lobule_coords:
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=lr, matrix=Matrix.Translation((lx, ly, lz)))

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    for poly in obj.data.polygons:
        poly.use_smooth = True

    duct_mat = create_pbr_mat(f"{name}_duct_mat", (0.95, 0.95, 0.90), roughness=0.4)
    duct_pts = [
        Vector((0.026, -0.001, 0.034)),
        Vector((0.012, -0.002, 0.029)),
        Vector((-0.002, -0.003, 0.024)),
        Vector((-0.014, -0.003, 0.019)),
    ]
    create_curved_tube(f"{name}_duct", duct_pts, 0.0008, duct_mat, collection)

    return obj

def build_small_intestine(name, mat, collection):
    pts = [
        Vector((-0.012, 0.0, 0.006)),   # End of duodenum
        Vector((0.005, -0.002, 0.002)),
        Vector((0.018, -0.004, -0.005)),
        Vector((0.010, -0.005, -0.012)),
        Vector((-0.008, -0.004, -0.008)),
        Vector((-0.018, -0.003, -0.015)),
        Vector((-0.005, -0.005, -0.022)),
        Vector((0.015, -0.004, -0.020)),
        Vector((0.018, -0.002, -0.028)),
        Vector((0.002, -0.004, -0.032)),
        Vector((-0.015, -0.003, -0.030)),
        Vector((-0.024, -0.001, -0.036)),  # Connects to caecum at ileocecal valve
    ]
    return create_curved_tube(name, pts, 0.0045, mat, collection, resolution=12)

def build_large_intestine(name, mat, collection):
    objects = []

    # Colon tube path: Inverted U-shape surrounding small intestine
    # Caecum and Appendix on anatomical right (viewer's left: X = -0.028)
    colon_pts = [
        Vector((-0.028, 0.002, -0.038)),  # Caecum base
        Vector((-0.028, 0.003, -0.018)),  # Ascending colon mid
        Vector((-0.027, 0.004, 0.005)),   # Hepatic flexure
        Vector((-0.014, 0.006, 0.012)),   # Transverse colon mid-left
        Vector((0.014, 0.006, 0.012)),    # Transverse colon mid-right
        Vector((0.032, 0.004, 0.016)),    # Splenic flexure
        Vector((0.032, 0.003, -0.015)),   # Descending colon mid
        Vector((0.030, 0.002, -0.038)),   # Sigmoid entrance
        Vector((0.018, 0.001, -0.048)),   # Sigmoid S-loop
        Vector((0.000, 0.001, -0.055)),   # Rectum
        Vector((0.000, 0.001, -0.068)),   # Anus
    ]
    colon_tube = create_curved_tube(f"{name}_trunk", colon_pts, 0.008, mat, collection, resolution=16)
    objects.append(colon_tube)

    app_mat = create_pbr_mat(f"{name}_app_mat", COLOR_APPENDIX, roughness=0.4)
    app_pts = [
        Vector((-0.028, 0.002, -0.042)),
        Vector((-0.033, 0.001, -0.048)),
        Vector((-0.030, -0.002, -0.054)),
    ]
    appendix = create_curved_tube(f"{name}_appendix", app_pts, 0.002, app_mat, collection)
    objects.append(appendix)

    haustra_locs = [
        (-0.028, 0.0025, -0.028),
        (-0.028, 0.0035, -0.008),
        (-0.020, 0.0050, 0.009),
        (0.000, 0.0060, 0.013),
        (0.022, 0.0050, 0.014),
        (0.032, 0.0035, 0.000),
        (0.032, 0.0025, -0.025),
    ]
    for h_idx, (hx, hy, hz) in enumerate(haustra_locs):
        h = kit.primitive_object(f"{name}_haustrum_{h_idx}", 'uv_sphere', mat,
                                size=(0.018, 0.016, 0.015),
                                location=(hx, hy, hz))
        collection.objects.link(h)
        objects.append(h)

    return objects

def build_digestive_system(prefix, is_section, collection):
    objs = []

    mat_buccal = create_pbr_mat(f"{prefix}_mat_buccal", COLOR_BUCCAL, roughness=0.4)
    mat_salivary = create_pbr_mat(f"{prefix}_mat_salivary", COLOR_SALIVARY, roughness=0.35)
    mat_esophagus = create_pbr_mat(f"{prefix}_mat_esophagus", COLOR_ESOPHAGUS, roughness=0.4)
    mat_stomach = create_pbr_mat(f"{prefix}_mat_stomach", COLOR_STOMACH, roughness=0.35)
    mat_liver = create_pbr_mat(f"{prefix}_mat_liver", COLOR_LIVER, roughness=0.38)
    mat_gall = create_pbr_mat(f"{prefix}_mat_gall", COLOR_GALLBLADDER, roughness=0.25)
    mat_bile = create_pbr_mat(f"{prefix}_mat_bile", COLOR_BILE_DUCT, roughness=0.3)
    mat_panc = create_pbr_mat(f"{prefix}_mat_panc", COLOR_PANCREAS, roughness=0.45)
    mat_duod = create_pbr_mat(f"{prefix}_mat_duod", COLOR_DUODENUM, roughness=0.4)
    mat_small = create_pbr_mat(f"{prefix}_mat_small", COLOR_SMALL_INT, roughness=0.4)
    mat_large = create_pbr_mat(f"{prefix}_mat_large", COLOR_LARGE_INT, roughness=0.42)

    # 1. Mouth / Buccal Cavity & Pharynx
    mouth = kit.primitive_object(f"{prefix}_Mouth", 'uv_sphere', mat_buccal,
                                size=(0.026, 0.022, 0.018),
                                location=(0.0, 0.0, 0.170))
    collection.objects.link(mouth)
    objs.append(mouth)

    # Salivary Glands
    gland_l = kit.primitive_object(f"{prefix}_Salivary_L", 'uv_sphere', mat_salivary,
                                  size=(0.008, 0.008, 0.006),
                                  location=(0.016, 0.002, 0.165))
    gland_r = kit.primitive_object(f"{prefix}_Salivary_R", 'uv_sphere', mat_salivary,
                                  size=(0.008, 0.008, 0.006),
                                  location=(-0.016, 0.002, 0.165))
    collection.objects.link(gland_l)
    collection.objects.link(gland_r)
    objs.extend([gland_l, gland_r])

    # 2. Esophagus
    eso_pts = [
        Vector((0.0, 0.0, 0.160)),
        Vector((0.0, 0.002, 0.135)),
        Vector((0.001, 0.004, 0.110)),
        Vector((0.002, 0.005, 0.082)),
    ]
    eso = create_curved_tube(f"{prefix}_Esophagus", eso_pts, 0.0045, mat_esophagus, collection)
    objs.append(eso)

    # 3. Stomach
    stomach = build_stomach_mesh(f"{prefix}_Stomach", mat_stomach, collection, is_section=is_section)
    objs.append(stomach)

    # 4. Liver & Gallbladder (Patient's right, viewer's left: X < 0)
    liver = build_liver(f"{prefix}_Liver", mat_liver, collection)
    objs.append(liver)

    # Gallbladder
    gall = kit.primitive_object(f"{prefix}_Gallbladder", 'uv_sphere', mat_gall,
                               size=(0.009, 0.009, 0.016),
                               location=(-0.020, -0.008, 0.052),
                               rotation_euler=(0.3, -0.2, 0.0))
    collection.objects.link(gall)
    objs.append(gall)

    # Common Bile Duct
    cbd_pts = [
        Vector((-0.020, -0.007, 0.046)),
        Vector((-0.016, -0.005, 0.038)),
        Vector((-0.016, -0.001, 0.024)),
    ]
    cbd = create_curved_tube(f"{prefix}_Common_Bile_Duct", cbd_pts, 0.0012, mat_bile, collection)
    objs.append(cbd)

    # 5. Duodenum (C-loop on patient's right, viewer's left)
    duod_pts = [
        Vector((-0.018, 0.000, 0.024)),
        Vector((-0.026, 0.001, 0.020)),
        Vector((-0.028, 0.001, 0.012)),
        Vector((-0.022, 0.000, 0.005)),
        Vector((-0.012, 0.000, 0.006)),
    ]
    duodenum = create_curved_tube(f"{prefix}_Duodenum", duod_pts, 0.0055, mat_duod, collection)
    objs.append(duodenum)

    # 6. Pancreas
    pancreas = build_pancreas(f"{prefix}_Pancreas", mat_panc, collection)
    objs.append(pancreas)

    # 7. Small Intestine
    small_int = build_small_intestine(f"{prefix}_Small_Intestine", mat_small, collection)
    objs.append(small_int)

    # 8. Large Intestine
    large_int_objs = build_large_intestine(f"{prefix}_Large_Intestine", mat_large, collection)
    objs.extend(large_int_objs)

    return objs

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (-0.35, -0.55, 0.35), (9.0, 9.0, 8.5), 10.0, 0.45),
        ("Fill_Light", 'AREA', (0.45, -0.45, 0.20), (5.0, 5.2, 5.5), 5.5, 0.55),
        ("Rim_Light", 'SPOT', (0.0, 0.50, 0.40), (8.0, 8.0, 8.0), 8.0, 0.35),
        ("Bottom_Bounce", 'POINT', (0.0, -0.25, -0.20), (2.5, 2.5, 2.8), 3.0, 0.20),
    ]

    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.1
            light_data.spot_blend = 0.35

        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance, elev_deg=5, azim_deg=0):
    elev_rad = math.radians(elev_deg)
    azim_rad = math.radians(azim_deg)

    cam_x = target_center.x + distance * math.cos(elev_rad) * math.sin(azim_rad)
    cam_y = target_center.y - distance * math.cos(elev_rad) * math.cos(azim_rad)
    cam_z = target_center.z + distance * math.sin(elev_rad)

    cam_obj.location = (cam_x, cam_y, cam_z)

    direction = target_center - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / 'out')

    bpy.context.scene.display_settings.display_device = 'sRGB'
    bpy.context.scene.view_settings.view_transform = 'AgX'
    bpy.context.scene.view_settings.look = 'AgX - Medium High Contrast'

    world = bpy.data.worlds.new("Digestive_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.016, 0.020, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Digestive_Full
    col_full = bpy.data.collections.new("Digestive_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_digestive_system("Full", is_section=False, collection=col_full)

    # 2. Collection: Digestive_Section
    col_section = bpy.data.collections.new("Digestive_Section")
    bpy.context.scene.collection.children.link(col_section)
    sec_objs = build_digestive_system("Sec", is_section=True, collection=col_section)

    col_section.hide_render = True
    col_section.hide_viewport = True

    # Camera setup with 50mm lens for natural full-body perspective
    cam_data = bpy.data.cameras.new("Macro_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Macro_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    col_section.hide_render = False
    col_section.hide_viewport = False
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[2] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    # Render Preview 1: Digestive_Full (Properly framed from buccal cavity down to rectum/anus)
    col_full.hide_render = False
    col_section.hide_render = True
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.05)), distance=0.58, elev_deg=3, azim_deg=0)
    kit.configure_render(width=1280, height=720, samples=32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Digestive_Section (Zoom in on stomach coronal cutaway and hepatopancreatic ampulla)
    col_full.hide_render = True
    col_section.hide_render = False
    frame_camera_on_target(cam_obj, Vector((0.005, 0.0, 0.045)), distance=0.22, elev_deg=6, azim_deg=4)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== DIGESTIVE SYSTEM BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
