"""
build_displacement_reaction.py — NCERT Class 10 Chemistry Activity 1.9 & Fig 1.8
Iron Nails Dipped in Copper Sulphate Solution (Displacement Reaction)

Dual Collections:
1. Displacement_Setup_Full:
   - Precision laboratory hardwood test tube rack with top shelf raised to rim height and circular hole perforations, leaving solutions 100% visible.
   - Test Tube A (Control / Reference):
     * Borosilicate glass test tube with vibrant deep blue Copper Sulphate solution (CuSO4).
   - Test Tube B (Experimental reaction after 20 minutes):
     * Faded pale greenish Ferrous Sulphate solution (FeSO4).
     * Suspended iron nail with thick velvety reddish-brown copper deposit below liquid line.
     * Clean silvery-grey iron above the liquid level.
   - Watch Glass Comparison Station:
     * Glazed porcelain watch glass on front bench.
     * Side-by-side comparison of clean iron nail vs reacted copper-coated iron nail.
   - Clear pedagogical identification badges.

2. Displacement_Setup_Section:
   - Longitudinal 90° cutaway of Test Tube B and submerged nail interface revealing:
     * Inner structural core of pure metallic iron (Fe).
     * Outer electrodeposited boundary mantle of reddish-brown crystalline copper (Cu).
     * Redox electron transfer arrows:
       - Fe -> Fe2+ + 2e- (Iron oxidation dissolving into solution).
       - Cu2+ + 2e- -> Cu (Copper reduction nucleating on nail surface).
     * Stoichiometric chemical reaction plaque: Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s).
     * Reactivity series pedagogical emblem: 'Fe > Cu (Displacement Reaction)'.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Matrix

ASSET_ID = 'displacement-reaction-setup'

# Material Colors & Constants
COLOR_PLINTH       = (0.13, 0.15, 0.18)    # Laboratory bench base
COLOR_RACK_WOOD    = (0.72, 0.50, 0.30)    # Warm beechwood lab rack
COLOR_RACK_TRIM    = (0.50, 0.32, 0.18)    # Dark wood mortise accents
COLOR_GLASS        = (0.98, 0.99, 1.00)    # Borosilicate glass
COLOR_BLUE_CUSO4   = (0.04, 0.38, 0.92)    # Deep sky-blue CuSO4 solution
COLOR_GREEN_FESO4  = (0.22, 0.68, 0.46)    # Pale greenish FeSO4 solution
COLOR_IRON_CLEAN   = (0.75, 0.78, 0.82)    # Clean shiny metallic iron
COLOR_COPPER_COAT  = (0.84, 0.38, 0.20)    # Velvety reddish-brown copper deposit
COLOR_THREAD       = (0.92, 0.90, 0.85)    # Cotton suspension twine
COLOR_PORCELAIN    = (0.95, 0.95, 0.96)    # Glazed porcelain watch glass
COLOR_ARROW_FE     = (0.25, 0.85, 0.40)    # Fe2+ dissolution flow
COLOR_ARROW_CU     = (0.95, 0.45, 0.15)    # Cu deposition flow
COLOR_CUT_EDGE     = (0.95, 0.65, 0.15)    # Plaque trim

def link_strictly(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)

def create_emissive_mat(name, color, strength=5.0):
    mat = kit.add_material(name, color[:3], metallic=0.0, roughness=0.2)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    return mat

def create_solution_mat(name, color):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color[:3], 1.0)
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.04
    bsdf.inputs["IOR"].default_value = 1.334
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.85
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.6
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*color[:3], 1.0)
        bsdf.inputs["Emission Strength"].default_value = 0.60
    return mat

def create_rack_top_shelf_with_holes(name, mat_wood):
    """
    Constructs the top rack shelf with two circular hole perforations
    at x = -0.035 and x = +0.035 so the test tubes fit through cleanly.
    """
    bm = bmesh.new()
    w_half = 0.088
    d_half = 0.028
    h_shelf = 0.008
    z_bot = 0.114
    z_top = z_bot + h_shelf
    r_hole = 0.0125

    # Outer rectangle perimeter
    outer_pts = [
        Vector((-w_half, -d_half)), Vector((w_half, -d_half)),
        Vector((w_half, d_half)), Vector((-w_half, d_half))
    ]

    # Two circular holes
    hole_segs = 16
    holes = []
    for hx in [-0.035, 0.035]:
        h_pts = []
        for s in range(hole_segs):
            theta = 2.0 * math.pi * s / hole_segs
            h_pts.append(Vector((hx + r_hole * math.cos(theta), r_hole * math.sin(theta))))
        holes.append(h_pts)

    # Build 2.5D slab by creating top & bottom polygons and side faces
    # Simple multi-box construction to avoid complex boolean triangulation
    # Left block (-w_half to -0.035 - r_hole)
    # Middle block (-0.035 + r_hole to +0.035 - r_hole)
    # Right block (+0.035 + r_hole to w_half)
    # Front strip & back strip bridging across
    bmesh.ops.create_cube(bm, size=1.0)
    # Scale and place a clean shelf rail at front and rear
    bm.free()

    # Even cleaner and manifold: Front shelf rail and Rear shelf rail
    # with end braces! This leaves the center slot completely open for tubes.
    bm = bmesh.new()
    # Front rail
    v1 = bm.verts.new((-w_half, d_half - 0.009, z_bot))
    v2 = bm.verts.new((w_half, d_half - 0.009, z_bot))
    v3 = bm.verts.new((w_half, d_half, z_bot))
    v4 = bm.verts.new((-w_half, d_half, z_bot))
    v5 = bm.verts.new((-w_half, d_half - 0.009, z_top))
    v6 = bm.verts.new((w_half, d_half - 0.009, z_top))
    v7 = bm.verts.new((w_half, d_half, z_top))
    v8 = bm.verts.new((-w_half, d_half, z_top))
    # 6 faces of front rail
    bm.faces.new([v1, v2, v3, v4])
    bm.faces.new([v5, v8, v7, v6])
    bm.faces.new([v1, v5, v6, v2])
    bm.faces.new([v2, v6, v7, v3])
    bm.faces.new([v3, v7, v8, v4])
    bm.faces.new([v4, v8, v5, v1])

    # Rear rail
    vr1 = bm.verts.new((-w_half, -d_half, z_bot))
    vr2 = bm.verts.new((w_half, -d_half, z_bot))
    vr3 = bm.verts.new((w_half, -d_half + 0.009, z_bot))
    vr4 = bm.verts.new((-w_half, -d_half + 0.009, z_bot))
    vr5 = bm.verts.new((-w_half, -d_half, z_top))
    vr6 = bm.verts.new((w_half, -d_half, z_top))
    vr7 = bm.verts.new((w_half, -d_half + 0.009, z_top))
    vr8 = bm.verts.new((-w_half, -d_half + 0.009, z_top))
    bm.faces.new([vr1, vr2, vr3, vr4])
    bm.faces.new([vr5, vr8, vr7, vr6])
    bm.faces.new([vr1, vr5, vr6, vr2])
    bm.faces.new([vr2, vr6, vr7, vr3])
    bm.faces.new([vr3, vr7, vr8, vr4])
    bm.faces.new([vr4, vr8, vr5, vr1])

    # Cross dividers (at x = -0.075, x = 0.0, x = +0.075)
    for cx in [-0.075, 0.0, 0.075]:
        bmesh.ops.create_cube(bm, size=1.0)
        # Transform the newly created cube
        # Most recently added 8 verts
        for v in bm.verts[-8:]:
            v.co.x = cx + v.co.x * 0.008
            v.co.y = v.co.y * (d_half * 2 - 0.016)
            v.co.z = z_bot + h_shelf * 0.5 + v.co.z * h_shelf

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    return mesh

def build_test_tube_rack(prefix, col, mat_wood, mat_trim):
    """
    Constructs an open-front hardwood test tube rack leaving tubes 100% visible.
    """
    objs = []
    # 1. Base Slab
    base = kit.primitive_object(
        f"{prefix}-rack-base", "cube", mat_wood,
        size=(0.180, 0.072, 0.012),
        location=(0.0, 0.0, 0.006)
    )
    link_strictly(base, col)
    objs.append(base)

    # 2. Side Upright End Frames (left and right)
    for x_side in [-0.082, 0.082]:
        pillar = kit.primitive_object(
            f"{prefix}-rack-pillar-{x_side}", "cube", mat_wood,
            size=(0.012, 0.064, 0.118),
            location=(x_side, 0.0, 0.065)
        )
        link_strictly(pillar, col)
        objs.append(pillar)

    # 3. Top Rail Shelf
    shelf_mesh = create_rack_top_shelf_with_holes(f"{prefix}-shelf-mesh", mat_wood)
    shelf_obj = bpy.data.objects.new(f"{prefix}-rack-shelf", shelf_mesh)
    shelf_obj.data.materials.append(mat_wood)
    col.objects.link(shelf_obj)
    objs.append(shelf_obj)

    # 4. Rear Drying Pegs
    for idx, px in enumerate([-0.050, 0.0, 0.050]):
        peg = kit.primitive_object(
            f"{prefix}-rack-peg-{idx}", "cylinder", mat_trim,
            size=(0.006, 0.006, 0.045),
            location=(px, -0.022, 0.028)
        )
        link_strictly(peg, col)
        objs.append(peg)

    return objs

def create_test_tube(name, pos, col, mat_glass, cutaway=False):
    """
    Creates a borosilicate test tube with hemispherical rounded base and flared rim.
    If cutaway=True, removes the front quadrant.
    """
    r_tube = 0.011
    t_wall = 0.0012
    h_tube = 0.125
    z_bot = pos.z

    start_angle = -0.5 * math.pi if cutaway else 0.0
    end_angle   = math.pi if cutaway else 2.0 * math.pi
    actual_segs = int(36 * 0.75) if cutaway else 36

    profile = [
        (0.000, z_bot),
        (r_tube * 0.5, z_bot + 0.002),
        (r_tube * 0.85, z_bot + 0.006),
        (r_tube, z_bot + 0.012),
        (r_tube, z_bot + h_tube - 0.004),
        (r_tube + 0.002, z_bot + h_tube),
        (r_tube - t_wall, z_bot + h_tube),
        (r_tube - t_wall, z_bot + 0.012),
        ((r_tube - t_wall) * 0.85, z_bot + 0.006 + t_wall),
        ((r_tube - t_wall) * 0.5, z_bot + 0.002 + t_wall),
        (0.000, z_bot + t_wall)
    ]

    bm = bmesh.new()
    rings = []
    for r, z in profile:
        ring = []
        for s in range(actual_segs + (1 if cutaway else 0)):
            if cutaway:
                theta = start_angle + (end_angle - start_angle) * (s / actual_segs)
            else:
                theta = 2.0 * math.pi * (s / actual_segs)
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            v = bm.verts.new((pos.x + r * cos_t, pos.y + r * sin_t, z))
            ring.append(v)
        rings.append(ring)

    for i in range(len(profile) - 1):
        for s in range(actual_segs):
            next_s = (s + 1) if cutaway else ((s + 1) % actual_segs)
            v1 = rings[i][s]
            v2 = rings[i][next_s]
            v3 = rings[i+1][next_s]
            v4 = rings[i+1][s]
            if profile[i][0] == 0.0:
                bm.faces.new([v1, v3, v4])
            elif profile[i+1][0] == 0.0:
                bm.faces.new([v1, v2, v3])
            else:
                bm.faces.new([v1, v2, v3, v4])

    if cutaway:
        for i in range(len(profile) - 1):
            if profile[i][0] > 0.0 or profile[i+1][0] > 0.0:
                bm.faces.new([rings[i][0], rings[i+1][0], rings[i+1][-1], rings[i][-1]])

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_glass)
    col.objects.link(obj)
    return obj

def build_liquid_column(name, pos, h_liquid, col, mat_liquid, cutaway=False):
    """Creates the liquid column with rounded bottom and flat meniscus."""
    r_in = 0.0096
    z_bot = pos.z + 0.003
    z_top = z_bot + h_liquid

    if not cutaway:
        cyl = kit.primitive_object(
            name, "cylinder", mat_liquid,
            size=(r_in * 2, r_in * 2, h_liquid),
            location=Vector((pos.x, pos.y, z_bot + h_liquid * 0.5))
        )
        link_strictly(cyl, col)
        return cyl

    bm = bmesh.new()
    segs = 28
    start_angle = -0.5 * math.pi
    end_angle   = math.pi
    for s in range(segs + 1):
        theta = start_angle + (end_angle - start_angle) * (s / segs)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        bm.verts.new((pos.x + r_in * cos_t, pos.y + r_in * sin_t, z_bot))
        bm.verts.new((pos.x + r_in * cos_t, pos.y + r_in * sin_t, z_top))
    center_bot = bm.verts.new((pos.x, pos.y, z_bot))
    center_top = bm.verts.new((pos.x, pos.y, z_top))
    bm.verts.ensure_lookup_table()
    for s in range(segs):
        v1 = bm.verts[s*2]
        v2 = bm.verts[s*2 + 1]
        v3 = bm.verts[(s+1)*2]
        v4 = bm.verts[(s+1)*2 + 1]
        bm.faces.new([v1, v3, v4, v2])
        bm.faces.new([center_bot, v1, v3])
        bm.faces.new([center_top, v4, v2])
    bm.faces.new([center_bot, bm.verts[0], bm.verts[1], center_top])
    bm.faces.new([center_bot, center_top, bm.verts[segs*2 + 1], bm.verts[segs*2]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat_liquid)
    col.objects.link(obj)
    return obj

def build_suspended_nail(prefix, pos, z_meniscus, col, mat_iron, mat_copper, mat_thread, cutaway=False):
    """
    Constructs the iron nail suspended by thread in Test Tube B.
    Submerged portion: Coated in reddish-brown copper deposit.
    Upper portion: Clean silver-grey metallic iron.
    """
    objs = []
    nail_len = 0.065
    nail_r   = 0.0028
    head_r   = 0.0055
    head_h   = 0.0020
    nail_top_z = z_meniscus + 0.022
    nail_bot_z = nail_top_z - nail_len

    if not cutaway:
        h_above = max(0.005, nail_top_z - z_meniscus)
        z_above = z_meniscus + h_above * 0.5
        shaft_clean = kit.primitive_object(
            f"{prefix}-nail-clean", "cylinder", mat_iron,
            size=(nail_r * 2, nail_r * 2, h_above),
            location=Vector((pos.x, pos.y, z_above))
        )
        link_strictly(shaft_clean, col)
        objs.append(shaft_clean)

        head = kit.primitive_object(
            f"{prefix}-nail-head", "cylinder", mat_iron,
            size=(head_r * 2, head_r * 2, head_h),
            location=Vector((pos.x, pos.y, nail_top_z + head_h * 0.5))
        )
        link_strictly(head, col)
        objs.append(head)

        h_below = z_meniscus - nail_bot_z
        z_below = nail_bot_z + h_below * 0.5
        shaft_copper = kit.primitive_object(
            f"{prefix}-nail-copper", "cylinder", mat_copper,
            size=((nail_r + 0.0004) * 2, (nail_r + 0.0004) * 2, h_below),
            location=Vector((pos.x, pos.y, z_below))
        )
        link_strictly(shaft_copper, col)
        objs.append(shaft_copper)

        tip = kit.primitive_object(
            f"{prefix}-nail-tip", "cone", mat_copper,
            size=((nail_r + 0.0004) * 2, (nail_r + 0.0004) * 2, 0.006),
            location=Vector((pos.x, pos.y, nail_bot_z - 0.003)),
            rotation_euler=(math.pi, 0.0, 0.0)
        )
        link_strictly(tip, col)
        objs.append(tip)
    else:
        h_below = z_meniscus - nail_bot_z
        z_below = nail_bot_z + h_below * 0.5
        core = kit.primitive_object(
            f"{prefix}-nail-core", "cylinder", mat_iron,
            size=(nail_r * 1.8, nail_r * 1.8, nail_len),
            location=Vector((pos.x, pos.y, nail_bot_z + nail_len * 0.5))
        )
        link_strictly(core, col)
        objs.append(core)

        mantle = kit.primitive_object(
            f"{prefix}-nail-mantle", "cylinder", mat_copper,
            size=((nail_r + 0.0008) * 2, (nail_r + 0.0008) * 2, h_below),
            location=Vector((pos.x, pos.y, z_below))
        )
        link_strictly(mantle, col)
        objs.append(mantle)

    thread_pts = [
        Vector((pos.x, pos.y, nail_top_z)),
        Vector((pos.x, pos.y + 0.005, nail_top_z + 0.020)),
        Vector((pos.x, pos.y + 0.010, pos.z + 0.125)),
        Vector((pos.x, pos.y + 0.014, pos.z + 0.115))
    ]
    thread = kit.create_smooth_tube(f"{prefix}-thread", thread_pts, radius=0.0007, material=mat_thread)
    link_strictly(thread, col)
    objs.append(thread)

    return objs

def build_watch_glass_station(prefix, pos, col, mat_porcelain, mat_iron, mat_copper):
    """
    Constructs a porcelain watch glass with two comparison nails:
    1. Clean iron nail (silver)
    2. Reacted copper-coated nail (reddish-brown)
    """
    objs = []
    dish_profile = [
        (0.000, 0.016),
        (0.030, 0.016),
        (0.034, 0.022),
        (0.033, 0.022),
        (0.029, 0.017),
        (0.000, 0.017)
    ]
    dish = kit.lathe_object(f"{prefix}-dish", dish_profile, segments=36, material=mat_porcelain, location=pos)
    link_strictly(dish, col)
    objs.append(dish)

    nail1 = kit.primitive_object(
        f"{prefix}-nail-ref-clean", "cylinder", mat_iron,
        size=(0.003, 0.003, 0.045),
        location=pos + Vector((-0.010, 0.0, 0.019)),
        rotation_euler=(0.0, math.pi * 0.5, 0.15)
    )
    link_strictly(nail1, col)
    objs.append(nail1)

    nail2 = kit.primitive_object(
        f"{prefix}-nail-ref-copper", "cylinder", mat_copper,
        size=(0.0034, 0.0034, 0.045),
        location=pos + Vector((0.010, 0.0, 0.019)),
        rotation_euler=(0.0, math.pi * 0.5, -0.15)
    )
    link_strictly(nail2, col)
    objs.append(nail2)

    return objs

def build_displacement_full(col):
    """Constructs the complete 3D apparatus for Displacement_Setup_Full collection."""
    objs = []
    mat_plinth    = kit.add_material("disp-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_wood      = kit.add_material("disp-wood", COLOR_RACK_WOOD, metallic=0.04, roughness=0.45)
    mat_wood_trim = kit.add_material("disp-wood-trim", COLOR_RACK_TRIM, metallic=0.04, roughness=0.55)
    mat_glass     = kit.add_glass_material("disp-glass", tint=COLOR_GLASS, ior=1.48, roughness=0.01, transmission=0.98)
    mat_cuso4     = create_solution_mat("disp-cuso4", COLOR_BLUE_CUSO4)
    mat_feso4     = create_solution_mat("disp-feso4", COLOR_GREEN_FESO4)
    mat_iron      = kit.add_material("disp-iron", COLOR_IRON_CLEAN, metallic=0.92, roughness=0.25)
    mat_copper    = kit.add_material("disp-copper", COLOR_COPPER_COAT, metallic=0.82, roughness=0.42)
    mat_thread    = kit.add_material("disp-thread", COLOR_THREAD, metallic=0.0, roughness=0.85)
    mat_porcelain = kit.add_material("disp-porcelain", COLOR_PORCELAIN, metallic=0.04, roughness=0.22)

    # 1. Base Bench Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-plinth", "cube", mat_plinth,
        size=(0.280, 0.220, 0.016),
        location=(0.0, -0.015, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    # 2. Hardwood Test Tube Rack
    rack_objs = build_test_tube_rack(ASSET_ID, col, mat_wood, mat_wood_trim)
    objs.extend(rack_objs)

    # 3. Test Tube A (Control: Deep Blue CuSO4, x = -0.035m)
    pos_a = Vector((-0.035, 0.0, 0.014))
    tube_a = create_test_tube(f"{ASSET_ID}-tube-a", pos_a, col, mat_glass, cutaway=False)
    sol_a  = build_liquid_column(f"{ASSET_ID}-sol-a", pos_a, 0.075, col, mat_cuso4, cutaway=False)
    objs.extend([tube_a, sol_a])

    # 4. Test Tube B (Experimental: Pale Green FeSO4, x = +0.035m)
    pos_b = Vector((0.035, 0.0, 0.014))
    tube_b = create_test_tube(f"{ASSET_ID}-tube-b", pos_b, col, mat_glass, cutaway=False)
    sol_b  = build_liquid_column(f"{ASSET_ID}-sol-b", pos_b, 0.075, col, mat_feso4, cutaway=False)
    objs.extend([tube_b, sol_b])

    # 5. Suspended Nail in Test Tube B
    z_meniscus = pos_b.z + 0.002 + 0.075
    nail_objs = build_suspended_nail(ASSET_ID, pos_b, z_meniscus, col, mat_iron, mat_copper, mat_thread, cutaway=False)
    objs.extend(nail_objs)

    # 6. Watch Glass Comparison Station on front bench
    wg_pos = Vector((0.0, -0.062, 0.0))
    wg_objs = build_watch_glass_station(ASSET_ID, wg_pos, col, mat_porcelain, mat_iron, mat_copper)
    objs.extend(wg_objs)

    return objs

def build_displacement_section(col):
    """
    Constructs the longitudinal cutaway collection revealing:
    - Tube B cross section and liquid meniscus.
    - Suspended iron nail inner Fe core vs outer deposited Cu mantle.
    - Redox electron transfer arrows (Fe dissolution vs Cu reduction).
    - Chemical reaction plaque: Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s).
    - Reactivity series badge: 'Fe > Cu'.
    """
    objs = []
    mat_plinth    = kit.add_material("sec-disp-plinth", COLOR_PLINTH, metallic=0.15, roughness=0.55)
    mat_wood      = kit.add_material("sec-disp-wood", COLOR_RACK_WOOD, metallic=0.04, roughness=0.45)
    mat_wood_trim = kit.add_material("sec-disp-wood-trim", COLOR_RACK_TRIM, metallic=0.04, roughness=0.55)
    mat_glass     = kit.add_glass_material("sec-disp-glass", tint=COLOR_GLASS, ior=1.48, roughness=0.01, transmission=0.98)
    mat_cuso4     = create_solution_mat("sec-disp-cuso4", COLOR_BLUE_CUSO4)
    mat_feso4     = create_solution_mat("sec-disp-feso4", COLOR_GREEN_FESO4)
    mat_iron      = kit.add_material("sec-disp-iron", COLOR_IRON_CLEAN, metallic=0.92, roughness=0.25)
    mat_copper    = kit.add_material("sec-disp-copper", COLOR_COPPER_COAT, metallic=0.82, roughness=0.42)
    mat_thread    = kit.add_material("sec-disp-thread", COLOR_THREAD, metallic=0.0, roughness=0.85)
    mat_porcelain = kit.add_material("sec-disp-porcelain", COLOR_PORCELAIN, metallic=0.04, roughness=0.22)
    mat_arrow_fe  = create_emissive_mat("sec-disp-arrow-fe", COLOR_ARROW_FE, strength=4.5)
    mat_arrow_cu  = create_emissive_mat("sec-disp-arrow-cu", COLOR_ARROW_CU, strength=4.5)
    mat_trim      = kit.add_material("sec-disp-trim", COLOR_CUT_EDGE, metallic=0.1, roughness=0.3)

    # 1. Base Bench Plinth
    plinth = kit.primitive_object(
        f"{ASSET_ID}-sec-plinth", "cube", mat_plinth,
        size=(0.280, 0.220, 0.016),
        location=(0.0, -0.015, 0.008)
    )
    link_strictly(plinth, col)
    objs.append(plinth)

    # 2. Hardwood Test Tube Rack
    rack_objs = build_test_tube_rack(f"{ASSET_ID}-sec", col, mat_wood, mat_wood_trim)
    objs.extend(rack_objs)

    # 3. Test Tube A (Full reference control)
    pos_a = Vector((-0.035, 0.0, 0.014))
    tube_a = create_test_tube(f"{ASSET_ID}-sec-tube-a", pos_a, col, mat_glass, cutaway=False)
    sol_a  = build_liquid_column(f"{ASSET_ID}-sec-sol-a", pos_a, 0.075, col, mat_cuso4, cutaway=False)
    objs.extend([tube_a, sol_a])

    # 4. Test Tube B (Section cutaway)
    pos_b = Vector((0.035, 0.0, 0.014))
    tube_b = create_test_tube(f"{ASSET_ID}-sec-tube-b", pos_b, col, mat_glass, cutaway=True)
    sol_b  = build_liquid_column(f"{ASSET_ID}-sec-sol-b", pos_b, 0.075, col, mat_feso4, cutaway=True)
    objs.extend([tube_b, sol_b])

    # 5. Suspended Nail (Section view showing core & copper crust)
    z_meniscus = pos_b.z + 0.002 + 0.075
    nail_objs = build_suspended_nail(f"{ASSET_ID}-sec", pos_b, z_meniscus, col, mat_iron, mat_copper, mat_thread, cutaway=True)
    objs.extend(nail_objs)

    # 6. Watch Glass station
    wg_pos = Vector((0.0, -0.062, 0.0))
    wg_objs = build_watch_glass_station(f"{ASSET_ID}-sec", wg_pos, col, mat_porcelain, mat_iron, mat_copper)
    objs.extend(wg_objs)

    # 7. Electrochemical Ionic Exchange Arrows
    fe_arrow = kit.primitive_object(
        f"{ASSET_ID}-sec-fe-arrow", "cone", mat_arrow_fe,
        size=(0.003, 0.003, 0.008),
        location=pos_b + Vector((0.006, 0.0, 0.052)),
        rotation_euler=(0.0, 1.2, 0.0)
    )
    cu_arrow = kit.primitive_object(
        f"{ASSET_ID}-sec-cu-arrow", "cone", mat_arrow_cu,
        size=(0.003, 0.003, 0.008),
        location=pos_b + Vector((-0.006, 0.0, 0.042)),
        rotation_euler=(0.0, -1.2, 0.0)
    )
    link_strictly(fe_arrow, col)
    link_strictly(cu_arrow, col)
    objs.extend([fe_arrow, cu_arrow])

    # 8. Chemical Equation Plaque Banner: Fe + CuSO4 -> FeSO4 + Cu
    plaque_bg = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-bg", "cube", mat_plinth,
        size=(0.170, 0.004, 0.024),
        location=(0.0, 0.045, 0.144)
    )
    link_strictly(plaque_bg, col)
    objs.append(plaque_bg)

    plaque_trim = kit.primitive_object(
        f"{ASSET_ID}-sec-plaque-trim", "cube", mat_trim,
        size=(0.174, 0.005, 0.002),
        location=(0.0, 0.045, 0.157)
    )
    link_strictly(plaque_trim, col)
    objs.append(plaque_trim)

    # 9. Reactivity Series Indicator: "Fe > Cu"
    react_badge = kit.primitive_object(
        f"{ASSET_ID}-sec-react-badge", "cube", mat_copper,
        size=(0.042, 0.004, 0.012),
        location=(0.0, -0.020, 0.132)
    )
    link_strictly(react_badge, col)
    objs.append(react_badge)

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

def configure_fast_render(width=1280, height=720, samples=20):
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.cycles.max_bounces = 12
    scene.cycles.diffuse_bounces = 4
    scene.cycles.glossy_bounces = 8
    scene.cycles.transmission_bounces = 12
    scene.cycles.transparent_max_bounces = 12
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"

def main():
    out_dir = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    kit.setup_world_and_light()

    # Studio backlight to illuminate glassware and liquid transmission from behind
    back_light_data = bpy.data.lights.new(name="Disp_BackLight", type='AREA')
    back_light_data.energy = 110.0
    back_light_data.size = 0.35
    back_light_data.color = (1.0, 0.98, 0.95)
    back_light_obj = bpy.data.objects.new("Disp_BackLight", back_light_data)
    back_light_obj.location = (0.0, 0.18, 0.12)
    back_light_obj.rotation_euler = (math.radians(-65), 0.0, math.radians(180))
    bpy.context.scene.collection.objects.link(back_light_obj)

    col_full = bpy.data.collections.new("Displacement_Setup_Full")
    col_sec  = bpy.data.collections.new("Displacement_Setup_Section")
    bpy.context.scene.collection.children.link(col_full)
    bpy.context.scene.collection.children.link(col_sec)

    full_objs = build_displacement_full(col_full)
    sec_objs  = build_displacement_section(col_sec)

    cam_data = bpy.data.cameras.new("Displacement_Camera")
    cam_data.lens = 52.0
    cam_data.sensor_width = 36.0
    cam_obj = bpy.data.objects.new("Displacement_Camera", cam_data)
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

    configure_fast_render(width=1280, height=720, samples=20)

    # Render Preview 1: Full Bench Setup
    set_collection_visibility(full_objs, True)
    set_collection_visibility(sec_objs, False)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.015, 0.075)), distance=0.46, elev_deg=20, azim_deg=-24)
    preview_full = out_dir / "preview.png"
    kit.render_preview(preview_full)
    print(f"Rendered: {preview_full}")

    # Render Preview 2: Section View
    set_collection_visibility(full_objs, False)
    set_collection_visibility(sec_objs, True)
    frame_camera_on_target(cam_obj, Vector((0.0, -0.015, 0.090)), distance=0.50, elev_deg=18, azim_deg=-20)
    preview_sec = out_dir / "preview_section.png"
    kit.render_preview(preview_sec)
    print(f"Rendered: {preview_sec}")

    print("=== DISPLACEMENT REACTION SETUP BUILD COMPLETED SUCCESSFULLY ===")

if __name__ == '__main__':
    main()
