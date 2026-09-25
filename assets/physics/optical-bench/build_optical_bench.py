"""
build_optical_bench.py — Dual-Rail Laboratory Optical Bench & Lens Formula Experiment
NCERT Class 10 Science Chapter 10 (Light) & Class 12 Physics Experiment (Focal length of convex lens by u-v method).

Dual Collections:
  1. Optical_Bench_Full:
     - 1.0-meter precision dual stainless-steel cylindrical guide rails (dia 18mm) on cast-iron end legs with knurled brass leveling screws.
     - Central inlaid satin aluminum metric millimeter rule with major centimeter graduations.
     - Three precision sliding rider saddles with brass clamping thumbscrews and vernier index pointers:
       * Rider 1 (x = -0.35m): Object pin upright with sharp hardened steel needle and red lacquer tip.
       * Rider 2 (x = 0.00m): Lens holder with turned brass bezel and biconvex crown glass lens (f = 17.5cm).
       * Rider 3 (x = +0.35m): Projection screen carrier with matte white diffusion face and real inverted image indicator.
  2. Optical_Bench_Section:
     - Longitudinal mechanical cutaway of the lens rider saddle displaying machined V-groove rail bearings, internal brass locking shoe, and vernier index plate.
     - 3D ray-tracing demonstration showing the 3 canonical rays (parallel, optical center, focal) from object tip through lens to screen forming a real, inverted image at u = 2f, v = 2f.
     - Principal foci locator rings at F1, 2F1, F2, 2F2 with optical axis line.
     - Dimension calipers for object distance u, image distance v, and focal length f.
     - Forward-angled laboratory educational plaque with lens formula and magnification relations.
"""

import sys, math, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

ASSET_ID = 'optical-bench'

# Laboratory Palette
COLOR_STEEL_RAIL   = (0.86, 0.88, 0.90)     # Polished stainless steel rails & posts
COLOR_CAST_IRON    = (0.05, 0.05, 0.07)     # Black wrinkle cast iron feet & rider bodies
COLOR_BRASS        = (0.86, 0.68, 0.22)     # Turned brass hardware, screws, bezels, verniers
COLOR_SCALE_BAR    = (0.82, 0.84, 0.86)     # Satin aluminum millimeter ruler
COLOR_SCALE_TICKS  = (0.05, 0.05, 0.06)     # High-contrast engraved tick marks
COLOR_GLASS        = (0.95, 0.98, 1.00)     # Crown glass biconvex lens (n = 1.52)
COLOR_WHITE_SCREEN = (0.94, 0.94, 0.94)     # Matte white projection screen
COLOR_PIN_STEEL    = (0.90, 0.92, 0.94)     # Steel needle shaft
COLOR_PIN_TIP      = (0.95, 0.12, 0.12)     # Bright vermilion red pin tip
COLOR_PLINTH       = (0.06, 0.07, 0.09)     # Studio pedestal / slate bench
COLOR_RAY_REAL     = (0.10, 0.95, 0.45)     # 532nm emerald laser ray (strength 14.0)
COLOR_AXIS         = (0.35, 0.50, 0.65)     # Principal optical axis reference line
COLOR_FOCAL_AMBER  = (1.00, 0.70, 0.15)     # Glowing amber focal locator rings

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
    mid = (v1 + v2) / 2.0
    rot = diff.to_track_quat('Z', 'Y').to_euler()

    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius,
        depth=length,
        location=mid,
        rotation=rot
    )
    cyl = bpy.context.active_object
    cyl.name = name
    if cyl.data.materials:
        cyl.data.materials[0] = mat
    else:
        cyl.data.materials.append(mat)
    link_strictly(cyl, collection)
    return cyl

