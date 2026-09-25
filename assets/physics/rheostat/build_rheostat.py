"""
build_rheostat.py — Laboratory Slide-Wire Rheostat (Variable Resistor & Potential Divider)
NCERT Class 10 Science Chapter 11 (Electricity), Activity 11.2, Fig 11.2, Fig 11.3.

Dual Collections:
  1. Rheostat_Full:
     - Real-world laboratory sliding rheostat with heavy cast-iron upright end brackets.
     - Glazed ceramic / porcelain insulating core tube (140mm length, 36mm diameter).
     - Tightly wound constantan / eureka resistance wire coil with polished contact track.
     - Machined brass slider guide rod and phosphor-bronze spring contact rider with black phenolic grip.
     - Three knurled brass terminal binding posts (A: fixed left, B: fixed right, C: variable slider).
     - Studio slate display plinth with gold trim.

  2. Rheostat_Section (Active Resistance Path & Current Flow Mechanism):
     - Annotated electro-mechanical view demonstrating Ohm's law and resistivity:
       * Active resistance path highlighted from Terminal A through effective length l to Slider C.
       * Luminescent cyan current flow vectors traversing the active coil section and slider bar.
       * Dimension caliper measuring effective conductor length l.
       * Educational plaque mounted on brass stanchions:
         - "SLIDE-WIRE RHEOSTAT (VARIABLE RESISTOR)"
         - "Resistance Law: R = rho * (l / A) => R proportional to length l"
         - "Modes: Variable Resistor (Terminals A & C) / Potential Divider (Terminals A, B, & C)"
         - "Wire Material: Constantan / Eureka (low temperature coefficient of resistance)"
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'rheostat'

# Calibrated Laboratory Palette
COLOR_CERAMIC       = (0.92, 0.90, 0.86)     # Glazed porcelain insulating cylinder
COLOR_WIRE_COIL     = (0.72, 0.46, 0.28)     # Oxidized constantan/nichrome resistance wire
COLOR_WIRE_ACTIVE   = (0.20, 0.85, 1.00)     # Glowing cyan active resistance current path
COLOR_BRACKET       = (0.16, 0.17, 0.19)     # Dark cast-iron upright end brackets
COLOR_BRASS         = (0.86, 0.70, 0.28)     # Machined brass slider rod & terminal posts
COLOR_KNOB          = (0.08, 0.08, 0.10)     # Molded black phenolic slider handle
COLOR_RIDER_SPRING  = (0.84, 0.65, 0.30)     # Phosphor-bronze contact rider
COLOR_DIMENSION     = (1.00, 0.60, 0.15)     # Amber dimension line for active length l
COLOR_PLINTH        = (0.12, 0.14, 0.18)     # Studio slate pedestal
COLOR_TRIM          = (0.95, 0.65, 0.15)     # Educational badge gold accent

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

def build_shared_plinth(prefix, collection):
    """Builds the stable studio plinth shared between both collections."""
    objs = []
    mat_plinth = kit.add_material(f"{prefix}_plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_trim   = kit.add_material(f"{prefix}_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    plinth = kit.primitive_object(f"{prefix}_plinth", "cube", mat_plinth,
                                 size=(0.300, 0.160, 0.016),
                                 location=(0.0, 0.0, 0.008))
    link_strictly(plinth, collection)

    rim = kit.primitive_object(f"{prefix}_plinth_rim", "cube", mat_trim,
                               size=(0.306, 0.166, 0.003),
                               location=(0.0, 0.0, 0.0015))
    link_strictly(rim, collection)
    objs.extend([plinth, rim])
    return objs

def build_rheostat_core(prefix, collection, mat_ceramic, mat_wire, mat_bracket, mat_brass, mat_knob, mat_spring, slider_x=0.015, z_base=0.016):
    """
    Constructs the mechanical assembly of the sliding rheostat:
    Brackets, ceramic cylinder, resistance wire winding, slider rod, rider, and 3 terminals.
    """
    objs = []
    tube_len = 0.140
    tube_r = 0.018
    z_center = z_base + 0.026

    # 1. Cast-iron Upright End Brackets (Left at -X, Right at +X)
    for sign, name in [(-1.0, "left"), (1.0, "right")]:
        bx = sign * (tube_len * 0.5 + 0.007)
        # Upright plate
        upright = kit.primitive_object(f"{prefix}_bracket_{name}", "cube", mat_bracket,
                                      size=(0.014, 0.052, 0.062),
                                      location=(bx, 0.0, z_center + 0.006))
        # Foot mounting base
        foot = kit.primitive_object(f"{prefix}_foot_{name}", "cube", mat_bracket,
                                   size=(0.020, 0.058, 0.008),
                                   location=(bx, 0.0, z_base + 0.004))
        link_strictly(upright, collection)
        link_strictly(foot, collection)
        objs.extend([upright, foot])

    # 2. Porcelain Ceramic Cylinder Core Tube
    core = kit.primitive_object(f"{prefix}_ceramic_core", "cylinder", mat_ceramic,
                               size=(tube_r * 2, tube_r * 2, tube_len),
                               location=(0.0, 0.0, z_center),
                               rotation_euler=(0.0, math.pi / 2, 0.0))
    link_strictly(core, collection)
    objs.append(core)

    # 3. Constantan / Nichrome Resistance Wire Coil Ribs (24 closely spaced turns)
    num_coils = 24
    coil_span = tube_len - 0.018
    for i in range(num_coils):
        frac = i / (num_coils - 1)
        cx = -coil_span * 0.5 + frac * coil_span
        ring = kit.primitive_object(f"{prefix}_wire_turn_{i}", "cylinder", mat_wire,
                                    size=(tube_r * 2 + 0.0016, tube_r * 2 + 0.0016, 0.0045),
                                    location=(cx, 0.0, z_center),
                                    rotation_euler=(0.0, math.pi / 2, 0.0))
        link_strictly(ring, collection)
        objs.append(ring)

    # 4. Top Square Slider Guide Bar (Machined Brass)
    z_bar = z_center + tube_r + 0.011
    bar_len = tube_len + 0.016
    bar = kit.primitive_object(f"{prefix}_slider_bar", "cube", mat_brass,
                              size=(bar_len, 0.006, 0.006),
                              location=(0.0, 0.0, z_bar))
    link_strictly(bar, collection)
    objs.append(bar)

    # 5. Moveable Slider Rider Contact & Insulated Handle Knob
    # Positioned along the bar at slider_x
    rider = kit.primitive_object(f"{prefix}_rider_block", "cube", mat_spring,
                                size=(0.018, 0.018, 0.012),
                                location=(slider_x, 0.0, z_bar))
    # Downward spring wiper touching the wire track
    wiper = kit.primitive_object(f"{prefix}_wiper_contact", "cube", mat_spring,
                                 size=(0.006, 0.008, 0.010),
                                 location=(slider_x, 0.0, z_center + tube_r + 0.005))
    # Phenolic grip handle knob
    knob = kit.primitive_object(f"{prefix}_slider_knob", "cylinder", mat_knob,
                                size=(0.014, 0.014, 0.018),
                                location=(slider_x, 0.0, z_bar + 0.014))
    for r_part in [rider, wiper, knob]:
        link_strictly(r_part, collection)
    objs.extend([rider, wiper, knob])

    # 6. Three Knurled Brass Binding Post Terminals:
    # Terminal A (Fixed Bottom Left: x = -tube_len/2 - 0.007, y = -0.024)
    # Terminal B (Fixed Bottom Right: x = tube_len/2 + 0.007, y = -0.024)
    # Terminal C (Variable Slider Top Left: x = -tube_len/2 - 0.007, y = 0.0, z = z_bar)
    term_a = kit.primitive_object(f"{prefix}_term_A", "cylinder", mat_brass,
                                 size=(0.009, 0.009, 0.014),
                                 location=(-tube_len * 0.5 - 0.007, -0.022, z_base + 0.015))
    term_b = kit.primitive_object(f"{prefix}_term_B", "cylinder", mat_brass,
                                 size=(0.009, 0.009, 0.014),
                                 location=(tube_len * 0.5 + 0.007, -0.022, z_base + 0.015))
    term_c = kit.primitive_object(f"{prefix}_term_C", "cylinder", mat_brass,
                                 size=(0.009, 0.009, 0.014),
                                 location=(-tube_len * 0.5 - 0.007, 0.0, z_bar + 0.010))
    for t in [term_a, term_b, term_c]:
        link_strictly(t, collection)
    objs.extend([term_a, term_b, term_c])

    return objs, {
        "x_left": -coil_span * 0.5,
        "x_slider": slider_x,
        "z_center": z_center,
        "z_bar": z_bar,
        "tube_r": tube_r,
        "term_a_pos": Vector((-tube_len * 0.5 - 0.007, -0.022, z_base + 0.015)),
        "term_c_pos": Vector((-tube_len * 0.5 - 0.007, 0.0, z_bar + 0.010)),
        "wiper_pos": Vector((slider_x, 0.0, z_center + tube_r))
    }

def build_rheostat_full(collection):
    """Builds the complete laboratory slide-wire rheostat."""
    objs = []
    prefix = "rheo_full"
    plinth_objs = build_shared_plinth(prefix, collection)
    objs.extend(plinth_objs)

    mat_ceramic = kit.add_material(f"{prefix}_ceramic", COLOR_CERAMIC, metallic=0.05, roughness=0.60)
    mat_wire    = kit.add_material(f"{prefix}_wire", COLOR_WIRE_COIL, metallic=0.85, roughness=0.35)
    mat_bracket = kit.add_material(f"{prefix}_bracket", COLOR_BRACKET, metallic=0.70, roughness=0.50)
    mat_brass   = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_knob    = kit.add_material(f"{prefix}_knob", COLOR_KNOB, metallic=0.10, roughness=0.40)
    mat_spring  = kit.add_machined_metal_material(f"{prefix}_spring", COLOR_RIDER_SPRING, metallic=0.90, roughness=0.25)

    mech_objs, _ = build_rheostat_core(prefix, collection, mat_ceramic, mat_wire, mat_bracket, mat_brass, mat_knob, mat_spring, slider_x=0.018)
    objs.extend(mech_objs)
    return objs

def build_rheostat_section(collection):
    """
    Builds the annotated active resistance circuit path:
    Active length l from Terminal A to Slider C, current flow lines, and educational plaque.
    """
    objs = []
    prefix = "rheo_sec"
    plinth_objs = build_shared_plinth(prefix, collection)
    objs.extend(plinth_objs)

    mat_ceramic = kit.add_material(f"{prefix}_ceramic", COLOR_CERAMIC, metallic=0.05, roughness=0.60)
    mat_wire    = kit.add_material(f"{prefix}_wire", COLOR_WIRE_COIL, metallic=0.85, roughness=0.35)
    mat_active  = create_emissive_mat(f"{prefix}_active_wire", COLOR_WIRE_ACTIVE, strength=14.0)
    mat_bracket = kit.add_material(f"{prefix}_bracket", COLOR_BRACKET, metallic=0.70, roughness=0.50)
    mat_brass   = kit.add_machined_metal_material(f"{prefix}_brass", COLOR_BRASS, metallic=0.92, roughness=0.25)
    mat_knob    = kit.add_material(f"{prefix}_knob", COLOR_KNOB, metallic=0.10, roughness=0.40)
    mat_spring  = kit.add_machined_metal_material(f"{prefix}_spring", COLOR_RIDER_SPRING, metallic=0.90, roughness=0.25)
    mat_dim     = create_emissive_mat(f"{prefix}_dimension", COLOR_DIMENSION, strength=12.0)
    mat_badge   = kit.add_material(f"{prefix}_badge_bg", COLOR_PLINTH, metallic=0.10, roughness=0.50)
    mat_trim    = kit.add_material(f"{prefix}_badge_trim", COLOR_TRIM, metallic=0.20, roughness=0.35)

    slider_x = 0.020
    mech_objs, geo = build_rheostat_core(prefix, collection, mat_ceramic, mat_wire, mat_bracket, mat_brass, mat_knob, mat_spring, slider_x=slider_x)
    objs.extend(mech_objs)

    # 1. Highlighted Active Resistance Path (From x_left to slider_x along top track)
    active_seg = create_cylinder_segment(f"{prefix}_active_track",
                                         Vector((geo["x_left"], 0.0, geo["z_center"] + geo["tube_r"] + 0.001)),
                                         Vector((geo["x_slider"], 0.0, geo["z_center"] + geo["tube_r"] + 0.001)),
                                         0.0018, mat_active, collection)
    # Current flow up through wiper into brass rod and along rod back to Terminal C
    flow_up = create_cylinder_segment(f"{prefix}_flow_up",
                                      Vector((geo["x_slider"], 0.0, geo["z_center"] + geo["tube_r"] + 0.001)),
                                      Vector((geo["x_slider"], 0.0, geo["z_bar"])),
                                      0.0014, mat_active, collection)
    flow_bar = create_cylinder_segment(f"{prefix}_flow_bar",
                                       Vector((geo["x_slider"], 0.0, geo["z_bar"])),
                                       Vector((geo["term_c_pos"].x, 0.0, geo["z_bar"])),
                                       0.0014, mat_active, collection)
    objs.extend([active_seg, flow_up, flow_bar])

    # 2. Dimension Caliper Line for Effective Length l
    dim_z = geo["z_center"] + geo["tube_r"] + 0.028
    dim_line = create_cylinder_segment(f"{prefix}_dim_line",
                                       Vector((geo["x_left"], 0.0, dim_z)),
                                       Vector((geo["x_slider"], 0.0, dim_z)),
                                       0.0009, mat_dim, collection)
    # End tick marks on dimension line
    tick_l = kit.primitive_object(f"{prefix}_dim_tick_l", "cube", mat_dim,
                                  size=(0.001, 0.002, 0.006),
                                  location=(geo["x_left"], 0.0, dim_z))
    tick_r = kit.primitive_object(f"{prefix}_dim_tick_r", "cube", mat_dim,
                                  size=(0.001, 0.002, 0.006),
                                  location=(geo["x_slider"], 0.0, dim_z))
    link_strictly(tick_l, collection)
    link_strictly(tick_r, collection)
    # Label badge 'l'
    badge_l = kit.primitive_object(f"{prefix}_badge_l", "cube", mat_dim,
                                   size=(0.010, 0.003, 0.007),
                                   location=((geo["x_left"] + geo["x_slider"]) * 0.5, 0.0, dim_z + 0.004))
    link_strictly(badge_l, collection)
    objs.extend([dim_line, tick_l, tick_r, badge_l])

    # 3. Educational Plaque Standing on Slate Plinth (Front Stanchions)
    plaque_w, plaque_h, plaque_th = 0.180, 0.038, 0.004
    plaque_y = -0.068
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
    plaque_trim = kit.primitive_object(f"{prefix}_plaque_trim", "cube", mat_trim,
                                       size=(plaque_w + 0.004, plaque_th + 0.001, 0.002),
                                       location=trim_pos,
                                       rotation_euler=tilt_rot)
    link_strictly(plaque_trim, collection)

    # Title Bar: "SLIDE-WIRE RHEOSTAT (VARIABLE RESISTOR)"
    bar_pos = local_plaque_pt(0.0, 0.010)
    title_bar = kit.primitive_object(f"{prefix}_title_bar", "cube", mat_trim,
                                     size=(plaque_w * 0.88, 0.001, 0.005),
                                     location=bar_pos,
                                     rotation_euler=tilt_rot)
    link_strictly(title_bar, collection)

    # Sub-bars:
    # 1. Resistance Law: R = rho * (l / A) => R proportional to length l
    sub1_pos = local_plaque_pt(0.0, 0.002)
    sub1 = kit.primitive_object(f"{prefix}_sub1", "cube", mat_active,
                                size=(plaque_w * 0.76, 0.001, 0.0035),
                                location=sub1_pos,
                                rotation_euler=tilt_rot)
    # 2. Modes: 2-Terminals (Variable Resistor) / 3-Terminals (Potential Divider)
    sub2_pos = local_plaque_pt(0.0, -0.006)
    sub2 = kit.primitive_object(f"{prefix}_sub2", "cube", mat_dim,
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

    col_full = bpy.data.collections.new("Rheostat_Full")
    col_sec  = bpy.data.collections.new("Rheostat_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_rheostat_full(col_full)
    sec_objs  = build_rheostat_section(col_sec)

    cam_data = bpy.data.cameras.new("Rheostat_Camera")
    cam_data.lens = 48.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Rheostat_Camera", cam_data)
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
        target_path = viewer_assets / f"{ASSET_ID}.glb"
        shutil.copy2(glb_path, target_path)
        print(f"Synced GLB to: {target_path}")

    configure_fast_render(width=1280, height=720, samples=24)

    # Render Preview 1: Rheostat Full Apparatus
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, 0.0, 0.042)), distance=0.45, elev_deg=28, azim_deg=-32)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section / Active Resistance Path
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.010, 0.042)), distance=0.42, elev_deg=30, azim_deg=-28)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== RHEOSTAT BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
