"""
build_graphite_lattice.py — NCERT Class 10 Chemistry Ch 4 Fig 4.7(b) Graphite Lattice
Features dual collections:
  - Graphite_Lattice_Full: 3 stacked hexagonal graphene sheets (ABAB stacking) with van der Waals interlayer links.
  - Graphite_Lattice_Detail: Exploded layer view demonstrating interlayer slippage (lubricity), delocalized pi-electrons (electrical conductivity), 120° trigonal angle arc, and educational plaque.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'graphite-lattice'

# Calibrated Palette
COLOR_CARBON_GRAPHITE = (0.08, 0.09, 0.11)    # Dark lustrous graphite carbon
COLOR_CARBON_ACTIVE   = (0.12, 0.50, 0.95)    # Highlighted sp2 carbon
COLOR_BOND_METAL      = (0.75, 0.78, 0.82)    # Silvery in-plane covalent bond
COLOR_VDW_LINK        = (0.25, 0.75, 0.95)    # Van der Waals interlayer force link
COLOR_PI_ELECTRON     = (0.20, 0.88, 1.00)    # Delocalized pi-electron cloud
COLOR_SLIP_ARROW      = (0.95, 0.65, 0.15)    # Layer slippage shear vector
COLOR_ANGLE_ARC       = (1.00, 0.78, 0.20)    # 120 deg trigonal planar angle arc
COLOR_PLINTH          = (0.12, 0.14, 0.18)    # Studio slate display pedestal
COLOR_TRIM            = (0.95, 0.65, 0.15)    # Educational badge accent

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

def create_carbon_mat(name, color, metallic=0.30, roughness=0.30):
    mat = kit.add_material(name, color[:3], metallic=metallic, roughness=roughness)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.7
    return mat

def generate_planar_hex_layer(bond_r=0.024, shift=(0.0, 0.0), r_cut=0.076):
    """
    Generates a planar graphene honeycomb sheet with sp2 hybridization (3-coordinated rings).
    Returns (nodes, bonds).
    """
    tau1 = (bond_r, 0.0)
    a1 = (1.5 * bond_r, -0.5 * math.sqrt(3.0) * bond_r)
    a2 = (1.5 * bond_r,  0.5 * math.sqrt(3.0) * bond_r)

    nodes = []
    for i in range(-5, 6):
        for j in range(-5, 6):
            rx = i * a1[0] + j * a2[0] + shift[0]
            ry = i * a1[1] + j * a2[1] + shift[1]
            if math.hypot(rx, ry) <= r_cut:
                nodes.append((rx, ry))
            bx = rx + tau1[0]
            by = ry + tau1[1]
            if math.hypot(bx, by) <= r_cut:
                nodes.append((bx, by))

    bonds = []
    for m in range(len(nodes)):
        for n in range(m + 1, len(nodes)):
            dist = math.hypot(nodes[m][0] - nodes[n][0], nodes[m][1] - nodes[n][1])
            if abs(dist - bond_r) < 1e-4:
                bonds.append((m, n))

    return nodes, bonds

def build_graphite_full(col):
    """
    Constructs 3 stacked parallel graphene sheets (Layer A, Layer B, Layer A')
    with vertical dashed van der Waals links mounted on a display plinth.
    """
    objs = []
    mat_carbon = create_carbon_mat("gph-carbon", COLOR_CARBON_GRAPHITE, metallic=0.30, roughness=0.30)
    mat_bond   = kit.add_machined_metal_material("gph-bond", COLOR_BOND_METAL, metallic=0.88, roughness=0.20)
    mat_vdw    = create_emissive_mat("gph-vdw", COLOR_VDW_LINK, strength=2.5)
    mat_plinth = kit.add_material("gph-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material("gph-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    bond_r = 0.024
    layer_gap = 0.052  # Van der Waals interlayer spacing (~2.2x bond_r)
    tau1 = (bond_r, 0.0)

    # 3 Layers: A (bottom), B (middle), A' (top)
    pts_A1, bonds_A1 = generate_planar_hex_layer(bond_r, shift=(0.0, 0.0), r_cut=0.076)
    pts_B,  bonds_B  = generate_planar_hex_layer(bond_r, shift=tau1, r_cut=0.076)
    pts_A2, bonds_A2 = generate_planar_hex_layer(bond_r, shift=(0.0, 0.0), r_cut=0.076)

    layers = [
        (pts_A1, bonds_A1, 0.038, "l1"),
        (pts_B,  bonds_B,  0.038 + layer_gap, "l2"),
        (pts_A2, bonds_A2, 0.038 + layer_gap * 2, "l3")
    ]

    # 1. Base Display Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-plinth", "cube", mat_plinth,
        size=(0.250, 0.250, 0.018),
        location=(0.0, 0.0, 0.009)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    plinth_rim = kit.primitive_object(
        f"{ASSET_ID}-plinth-rim", "cube", mat_trim,
        size=(0.256, 0.256, 0.003),
        location=(0.0, 0.0, 0.0015)
    )
    link_strictly(plinth_rim, col)
    objs.append(plinth_rim)

    # 2. Build 3 Planar Graphene Sheets
    r_atom = 0.0095
    r_bond = 0.0034

    for pts_layer, bonds_layer, z_val, l_name in layers:
        for v_idx, (px, py) in enumerate(pts_layer):
            atom = kit.primitive_object(
                f"{ASSET_ID}-atom-{l_name}-{v_idx}", "uv_sphere", mat_carbon,
                size=(r_atom * 2, r_atom * 2, r_atom * 2),
                location=(px, py, z_val)
            )
            link_strictly(atom, col)
            objs.append(atom)

        for b_idx, (i1, i2) in enumerate(bonds_layer):
            p1 = Vector((pts_layer[i1][0], pts_layer[i1][1], z_val))
            p2 = Vector((pts_layer[i2][0], pts_layer[i2][1], z_val))
            mid = (p1 + p2) * 0.5
            delta = p2 - p1
            direction = delta.normalized()
            rot = direction.to_track_quat('Z', 'Y').to_euler()

            bond = kit.primitive_object(
                f"{ASSET_ID}-bond-{l_name}-{b_idx}", "cylinder", mat_bond,
                size=(r_bond * 2, r_bond * 2, delta.length),
                location=mid,
                rotation_euler=rot
            )
            link_strictly(bond, col)
            objs.append(bond)

    # 3. Interlayer Van der Waals vertical dashed links (between Layer 1-2 and 2-3)
    vdw_count = 0
    # Between Layer 1 (A1) and Layer 2 (B)
    z1 = 0.038
    z2 = z1 + layer_gap
    z3 = z2 + layer_gap

    for pA in pts_A1:
        for pB in pts_B:
            if math.hypot(pA[0] - pB[0], pA[1] - pB[1]) < 0.002:
                # Vertical link between 1 and 2
                link1 = kit.primitive_object(
                    f"{ASSET_ID}-vdw-1-{vdw_count}", "cylinder", mat_vdw,
                    size=(0.0016, 0.0016, layer_gap * 0.88),
                    location=(pA[0], pA[1], (z1 + z2) * 0.5)
                )
                link_strictly(link1, col)
                objs.append(link1)

                # Vertical link between 2 and 3
                link2 = kit.primitive_object(
                    f"{ASSET_ID}-vdw-2-{vdw_count}", "cylinder", mat_vdw,
                    size=(0.0016, 0.0016, layer_gap * 0.88),
                    location=(pA[0], pA[1], (z2 + z3) * 0.5)
                )
                link_strictly(link2, col)
                objs.append(link2)

                vdw_count += 1

    return objs

def build_graphite_detail(col):
    """
    Constructs the detail exploded collection demonstrating:
      - Interlayer slippage / shear vectors (solid lubricant property).
      - Delocalized pi-electron cloud / conductivity flow.
      - 120° in-plane trigonal planar bond angle arc.
      - Bond length caliper: 1.42 Å in-plane vs 3.35 Å interlayer gap.
      - Educational property plaque.
    """
    objs = []
    mat_carbon_base   = create_carbon_mat("det-gph-c", COLOR_CARBON_GRAPHITE, metallic=0.30, roughness=0.30)
    mat_carbon_active = create_carbon_mat("det-gph-c-act", COLOR_CARBON_ACTIVE, metallic=0.20, roughness=0.25)
    mat_bond          = kit.add_machined_metal_material("det-gph-bond", COLOR_BOND_METAL, metallic=0.88, roughness=0.20)
    mat_vdw           = create_emissive_mat("det-gph-vdw", COLOR_VDW_LINK, strength=2.5)
    mat_electron      = create_emissive_mat("det-gph-elec", COLOR_PI_ELECTRON, strength=5.5)
    mat_slip          = create_emissive_mat("det-gph-slip", COLOR_SLIP_ARROW, strength=4.5)
    mat_arc           = create_emissive_mat("det-gph-arc", COLOR_ANGLE_ARC, strength=4.5)
    mat_plinth        = kit.add_material("det-gph-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim          = kit.add_material("det-gph-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    bond_r = 0.024
    layer_gap = 0.072  # Slightly exploded gap for clear inspection
    tau1 = (bond_r, 0.0)

    # 1. Base Display Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-det-plinth", "cube", mat_plinth,
        size=(0.260, 0.240, 0.018),
        location=(0.0, 0.0, 0.009)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    plinth_rim = kit.primitive_object(
        f"{ASSET_ID}-det-plinth-rim", "cube", mat_trim,
        size=(0.266, 0.246, 0.003),
        location=(0.0, 0.0, 0.0015)
    )
    link_strictly(plinth_rim, col)
    objs.append(plinth_rim)

    # 2 Layers with lateral slip offset
    # Lower layer fixed at z = 0.045
    # Upper layer shifted along +X by 0.018m at z = 0.045 + layer_gap
    pts_lower, bonds_lower = generate_planar_hex_layer(bond_r, shift=(0.0, 0.0), r_cut=0.068)
    pts_upper, bonds_upper = generate_planar_hex_layer(bond_r, shift=(tau1[0] + 0.016, 0.0), r_cut=0.068)

    z_low = 0.048
    z_up  = z_low + layer_gap

    # Build Lower Sheet
    r_atom = 0.0095
    r_bond = 0.0034

    for v_idx, (px, py) in enumerate(pts_lower):
        atom = kit.primitive_object(
            f"{ASSET_ID}-det-atom-low-{v_idx}", "uv_sphere", mat_carbon_base,
            size=(r_atom * 2, r_atom * 2, r_atom * 2),
            location=(px, py, z_low)
        )
        link_strictly(atom, col)
        objs.append(atom)

    for b_idx, (i1, i2) in enumerate(bonds_lower):
        p1 = Vector((pts_lower[i1][0], pts_lower[i1][1], z_low))
        p2 = Vector((pts_lower[i2][0], pts_lower[i2][1], z_low))
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        direction = delta.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()

        bond = kit.primitive_object(
            f"{ASSET_ID}-det-bond-low-{b_idx}", "cylinder", mat_bond,
            size=(r_bond * 2, r_bond * 2, delta.length),
            location=mid,
            rotation_euler=rot
        )
        link_strictly(bond, col)
        objs.append(bond)

    # Build Upper Sheet (with highlighted sp2 central node)
    center_idx = 0
    min_dist = 999.0
    for idx, (px, py) in enumerate(pts_upper):
        d = math.hypot(px, py)
        if d < min_dist:
            min_dist = d
            center_idx = idx

    for v_idx, (px, py) in enumerate(pts_upper):
        mat_c = mat_carbon_active if v_idx == center_idx else mat_carbon_base
        atom = kit.primitive_object(
            f"{ASSET_ID}-det-atom-up-{v_idx}", "uv_sphere", mat_c,
            size=(r_atom * 2.1 if v_idx == center_idx else r_atom * 2,
                  r_atom * 2.1 if v_idx == center_idx else r_atom * 2,
                  r_atom * 2.1 if v_idx == center_idx else r_atom * 2),
            location=(px, py, z_up)
        )
        link_strictly(atom, col)
        objs.append(atom)

    for b_idx, (i1, i2) in enumerate(bonds_upper):
        p1 = Vector((pts_upper[i1][0], pts_upper[i1][1], z_up))
        p2 = Vector((pts_upper[i2][0], pts_upper[i2][1], z_up))
        mid = (p1 + p2) * 0.5
        delta = p2 - p1
        direction = delta.normalized()
        rot = direction.to_track_quat('Z', 'Y').to_euler()

        bond = kit.primitive_object(
            f"{ASSET_ID}-det-bond-up-{b_idx}", "cylinder", mat_bond,
            size=(r_bond * 2, r_bond * 2, delta.length),
            location=mid,
            rotation_euler=rot
        )
        link_strictly(bond, col)
        objs.append(bond)

    # 3. Interlayer Slippage / Shear Arrows (indicating sliding layers / lubricity)
    slip_arrow_1 = kit.primitive_object(
        f"{ASSET_ID}-det-slip-1", "cone", mat_slip,
        size=(0.005, 0.005, 0.016),
        location=Vector((0.075, 0.035, z_up)),
        rotation_euler=(0.0, math.pi * 0.5, 0.0)
    )
    slip_shaft_1 = kit.primitive_object(
        f"{ASSET_ID}-det-slip-shaft-1", "cylinder", mat_slip,
        size=(0.0022, 0.0022, 0.025),
        location=Vector((0.055, 0.035, z_up)),
        rotation_euler=(0.0, math.pi * 0.5, 0.0)
    )
    link_strictly(slip_arrow_1, col)
    link_strictly(slip_shaft_1, col)
    objs.extend([slip_arrow_1, slip_shaft_1])

    slip_arrow_2 = kit.primitive_object(
        f"{ASSET_ID}-det-slip-2", "cone", mat_slip,
        size=(0.005, 0.005, 0.016),
        location=Vector((-0.075, -0.035, z_low)),
        rotation_euler=(0.0, -math.pi * 0.5, 0.0)
    )
    slip_shaft_2 = kit.primitive_object(
        f"{ASSET_ID}-det-slip-shaft-2", "cylinder", mat_slip,
        size=(0.0022, 0.0022, 0.025),
        location=Vector((-0.055, -0.035, z_low)),
        rotation_euler=(0.0, -math.pi * 0.5, 0.0)
    )
    link_strictly(slip_arrow_2, col)
    link_strictly(slip_shaft_2, col)
    objs.extend([slip_arrow_2, slip_shaft_2])

    # 4. Delocalized Pi-Electrons (free electrons moving freely within the plane)
    pi_pts = [
        Vector((-0.020,  0.015, z_up + 0.004)),
        Vector(( 0.005,  0.025, z_up + 0.004)),
        Vector(( 0.030,  0.008, z_up + 0.004)),
        Vector((-0.010, -0.022, z_up + 0.004)),
        Vector(( 0.022, -0.018, z_up + 0.004))
    ]
    for e_idx, e_pos in enumerate(pi_pts):
        e_sphere = kit.primitive_object(
            f"{ASSET_ID}-det-pi-e-{e_idx}", "uv_sphere", mat_electron,
            size=(0.0035, 0.0035, 0.0035),
            location=e_pos
        )
        link_strictly(e_sphere, col)
        objs.append(e_sphere)

    # 5. 120° Trigonal Planar Angle Arc at center atom
    c_pos = Vector((pts_upper[center_idx][0], pts_upper[center_idx][1], z_up))
    # Find two neighbor bonds from center_idx
    neighbors = []
    for (i1, i2) in bonds_upper:
        if i1 == center_idx:
            neighbors.append(Vector((pts_upper[i2][0], pts_upper[i2][1], z_up)))
        elif i2 == center_idx:
            neighbors.append(Vector((pts_upper[i1][0], pts_upper[i1][1], z_up)))
        if len(neighbors) == 2:
            break

    if len(neighbors) == 2:
        v1 = (neighbors[0] - c_pos).normalized()
        v2 = (neighbors[1] - c_pos).normalized()
        r_arc = 0.016
        num_pts = 16
        ang_tot = math.acos(max(-1.0, min(1.0, v1.dot(v2))))

        arc_pts = []
        e_x = v1
        e_y = (v2 - (v1.dot(v2)) * v1).normalized()
        for s in range(num_pts):
            theta = ang_tot * (s / (num_pts - 1))
            pt = c_pos + (e_x * math.cos(theta) + e_y * math.sin(theta)) * r_arc
            arc_pts.append(pt)

        arc_tube = kit.create_smooth_tube(f"{ASSET_ID}-det-arc-120", arc_pts, radius=0.0014, material=mat_arc)
        link_strictly(arc_tube, col)
        objs.append(arc_tube)

        # 120° badge
        arc_mid = c_pos + (e_x * math.cos(ang_tot * 0.5) + e_y * math.sin(ang_tot * 0.5)) * (r_arc + 0.008)
        badge_120 = kit.primitive_object(
            f"{ASSET_ID}-det-badge-120", "cube", mat_arc,
            size=(0.020, 0.004, 0.009),
            location=arc_mid
        )
        link_strictly(badge_120, col)
        objs.append(badge_120)

    # 6. Interlayer Gap Caliper (3.35 Å vs 1.42 Å)
    cal_rod = kit.primitive_object(
        f"{ASSET_ID}-det-cal-rod", "cylinder", mat_trim,
        size=(0.0016, 0.0016, layer_gap * 0.95),
        location=Vector((-0.065, 0.055, (z_low + z_up) * 0.5))
    )
    link_strictly(cal_rod, col)
    objs.append(cal_rod)

    cal_badge = kit.primitive_object(
        f"{ASSET_ID}-det-cal-badge", "cube", mat_trim,
        size=(0.024, 0.004, 0.009),
        location=Vector((-0.065, 0.055, (z_low + z_up) * 0.5 + 0.012))
    )
    link_strictly(cal_badge, col)
    objs.append(cal_badge)

    # 7. Educational Signage Plaque Banner
    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-det-plaque-bg", "cube", mat_plinth,
        size=(0.200, 0.004, 0.024),
        location=(0.0, 0.075, 0.150)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-det-plaque-trim", "cube", mat_trim,
        size=(0.204, 0.005, 0.002),
        location=(0.0, 0.075, 0.162)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    # Conductor / Lubricant property badge
    prop_badge = kit.primitive_object(
        f"{ASSET_ID}-det-prop-badge", "cube", mat_carbon_active,
        size=(0.048, 0.004, 0.012),
        location=(0.0, -0.075, 0.035)
    )
    link_strictly(prop_badge, col)
    objs.append(prop_badge)

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

    col_full = bpy.data.collections.new("Graphite_Lattice_Full")
    col_det  = bpy.data.collections.new("Graphite_Lattice_Detail")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_det)

    full_objs = build_graphite_full(col_full)
    det_objs  = build_graphite_detail(col_det)

    cam_data = bpy.data.cameras.new("Graphite_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Graphite_Camera", cam_data)
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

    # Render Preview 1: Full 3-Layer Graphite Stack
    set_collection_visibility(full_objs, True)
    set_collection_visibility(det_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.090)), distance=0.52, elev_deg=22, azim_deg=-30)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Detail Exploded View (Slippage & Conduction)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(det_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.095)), distance=0.48, elev_deg=18, azim_deg=-24)
    preview_det = out_dir / "preview_section.png"
    kit.render_preview(preview_det)
    print(f"Rendered: {preview_det}")

    print("=== GRAPHITE LATTICE BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
