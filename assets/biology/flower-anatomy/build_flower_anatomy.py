"""
build_flower_anatomy.py — Longitudinal Section of a Typical Bisexual Flower (NCERT Class 10 Fig 8.7)
High-fidelity botanical 3D model with dual collections:
- Flower_Full: Complete blooming flower with 5 petals, 6 stamens, and intact pistil
- Flower_Section: Textbook longitudinal section (Fig 8.7) with backdrop petals,
  bisected ovary exposing central placenta, funiculi, and bitegmic ovules with embryo sacs,
  and clearly framed stamens and pistil.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'flower-anatomy'

# Botanical PBR Color Palette
COLOR_PEDICEL = (0.28, 0.58, 0.22)
COLOR_RECEPTACLE = (0.32, 0.62, 0.25)
COLOR_SEPAL = (0.24, 0.52, 0.18)
COLOR_PETAL = (0.92, 0.20, 0.48)        # Vibrant velvety magenta/rose
COLOR_FILAMENT = (0.90, 0.95, 0.82)     # Pale translucent cream-green
COLOR_ANTHER = (0.96, 0.82, 0.15)       # Golden yellow bilobed anthers
COLOR_POLLEN = (0.98, 0.88, 0.20)       # Golden yellow pollen grains
COLOR_PISTIL_STYLE = (0.38, 0.70, 0.32) # Smooth green style
COLOR_STIGMA = (0.42, 0.75, 0.35)       # Papillate receptive stigma
COLOR_OVARY_WALL = (0.34, 0.65, 0.28)   # Fleshy ovary wall
COLOR_PLACENTA = (0.75, 0.85, 0.60)     # Central placenta ridge
COLOR_OVULE = (0.95, 0.94, 0.85)        # Pale ivory embryonic ovule
COLOR_EMBRYO_SAC = (0.98, 0.92, 0.75)   # Embryo sac / egg cell core

def create_pbr_mat(name, base_color, roughness=0.4, metallic=0.04):
    mat = kit.add_material(name, base_color[:3], metallic=metallic, roughness=roughness)
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = 0.0
    return mat

def create_curved_tube(name, points, radius, mat, collection, resolution=12):
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

def build_petal_mesh(name, mat, collection, angle_deg, flare_factor=1.0):
    """
    Creates an organically curved, broad floral petal positioned radially at angle_deg.
    0 deg is +X, 90 deg is +Y (back), 180 deg is -X, 270 deg is -Y (front).
    """
    bm = bmesh.new()
    rad = math.radians(angle_deg)

    u_steps = 7
    v_steps = 9

    verts_grid = []
    for v_i in range(v_steps):
        v_frac = v_i / (v_steps - 1)
        row = []
        width = math.sin(v_frac * math.pi) * 0.038 + v_frac * 0.012
        height_z = 0.048 + v_frac * 0.095
        radial_dist = 0.018 + math.pow(v_frac, 1.3) * 0.075 * flare_factor
        if v_frac > 0.7:
            height_z -= math.pow(v_frac - 0.7, 2.0) * 0.035

        for u_i in range(u_steps):
            u_frac = (u_i / (u_steps - 1)) * 2.0 - 1.0
            cup_depth = (1.0 - u_frac * u_frac) * 0.008

            local_x = u_frac * (width * 0.5)
            # Local Y is radial outward vector
            local_r = radial_dist - cup_depth

            # Rotate radial vector to angle_deg
            rot_x = local_r * math.cos(rad) - local_x * math.sin(rad)
            rot_y = local_r * math.sin(rad) + local_x * math.cos(rad)
            rot_z = height_z

            vert = bm.verts.new((rot_x, rot_y, rot_z))
            row.append(vert)
        verts_grid.append(row)

    bm.verts.ensure_lookup_table()

    for v_i in range(v_steps - 1):
        for u_i in range(u_steps - 1):
            v0 = verts_grid[v_i][u_i]
            v1 = verts_grid[v_i][u_i + 1]
            v2 = verts_grid[v_i + 1][u_i + 1]
            v3 = verts_grid[v_i + 1][u_i]
            bm.faces.new((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    mod_sol = obj.modifiers.new(name='Thickness', type='SOLIDIFY')
    mod_sol.thickness = 0.0006
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Thickness')
    obj.select_set(False)

    for poly in obj.data.polygons:
        poly.use_smooth = True

    return obj

def build_sepal(name, mat, collection, angle_deg):
    rad = math.radians(angle_deg)
    bm = bmesh.new()

    v_steps = 6
    u_steps = 5
    verts_grid = []

    for v_i in range(v_steps):
        v_frac = v_i / (v_steps - 1)
        width = (1.0 - v_frac) * 0.014 * math.sin(v_frac * math.pi * 0.5 + 0.3)
        height_z = 0.040 + v_frac * 0.042 - math.pow(v_frac, 2.0) * 0.015
        radial_dist = 0.016 + v_frac * 0.038

        row = []
        for u_i in range(u_steps):
            u_frac = (u_i / (u_steps - 1)) * 2.0 - 1.0
            midrib_ridge = (1.0 - abs(u_frac)) * 0.003

            local_x = u_frac * (width * 0.5)
            local_r = radial_dist - midrib_ridge

            rot_x = local_r * math.cos(rad) - local_x * math.sin(rad)
            rot_y = local_r * math.sin(rad) + local_x * math.cos(rad)
            rot_z = height_z

            v = bm.verts.new((rot_x, rot_y, rot_z))
            row.append(v)
        verts_grid.append(row)

    bm.verts.ensure_lookup_table()
    for v_i in range(v_steps - 1):
        for u_i in range(u_steps - 1):
            v0 = verts_grid[v_i][u_i]
            v1 = verts_grid[v_i][u_i + 1]
            v2 = verts_grid[v_i + 1][u_i + 1]
            v3 = verts_grid[v_i + 1][u_i]
            bm.faces.new((v0, v1, v2, v3))

    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    collection.objects.link(obj)

    mod_sol = obj.modifiers.new(name='Thickness', type='SOLIDIFY')
    mod_sol.thickness = 0.0008
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier='Thickness')
    obj.select_set(False)

    for poly in obj.data.polygons:
        poly.use_smooth = True

    return obj

def build_anther_mesh(name, anther_mat, pollen_mat, collection, loc, rot_euler):
    objs = []
    for lobe_idx, offset_x in enumerate([-0.0022, 0.0022]):
        theca = kit.primitive_object(
            f"{name}_theca_{lobe_idx}", 'uv_sphere', anther_mat,
            size=(0.0026, 0.0035, 0.0085),
            location=(loc[0] + offset_x, loc[1], loc[2]),
            rotation_euler=rot_euler
        )
        collection.objects.link(theca)
        objs.append(theca)

        furrow_pts = [
            Vector((loc[0] + offset_x, loc[1] - 0.0018, loc[2] - 0.0035)),
            Vector((loc[0] + offset_x, loc[1] - 0.0020, loc[2])),
            Vector((loc[0] + offset_x, loc[1] - 0.0018, loc[2] + 0.0035)),
        ]
        furrow = create_curved_tube(f"{name}_furrow_{lobe_idx}", furrow_pts, 0.0004, pollen_mat, collection)
        objs.append(furrow)

    connective = kit.primitive_object(
        f"{name}_connective", 'cube', anther_mat,
        size=(0.0030, 0.0018, 0.0060),
        location=(loc[0], loc[1] + 0.0010, loc[2]),
        rotation_euler=rot_euler
    )
    collection.objects.link(connective)
    objs.append(connective)

    return objs

def build_stamen(name, fil_mat, anther_mat, pollen_mat, collection, angle_deg):
    objs = []
    rad = math.radians(angle_deg)

    base_r = 0.014
    base_x = base_r * math.cos(rad)
    base_y = base_r * math.sin(rad)
    base_z = 0.052

    mid_r = 0.024
    mid_x = mid_r * math.cos(rad)
    mid_y = mid_r * math.sin(rad)
    mid_z = 0.098

    tip_r = 0.019
    tip_x = tip_r * math.cos(rad)
    tip_y = tip_r * math.sin(rad)
    tip_z = 0.138

    fil_pts = [
        Vector((base_x, base_y, base_z)),
        Vector((mid_x, mid_y, mid_z)),
        Vector((tip_x, tip_y, tip_z)),
    ]
    filament = create_curved_tube(f"{name}_filament", fil_pts, 0.0011, fil_mat, collection)
    objs.append(filament)

    rot = (0.2, 0.0, rad)
    anther_objs = build_anther_mesh(f"{name}_anther", anther_mat, pollen_mat, collection,
                                   (tip_x, tip_y, tip_z + 0.004), rot)
    objs.extend(anther_objs)

    return objs

def build_carpel_pistil(prefix, is_section, collection):
    objs = []

    mat_ovary = create_pbr_mat(f"{prefix}_mat_ovary", COLOR_OVARY_WALL, roughness=0.38)
    mat_style = create_pbr_mat(f"{prefix}_mat_style", COLOR_PISTIL_STYLE, roughness=0.40)
    mat_stigma = create_pbr_mat(f"{prefix}_mat_stigma", COLOR_STIGMA, roughness=0.35)
    mat_placenta = create_pbr_mat(f"{prefix}_mat_placenta", COLOR_PLACENTA, roughness=0.42)
    mat_ovule = create_pbr_mat(f"{prefix}_mat_ovule", COLOR_OVULE, roughness=0.30)
    mat_embryo = create_pbr_mat(f"{prefix}_mat_embryo", COLOR_EMBRYO_SAC, roughness=0.25)

    # 1. Ovary Wall
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=24, radius=0.018)
    for v in bm.verts:
        v.co.x *= 1.05
        v.co.y *= 1.05
        v.co.z = v.co.z * 1.25 + 0.068
        if v.co.z > 0.076:
            taper = 1.0 - (v.co.z - 0.076) / 0.018
            v.co.x *= max(0.25, taper)
            v.co.y *= max(0.25, taper)

    mesh_ovary = bpy.data.meshes.new(f"{prefix}_Ovary_mesh")
    bm.to_mesh(mesh_ovary)
    bm.free()

    ovary_obj = bpy.data.objects.new(f"{prefix}_Ovary", mesh_ovary)
    ovary_obj.data.materials.append(mat_ovary)
    collection.objects.link(ovary_obj)
    objs.append(ovary_obj)

    for poly in ovary_obj.data.polygons:
        poly.use_smooth = True

    if is_section:
        bm = bmesh.new()
        bm.from_mesh(ovary_obj.data)
        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
        bmesh.ops.bisect_plane(
            bm,
            geom=geom,
            plane_co=(0.0, 0.001, 0.0),
            plane_no=(0.0, -1.0, 0.0),
            clear_outer=True,
            clear_inner=False
        )
        bm.to_mesh(ovary_obj.data)
        bm.free()
        ovary_obj.data.update()

        mod_sol = ovary_obj.modifiers.new(name='OvaryWallThickness', type='SOLIDIFY')
        mod_sol.thickness = 0.0022
        mod_sol.offset = -1.0
        bpy.context.view_layer.objects.active = ovary_obj
        ovary_obj.select_set(True)
        bpy.ops.object.modifier_apply(modifier='OvaryWallThickness')
        ovary_obj.select_set(False)

        # Central Placenta column
        placenta = kit.primitive_object(
            f"{prefix}_Placenta", 'cylinder', mat_placenta,
            size=(0.0035, 0.0035, 0.024),
            location=(0.0, 0.004, 0.066)
        )
        collection.objects.link(placenta)
        objs.append(placenta)

        # 4 Anatropous Ovules attached to placenta
        ovule_coords = [
            (-0.007, 0.003, 0.060, 0.3),
            (0.007, 0.003, 0.060, -0.3),
            (-0.0075, 0.003, 0.072, 0.2),
            (0.0075, 0.003, 0.072, -0.2),
        ]
        for ov_i, (ox, oy, oz, orot) in enumerate(ovule_coords):
            fun_pts = [Vector((0.0, 0.004, oz)), Vector((ox * 0.5, oy, oz)), Vector((ox, oy, oz))]
            fun = create_curved_tube(f"{prefix}_Funiculus_{ov_i}", fun_pts, 0.0006, mat_placenta, collection)
            objs.append(fun)

            ovule_body = kit.primitive_object(
                f"{prefix}_Ovule_{ov_i}", 'uv_sphere', mat_ovule,
                size=(0.0050, 0.0042, 0.0065),
                location=(ox, oy, oz),
                rotation_euler=(0.0, orot, 0.0)
            )
            collection.objects.link(ovule_body)
            objs.append(ovule_body)

            embryo_sac = kit.primitive_object(
                f"{prefix}_Embryo_Sac_{ov_i}", 'uv_sphere', mat_embryo,
                size=(0.0022, 0.0020, 0.0032),
                location=(ox, oy - 0.0015, oz)
            )
            collection.objects.link(embryo_sac)
            objs.append(embryo_sac)

    # 2. Style
    style_pts = [
        Vector((0.0, 0.0, 0.086)),
        Vector((0.0, 0.001, 0.115)),
        Vector((0.0, 0.0, 0.144)),
    ]
    style = create_curved_tube(f"{prefix}_Style", style_pts, 0.0024, mat_style, collection)
    objs.append(style)

    # 3. Stigma
    stigma_center = kit.primitive_object(
        f"{prefix}_Stigma_Center", 'uv_sphere', mat_stigma,
        size=(0.0055, 0.0055, 0.0035),
        location=(0.0, 0.0, 0.147)
    )
    collection.objects.link(stigma_center)
    objs.append(stigma_center)

    for st_i in range(5):
        s_rad = math.radians(st_i * 72.0)
        sx = 0.0045 * math.cos(s_rad)
        sy = 0.0045 * math.sin(s_rad)
        lobe = kit.primitive_object(
            f"{prefix}_Stigma_Lobe_{st_i}", 'uv_sphere', mat_stigma,
            size=(0.0040, 0.0040, 0.0030),
            location=(sx, sy, 0.149),
            rotation_euler=(0.2 * math.sin(s_rad), -0.2 * math.cos(s_rad), s_rad)
        )
        collection.objects.link(lobe)
        objs.append(lobe)

    return objs

def build_flower_system(prefix, is_section, collection):
    objs = []

    mat_pedicel = create_pbr_mat(f"{prefix}_mat_pedicel", COLOR_PEDICEL, roughness=0.45)
    mat_receptacle = create_pbr_mat(f"{prefix}_mat_receptacle", COLOR_RECEPTACLE, roughness=0.42)
    mat_sepal = create_pbr_mat(f"{prefix}_mat_sepal", COLOR_SEPAL, roughness=0.40)
    mat_petal = create_pbr_mat(f"{prefix}_mat_petal", COLOR_PETAL, roughness=0.38)
    mat_fil = create_pbr_mat(f"{prefix}_mat_fil", COLOR_FILAMENT, roughness=0.35)
    mat_anther = create_pbr_mat(f"{prefix}_mat_anther", COLOR_ANTHER, roughness=0.30)
    mat_pollen = create_pbr_mat(f"{prefix}_mat_pollen", COLOR_POLLEN, roughness=0.45)

    # 1. Pedicel
    pedicel_pts = [
        Vector((0.0, 0.0, 0.000)),
        Vector((0.0, 0.001, 0.020)),
        Vector((0.0, 0.0, 0.038)),
    ]
    pedicel = create_curved_tube(f"{prefix}_Pedicel", pedicel_pts, 0.0038, mat_pedicel, collection)
    objs.append(pedicel)

    # 2. Thalamus / Receptacle
    receptacle = kit.lathe_object(
        f"{prefix}_Receptacle",
        [(0.0, 0.036), (0.0045, 0.036), (0.012, 0.044), (0.016, 0.050), (0.000, 0.050)],
        segments=32, material=mat_receptacle
    )
    collection.objects.link(receptacle)
    objs.append(receptacle)

    # 3. Calyx (Sepals)
    if is_section:
        # In section view, keep the lateral/posterior sepals framing the thalamus
        sepal_angles = [45.0, 90.0, 135.0, 225.0, 315.0]
    else:
        sepal_angles = [i * 72.0 + 36.0 for i in range(5)]

    for s_i, s_deg in enumerate(sepal_angles):
        sepal = build_sepal(f"{prefix}_Sepal_{s_i}", mat_sepal, collection, s_deg)
        objs.append(sepal)

    # 4. Corolla (Petals)
    if is_section:
        # 3 backdrop petals fanning out behind the reproductive organs (+Y hemisphere: 50°, 90°, 130°)
        petal_angles = [50.0, 90.0, 130.0]
    else:
        # 5 petals in radial bloom (72° increments starting at 18°)
        petal_angles = [i * 72.0 + 18.0 for i in range(5)]

    for p_i, p_deg in enumerate(petal_angles):
        petal = build_petal_mesh(f"{prefix}_Petal_{p_i}", mat_petal, collection, p_deg, flare_factor=1.0)
        objs.append(petal)

    # 5. Gynoecium / Pistil
    pistil_objs = build_carpel_pistil(prefix, is_section=is_section, collection=collection)
    objs.extend(pistil_objs)

    # 6. Androecium (Stamens)
    if is_section:
        # Clearly frame 4 stamens to the left and right in textbook Fig 8.7 presentation
        stamen_angles = [30.0, 65.0, 115.0, 150.0]
    else:
        stamen_angles = [i * 60.0 + 15.0 for i in range(6)]

    for st_i, st_deg in enumerate(stamen_angles):
        stamen_objs = build_stamen(f"{prefix}_Stamen_{st_i}", mat_fil, mat_anther, mat_pollen, collection, st_deg)
        objs.extend(stamen_objs)

    return objs

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.35, -0.45, 0.28), (9.5, 9.5, 9.0), 9.5, 0.40),
        ("Fill_Light", 'AREA', (-0.40, -0.35, 0.18), (5.5, 5.5, 6.0), 5.5, 0.50),
        ("Rim_Light", 'SPOT', (0.0, 0.40, 0.35), (8.5, 8.5, 8.5), 8.5, 0.30),
        ("Bottom_Bounce", 'POINT', (0.0, -0.20, -0.10), (3.0, 3.0, 3.2), 3.0, 0.15),
    ]

    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.15
            light_data.spot_blend = 0.30

        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance, elev_deg=10, azim_deg=0):
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

    world = bpy.data.worlds.new("Flower_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs["Strength"].default_value = 0.5
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Flower_Full
    col_full = bpy.data.collections.new("Flower_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_flower_system("Full", is_section=False, collection=col_full)

    # 2. Collection: Flower_Section
    col_section = bpy.data.collections.new("Flower_Section")
    bpy.context.scene.collection.children.link(col_section)
    sec_objs = build_flower_system("Sec", is_section=True, collection=col_section)

    col_section.hide_render = True
    col_section.hide_viewport = True

    # Camera setup (55mm macro lens)
    cam_data = bpy.data.cameras.new("Macro_Camera")
    cam_data.lens = 55.0
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

    # Render Preview 1: Flower_Full (Full blooming flower)
    col_full.hide_render = False
    col_section.hide_render = True
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.095)), distance=0.34, elev_deg=18, azim_deg=-15)
    kit.configure_render(width=1280, height=720, samples=32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Flower_Section (Textbook Fig 8.7 longitudinal section framing entire flower)
    col_full.hide_render = True
    col_section.hide_render = False
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.095)), distance=0.32, elev_deg=6, azim_deg=0)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== FLOWER ANATOMY BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