# -----------------------------------------------------------------------------
# BUILD OPTICAL BENCH FULL
# -----------------------------------------------------------------------------
def build_optical_bench_full(collection):
    steel = kit.add_machined_metal_material("bench-steel-rail", COLOR_STEEL_RAIL, metallic=0.98, roughness=0.14)
    cast_iron = kit.add_material("bench-cast-iron", COLOR_CAST_IRON, metallic=0.15, roughness=0.75)
    brass = kit.add_machined_metal_material("bench-brass-hw", COLOR_BRASS, metallic=0.92, roughness=0.22)
    scale_mat = kit.add_machined_metal_material("bench-scale-bar", COLOR_SCALE_BAR, metallic=0.35, roughness=0.40)
    tick_mat = kit.add_material("bench-scale-ticks", COLOR_SCALE_TICKS, metallic=0.0, roughness=0.8)
    glass = kit.add_glass_material("bench-lens-glass", COLOR_GLASS, ior=1.52, roughness=0.015)
    white_screen = kit.add_material("bench-white-screen", COLOR_WHITE_SCREEN, metallic=0.0, roughness=0.92)
    pin_steel = kit.add_machined_metal_material("bench-pin-steel", COLOR_PIN_STEEL, metallic=0.95, roughness=0.15)
    pin_red = kit.add_material("bench-pin-red", COLOR_PIN_TIP, metallic=0.05, roughness=0.25)
    pin_inverted = kit.add_material("bench-pin-inverted", (0.15, 0.75, 0.35), metallic=0.05, roughness=0.25)

    rail_len = 1.04
    rail_radius = 0.009
    rail_y = 0.035
    rail_z = 0.050

    # 1. Dual Stainless Steel Guide Rails (X axis)
    for i, y_sign in enumerate([-1, 1]):
        rail = kit.primitive_object(
            f"{ASSET_ID}_Rail_{i}", "cylinder", steel,
            size=(rail_radius*2, rail_radius*2, rail_len),
            location=(0.0, y_sign * rail_y, rail_z),
            rotation_euler=(0.0, math.pi / 2, 0.0)
        )
        link_strictly(rail, collection)

    # 2. Central Metric Scale Strip
    scale_strip = kit.primitive_object(
        f"{ASSET_ID}_Scale_Strip", "cube", scale_mat,
        size=(1.00, 0.026, 0.004),
        location=(0.0, 0.0, rail_z + 0.001)
    )
    link_strictly(scale_strip, collection)

    # Scale graduations: centimeter marks along X
    for cm in range(-50, 51, 5):
        x_pos = cm * 0.01
        is_major = (cm % 10 == 0)
        tick_len = 0.020 if is_major else 0.012
        tick = kit.primitive_object(
            f"{ASSET_ID}_Scale_Tick_{cm}", "cube", tick_mat,
            size=(0.0015 if is_major else 0.0008, tick_len, 0.0008),
            location=(x_pos, 0.0, rail_z + 0.0035)
        )
        link_strictly(tick, collection)

    # 3. Cast Iron End Support Feet (Left: -0.52m, Right: +0.52m)
    for side_idx, side_x in enumerate([-0.52, 0.52]):
        # Main cross-beam
        beam = kit.primitive_object(
            f"{ASSET_ID}_Foot_Beam_{side_idx}", "cube", cast_iron,
            size=(0.045, 0.160, 0.040),
            location=(side_x, 0.0, 0.035)
        )
        link_strictly(beam, collection)

        # Flanged leg outriggers
        for leg_y in [-0.065, 0.065]:
            leg = kit.primitive_object(
                f"{ASSET_ID}_Leg_Outrigger_{side_idx}_{leg_y}", "cube", cast_iron,
                size=(0.055, 0.032, 0.025),
                location=(side_x, leg_y, 0.018)
            )
            link_strictly(leg, collection)

            # Knurled brass leveling screw
            screw = kit.primitive_object(
                f"{ASSET_ID}_Level_Screw_{side_idx}_{leg_y}", "cylinder", brass,
                size=(0.022, 0.022, 0.018),
                location=(side_x, leg_y, 0.012)
            )
            link_strictly(screw, collection)

            # Rubber foot pad
            pad = kit.primitive_object(
                f"{ASSET_ID}_Foot_Pad_{side_idx}_{leg_y}", "cylinder", cast_iron,
                size=(0.026, 0.026, 0.004),
                location=(side_x, leg_y, 0.002)
            )
            link_strictly(pad, collection)

        # Chrome/brass end caps on rails
        for yr in [-rail_y, rail_y]:
            cap = kit.primitive_object(
                f"{ASSET_ID}_Rail_Cap_{side_idx}_{yr}", "cylinder", brass,
                size=(0.020, 0.020, 0.006),
                location=(side_x + (0.022 if side_x > 0 else -0.022), yr, rail_z),
                rotation_euler=(0.0, math.pi / 2, 0.0)
            )
            link_strictly(cap, collection)

    # 4. Sliding saddle builder
    def make_saddle(name, x_pos):
        parts = []
        saddle = kit.primitive_object(
            f"{name}_Saddle", "cube", cast_iron,
            size=(0.068, 0.125, 0.036),
            location=(x_pos, 0.0, rail_z + 0.010)
        )
        parts.append(saddle)

        vernier = kit.primitive_object(
            f"{name}_Vernier_Plate", "cube", brass,
            size=(0.038, 0.004, 0.024),
            location=(x_pos, -0.064, rail_z + 0.010)
        )
        parts.append(vernier)

        pointer = kit.primitive_object(
            f"{name}_Pointer", "cube", tick_mat,
            size=(0.0015, 0.001, 0.020),
            location=(x_pos, -0.0665, rail_z + 0.010)
        )
        parts.append(pointer)

        clamp_knob = kit.primitive_object(
            f"{name}_Clamp_Knob", "cylinder", brass,
            size=(0.018, 0.018, 0.014),
            location=(x_pos, -0.073, rail_z + 0.010),
            rotation_euler=(math.pi / 2, 0.0, 0.0)
        )
        parts.append(clamp_knob)

        boss = kit.primitive_object(
            f"{name}_Socket_Boss", "cylinder", brass,
            size=(0.026, 0.026, 0.024),
            location=(x_pos, 0.0, rail_z + 0.034)
        )
        parts.append(boss)

        collar = kit.primitive_object(
            f"{name}_Collar", "cylinder", brass,
            size=(0.022, 0.022, 0.010),
            location=(x_pos, 0.0, rail_z + 0.050)
        )
        parts.append(collar)

        trans_knob = kit.primitive_object(
            f"{name}_Trans_Knob", "cylinder", brass,
            size=(0.014, 0.014, 0.012),
            location=(x_pos, 0.068, rail_z + 0.020),
            rotation_euler=(math.pi / 2, 0.0, 0.0)
        )
        parts.append(trans_knob)

        for p in parts:
            link_strictly(p, collection)
        return parts

    # --- Rider 1: Object Pin Upright (at x = -0.35m) ---
    make_saddle(f"{ASSET_ID}_Rider_Obj", -0.35)
    obj_post = kit.primitive_object(
        f"{ASSET_ID}_Obj_Post", "cylinder", steel,
        size=(0.012, 0.012, 0.120),
        location=(-0.35, 0.0, 0.135)
    )
    link_strictly(obj_post, collection)
    obj_chuck = kit.primitive_object(
        f"{ASSET_ID}_Obj_Chuck", "cylinder", brass,
        size=(0.018, 0.018, 0.025),
        location=(-0.35, 0.0, 0.185)
    )
    link_strictly(obj_chuck, collection)
    obj_pin_stem = kit.primitive_object(
        f"{ASSET_ID}_Obj_Pin_Stem", "cylinder", pin_steel,
        size=(0.0035, 0.0035, 0.040),
        location=(-0.35, 0.0, 0.210)
    )
    link_strictly(obj_pin_stem, collection)
    obj_pin_tip = kit.primitive_object(
        f"{ASSET_ID}_Obj_Pin_Tip", "cone", pin_red,
        size=(0.0045, 0.0045, 0.014),
        location=(-0.35, 0.0, 0.235)
    )
    link_strictly(obj_pin_tip, collection)

    # --- Rider 2: Convex Lens Upright (at x = 0.00m) ---
    make_saddle(f"{ASSET_ID}_Rider_Lens", 0.00)
    lens_post = kit.primitive_object(
        f"{ASSET_ID}_Lens_Post", "cylinder", steel,
        size=(0.012, 0.012, 0.100),
        location=(0.00, 0.0, 0.125)
    )
    link_strictly(lens_post, collection)
    lens_bracket = kit.primitive_object(
        f"{ASSET_ID}_Lens_Bracket", "cube", brass,
        size=(0.016, 0.028, 0.018),
        location=(0.00, 0.0, 0.165)
    )
    link_strictly(lens_bracket, collection)
    lens_ring = kit.primitive_object(
        f"{ASSET_ID}_Lens_Bezel", "cylinder", brass,
        size=(0.082, 0.082, 0.012),
        location=(0.00, 0.0, 0.200),
        rotation_euler=(0.0, math.pi / 2, 0.0)
    )
    link_strictly(lens_ring, collection)
    lens_screw = kit.primitive_object(
        f"{ASSET_ID}_Lens_ThumbScrew", "cylinder", brass,
        size=(0.012, 0.012, 0.012),
        location=(0.00, 0.0, 0.246)
    )
    link_strictly(lens_screw, collection)
    lens_glass = kit.primitive_object(
        f"{ASSET_ID}_Lens_Glass", "uv_sphere", glass,
        size=(0.076, 0.076, 0.076),
        location=(0.00, 0.0, 0.200)
    )
    lens_glass.scale = (0.16, 1.0, 1.0)
    link_strictly(lens_glass, collection)

    # --- Rider 3: Projection Screen Carrier (at x = +0.35m) ---
    make_saddle(f"{ASSET_ID}_Rider_Screen", 0.35)
    screen_post = kit.primitive_object(
        f"{ASSET_ID}_Screen_Post", "cylinder", steel,
        size=(0.012, 0.012, 0.100),
        location=(0.35, 0.0, 0.125)
    )
    link_strictly(screen_post, collection)
    screen_frame = kit.primitive_object(
        f"{ASSET_ID}_Screen_Frame", "cube", cast_iron,
        size=(0.010, 0.120, 0.120),
        location=(0.35, 0.0, 0.200)
    )
    link_strictly(screen_frame, collection)
    screen_face = kit.primitive_object(
        f"{ASSET_ID}_Screen_Face", "cube", white_screen,
        size=(0.004, 0.108, 0.108),
        location=(0.344, 0.0, 0.200)
    )
    link_strictly(screen_face, collection)
    cross_h = kit.primitive_object(
        f"{ASSET_ID}_Screen_Cross_H", "cube", tick_mat,
        size=(0.001, 0.080, 0.001),
        location=(0.3418, 0.0, 0.200)
    )
    link_strictly(cross_h, collection)
    cross_v = kit.primitive_object(
        f"{ASSET_ID}_Screen_Cross_V", "cube", tick_mat,
        size=(0.001, 0.001, 0.080),
        location=(0.3418, 0.0, 0.200)
    )
    link_strictly(cross_v, collection)
    inv_tip = kit.primitive_object(
        f"{ASSET_ID}_Screen_Inv_Image", "cone", pin_inverted,
        size=(0.005, 0.005, 0.018),
        location=(0.3415, 0.0, 0.165),
        rotation_euler=(0.0, 0.0, math.pi)
    )
    link_strictly(inv_tip, collection)

    print("Built Optical_Bench_Full successfully.")

