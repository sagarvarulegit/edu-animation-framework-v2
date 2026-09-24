"""
build_diamond_lattice.py — NCERT Class 10 Chemistry Ch 4 Fig 4.7(a) Diamond Lattice
Features dual collections:
  - Diamond_Lattice_Full: Macro 3D tetrahedral crystal network grounded on display plinth.
  - Diamond_Lattice_Detail: Isolated tetrahedral unit, 109.5° bond angle arc, covalent electron pairs, and educational plaque.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Quaternion, Matrix

ASSET_ID = 'diamond-lattice'

# Calibrated Palette
COLOR_CARBON_LATTICE = (0.07, 0.08, 0.10)     # Deep lustrous carbon graphite
COLOR_CARBON_DETAIL  = (0.12, 0.50, 0.95)     # Highlighted central sp3 carbon (cobalt blue)
COLOR_BOND_METAL     = (0.75, 0.78, 0.82)     # Silvery covalent bond rod
COLOR_ELECTRON       = (0.30, 0.85, 1.00)     # Luminescent valence electron pairs
COLOR_ANGLE_ARC      = (1.00, 0.75, 0.20)     # 109.5 deg tetrahedral angle indicator
COLOR_PLINTH         = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM           = (0.95, 0.65, 0.15)     # Educational badge accent
COLOR_TEXT           = (0.95, 0.96, 0.98)     # Signage text

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=4.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_carbon_mat(name, color, metallic=0.45, roughness=0.18):
    mat = kit.add_material(name, color[:3], metallic=metallic, roughness=roughness)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.8
    return mat

def generate_diamond_coordinates(d=0.038, r_cut=0.082):
    """
    Generates diamond cubic crystallographic node coordinates (Fd-3m space group).
    Bond distance d = 0.038m.
    Returns (nodes, edges).
    """
    u = d / math.sqrt(3.0)
    t_dirs_A = [
        Vector((u, u, u)),
        Vector((u, -u, -u)),
        Vector((-u, u, -u)),
        Vector((-u, -u, u))
    ]
    t_dirs_B = [-v for v in t_dirs_A]

    nodes = [Vector((0.0, 0.0, 0.0))]
    sublattices = ['A']
    edges = set()
    queue = [(0, 0)]  # (node_idx, depth)
    max_depth = 4

    while queue:
        curr_idx, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        curr_pos = nodes[curr_idx]
        sub = sublattices[curr_idx]
        dirs = t_dirs_A if sub == 'A' else t_dirs_B
        next_sub = 'B' if sub == 'A' else 'A'

        for dt in dirs:
            next_pos = curr_pos + dt
            if next_pos.length > r_cut + 1e-4:
                continue

            match_idx = None
            for i, p in enumerate(nodes):
                if (p - next_pos).length < 0.001:
                    match_idx = i
                    break

            if match_idx is None:
                match_idx = len(nodes)
                nodes.append(next_pos)
                sublattices.append(next_sub)
                queue.append((match_idx, depth + 1))

            edge = tuple(sorted((curr_idx, match_idx)))
            edges.add(edge)

    return nodes, edges

def build_diamond_full(col):
    """Constructs the macro 3D crystal lattice collection on display plinth."""
    objs = []
    mat_carbon = create_carbon_mat("dia-carbon", COLOR_CARBON_LATTICE, metallic=0.50, roughness=0.16)
    mat_bond   = kit.add_machined_metal_material("dia-bond", COLOR_BOND_METAL, metallic=0.88, roughness=0.20)
    mat_plinth = kit.add_material("dia-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material("dia-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    nodes, edges = generate_diamond_coordinates(d=0.038, r_cut=0.082)

    # Calculate bounding box to offset above plinth
    min_z = min(p.z for p in nodes)
    z_offset = -min_z + 0.035  # Lift so lowest atom is at z = 0.035

    # 1. Base Display Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-plinth", "cube", mat_plinth,
        size=(0.240, 0.240, 0.018),
        location=(0.0, 0.0, 0.009)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    plinth_rim = kit.primitive_object(
        f"{ASSET_ID}-plinth-rim", "cube", mat_trim,
        size=(0.246, 0.246, 0.003),
        location=(0.0, 0.0, 0.0015)
    )
    link_strictly(plinth_rim, col)
    objs.append(plinth_rim)

    # 2. Carbon Atom Spheres
    r_atom = 0.0105
    for idx, pos in enumerate(nodes):
        world_pos = pos + Vector((0.0, 0.0, z_offset))
        atom = kit.primitive_object(
            f"{ASSET_ID}-atom-{idx}", "uv_sphere", mat_carbon,
            size=(r_atom * 2, r_atom * 2, r_atom * 2),
            location=world_pos
        )
        link_strictly(atom, col)
        objs.append(atom)

    # 3. Covalent Bond Cylinders
    r_bond = 0.0036
    for b_idx, (i1, i2) in enumerate(sorted(list(edges))):
        p1 = nodes[i1] + Vector((0.0, 0.0, z_offset))
        p2 = nodes[i2] + Vector((0.0, 0.0, z_offset))
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        direction = delta.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()

        bond = kit.primitive_object(
            f"{ASSET_ID}-bond-{b_idx}", "cylinder", mat_bond,
            size=(r_bond * 2, r_bond * 2, delta.length),
            location=mid,
            rotation_euler=rot
        )
        link_strictly(bond, col)
        objs.append(bond)

    return objs

def build_diamond_detail(col):
    """
    Constructs the isolated tetrahedral unit collection with:
      - Central carbon atom with 4 tetrahedral coordination vectors.
      - 109.5° bond angle measurement arc.
      - Shared valence electron pairs (2e- per bond).
      - C-C bond length caliper ($1.54 \AA$).
      - Educational property plaque.
    """
    objs = []
    mat_carbon_center = create_carbon_mat("det-carbon-c", (0.95, 0.45, 0.15), metallic=0.35, roughness=0.18)
    mat_carbon_outer  = create_carbon_mat("det-carbon-o", COLOR_CARBON_LATTICE, metallic=0.50, roughness=0.16)
    mat_bond          = kit.add_machined_metal_material("det-bond", COLOR_BOND_METAL, metallic=0.88, roughness=0.20)
    mat_electron      = create_emissive_mat("det-electron", COLOR_ELECTRON, strength=5.0)
    mat_arc           = create_emissive_mat("det-arc", COLOR_ANGLE_ARC, strength=4.5)
    mat_plinth        = kit.add_material("det-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim          = kit.add_material("det-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    # 1. Base Display Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-det-plinth", "cube", mat_plinth,
        size=(0.260, 0.220, 0.018),
        location=(0.0, 0.0, 0.009)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    plinth_rim = kit.primitive_object(
        f"{ASSET_ID}-det-plinth-rim", "cube", mat_trim,
        size=(0.266, 0.226, 0.003),
        location=(0.0, 0.0, 0.0015)
    )
    link_strictly(plinth_rim, col)
    objs.append(plinth_rim)

    # Central carbon location
    center_pos = Vector((0.0, -0.015, 0.088))
    d_bond = 0.052  # Slightly enlarged for clear educational inspection
    u = d_bond / math.sqrt(3.0)

    # 4 Tetrahedral coordination vectors (109.47 degrees apart)
    t_dirs = [
        Vector((u, u, u)),
        Vector((u, -u, -u)),
        Vector((-u, u, -u)),
        Vector((-u, -u, u))
    ]

    # Central Carbon Atom C0
    r_center = 0.0135
    c_center = kit.primitive_object(
        f"{ASSET_ID}-det-c0", "uv_sphere", mat_carbon_center,
        size=(r_center * 2, r_center * 2, r_center * 2),
        location=center_pos
    )
    link_strictly(c_center, col)
    objs.append(c_center)

    r_outer = 0.0115
    r_bond = 0.0038

    # Build 4 tetrahedral arms
    outer_positions = []
    for i, t_dir in enumerate(t_dirs):
        p_outer = center_pos + t_dir
        outer_positions.append(p_outer)

        # Outer carbon atom
        c_outer = kit.primitive_object(
            f"{ASSET_ID}-det-c{i+1}", "uv_sphere", mat_carbon_outer,
            size=(r_outer * 2, r_outer * 2, r_outer * 2),
            location=p_outer
        )
        link_strictly(c_outer, col)
        objs.append(c_outer)

        # Bond cylinder
        mid = (center_pos + p_outer) * 0.5
        delta = p_outer - center_pos
        direction = delta.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()

        bond = kit.primitive_object(
            f"{ASSET_ID}-det-bond-{i}", "cylinder", mat_bond,
            size=(r_bond * 2, r_bond * 2, delta.length),
            location=mid,
            rotation_euler=rot
        )
        link_strictly(bond, col)
        objs.append(bond)

        # Shared electron pair (2 covalent electrons per single sigma bond)
        # Positioned along bond at 0.42 and 0.58 distance with slight lateral offset
        e_dir_perp = Vector((-direction.y, direction.x, 0.0)).normalized() if abs(direction.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        e1_pos = center_pos + delta * 0.44 + e_dir_perp * 0.0042
        e2_pos = center_pos + delta * 0.56 - e_dir_perp * 0.0042

        e1 = kit.primitive_object(
            f"{ASSET_ID}-det-e1-{i}", "uv_sphere", mat_electron,
            size=(0.0032, 0.0032, 0.0032),
            location=e1_pos
        )
        e2 = kit.primitive_object(
            f"{ASSET_ID}-det-e2-{i}", "uv_sphere", mat_electron,
            size=(0.0032, 0.0032, 0.0032),
            location=e2_pos
        )
        link_strictly(e1, col)
        link_strictly(e2, col)
        objs.extend([e1, e2])

    # 2. 109.5° Tetrahedral Bond Angle Measurement Arc between arm 0 and arm 2
    # Arm 0: (u, u, u), Arm 2: (-u, u, -u). Angle in plane is arccos(-1/3) ~ 109.47 deg.
    v_a = t_dirs[0].normalized()
    v_b = t_dirs[2].normalized()
    r_arc = 0.024
    num_arc_pts = 18

    # Normal to angle plane
    n_plane = v_a.cross(v_b).normalized()
    # Orthonormal basis in plane: e1 = v_a, e2 = (v_b - (v_a.dot(v_b))*v_a).normalized()
    e_x = v_a
    e_y = (v_b - (v_a.dot(v_b)) * v_a).normalized()
    total_angle = math.acos(v_a.dot(v_b))

    arc_pts = []
    for s in range(num_arc_pts):
        ang = total_angle * (s / (num_arc_pts - 1))
        p = center_pos + (e_x * math.cos(ang) + e_y * math.sin(ang)) * r_arc
        arc_pts.append(p)

    arc_tube = kit.create_smooth_tube(f"{ASSET_ID}-det-angle-arc", arc_pts, radius=0.0016, material=mat_arc)
    link_strictly(arc_tube, col)
    objs.append(arc_tube)

    # Angle label badge: 109.5°
    mid_arc_pos = center_pos + (e_x * math.cos(total_angle * 0.5) + e_y * math.sin(total_angle * 0.5)) * (r_arc + 0.009)
    angle_badge = kit.primitive_object(
        f"{ASSET_ID}-det-angle-badge", "cube", mat_arc,
        size=(0.024, 0.004, 0.010),
        location=mid_arc_pos
    )
    link_strictly(angle_badge, col)
    objs.append(angle_badge)

    # 3. Bond Length Indicator Caliper ($1.54 \AA$) along arm 1
    p1_cal = center_pos + t_dirs[1] * 0.15
    p2_cal = center_pos + t_dirs[1] * 0.85
    cal_mid = (p1_cal + p2_cal) * 0.5 + Vector((0.0, -0.010, 0.0))
    cal_rod = kit.primitive_object(
        f"{ASSET_ID}-det-cal-rod", "cylinder", mat_trim,
        size=(0.0018, 0.0018, (p2_cal - p1_cal).length),
        location=cal_mid,
        rotation_euler=t_dirs[1].to_track_quat('Z', 'Y').to_euler()
    )
    link_strictly(cal_rod, col)
    objs.append(cal_rod)

    cal_badge = kit.primitive_object(
        f"{ASSET_ID}-det-cal-badge", "cube", mat_trim,
        size=(0.022, 0.004, 0.009),
        location=cal_mid + Vector((0.0, -0.008, 0.0))
    )
    link_strictly(cal_badge, col)
    objs.append(cal_badge)

    # 4. Educational Signage Plaque Banner
    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-det-plaque-bg", "cube", mat_plinth,
        size=(0.200, 0.004, 0.024),
        location=(0.0, 0.045, 0.140)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-det-plaque-trim", "cube", mat_trim,
        size=(0.204, 0.005, 0.002),
        location=(0.0, 0.045, 0.152)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    # Carbon sp3 hybridization badge
    sp3_badge = kit.primitive_object(
        f"{ASSET_ID}-det-sp3-badge", "cube", mat_carbon_center,
        size=(0.048, 0.004, 0.012),
        location=(0.0, -0.065, 0.035)
    )
    link_strictly(sp3_badge, col)
    objs.append(sp3_badge)

    return objs

def set_collection_visibility(objs, visible):
    for obj in objs:
        obj.hide_render = not visible
        obj.hide_viewport = not visible

def frame_camera_on_target(cam_obj, target_pos, distance, elev_deg, azim_deg):
    elev = math.radians(elev_deg)
    azim = math.radians(azim_deg)
    cx = target_pos.x + distance * math.cos(elev) * math.sin(azim)
    cy = target_pos.y - distance * math.cos(elev) * math.cos(azim)
    cz = target_pos.z + distance * math.sin(elev)
    cam_obj.location = Vector((cx, cy, cz))
    direction = (target_pos - cam_obj.location).normalized()
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def configure_fast_render(width=1280, height=720, samples=24):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.cycles.max_bounces = 8
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 6
    scene.cycles.transmission_bounces = 8
    scene.cycles.transparent_max_bounces = 8
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    col_full = bpy.data.collections.new("Diamond_Lattice_Full")
    col_det  = bpy.data.collections.new("Diamond_Lattice_Detail")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_det)

    full_objs = build_diamond_full(col_full)
    det_objs  = build_diamond_detail(col_det)

    cam_data = bpy.data.cameras.new("Diamond_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Diamond_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    set_collection_visibility(full_objs, True)
    set_collection_visibility(det_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        import shutil
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    configure_fast_render(width=1280, height=720, samples=24)

    # Render Preview 1: Full Diamond Crystal Lattice Block
    set_collection_visibility(full_objs, True)
    set_collection_visibility(det_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.075)), distance=0.54, elev_deg=22, azim_deg=-32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Detail Tetrahedral Unit Breakdown
    set_collection_visibility(full_objs, False)
    set_collection_visibility(det_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.080)), distance=0.48, elev_deg=18, azim_deg=-24)
    preview_det = out_dir / "preview_section.png"
    kit.render_preview(preview_det)
    print(f"Rendered: {preview_det}")

    print("=== DIAMOND LATTICE BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
