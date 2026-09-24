"""
build_soap_micelle.py — NCERT Class 10 Chemistry Ch 4 Fig 4.12 & 4.13 Soap Micelle
Features dual collections:
  - Soap_Micelle_Full: 3D spherical micelle with 46 radial soap molecules (zigzag hydrocarbon tails and polar ionic heads) enclosing a central oily dirt droplet.
  - Soap_Micelle_Section: Hemispherical cutaway revealing the trapped interior oil droplet, hydrophobic tail insertion, surrounding polar water molecules (H2O), emulsification vectors, and educational plaque.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Quaternion, Matrix

ASSET_ID = 'soap-micelle'

# Calibrated Palette
COLOR_OIL_CORE     = (0.92, 0.70, 0.15)    # Trapped grease / oily dirt droplet
COLOR_TAIL         = (0.88, 0.78, 0.42)    # Non-polar hydrophobic hydrocarbon tail
COLOR_HEAD_COO     = (0.15, 0.58, 0.95)    # Polar hydrophilic ionic head (-COO-)
COLOR_ION_NA       = (0.98, 0.75, 0.18)    # Sodium counter-ion (Na+)
COLOR_WATER_O      = (0.90, 0.22, 0.22)    # Oxygen in water (red)
COLOR_WATER_H      = (0.92, 0.94, 0.96)    # Hydrogen in water (white)
COLOR_EMULS_ARROW  = (0.25, 0.85, 0.40)    # Solubilization / emulsification pull arrow
COLOR_PLINTH       = (0.12, 0.14, 0.18)    # Studio slate pedestal
COLOR_TRIM         = (0.95, 0.65, 0.15)    # Educational badge accent

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

def create_oil_material(name="OilDroplet"):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*COLOR_OIL_CORE, 1.0)
    bsdf.inputs["Metallic"].default_value = 0.05
    bsdf.inputs["Roughness"].default_value = 0.12
    bsdf.inputs["IOR"].default_value = 1.46
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.82
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.6
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*COLOR_OIL_CORE, 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.45
    return mat

def create_zigzag_tail_mesh(name, dir_vec, r_inner=0.022, r_outer=0.058, num_kinks=6, kink_amp=0.0032):
    """
    Constructs an organic zigzag hydrocarbon chain (-CH2-CH2-) along radial dir_vec.
    Creates a smooth extruded spline or tube across the zigzag vertices.
    """
    # Orthonormal perpendicular vector for lateral zigzag oscillation
    if abs(dir_vec.z) < 0.9:
        perp = Vector((-dir_vec.y, dir_vec.x, 0.0)).normalized()
    else:
        perp = Vector((1.0, 0.0, 0.0))

    pts = []
    for k in range(num_kinks + 1):
        frac = k / num_kinks
        r = r_inner + frac * (r_outer - r_inner)
        # Alternate lateral offset to form authentic zigzag
        offset_sign = 1.0 if (k % 2 == 1) else -1.0
        # Taper kink amplitude slightly near the head and inside the oil
        amp = kink_amp * math.sin(frac * math.pi)
        pos = dir_vec * r + perp * (offset_sign * amp)
        pts.append(pos)

    return pts

def build_water_molecule(name, pos, rot_euler, col, mat_o, mat_h):
    """Constructs a Mickey Mouse water molecule (H2O: angle 104.5 deg)."""
    objs = []
    # Oxygen sphere (radius 0.0042)
    o_atom = kit.primitive_object(
        f"{name}-O", "uv_sphere", mat_o,
        size=(0.0084, 0.0084, 0.0084),
        location=pos
    )
    link_strictly(o_atom, col)
    objs.append(o_atom)

    # Two hydrogen spheres (radius 0.0026) at 104.5 degrees
    ang_half = math.radians(52.25)
    d_oh = 0.0068
    h1_local = Vector((d_oh * math.sin(ang_half), 0.0, d_oh * math.cos(ang_half)))
    h2_local = Vector((-d_oh * math.sin(ang_half), 0.0, d_oh * math.cos(ang_half)))

    # Apply rotation
    rot_q = rot_euler.to_quaternion()
    h1_pos = pos + rot_q @ h1_local
    h2_pos = pos + rot_q @ h2_local

    h1 = kit.primitive_object(
        f"{name}-H1", "uv_sphere", mat_h,
        size=(0.0052, 0.0052, 0.0052),
        location=h1_pos
    )
    h2 = kit.primitive_object(
        f"{name}-H2", "uv_sphere", mat_h,
        size=(0.0052, 0.0052, 0.0052),
        location=h2_pos
    )
    link_strictly(h1, col)
    link_strictly(h2, col)
    objs.extend([h1, h2])
    return objs

def build_soap_full(col):
    """Constructs the complete 3D spherical soap micelle on a display plinth."""
    objs = []
    mat_oil    = create_oil_material("mic-oil")
    mat_tail   = kit.add_material("mic-tail", COLOR_TAIL, metallic=0.08, roughness=0.45)
    mat_head   = kit.add_material("mic-head", COLOR_HEAD_COO, metallic=0.15, roughness=0.25)
    bsdf_head  = mat_head.node_tree.nodes.get("Principled BSDF")
    if bsdf_head:
        bsdf_head.inputs["Emission Color"].default_value = (*COLOR_HEAD_COO, 1.0)
        bsdf_head.inputs["Emission Strength"].default_value = 0.65

    mat_na     = create_emissive_mat("mic-na", COLOR_ION_NA, strength=3.0)
    mat_plinth = kit.add_material("mic-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material("mic-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    center_pos = Vector((0.0, 0.0, 0.095))

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

    # 2. Central Trapped Oil/Grease Droplet (r = 0.024m)
    r_oil = 0.024
    oil_core = kit.primitive_object(
        f"{ASSET_ID}-oil-core", "uv_sphere", mat_oil,
        size=(r_oil * 2, r_oil * 2, r_oil * 2),
        location=center_pos
    )
    link_strictly(oil_core, col)
    objs.append(oil_core)

    # 3. Radial Soap Molecules (Fibonacci sphere distribution of 44 molecules)
    num_mols = 44
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0

    r_inner = 0.020
    r_head  = 0.060
    r_na    = 0.072

    for i in range(num_mols):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / num_mols)

        dir_vec = Vector((
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        )).normalized()

        # Zigzag hydrocarbon tail
        tail_pts = create_zigzag_tail_mesh(f"tail-{i}", dir_vec, r_inner=r_inner, r_outer=r_head - 0.006, num_kinks=6)
        world_tail_pts = [center_pos + p for p in tail_pts]
        tail_tube = kit.create_smooth_tube(f"{ASSET_ID}-tail-{i}", world_tail_pts, radius=0.0018, material=mat_tail)
        link_strictly(tail_tube, col)
        objs.append(tail_tube)

        # Polar Hydrophilic Ionic Head (-COO-)
        head_pos = center_pos + dir_vec * r_head
        r_head_sph = 0.0072
        head_sph = kit.primitive_object(
            f"{ASSET_ID}-head-{i}", "uv_sphere", mat_head,
            size=(r_head_sph * 2, r_head_sph * 2, r_head_sph * 2),
            location=head_pos
        )
        link_strictly(head_sph, col)
        objs.append(head_sph)

        # Sodium Counter-ion (Na+) situated near head
        if i % 2 == 0:
            na_pos = center_pos + dir_vec * r_na + Vector((0.002, 0.002, 0.002))
            r_na_sph = 0.0042
            na_sph = kit.primitive_object(
                f"{ASSET_ID}-na-{i}", "uv_sphere", mat_na,
                size=(r_na_sph * 2, r_na_sph * 2, r_na_sph * 2),
                location=na_pos
            )
            link_strictly(na_sph, col)
            objs.append(na_sph)

    return objs

def build_soap_section(col):
    """
    Constructs the longitudinal cutaway collection:
      - Front hemisphere cut open revealing the trapped oily grease droplet at center.
      - Zigzag tails dissolving into the lipid core.
      - Surrounding polar water molecules (H2O) forming hydration shell.
      - Emulsification pulling vector arrows.
      - Educational property plaque.
    """
    objs = []
    mat_oil    = create_oil_material("sec-mic-oil")
    mat_tail   = kit.add_material("sec-mic-tail", COLOR_TAIL, metallic=0.08, roughness=0.45)
    mat_head   = kit.add_material("sec-mic-head", COLOR_HEAD_COO, metallic=0.15, roughness=0.25)
    bsdf_head  = mat_head.node_tree.nodes.get("Principled BSDF")
    if bsdf_head:
        bsdf_head.inputs["Emission Color"].default_value = (*COLOR_HEAD_COO, 1.0)
        bsdf_head.inputs["Emission Strength"].default_value = 0.70

    mat_na     = create_emissive_mat("sec-mic-na", COLOR_ION_NA, strength=3.2)
    mat_o      = kit.add_material("sec-mic-water-o", COLOR_WATER_O, metallic=0.05, roughness=0.25)
    mat_h      = kit.add_material("sec-mic-water-h", COLOR_WATER_H, metallic=0.05, roughness=0.25)
    mat_arrow  = create_emissive_mat("sec-mic-arrow", COLOR_EMULS_ARROW, strength=4.5)
    mat_plinth = kit.add_material("sec-mic-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material("sec-mic-trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    center_pos = Vector((0.0, 0.0, 0.095))

    # 1. Base Display Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-sec-plinth", "cube", mat_plinth,
        size=(0.260, 0.240, 0.018),
        location=(0.0, 0.0, 0.009)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    plinth_rim = kit.primitive_object(
        f"{ASSET_ID}-sec-plinth-rim", "cube", mat_trim,
        size=(0.266, 0.246, 0.003),
        location=(0.0, 0.0, 0.0015)
    )
    link_strictly(plinth_rim, col)
    objs.append(plinth_rim)

    # 2. Cutaway Oil Droplet (Half Sphere: Y >= 0 facing rear, front Y < 0 cut open)
    bm_oil = bmesh.new()
    segs = 32
    rings = 16
    r_oil = 0.024
    # Revolve half circle from theta = 0 to pi (Y >= 0)
    for ri in range(rings + 1):
        phi = math.pi * (ri / rings)  # 0 to pi (Z from +r to -r)
        z = r_oil * math.cos(phi)
        r_ring = r_oil * math.sin(phi)
        for si in range(segs + 1):
            theta = math.pi * (si / segs)  # 0 to pi (Y >= 0)
            x = r_ring * math.cos(theta)
            y = r_ring * math.sin(theta)
            bm_oil.verts.new((x, y, z))

    bm_oil.verts.ensure_lookup_table()
    for ri in range(rings):
        for si in range(segs):
            v1 = bm_oil.verts[ri * (segs + 1) + si]
            v2 = bm_oil.verts[ri * (segs + 1) + (si + 1)]
            v3 = bm_oil.verts[(ri + 1) * (segs + 1) + (si + 1)]
            v4 = bm_oil.verts[(ri + 1) * (segs + 1) + si]
            bm_oil.faces.new([v1, v2, v3, v4])

    # Flat cross-section face along X-Z plane at Y = 0
    # Left edge: si = segs (theta = pi, x = -r, y = 0)
    # Right edge: si = 0 (theta = 0, x = +r, y = 0)
    flat_verts_right = [bm_oil.verts[ri * (segs + 1)] for ri in range(rings + 1)]
    flat_verts_left  = [bm_oil.verts[ri * (segs + 1) + segs] for ri in range(rings + 1)]
    # Connect flat face
    for ri in range(rings):
        v_rt1 = flat_verts_right[ri]
        v_rt2 = flat_verts_right[ri + 1]
        v_lt1 = flat_verts_left[ri]
        v_lt2 = flat_verts_left[ri + 1]
        bm_oil.faces.new([v_rt1, v_lt1, v_lt2, v_rt2])

    bmesh.ops.recalc_face_normals(bm_oil, faces=bm_oil.faces)
    mesh_oil = bpy.data.meshes.new(f"{ASSET_ID}-sec-oil-mesh")
    bm_oil.to_mesh(mesh_oil)
    bm_oil.free()
    for poly in mesh_oil.polygons:
        poly.use_smooth = True
    oil_obj = bpy.data.objects.new(f"{ASSET_ID}-sec-oil", mesh_oil)
    oil_obj.location = center_pos
    oil_obj.data.materials.append(mat_oil)
    col.objects.link(oil_obj)
    objs.append(oil_obj)

    # 3. Rear Half-Sphere of Soap Molecules (Y >= -0.005)
    num_mols = 50
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0
    r_inner = 0.020
    r_head  = 0.060
    r_na    = 0.072

    mol_idx = 0
    for i in range(num_mols):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / num_mols)

        dir_vec = Vector((
            math.sin(phi) * math.cos(theta),
            math.sin(phi) * math.sin(theta),
            math.cos(phi)
        )).normalized()

        # Only retain molecules in the rear hemisphere (Y >= -0.006) to show internal cross-section
        if dir_vec.y < -0.08:
            continue

        tail_pts = create_zigzag_tail_mesh(f"sec-tail-{mol_idx}", dir_vec, r_inner=r_inner, r_outer=r_head - 0.006, num_kinks=6)
        world_tail_pts = [center_pos + p for p in tail_pts]
        tail_tube = kit.create_smooth_tube(f"{ASSET_ID}-sec-tail-{mol_idx}", world_tail_pts, radius=0.0018, material=mat_tail)
        link_strictly(tail_tube, col)
        objs.append(tail_tube)

        head_pos = center_pos + dir_vec * r_head
        r_head_sph = 0.0072
        head_sph = kit.primitive_object(
            f"{ASSET_ID}-sec-head-{mol_idx}", "uv_sphere", mat_head,
            size=(r_head_sph * 2, r_head_sph * 2, r_head_sph * 2),
            location=head_pos
        )
        link_strictly(head_sph, col)
        objs.append(head_sph)

        if mol_idx % 2 == 0:
            na_pos = center_pos + dir_vec * r_na + Vector((0.002, 0.002, 0.002))
            r_na_sph = 0.0042
            na_sph = kit.primitive_object(
                f"{ASSET_ID}-sec-na-{mol_idx}", "uv_sphere", mat_na,
                size=(r_na_sph * 2, r_na_sph * 2, r_na_sph * 2),
                location=na_pos
            )
            link_strictly(na_sph, col)
            objs.append(na_sph)

        mol_idx += 1

    # 4. Polar Water Molecules (H2O) forming hydration shell around ionic heads
    water_positions = [
        Vector(( 0.076, -0.015, 0.125)),
        Vector((-0.076, -0.015, 0.125)),
        Vector(( 0.045, -0.035, 0.155)),
        Vector((-0.045, -0.035, 0.155)),
        Vector(( 0.082, -0.020, 0.065)),
        Vector((-0.082, -0.020, 0.065)),
        Vector(( 0.000, -0.045, 0.035))
    ]
    for w_idx, w_pos in enumerate(water_positions):
        rot_e = (Vector((0.0, 0.0, 0.095)) - w_pos).to_track_quat('Z', 'Y').to_euler()
        w_objs = build_water_molecule(f"{ASSET_ID}-sec-water-{w_idx}", w_pos, rot_e, col, mat_o, mat_h)
        objs.extend(w_objs)

    # 5. Emulsification / Solubilization Pull Vector Arrows
    # Green arrows radiating outwards from oil core through heads indicating mechanical lifting of dirt
    arrow_dirs = [
        Vector(( 0.065, -0.010, 0.045)),
        Vector((-0.065, -0.010, 0.045)),
        Vector(( 0.000, -0.015, 0.065))
    ]
    for a_idx, a_dir in enumerate(arrow_dirs):
        norm_dir = a_dir.normalized()
        tip_pos = center_pos + norm_dir * (r_head + 0.022)
        shaft_pos = center_pos + norm_dir * (r_head + 0.010)
        rot = norm_dir.to_track_quat('Z', 'Y').to_euler()

        arrow_tip = kit.primitive_object(
            f"{ASSET_ID}-sec-arrow-tip-{a_idx}", "cone", mat_arrow,
            size=(0.005, 0.005, 0.012),
            location=tip_pos,
            rotation_euler=rot
        )
        arrow_shaft = kit.primitive_object(
            f"{ASSET_ID}-sec-arrow-shaft-{a_idx}", "cylinder", mat_arrow,
            size=(0.002, 0.002, 0.016),
            location=shaft_pos,
            rotation_euler=rot
        )
        link_strictly(arrow_tip, col)
        link_strictly(arrow_shaft, col)
        objs.extend([arrow_tip, arrow_shaft])

    # 6. Educational Signage Plaque Banner
    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-bg", "cube", mat_plinth,
        size=(0.200, 0.004, 0.024),
        location=(0.0, 0.080, 0.165)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-trim", "cube", mat_trim,
        size=(0.204, 0.005, 0.002),
        location=(0.0, 0.080, 0.177)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    # Hydrophobic / Hydrophilic dual-nature indicator badge
    dual_badge = kit.primitive_object(
        f"{ASSET_ID}-sec-dual-badge", "cube", mat_head,
        size=(0.052, 0.004, 0.012),
        location=(0.0, -0.075, 0.035)
    )
    link_strictly(dual_badge, col)
    objs.append(dual_badge)

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
    scene.cycles.max_bounces = 10
    scene.cycles.diffuse_bounces = 3
    scene.cycles.glossy_bounces = 6
    scene.cycles.transmission_bounces = 10
    scene.cycles.transparent_max_bounces = 10
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    col_full = bpy.data.collections.new("Soap_Micelle_Full")
    col_sec  = bpy.data.collections.new("Soap_Micelle_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_soap_full(col_full)
    sec_objs  = build_soap_section(col_sec)

    cam_data = bpy.data.cameras.new("Micelle_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Micelle_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

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

    configure_fast_render(width=1280, height=720, samples=24)

    # Render Preview 1: Full Spherical Soap Micelle
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.095)), distance=0.48, elev_deg=22, azim_deg=-28)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section View (Trapped Oil, Cutaway Tails, H2O molecules)
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.098)), distance=0.46, elev_deg=18, azim_deg=-22)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== SOAP MICELLE BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