# -----------------------------------------------------------------------------
# BUILD OPTICAL BENCH SECTION (Optics Ray Tracing & Saddle Cutaway)
# -----------------------------------------------------------------------------
def build_optical_bench_section(collection):
    steel = kit.add_machined_metal_material("sec-steel", COLOR_STEEL_RAIL, metallic=0.98, roughness=0.15)
    cast_iron = kit.add_material("sec-cast-iron", COLOR_CAST_IRON, metallic=0.15, roughness=0.75)
    cut_metal = kit.add_material("sec-cut-metal", (0.95, 0.40, 0.20), metallic=0.7, roughness=0.3)
    brass = kit.add_machined_metal_material("sec-brass", COLOR_BRASS, metallic=0.92, roughness=0.22)
    glass = kit.add_glass_material("sec-glass", COLOR_GLASS, ior=1.52, roughness=0.015)
    white_screen = kit.add_material("sec-screen", COLOR_WHITE_SCREEN, metallic=0.0, roughness=0.92)
    pin_steel = kit.add_machined_metal_material("sec-pin-steel", COLOR_PIN_STEEL, metallic=0.95, roughness=0.15)
    pin_red = kit.add_material("sec-pin-red", COLOR_PIN_TIP, metallic=0.05, roughness=0.25)
    pin_inv = kit.add_material("sec-pin-inv", (0.15, 0.75, 0.35), metallic=0.05, roughness=0.25)

    ray_mat = create_emissive_mat("sec-ray-emerald", COLOR_RAY_REAL, strength=14.0)
    axis_mat = create_emissive_mat("sec-axis-cyan", COLOR_AXIS, strength=5.0)
    focal_mat = create_emissive_mat("sec-focal-amber", COLOR_FOCAL_AMBER, strength=12.0)
    dim_mat = kit.add_material("sec-dim-brass", (0.95, 0.80, 0.25), metallic=0.9, roughness=0.2)

    rail_len = 1.04
    rail_radius = 0.009
    rail_y = 0.035
    rail_z = 0.050

    # 1. Base Bench Rails & Cast-Iron Supports
    for i, y_sign in enumerate([-1, 1]):
        rail = kit.primitive_object(
            f"Sec_Rail_{i}", "cylinder", steel,
            size=(rail_radius*2, rail_radius*2, rail_len),
            location=(0.0, y_sign * rail_y, rail_z),
            rotation_euler=(0.0, math.pi / 2, 0.0)
        )
        link_strictly(rail, collection)

    for side_idx, side_x in enumerate([-0.52, 0.52]):
        beam = kit.primitive_object(
            f"Sec_Foot_Beam_{side_idx}", "cube", cast_iron,
            size=(0.045, 0.160, 0.040),
            location=(side_x, 0.0, 0.035)
        )
        link_strictly(beam, collection)
        for leg_y in [-0.065, 0.065]:
            screw = kit.primitive_object(
                f"Sec_Level_Screw_{side_idx}_{leg_y}", "cylinder", brass,
                size=(0.022, 0.022, 0.018),
                location=(side_x, leg_y, 0.012)
            )
            link_strictly(screw, collection)

    # 2. Object Pin Assembly (at x = -0.35m, ho = +0.035m)
    obj_post = kit.primitive_object("Sec_Obj_Post", "cylinder", steel, size=(0.012, 0.012, 0.120), location=(-0.35, 0.0, 0.135))
    obj_chuck = kit.primitive_object("Sec_Obj_Chuck", "cylinder", brass, size=(0.018, 0.018, 0.025), location=(-0.35, 0.0, 0.185))
    obj_stem = kit.primitive_object("Sec_Obj_Stem", "cylinder", pin_steel, size=(0.0035, 0.0035, 0.040), location=(-0.35, 0.0, 0.210))
    obj_tip = kit.primitive_object("Sec_Obj_Tip", "cone", pin_red, size=(0.0045, 0.0045, 0.014), location=(-0.35, 0.0, 0.235))
    link_strictly(obj_post, collection)
    link_strictly(obj_chuck, collection)
    link_strictly(obj_stem, collection)
    link_strictly(obj_tip, collection)

    # 3. Lens Mount with Cutaway Saddle
    cut_saddle = kit.primitive_object(
        "Sec_Lens_Saddle_Cut", "cube", cast_iron,
        size=(0.068, 0.065, 0.036),
        location=(0.0, 0.032, rail_z + 0.010)
    )
    link_strictly(cut_saddle, collection)

    cut_section_face = kit.primitive_object(
        "Sec_Saddle_Section_Face", "cube", cut_metal,
        size=(0.066, 0.002, 0.034),
        location=(0.0, 0.001, rail_z + 0.010)
    )
    link_strictly(cut_section_face, collection)

    shoe = kit.primitive_object(
        "Sec_Locking_Shoe", "cube", brass,
        size=(0.020, 0.015, 0.012),
        location=(0.0, -0.025, rail_z + 0.012)
    )
    link_strictly(shoe, collection)

    lens_post = kit.primitive_object("Sec_Lens_Post", "cylinder", steel, size=(0.012, 0.012, 0.100), location=(0.00, 0.0, 0.125))
    lens_bracket = kit.primitive_object("Sec_Lens_Bracket", "cube", brass, size=(0.016, 0.028, 0.018), location=(0.00, 0.0, 0.165))
    lens_ring = kit.primitive_object("Sec_Lens_Bezel", "cylinder", brass, size=(0.082, 0.082, 0.012), location=(0.00, 0.0, 0.200), rotation_euler=(0.0, math.pi / 2, 0.0))
    lens_glass = kit.primitive_object("Sec_Lens_Glass", "uv_sphere", glass, size=(0.076, 0.076, 0.076), location=(0.00, 0.0, 0.200))
    lens_glass.scale = (0.16, 1.0, 1.0)
    link_strictly(lens_post, collection)
    link_strictly(lens_bracket, collection)
    link_strictly(lens_ring, collection)
    link_strictly(lens_glass, collection)

    # 4. Projection Screen Assembly at x = +0.35m
    screen_post = kit.primitive_object("Sec_Screen_Post", "cylinder", steel, size=(0.012, 0.012, 0.100), location=(0.35, 0.0, 0.125))
    screen_frame = kit.primitive_object("Sec_Screen_Frame", "cube", cast_iron, size=(0.010, 0.120, 0.120), location=(0.35, 0.0, 0.200))
    screen_face = kit.primitive_object("Sec_Screen_Face", "cube", white_screen, size=(0.004, 0.108, 0.108), location=(0.344, 0.0, 0.200))
    screen_inv_img = kit.primitive_object("Sec_Screen_Inv_Pin", "cone", pin_inv, size=(0.0045, 0.0045, 0.014), location=(0.3415, 0.0, 0.165), rotation_euler=(0.0, 0.0, math.pi))
    link_strictly(screen_post, collection)
    link_strictly(screen_frame, collection)
    link_strictly(screen_face, collection)
    link_strictly(screen_inv_img, collection)

    # 5. Ray Optics Tracing
    create_cylinder_segment("Sec_Optical_Axis", (-0.48, 0.0, 0.200), (0.48, 0.0, 0.200), 0.0016, axis_mat, collection)

    focal_points = [
        ("2F1", -0.350),
        ("F1",  -0.175),
        ("F2",  +0.175),
        ("2F2", +0.350)
    ]
    for lbl, fx in focal_points:
        ring = kit.primitive_object(
            f"Sec_Focal_Ring_{lbl}", "cylinder", focal_mat,
            size=(0.016, 0.016, 0.003),
            location=(fx, 0.0, 0.200),
            rotation_euler=(0.0, math.pi / 2, 0.0)
        )
        link_strictly(ring, collection)
        drop_rod = kit.primitive_object(
            f"Sec_Focal_Drop_{lbl}", "cylinder", brass,
            size=(0.002, 0.002, 0.146),
            location=(fx, 0.0, 0.126)
        )
        link_strictly(drop_rod, collection)

    p_obj = (-0.35, 0.0, 0.235)
    p_img = (0.344, 0.0, 0.165)
    ray_radius = 0.0018

    # Ray 1: Parallel to axis -> refracts through F2 (+0.175, 0, 0.200)
    p_lens_top = (0.0, 0.0, 0.235)
    p_f2 = (0.175, 0.0, 0.200)
    create_cylinder_segment("Sec_Ray1_A", p_obj, p_lens_top, ray_radius, ray_mat, collection)
    create_cylinder_segment("Sec_Ray1_B", p_lens_top, p_f2, ray_radius, ray_mat, collection)
    create_cylinder_segment("Sec_Ray1_C", p_f2, p_img, ray_radius, ray_mat, collection)

    # Ray 2: Straight through optical center O (0.0, 0.0, 0.200)
    p_o = (0.0, 0.0, 0.200)
    create_cylinder_segment("Sec_Ray2_A", p_obj, p_o, ray_radius, ray_mat, collection)
    create_cylinder_segment("Sec_Ray2_B", p_o, p_img, ray_radius, ray_mat, collection)

    # Ray 3: Through F1 (-0.175, 0.0, 0.200) -> emerges parallel
    p_f1 = (-0.175, 0.0, 0.200)
    p_lens_bot = (0.0, 0.0, 0.165)
    create_cylinder_segment("Sec_Ray3_A", p_obj, p_f1, ray_radius, ray_mat, collection)
    create_cylinder_segment("Sec_Ray3_B", p_f1, p_lens_bot, ray_radius, ray_mat, collection)
    create_cylinder_segment("Sec_Ray3_C", p_lens_bot, p_img, ray_radius, ray_mat, collection)

    # 6. Dimension Calipers
    create_cylinder_segment("Sec_Caliper_u", (-0.35, -0.060, 0.285), (0.0, -0.060, 0.285), 0.0015, dim_mat, collection)
    for cx in [-0.35, 0.0]:
        create_cylinder_segment(f"Sec_Caliper_u_tick_{cx}", (cx, -0.060, 0.277), (cx, -0.060, 0.293), 0.0015, dim_mat, collection)

    create_cylinder_segment("Sec_Caliper_v", (0.0, -0.060, 0.285), (0.35, -0.060, 0.285), 0.0015, dim_mat, collection)
    for cx in [0.0, 0.35]:
        create_cylinder_segment(f"Sec_Caliper_v_tick_{cx}", (cx, -0.060, 0.277), (cx, -0.060, 0.293), 0.0015, dim_mat, collection)

    create_cylinder_segment("Sec_Caliper_f", (0.0, 0.060, 0.285), (0.175, 0.060, 0.285), 0.0015, dim_mat, collection)
    for cx in [0.0, 0.175]:
        create_cylinder_segment(f"Sec_Caliper_f_tick_{cx}", (cx, 0.060, 0.277), (cx, 0.060, 0.293), 0.0015, dim_mat, collection)

    # 7. Educational Plaque
    plaque_bg = kit.add_material("sec-plaque-bg", (0.06, 0.07, 0.09), metallic=0.6, roughness=0.4)
    plaque_gold = kit.add_machined_metal_material("sec-plaque-gold", (0.95, 0.75, 0.20), metallic=0.92, roughness=0.20)

    board = kit.primitive_object(
        "Sec_Plaque_Board", "cube", plaque_bg,
        size=(0.460, 0.008, 0.095),
        location=(0.0, -0.165, 0.055),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(board, collection)

    frame = kit.primitive_object(
        "Sec_Plaque_Frame", "cube", plaque_gold,
        size=(0.470, 0.006, 0.102),
        location=(0.0, -0.166, 0.055),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(frame, collection)

    bar_title = kit.primitive_object(
        "Sec_Plaque_Bar_Title", "cube", plaque_gold,
        size=(0.400, 0.002, 0.013),
        location=(0.0, -0.161, 0.082),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_title, collection)

    bar_eq = kit.primitive_object(
        "Sec_Plaque_Bar_Eq", "cube", dim_mat,
        size=(0.340, 0.002, 0.010),
        location=(0.0, -0.163, 0.061),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_eq, collection)

    bar_sub = kit.primitive_object(
        "Sec_Plaque_Bar_Case", "cube", axis_mat,
        size=(0.380, 0.002, 0.008),
        location=(0.0, -0.165, 0.041),
        rotation_euler=(math.radians(26), 0.0, 0.0)
    )
    link_strictly(bar_sub, collection)

    for sx in [-0.17, 0.17]:
        stanchion = kit.primitive_object(
            f"Sec_Plaque_Stanchion_{sx}", "cylinder", brass,
            size=(0.009, 0.009, 0.060),
            location=(sx, -0.160, 0.030)
        )
        link_strictly(stanchion, collection)

    print("Built Optical_Bench_Section successfully.")

# -----------------------------------------------------------------------------
# CAMERA & LIGHTING (Wide Perspective View)
# -----------------------------------------------------------------------------
def setup_camera_and_lighting():
    for obj in list(bpy.data.objects):
        if obj.type in {'CAMERA', 'LIGHT'}:
            bpy.data.objects.remove(obj, do_unlink=True)

    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 38.0
    cam_data.clip_start = 0.05
    cam_data.clip_end = 50.0

    cam_obj = bpy.data.objects.new("Camera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Wide perspective 3/4 view: shows full 1.04m bench length, both end legs, and riders in 3D depth
    cam_obj.location = Vector((-0.28, -1.22, 0.52))
    direction = Vector((0.0, 0.0, 0.16)) - cam_obj.location
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    # Balanced Studio Lighting Rig
    def make_light(name, ltype, pos, power, size=0.6):
        ldata = bpy.data.lights.new(name=name, type=ltype)
        ldata.energy = power
        if ltype == 'AREA':
            ldata.size = size
            ldata.shape = 'RECTANGLE'
            ldata.size_y = size * 0.5
        lobj = bpy.data.objects.new(name=name, object_data=ldata)
        lobj.location = pos
        bpy.context.scene.collection.objects.link(lobj)
        return lobj

    make_light("Key_Left", "AREA", (-0.50, -1.00, 0.70), 120.0, 0.8)
    make_light("Key_Right", "AREA", (0.50, -1.00, 0.70), 120.0, 0.8)
    make_light("Fill_Center", "AREA", (0.0, -0.80, 0.50), 70.0, 1.2)
    make_light("Top_Rim", "AREA", (0.0, 0.40, 0.85), 110.0, 1.4)

# -----------------------------------------------------------------------------
# MAIN PIPELINE
# -----------------------------------------------------------------------------
def main():
    kit.reset_scene()
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")

    full_col = bpy.data.collections.new("Optical_Bench_Full")
    sec_col  = bpy.data.collections.new("Optical_Bench_Section")
    bpy.context.scene.collection.children.link(full_col)
    bpy.context.scene.collection.children.link(sec_col)

    build_optical_bench_full(full_col)
    build_optical_bench_section(sec_col)
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

    # Render Preview 1: Optical_Bench_Full
    kit.configure_render(width=1280, height=720, samples=28)
    kit.render_preview(out_dir / "preview.png")

    # Render Preview 2: Optical_Bench_Section
    full_col.hide_viewport = True
    full_col.hide_render = True
    sec_col.hide_viewport = False
    sec_col.hide_render = False
    kit.render_preview(out_dir / "preview_section.png")

    print(f"=== {ASSET_ID.upper()} BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()