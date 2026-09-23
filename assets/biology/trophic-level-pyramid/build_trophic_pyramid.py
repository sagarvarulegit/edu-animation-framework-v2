"""
build_trophic_pyramid.py — 4-Tier 3D Ecological Step Pyramid & Lindeman's 10% Energy Flow
CBSE Class 10 Biology, Chapter 15: Our Environment (Fig 15.2)
CBSE Class 12 Biology, Chapter 14: Ecosystem — Energy Flow (Fig 14.4)

Dual Collections:
1. Pyramid_Full:
   - 4-Tier Architectural Frustum Stepped Pyramid:
     * Tier 1: Producers (10,000 J, Lush Forest Green)
     * Tier 2: Primary Consumers / Herbivores (1,000 J, Golden Savanna Yellow)
     * Tier 3: Secondary Consumers / Carnivores (100 J, Amber Orange)
     * Tier 4: Tertiary Consumers / Apex Predators (10 J, Crimson Red)
   - Ascending 10% Energy Transfer Flow Arrows on front face.
   - Demarcated step trims and energy plaques.
   - Polished exhibition pedestal base.

2. Pyramid_Section:
   - Longitudinal 90° Cutaway revealing thermodynamic energy balance:
     * Inner core of retained biomass energy (10%).
     * 90% Heat Dissipation Loss arrows radiating outward horizontally into environment.
     * Thermal dissipation wave plumes at each trophic transition.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'trophic-level-pyramid'

# Calibrated Ecological Colors
COLOR_T1_PRODUCERS  = (0.08, 0.48, 0.18)   # Lush Chlorophyll Green
COLOR_T2_HERBIVORES = (0.85, 0.68, 0.12)   # Golden Savanna Yellow
COLOR_T3_CARNIVORES = (0.88, 0.40, 0.08)   # Warm Amber Orange
COLOR_T4_APEX       = (0.82, 0.12, 0.15)   # Deep Crimson Red
COLOR_TRIM          = (0.95, 0.96, 0.98)   # White Step Trim
COLOR_FLOW_ARROW    = (0.15, 0.75, 0.95)   # Cyan 10% Retained Energy Stream
COLOR_HEAT_ARROW    = (0.95, 0.25, 0.05)   # Luminous 90% Heat Loss
COLOR_PEDESTAL      = (0.12, 0.14, 0.16)   # Matte Dark Exhibition Base
COLOR_BRASS         = (0.82, 0.68, 0.22)   # Brass Plinth

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=5.0):
    mat = kit.add_material(name, color[:3], metallic=0.1, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_pyramid_frustum(name, base_w, top_w, height, material, z_bot, collection, cutaway=False):
    """
    Constructs a 4-sided truncated pyramid frustum.
    If cutaway=True, removes the front-right quadrant (x > 0, y < 0) to expose interior.
    """
    bm = bmesh.new()
    hb = base_w * 0.5
    ht = top_w * 0.5
    zb = z_bot
    zt = z_bot + height

    if not cutaway:
        # Full 4-sided frustum
        v_b0 = bm.verts.new((-hb, -hb, zb))
        v_b1 = bm.verts.new(( hb, -hb, zb))
        v_b2 = bm.verts.new(( hb,  hb, zb))
        v_b3 = bm.verts.new((-hb,  hb, zb))

        v_t0 = bm.verts.new((-ht, -ht, zt))
        v_t1 = bm.verts.new(( ht, -ht, zt))
        v_t2 = bm.verts.new(( ht,  ht, zt))
        v_t3 = bm.verts.new((-ht,  ht, zt))

        # Bottom & Top faces
        bm.faces.new([v_b3, v_b2, v_b1, v_b0])
        bm.faces.new([v_t0, v_t1, v_t2, v_t3])

        # 4 Slanted Side faces
        bm.faces.new([v_b0, v_b1, v_t1, v_t0])  # Front (-Y)
        bm.faces.new([v_b1, v_b2, v_t2, v_t1])  # Right (+X)
        bm.faces.new([v_b2, v_b3, v_t3, v_t2])  # Back (+Y)
        bm.faces.new([v_b3, v_b0, v_t0, v_t3])  # Left (-X)
    else:
        # 90° Cutaway: remove x > 0 and y < 0
        # Bottom polygon: (-hb,-hb) to (0,-hb) to (0,0) to (hb,0) to (hb,hb) to (-hb,hb)
        v_b0 = bm.verts.new((-hb, -hb, zb))
        v_b1 = bm.verts.new((0.0, -hb, zb))
        v_bc = bm.verts.new((0.0,  0.0, zb))
        v_b2 = bm.verts.new(( hb,  0.0, zb))
        v_b3 = bm.verts.new(( hb,  hb, zb))
        v_b4 = bm.verts.new((-hb,  hb, zb))

        v_t0 = bm.verts.new((-ht, -ht, zt))
        v_t1 = bm.verts.new((0.0, -ht, zt))
        v_tc = bm.verts.new((0.0,  0.0, zt))
        v_t2 = bm.verts.new(( ht,  0.0, zt))
        v_t3 = bm.verts.new(( ht,  ht, zt))
        v_t4 = bm.verts.new((-ht,  ht, zt))

        bm.faces.new([v_b4, v_b3, v_b2, v_bc, v_b1, v_b0])
        bm.faces.new([v_t0, v_t1, v_tc, v_t2, v_t3, v_t4])

        # Exterior side faces
        bm.faces.new([v_b0, v_b1, v_t1, v_t0])  # Left front
        bm.faces.new([v_b3, v_b4, v_t4, v_t3])  # Back (+Y)
        bm.faces.new([v_b4, v_b0, v_t0, v_t4])  # Left (-X)
        bm.faces.new([v_b2, v_b3, v_t3, v_t2])  # Back right

        # Cut cross-section walls facing viewer
        bm.faces.new([v_b1, v_bc, v_tc, v_t1])  # X=0 plane face
        bm.faces.new([v_bc, v_b2, v_t2, v_tc])  # Y=0 plane face

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = False

    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    link_strictly(obj, collection)
    return obj

def create_arrow_mesh(name, start_pt, end_pt, radius, head_len, head_rad, material, collection):
    """Creates a 3D directional arrow with cylindrical shaft and cone head."""
    objs = []
    disp = end_pt - start_pt
    length = disp.length
    if length < 1e-4:
        return objs

    dir_norm = disp.normalized()
    rot_euler = dir_norm.to_track_quat('Z', 'Y').to_euler()

    shaft_len = max(length - head_len, 0.001)
    shaft_center = start_pt + dir_norm * (shaft_len * 0.5)

    shaft = kit.primitive_object(f"{name}_Shaft", "cylinder", material,
                                size=(radius * 2, radius * 2, shaft_len),
                                location=(shaft_center.x, shaft_center.y, shaft_center.z),
                                rotation_euler=rot_euler)
    link_strictly(shaft, collection)
    objs.append(shaft)

    # Cone Head
    bm_head = bmesh.new()
    bmesh.ops.create_cone(
        bm_head, cap_ends=True, cap_tris=True, segments=16,
        radius1=head_rad, radius2=0.0, depth=head_len
    )
    bmesh.ops.recalc_face_normals(bm_head, faces=bm_head.faces)
    mesh_h = bpy.data.meshes.new(f"{name}_Head_Mesh")
    bm_head.to_mesh(mesh_h)
    bm_head.free()
    for p in mesh_h.polygons:
        p.use_smooth = True
    head_obj = bpy.data.objects.new(f"{name}_Head", mesh_h)
    head_obj.data.materials.append(material)
    head_center = start_pt + dir_norm * (shaft_len + head_len * 0.5)
    head_obj.location = head_center
    head_obj.rotation_euler = rot_euler
    link_strictly(head_obj, collection)
    objs.append(head_obj)

    return objs

def build_pyramid_full(collection):
    """Constructs the canonical 4-tier stepped ecological pyramid with 10% transfer arrows."""
    objs = []

    mat_t1 = kit.add_material("Full_T1_Producers", COLOR_T1_PRODUCERS, metallic=0.10, roughness=0.30)
    mat_t2 = kit.add_material("Full_T2_Herbivores", COLOR_T2_HERBIVORES, metallic=0.10, roughness=0.30)
    mat_t3 = kit.add_material("Full_T3_Carnivores", COLOR_T3_CARNIVORES, metallic=0.10, roughness=0.30)
    mat_t4 = kit.add_material("Full_T4_Apex", COLOR_T4_APEX, metallic=0.10, roughness=0.30)
    mat_trim = kit.add_material("Full_Trim", COLOR_TRIM, metallic=0.15, roughness=0.25)
    mat_pedestal = kit.add_material("Full_Pedestal", COLOR_PEDESTAL, metallic=0.85, roughness=0.22)
    mat_plinth = kit.add_material("Full_Plinth", COLOR_BRASS, metallic=0.92, roughness=0.18)
    mat_flow = create_emissive_mat("Full_EnergyFlow", COLOR_FLOW_ARROW, strength=8.0)

    # 4 Stepped Tiers specifications: (base_w, top_w, height, material, label)
    tier_specs = [
        (0.180, 0.145, 0.034, mat_t1, "Producers_10000J"),
        (0.140, 0.105, 0.034, mat_t2, "Herbivores_1000J"),
        (0.100, 0.065, 0.034, mat_t3, "Carnivores_100J"),
        (0.060, 0.025, 0.034, mat_t4, "Apex_10J"),
    ]

    total_h = 0.0
    z_bot = 0.0

    for idx, (bw, tw, th, mat, name) in enumerate(tier_specs):
        tier_obj = create_pyramid_frustum(f"Full_Tier_{idx}_{name}", bw, tw, th, mat, z_bot, collection, cutaway=False)
        objs.append(tier_obj)

        # White Trim step border around the top perimeter
        trim = kit.primitive_object(f"Full_Trim_{idx}", "cube", mat_trim,
                                    size=(tw + 0.002, tw + 0.002, 0.0016),
                                    location=(0.0, 0.0, z_bot + th + 0.0008))
        link_strictly(trim, collection)
        objs.append(trim)

        # Front Face Energy Plaque Badge (e.g. 10,000 J, 1,000 J, 100 J, 10 J)
        badge_mat = kit.add_material(f"Full_BadgeMat_{idx}", (0.10, 0.12, 0.14), metallic=0.5, roughness=0.3)
        y_front = -(bw + tw) * 0.25 - 0.0015
        badge = kit.primitive_object(f"Full_Badge_{idx}", "cube", badge_mat,
                                    size=(tw * 0.55, 0.002, th * 0.38),
                                    location=(0.0, y_front, z_bot + th * 0.5))
        # Slant badge to match the frustum face angle
        face_angle = math.atan2(th, (bw - tw) * 0.5)
        badge.rotation_euler = (math.pi * 0.5 - face_angle, 0.0, 0.0)
        link_strictly(badge, collection)
        objs.append(badge)

        z_bot += th
    total_h = z_bot

    # Ascending 10% Energy Transfer Arrow along Left Front Edge
    arrow_pts = [
        Vector((-0.105, -0.105, 0.015)),
        Vector((-0.082, -0.082, 0.050)),
        Vector((-0.058, -0.058, 0.084)),
        Vector((-0.035, -0.035, 0.118)),
        Vector((-0.015, -0.015, 0.148)),
    ]
    for a_i in range(len(arrow_pts) - 1):
        a_objs = create_arrow_mesh(f"Full_TransferArrow_{a_i}",
                                   arrow_pts[a_i], arrow_pts[a_i + 1],
                                   radius=0.0022, head_len=0.008, head_rad=0.0045,
                                   material=mat_flow, collection=collection)
        objs.extend(a_objs)

    # Exhibition Plinth & Stand
    plinth = kit.primitive_object("Full_Plinth", "cube", mat_plinth,
                                  size=(0.204, 0.204, 0.006),
                                  location=(0.0, 0.0, -0.003))
    link_strictly(plinth, collection)
    objs.append(plinth)

    base = kit.primitive_object("Full_Pedestal", "cube", mat_pedestal,
                                size=(0.220, 0.220, 0.014),
                                location=(0.0, 0.0, -0.013))
    link_strictly(base, collection)
    objs.append(base)

    return objs

def build_pyramid_section(collection):
    """
    Constructs a 90° cutaway section of the pyramid revealing Lindeman's 10% law:
    - Retained core of biomass energy.
    - 90% horizontal Heat Dissipation Loss arrows radiating into environment at each tier transition.
    """
    objs = []

    mat_t1 = kit.add_material("Sec_T1_Producers", COLOR_T1_PRODUCERS, metallic=0.10, roughness=0.30)
    mat_t2 = kit.add_material("Sec_T2_Herbivores", COLOR_T2_HERBIVORES, metallic=0.10, roughness=0.30)
    mat_t3 = kit.add_material("Sec_T3_Carnivores", COLOR_T3_CARNIVORES, metallic=0.10, roughness=0.30)
    mat_t4 = kit.add_material("Sec_T4_Apex", COLOR_T4_APEX, metallic=0.10, roughness=0.30)
    mat_trim = kit.add_material("Sec_Trim", COLOR_TRIM, metallic=0.15, roughness=0.25)
    mat_heat = create_emissive_mat("Sec_HeatLoss", COLOR_HEAT_ARROW, strength=9.0)
    mat_retained = create_emissive_mat("Sec_RetainedCore", COLOR_FLOW_ARROW, strength=6.0)
    mat_pedestal = kit.add_material("Sec_Pedestal", COLOR_PEDESTAL, metallic=0.85, roughness=0.22)
    mat_plinth = kit.add_material("Sec_Plinth", COLOR_BRASS, metallic=0.92, roughness=0.18)

    tier_specs = [
        (0.180, 0.145, 0.034, mat_t1, "Producers"),
        (0.140, 0.105, 0.034, mat_t2, "Herbivores"),
        (0.100, 0.065, 0.034, mat_t3, "Carnivores"),
        (0.060, 0.025, 0.034, mat_t4, "Apex"),
    ]

    z_bot = 0.0
    for idx, (bw, tw, th, mat, name) in enumerate(tier_specs):
        tier_obj = create_pyramid_frustum(f"Sec_Tier_{idx}_{name}", bw, tw, th, mat, z_bot, collection, cutaway=True)
        objs.append(tier_obj)

        # 90% Heat Dissipation Loss arrows radiating horizontally outward from the step shelf
        # (at each step transition, 90% of energy is dissipated as unrecoverable heat)
        shelf_x = tw * 0.5 + 0.005
        heat_arrow = create_arrow_mesh(f"Sec_HeatLoss_Arrow_X_{idx}",
                                       Vector((shelf_x, 0.0, z_bot + th * 0.5)),
                                       Vector((shelf_x + 0.032, 0.0, z_bot + th * 0.5)),
                                       radius=0.0020, head_len=0.007, head_rad=0.0042,
                                       material=mat_heat, collection=collection)
        objs.extend(heat_arrow)

        shelf_y = tw * 0.5 + 0.005
        heat_arrow_y = create_arrow_mesh(f"Sec_HeatLoss_Arrow_Y_{idx}",
                                         Vector((0.0, -shelf_y, z_bot + th * 0.5)),
                                         Vector((0.0, -shelf_y - 0.032, z_bot + th * 0.5)),
                                         radius=0.0020, head_len=0.007, head_rad=0.0042,
                                         material=mat_heat, collection=collection)
        objs.extend(heat_arrow_y)

        # Small thermal dissipation plume beads along the arrow
        for b_i in range(3):
            bx = shelf_x + 0.010 + b_i * 0.008
            p_bead = kit.primitive_object(f"Sec_Plume_{idx}_{b_i}", "uv_sphere", mat_heat,
                                          size=(0.0022, 0.0022, 0.0022),
                                          location=(bx, 0.002 * (b_i % 2), z_bot + th * 0.5 + 0.004 * (b_i + 1)))
            link_strictly(p_bead, collection)
            objs.append(p_bead)

        z_bot += th

    # Central Core: Luminous column indicating the 10% retained biomass energy channel
    core_column = kit.primitive_object("Sec_RetainedCore_Column", "cylinder", mat_retained,
                                       size=(0.014, 0.014, z_bot),
                                       location=(0.0, 0.0, z_bot * 0.5))
    link_strictly(core_column, collection)
    objs.append(core_column)

    # Base Pedestal with matching 90° Cutaway
    plinth = kit.primitive_object("Sec_Plinth", "cube", mat_plinth,
                                  size=(0.204, 0.204, 0.006),
                                  location=(0.0, 0.0, -0.003))
    link_strictly(plinth, collection)
    objs.append(plinth)

    base = kit.primitive_object("Sec_Pedestal", "cube", mat_pedestal,
                                size=(0.220, 0.220, 0.014),
                                location=(0.0, 0.0, -0.013))
    link_strictly(base, collection)
    objs.append(base)

    return objs

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def setup_studio_lighting():
    lights = [
        ("Key_Light", 'AREA', (0.24, -0.26, 0.22), (9.5, 9.6, 9.8), 6.5, 0.30),
        ("Fill_Light", 'AREA', (-0.25, -0.18, 0.15), (7.5, 7.8, 8.2), 3.5, 0.32),
        ("Rim_Light", 'SPOT', (0.0, 0.26, 0.24), (9.0, 9.2, 9.8), 5.5, 0.22),
        ("Bottom_Bounce", 'AREA', (0.0, -0.12, -0.10), (6.0, 6.5, 7.0), 2.2, 0.25),
    ]
    for name, l_type, loc, color, energy, size in lights:
        light_data = bpy.data.lights.new(name=name, type=l_type)
        light_data.energy = energy
        light_data.color = (color[0]/10.0, color[1]/10.0, color[2]/10.0)
        if l_type == 'AREA':
            light_data.size = size
        elif l_type == 'SPOT':
            light_data.spot_size = 1.15
            light_data.spot_blend = 0.35
        light_obj = bpy.data.objects.new(name, light_data)
        light_obj.location = loc
        bpy.context.scene.collection.objects.link(light_obj)

def frame_camera_on_target(cam_obj, target_center, distance=0.45, elev_deg=28, azim_deg=-35):
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

    world = bpy.data.worlds.new("Pyramid_World")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs["Strength"].default_value = 0.50
    bpy.context.scene.world = world

    setup_studio_lighting()

    # 1. Collection: Pyramid_Full
    col_full = bpy.data.collections.new("Pyramid_Full")
    bpy.context.scene.collection.children.link(col_full)
    full_objs = build_pyramid_full(col_full)

    # 2. Collection: Pyramid_Section (90° cutaway with 90% heat loss vectors)
    col_sec = bpy.data.collections.new("Pyramid_Section")
    bpy.context.scene.collection.children.link(col_sec)
    sec_objs = build_pyramid_section(col_sec)

    cam_data = bpy.data.cameras.new("Pyramid_Camera")
    cam_data.lens = 55.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Pyramid_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    # Export GLB with both collections active
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    # Render Preview 1: Pyramid_Full
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.065)), distance=0.42, elev_deg=26, azim_deg=-32)
    kit.configure_render(width=1280, height=720, samples=24)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Pyramid_Section (Cutaway with 90% Heat Dissipation vectors)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.065)), distance=0.42, elev_deg=26, azim_deg=-32)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== TROPHIC LEVEL PYRAMID BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
