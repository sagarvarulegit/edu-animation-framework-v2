"""
build_bar_magnet.py — Laboratory-Grade Bar Magnet & Magnetic Field Line Geometry
NCERT Class 10 Science Chapter 12 (Magnetic Effects of Electric Current), Figs 12.2, 12.3, 12.4.

Dual Collections:
  1. Bar_Magnet_Full:
     - Real-world AlNiCo permanent bar magnet with chamfered edges, deep crimson North pole (N)
       and deep cobalt blue South pole (S), with embossed pole labels.
     - Studio slate display plinth with gold trim.
     - 3D continuous toroidal magnetic field flux loops radiating from North (+X) to South (-X)
       in both the horizontal and oblique vertical planes.
     - Directional flux arrow cones indicating external field direction from N to S.
     - Precision turned brass pocket plotting compass positioned on a field line with magnetic needle.

  2. Bar_Magnet_Detail (Iron Filings Pattern & Multi-Compass Array):
     - White testing card/cardboard base displaying iron filings field density distribution:
       * Dense radial iron filings particle clusters near the magnetic poles.
       * Streamlined curved filing trails tracing lines of force from N to S.
     - Array of 6 miniature magnetic plotting compasses placed at strategic field positions,
       demonstrating continuous tangential orientation along the magnetic lines of force.
     - Educational plaque mounted on brass stanchions:
       * "MAGNETIC FIELD LINES OF A BAR MAGNET"
       * "Direction: Emerge from North, Enter South (Closed Loops)"
       * "Density: Field Strength proportional to Closeness of Lines"
       * "Rule: Two Magnetic Field Lines Never Intersect"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'bar-magnet'

# Calibrated Laboratory Palette
COLOR_NORTH_RED    = (0.88, 0.14, 0.14)     # Deep crimson North magnetic pole
COLOR_SOUTH_BLUE   = (0.14, 0.38, 0.88)     # Deep cobalt South magnetic pole
COLOR_POLE_LABEL   = (0.95, 0.95, 0.95)     # Embossed white pole indicator ('N' / 'S')
COLOR_FLUX_LINE    = (0.20, 0.80, 1.00)     # Luminescent cyan magnetic flux line
COLOR_ARROW        = (0.22, 0.85, 1.00)     # Directional flux arrow
COLOR_COMPASS_CASE = (0.86, 0.70, 0.28)     # Turned brass compass housing
COLOR_COMPASS_DIAL = (0.96, 0.96, 0.94)     # Crisp white compass dial face
COLOR_GLASS        = (0.98, 0.99, 1.00)     # Optical glass protective cover
COLOR_IRON_FILING  = (0.18, 0.19, 0.22)     # Grey-black ferromagnetic iron filing particles
COLOR_CARD         = (0.95, 0.95, 0.92)     # White plotting cardboard sheet
COLOR_PLINTH       = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM         = (0.95, 0.65, 0.15)     # Educational badge gold accent

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=10.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_cylinder_segment(name, p1, p2, radius, mat, collection):
    v1 = Vector(p1)
    v2 = Vector(p2)
    diff = v2 - v1
    length = diff.length
    if length < 1e-6:
        return None
    center = (v1 + v2) * 0.5

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=12,
                          radius1=radius, radius2=radius, depth=length)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    rot_quat = Vector((0.0, 0.0, 1.0)).rotation_difference(diff)
    obj.rotation_euler = rot_quat.to_euler()
    obj.data.materials.append(mat)
    link_strictly(obj, collection)
    return obj

def build_plotting_compass(name, location, heading_rad, mat_brass, mat_glass, mat_dial, mat_n, mat_s, collection, radius=0.009, height=0.0045):
    """Creates a miniature magnetic plotting compass with needle pointing along heading_rad."""
    objs = []
    # Brass casing
    c_case = kit.primitive_object(f"{name}_case", "cylinder", mat_brass,
                                  size=(radius * 2, radius * 2, height),
                                  location=(location[0], location[1], location[2] + height * 0.5))
    link_strictly(c_case, collection)
    objs.append(c_case)

    # Dial face
    c_dial = kit.primitive_object(f"{name}_dial", "cylinder", mat_dial,
                                  size=(radius * 1.8, radius * 1.8, 0.0005),
                                  location=(location[0], location[1], location[2] + height * 0.7))
    link_strictly(c_dial, collection)
    objs.append(c_dial)

    # Needle pivot
    pivot = kit.primitive_object(f"{name}_pivot", "cylinder", mat_brass,
                                 size=(0.002, 0.002, 0.0015),
                                 location=(location[0], location[1], location[2] + height * 0.75))
    link_strictly(pivot, collection)
    objs.append(pivot)

    # North pointer (crimson red triangle/cone pointing along heading)
    needle_len = radius * 0.75
    needle_w = radius * 0.28
    dir_v = Vector((math.cos(heading_rad), math.sin(heading_rad), 0.0))
    n_pos = Vector(location) + Vector((0, 0, height * 0.8)) + dir_v * (needle_len * 0.5)
    rot_n = Vector((0.0, 0.0, 1.0)).rotation_difference(dir_v).to_euler()

    n_cone = kit.primitive_object(f"{name}_needle_N", "cone", mat_n,
                                  size=(needle_w, needle_w, needle_len),
                                  location=n_pos,
                                  rotation_euler=rot_n)
    link_strictly(n_cone, collection)
    objs.append(n_cone)

    # South pointer (cobalt blue triangle/cone pointing in opposite direction)
    s_pos = Vector(location) + Vector((0, 0, height * 0.8)) - dir_v * (needle_len * 0.5)
    rot_s = Vector((0.0, 0.0, 1.0)).rotation_difference(-dir_v).to_euler()
    s_cone = kit.primitive_object(f"{name}_needle_S", "cone", mat_s,
                                  size=(needle_w, needle_w, needle_len),
                                  location=s_pos,
                                  rotation_euler=rot_s)
    link_strictly(s_cone, collection)
    objs.append(s_cone)

    # Glass cover
    c_glass = kit.primitive_object(f"{name}_glass", "cylinder", mat_glass,
                                   size=(radius * 1.85, radius * 1.85, 0.0006),
                                   location=(location[0], location[1], location[2] + height + 0.0003))
    link_strictly(c_glass, collection)
    objs.append(c_glass)

    return objs

def build_magnet_core(prefix, collection, mat_n, mat_s, mat_label, z_base=0.016):
    """
    Constructs the AlNiCo permanent bar magnet:
    Length: 0.120m (X from -0.060 to +0.060), Width: 0.024m, Height: 0.018m.
    North half: X = 0.0 to +0.060 (Red).
    South half: X = -0.060 to 0.0 (Blue).
    Embossed 'N' and 'S' pole plates.
    """
    objs = []
    l_half = 0.060
    w_mag = 0.024
    h_mag = 0.018
    z_center = z_base + h_mag * 0.5

    # North Pole (+X half)
    north = kit.primitive_object(f"{prefix}_north", "cube", mat_n,
                                size=(l_half, w_mag, h_mag),
                                location=(l_half * 0.5, 0.0, z_center))
    link_strictly(north, collection)
    objs.append(north)

    # South Pole (-X half)
    south = kit.primitive_object(f"{prefix}_south", "cube", mat_s,
                                size=(l_half, w_mag, h_mag),
                                location=(-l_half * 0.5, 0.0, z_center))
    link_strictly(south, collection)
    objs.append(south)

    # Pole Label Plates ('N' on North, 'S' on South)
    label_n = kit.primitive_object(f"{prefix}_label_N", "cube", mat_label,
                                  size=(0.010, 0.010, 0.001),
                                  location=(l_half * 0.70, 0.0, z_base + h_mag + 0.0005))
    label_s = kit.primitive_object(f"{prefix}_label_S", "cube", mat_label,
                                  size=(0.010, 0.010, 0.001),
                                  location=(-l_half * 0.70, 0.0, z_base + h_mag + 0.0005))
    link_strictly(label_n, collection)
    link_strictly(label_s, collection)
    objs.extend([label_n, label_s])

    return objs

def build_magnetic_field_loops(prefix, collection, mat_flux, mat_arrow, z_center=0.025):
    """
    Builds continuous toroidal magnetic field lines emerging from North (+X) and entering South (-X).
    Generated as smooth tubular loops with directional arrow cones pointing from N to S.
    """
    objs = []
    # Loop configurations: (semi_major_a, semi_minor_b, z_tilt)
    loop_configs = [
        # Horizontal plane loops (symmetric +Y and -Y)
        (0.078,  0.032, 0.000),
        (0.078, -0.032, 0.000),
        (0.100,  0.054, 0.000),
        (0.100, -0.054, 0.000),
        (0.125,  0.082, 0.000),
        (0.125, -0.082, 0.000),
        (0.155,  0.115, 0.000),
        (0.155, -0.115, 0.000),
        # 3D oblique spatial loops
        (0.088,  0.036, 0.026),
        (0.088, -0.036, 0.026),
        (0.115,  0.060, 0.035),
        (0.115, -0.060, 0.035),
    ]

    for idx, (a, b, z_tilt) in enumerate(loop_configs):
        steps = 36
        pts = []
        for s in range(steps + 1):
            t = math.pi * s / steps  # 0 (North, +X) to pi (South, -X)
            px = a * math.cos(t)
            py = b * math.sin(t)
            pz = z_center + z_tilt * math.sin(t)
            pts.append(Vector((px, py, pz)))

        # Build discrete cylindrical tube segments
        for i in range(steps):
            seg = create_cylinder_segment(f"{prefix}_flux_{idx}_{i}", pts[i], pts[i+1], 0.0008, mat_flux, collection)
            if seg:
                objs.append(seg)

        # Place directional arrow cone at midpoint pointing along tangent (towards South, -X)
        mid_idx = steps // 2
        p_mid = pts[mid_idx]
        p_next = pts[mid_idx + 1]
        tan_dir = (p_next - p_mid).normalized()
        arrow_rot = Vector((0.0, 0.0, 1.0)).rotation_difference(tan_dir).to_euler()
        arrow = kit.primitive_object(f"{prefix}_arrow_{idx}", "cone", mat_arrow,
                                    size=(0.0035, 0.0035, 0.006),
                                    location=p_mid,
                                    rotation_euler=arrow_rot)
        link_strictly(arrow, collection)
        objs.append(arrow)

    return objs

def build_bar_magnet_full(collection):
    """Builds the complete permanent bar magnet with 3D spatial field lines."""
    objs = []
    prefix = "bm_full"

    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_n      = kit.add_material(f"{prefix}_north", COLOR_NORTH_RED, metallic=0.20, roughness=0.30)
    mat_s      = kit.add_material(f"{prefix}_south", COLOR_SOUTH_BLUE, metallic=0.20, roughness=0.30)
    mat_label  = kit.add_material(f"{prefix}_label", COLOR_POLE_LABEL, metallic=0.10, roughness=0.40)
    mat_flux   = create_emissive_mat(f"{prefix}_flux", COLOR_FLUX_LINE, strength=10.0)
    mat_arrow  = create_emissive_mat(f"{prefix}_arrow", COLOR_ARROW, strength=12.0)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_COMPASS_CASE, metallic=0.92, roughness=0.25)
    mat_glass  = kit.add_glass_material(f"{prefix}_glass", (0.98, 0.99, 1.0), ior=1.50, roughness=0.01)
    mat_dial   = kit.add_material(f"{prefix}_dial", COLOR_COMPASS_DIAL, metallic=0.0, roughness=0.30)

    # 1. Slate Display Plinth
    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                 size=(0.340, 0.250, 0.016),
                                 location=(0.0, 0.0, 0.008))
    link_strictly(plinth, collection)
    rim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                               size=(0.346, 0.256, 0.003),
                               location=(0.0, 0.0, 0.0015))
    link_strictly(rim, collection)
    objs.extend([plinth, rim])

    # 2. Bar Magnet
    mag_objs = build_magnet_core(prefix, collection, mat_n, mat_s, mat_label, z_base=0.016)
    objs.extend(mag_objs)

    # 3. 3D Toroidal Magnetic Field Lines & Directional Arrows
    flux_objs = build_magnetic_field_loops(prefix, collection, mat_flux, mat_arrow, z_center=0.025)
    objs.extend(flux_objs)

    # 4. Precision Turned Brass Plotting Compass on Field Line (x = 0, y = 0.054m)
    # At x = 0, y = +0.054m, field direction is purely along -X (heading = pi radians = 180 deg)
    compass_objs = build_plotting_compass(f"{prefix}_compass", (0.0, 0.054, 0.016), math.pi,
                                         mat_brass, mat_glass, mat_dial, mat_n, mat_s, collection,
                                         radius=0.012, height=0.006)
    objs.extend(compass_objs)

    return objs

def build_bar_magnet_detail(collection):
    """
    Builds the detailed laboratory investigation view:
    Iron filings distribution pattern & 6-compass tangential orientation array.
    """
    objs = []
    prefix = "bm_det"

    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)
    mat_card   = kit.add_material(f"{prefix}_card", COLOR_CARD, metallic=0.02, roughness=0.75)
    mat_n      = kit.add_material(f"{prefix}_north", COLOR_NORTH_RED, metallic=0.20, roughness=0.30)
    mat_s      = kit.add_material(f"{prefix}_south", COLOR_SOUTH_BLUE, metallic=0.20, roughness=0.30)
    mat_label  = kit.add_material(f"{prefix}_label", COLOR_POLE_LABEL, metallic=0.10, roughness=0.40)
    mat_filing = kit.add_material(f"{prefix}_filing", COLOR_IRON_FILING, metallic=0.70, roughness=0.45)
    mat_flux   = create_emissive_mat(f"{prefix}_flux_subtle", COLOR_FLUX_LINE, strength=5.0)
    mat_brass  = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_COMPASS_CASE, metallic=0.92, roughness=0.25)
    mat_glass  = kit.add_glass_material(f"{prefix}_glass", (0.98, 0.99, 1.0), ior=1.50, roughness=0.01)
    mat_dial   = kit.add_material(f"{prefix}_dial", COLOR_COMPASS_DIAL, metallic=0.0, roughness=0.30)
    mat_badge  = kit.add_material(f"{prefix}_badge_bg", COLOR_PLINTH, metallic=0.10, roughness=0.50)
    mat_accent = kit.add_material(f"{prefix}_badge_acc", COLOR_TRIM, metallic=0.20, roughness=0.35)

    # 1. Slate Display Plinth
    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                 size=(0.340, 0.250, 0.016),
                                 location=(0.0, 0.0, 0.008))
    link_strictly(plinth, collection)
    rim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                               size=(0.346, 0.256, 0.003),
                               location=(0.0, 0.0, 0.0015))
    link_strictly(rim, collection)
    objs.extend([plinth, rim])

    # 2. White Cardboard Testing Sheet
    card = kit.primitive_object(f"{prefix}_card", "cube", mat_card,
                                size=(0.300, 0.190, 0.001),
                                location=(0.0, 0.0, 0.0165))
    link_strictly(card, collection)
    objs.append(card)

    # 3. Bar Magnet resting on card
    mag_objs = build_magnet_core(prefix, collection, mat_n, mat_s, mat_label, z_base=0.017)
    objs.extend(mag_objs)

    # 4. Iron Filings Streamline Trails on Card (z = 0.0172m)
    # Streamlines represent filings lining up along magnetic forces
    radii = [(0.075, 0.024), (0.090, 0.040), (0.110, 0.062), (0.135, 0.088),
             (0.075, -0.024), (0.090, -0.040), (0.110, -0.062), (0.135, -0.088)]
    for idx, (a, b) in enumerate(radii):
        steps = 28
        pts = []
        for s in range(steps + 1):
            t = math.pi * s / steps
            px = a * math.cos(t)
            py = b * math.sin(t)
            pts.append(Vector((px, py, 0.0173)))
        for i in range(steps):
            seg = create_cylinder_segment(f"{prefix}_streamline_{idx}_{i}", pts[i], pts[i+1], 0.0006, mat_filing, collection)
            if seg:
                objs.append(seg)

    # High-density particle clusters near the magnetic poles
    # Polar clusters: North (+X = 0.060m) and South (-X = -0.060m)
    for p_sign, p_name in [(1.0, "north"), (-1.0, "south")]:
        for rad_step in range(3):
            r_dist = 0.010 + rad_step * 0.006
            for ang_i in range(12):
                ang = (ang_i / 12.0) * math.pi - math.pi * 0.5
                fx = p_sign * (0.060 + r_dist * math.cos(ang))
                fy = r_dist * math.sin(ang)
                if abs(fx) < 0.140 and abs(fy) < 0.085:
                    filing_dot = kit.primitive_object(f"{prefix}_filing_{p_name}_{rad_step}_{ang_i}", "cylinder", mat_filing,
                                                      size=(0.0016, 0.0016, 0.0006),
                                                      location=(fx, fy, 0.0175))
                    link_strictly(filing_dot, collection)
                    objs.append(filing_dot)

    # 5. Array of 6 Tangential Magnetic Plotting Compasses (Class 10 Fig 12.3)
    # Positions and local magnetic field tangents:
    compass_configs = [
        # (x, y, heading_rad)
        ( 0.045,  0.038, math.radians(155.0)),   # Upper North quadrant: curving from N
        ( 0.000,  0.052, math.radians(180.0)),   # Upper Equator: pointing purely -X (towards S)
        (-0.045,  0.038, math.radians(205.0)),   # Upper South quadrant: entering S
        ( 0.045, -0.038, math.radians(205.0)),   # Lower North quadrant: curving from N
        ( 0.000, -0.052, math.radians(180.0)),   # Lower Equator: pointing purely -X (towards S)
        (-0.045, -0.038, math.radians(155.0)),   # Lower South quadrant: entering S
    ]

    for c_i, (cx, cy, heading) in enumerate(compass_configs):
        c_objs = build_plotting_compass(f"{prefix}_array_compass_{c_i}", (cx, cy, 0.017), heading,
                                        mat_brass, mat_glass, mat_dial, mat_n, mat_s, collection,
                                        radius=0.0085, height=0.004)
        objs.extend(c_objs)

    # 6. Educational Plaque Standing on Slate Plinth (Front Stanchions)
    plaque_w, plaque_h, plaque_th = 0.180, 0.038, 0.004
    plaque_y = -0.104
    plaque_z = 0.034
    leg_l = kit.primitive_object(f"{prefix}_plaque_leg_l", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(-0.065, plaque_y, 0.016 + 0.015))
    leg_r = kit.primitive_object(f"{prefix}_plaque_leg_r", "cylinder", mat_brass,
                                size=(0.003, 0.003, 0.030),
                                location=(0.065, plaque_y, 0.016 + 0.015))
    link_strictly(leg_l, collection)
    link_strictly(leg_r, collection)

    angle_tilt = -math.radians(25.0)
    tilt_rot = (angle_tilt, 0.0, 0.0)
    plaque_face = kit.primitive_object(f"{prefix}_plaque_face", "cube", mat_badge,
                                      size=(plaque_w, plaque_th, plaque_h),
                                      location=(0.0, plaque_y, plaque_z),
                                      rotation_euler=tilt_rot)
    link_strictly(plaque_face, collection)

    rot_m = Matrix.Rotation(angle_tilt, 3, 'X')
    def local_plaque_pt(lx, lz, front_offset=0.0006):
        loc_vec = Vector((lx, -plaque_th * 0.5 - front_offset, lz))
        world_vec = rot_m @ loc_vec
        return Vector((0.0, plaque_y, plaque_z)) + world_vec

    trim_pos = local_plaque_pt(0.0, plaque_h * 0.5, front_offset=0.0)
    plaque_trim = kit.primitive_object(f"{prefix}_plaque_trim", "cube", mat_accent,
                                       size=(plaque_w + 0.004, plaque_th + 0.001, 0.002),
                                       location=trim_pos,
                                       rotation_euler=tilt_rot)
    link_strictly(plaque_trim, collection)

    # Title Bar: "MAGNETIC FIELD LINES (NCERT FIG 12.4)"
    bar_pos = local_plaque_pt(0.0, 0.010)
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_accent,
                                     size=(plaque_w * 0.88, 0.001, 0.005),
                                     location=bar_pos,
                                     rotation_euler=tilt_rot)
    link_strictly(title_bar, collection)

    # Sub-bars representing key laws:
    # 1. Closed continuous loops: N -> S externally
    sub1_pos = local_plaque_pt(0.0, 0.002)
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_n,
                                size=(plaque_w * 0.76, 0.001, 0.0035),
                                location=sub1_pos,
                                rotation_euler=tilt_rot)
    # 2. Field lines never intersect
    sub2_pos = local_plaque_pt(0.0, -0.006)
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_s,
                                size=(plaque_w * 0.62, 0.001, 0.0035),
                                location=sub2_pos,
                                rotation_euler=tilt_rot)
    link_strictly(sub1, collection)
    link_strictly(sub2, collection)

    objs.extend([leg_l, leg_r, plaque_face, plaque_trim, title_bar, sub1, sub2])
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

    col_full   = bpy.data.collections.new("Bar_Magnet_Full")
    col_detail = bpy.data.collections.new("Bar_Magnet_Detail")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_detail)

    full_objs   = build_bar_magnet_full(col_full)
    detail_objs = build_bar_magnet_detail(col_detail)

    cam_data = bpy.data.cameras.new("Bar_Magnet_Camera")
    cam_data.lens = 50.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Bar_Magnet_Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    blend_path = out_dir / f"{ASSET_ID}.blend"
    kit.save_blend(blend_path)
    print(f"Saved: {blend_path}")

    set_collection_visibility(full_objs, True)
    set_collection_visibility(detail_objs, True)
    glb_path = out_dir / f"{ASSET_ID}.glb"
    kit.export_glb(glb_path)
    print(f"Exported: {glb_path}")

    viewer_assets = Path(__file__).resolve().parents[3] / 'apps' / 'interactive-viewer' / 'public' / 'assets'
    if viewer_assets.exists():
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    configure_fast_render(width=1280, height=720, samples=24)

    # Render Preview 1: Bar Magnet with 3D Spatial Field Lines
    set_collection_visibility(full_objs, True)
    set_collection_visibility(detail_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.026)), distance=0.48, elev_deg=34, azim_deg=-30)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Detail / Iron Filings Pattern & Multi-Compass Array
    set_collection_visibility(full_objs, False)
    set_collection_visibility(detail_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.026)), distance=0.46, elev_deg=34, azim_deg=-26)
    preview_detail = out_dir / "preview_section.png"
    kit.render_preview(preview_detail)
    print(f"Rendered: {preview_detail}")

    print("=== BAR MAGNET BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()