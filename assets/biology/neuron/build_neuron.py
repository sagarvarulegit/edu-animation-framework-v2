"""
build_neuron.py — Medical-Grade Multipolar Motor Neuron
NCERT / CBSE Class 10 Biology (Chapter 7: Control and Coordination, Fig 7.1)
CBSE Class 11 Biology (Chapter 21: Neural Control and Coordination, Fig 21.1)

Features:
- Organic multipolar Cyton (Cell Body / Perikaryon) with dendritic trunk tapers.
- Prominent spherical Nucleus, dense Nucleolus, and visible Nissl's granules.
- Gracefully branching Dendritic Arbor with primary, secondary, and tertiary branches with spines.
- Conical Axon Hillock transitioning into long central Axon cylinder.
- Segmented Schwann cell Myelin Sheaths with rounded ends, distinct Nodes of Ranvier, and Schwann nuclei.
- Axon terminal arborization (Telodendria) with swollen bulbous Synaptic Knobs / Boutons.
- Dual Collections:
    * Neuron_Full: Complete neuron with transparent/subsurface cyton and full myelination.
    * Neuron_Section: Coronal cross-section of cyton exposing interior nucleus & Nissl granules, plus cutaway myelin sheath showing axoplasm core.
- Calibrated 4-point studio macro lighting and AgX High Contrast rendering.
"""

import sys, math, os, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Euler, Matrix

ASSET_ID = "neuron"


def create_tissue_material(name, base_color, subsurface=0.0, roughness=0.4, metallic=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if subsurface > 0.0 and "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = transmission
    return mat


def create_smooth_spline_tube(name, points, radius, material, bevel_resolution=4):
    """Creates a smooth 3D tube along bezier spline points with capped ends."""
    curve_data = bpy.data.curves.new(f"{name}_curve", type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.bevel_depth = radius
    curve_data.bevel_resolution = bevel_resolution
    curve_data.fill_mode = 'FULL'

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for i, pt in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = Vector(pt)
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)

    prev_active = bpy.context.view_layer.objects.active
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    if prev_active and prev_active.name in bpy.context.scene.objects:
        bpy.context.view_layer.objects.active = prev_active

    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    boundary_edges = [e for e in bm.edges if e.is_boundary]
    if boundary_edges:
        bmesh.ops.holes_fill(bm, edges=boundary_edges, sides=len(boundary_edges))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    if material:
        obj.data.materials.append(material)
    return obj


def create_tapered_branch(name, start_pt, end_pt, start_radius, end_radius, material, segments=8):
    """Creates a conical/tapered limb between two points."""
    bm = bmesh.new()
    v_start = Vector(start_pt)
    v_end = Vector(end_pt)
    axis = (v_end - v_start)
    length = axis.length
    if length < 1e-5:
        bm.free()
        return None

    dir_vec = axis.normalized()
    rot_quat = Vector((0, 0, 1)).rotation_difference(dir_vec)
    mat_rot = rot_quat.to_matrix().to_4x4()

    num_rings = 4
    ring_verts = []
    for r in range(num_rings):
        t = r / (num_rings - 1)
        curr_rad = start_radius * (1.0 - t) + end_radius * t
        curr_pos = v_start + dir_vec * (length * t)
        ring = []
        for s in range(segments):
            angle = 2.0 * math.pi * s / segments
            lx = curr_rad * math.cos(angle)
            ly = curr_rad * math.sin(angle)
            pos_local = mat_rot @ Vector((lx, ly, 0))
            v = bm.verts.new(curr_pos + pos_local)
            ring.append(v)
        ring_verts.append(ring)

    for r in range(num_rings - 1):
        for s in range(segments):
            s_next = (s + 1) % segments
            bm.faces.new([
                ring_verts[r][s],
                ring_verts[r][s_next],
                ring_verts[r + 1][s_next],
                ring_verts[r + 1][s]
            ])

    bm.faces.new(list(reversed(ring_verts[0])))
    bm.faces.new(ring_verts[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    if material:
        obj.data.materials.append(material)
    return obj


def create_organic_soma(name, center, radius, dendritic_roots, hillock_pt, material):
    """
    Creates an authentic multipolar cyton (perikaryon) deformed organically toward
    the dendritic root origins and axon hillock.
    """
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=radius)

    center_v = Vector(center)
    hillock_v = Vector(hillock_pt)

    for v in bm.verts:
        pos = v.co + center_v
        disp = Vector((0, 0, 0))

        for root in dendritic_roots:
            rv = Vector(root)
            diff = rv - center_v
            d_len = diff.length
            if d_len > 1e-4:
                dir_n = diff.normalized()
                dot = max(0.0, v.co.normalized().dot(dir_n))
                if dot > 0.4:
                    influence = math.pow((dot - 0.4) / 0.6, 2.0) * (d_len - radius) * 0.75
                    disp += dir_n * influence

        h_diff = hillock_v - center_v
        h_len = h_diff.length
        if h_len > 1e-4:
            h_dir = h_diff.normalized()
            h_dot = max(0.0, v.co.normalized().dot(h_dir))
            if h_dot > 0.5:
                h_inf = math.pow((h_dot - 0.5) / 0.5, 2.5) * (h_len - radius) * 0.85
                disp += h_dir * h_inf

        noise = math.sin(v.co.x * 200.0) * math.cos(v.co.y * 200.0) * 0.0005
        v.co += disp + v.co.normalized() * noise

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center_v

    sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    sub.levels = 1
    sub.render_levels = 2

    if material:
        obj.data.materials.append(material)
    return obj


def create_synaptic_bouton(name, location, direction, material, radius=0.0032):
    """Creates a bulbous teardrop-shaped synaptic knob."""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=radius)
    for v in bm.verts:
        if v.co.z < 0:
            factor = 1.0 - (v.co.z / radius) * 0.35
            v.co.x *= factor
            v.co.y *= factor
        else:
            factor = 1.0 + (v.co.z / radius) * 0.2
            v.co.x *= factor
            v.co.y *= factor

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = Vector(location)

    dir_n = Vector(direction).normalized()
    obj.rotation_euler = dir_n.to_track_quat("Z", "Y").to_euler()

    if material:
        obj.data.materials.append(material)
    return obj


def create_myelin_segment(name, center_x, length, inner_rad, outer_rad, myelin_mat, nuc_mat, cutaway=False):
    """
    Creates a realistic sausage-like Schwann cell myelin sheath with rounded beveled ends
    constricting down towards the node of Ranvier, and an eccentric Schwann cell nucleus.
    If cutaway=True, cleanly applies a Boolean difference to expose concentric myelin layers and axon core.
    """
    bm = bmesh.new()
    segments_circum = 20
    rings = 8

    half_l = length * 0.5
    ring_xs = []
    ring_rads = []
    for r in range(rings):
        t = r / (rings - 1)
        x = -half_l + length * t
        profile = math.sin(t * math.pi)
        rad = inner_rad + (outer_rad - inner_rad) * (0.4 + 0.6 * math.sqrt(profile))
        ring_xs.append(x)
        ring_rads.append(rad)

    ring_verts = []
    for r in range(rings):
        ring = []
        for s in range(segments_circum):
            angle = 2.0 * math.pi * s / segments_circum
            y = ring_rads[r] * math.cos(angle)
            z = ring_rads[r] * math.sin(angle)
            v = bm.verts.new((ring_xs[r], y, z))
            ring.append(v)
        ring_verts.append(ring)

    for r in range(rings - 1):
        for s in range(segments_circum):
            s_next = (s + 1) % segments_circum
            bm.faces.new([
                ring_verts[r][s],
                ring_verts[r][s_next],
                ring_verts[r + 1][s_next],
                ring_verts[r + 1][s]
            ])

    bm.faces.new(list(reversed(ring_verts[0])))
    bm.faces.new(ring_verts[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_mesh")
    bm.to_mesh(mesh)
    bm.free()

    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (center_x, 0.0, 0.0)

    if myelin_mat:
        obj.data.materials.append(myelin_mat)

    created_objs = [obj]

    nuc = kit.primitive_object(
        f"{name}_schwann_nucleus", "uv_sphere", nuc_mat,
        size=(0.0042, 0.0022, 0.0018),
        location=(center_x, 0.0, outer_rad * 0.95)
    )
    created_objs.append(nuc)

    if cutaway:
        cutter = kit.primitive_object(
            f"{name}_cutter", "cube", None,
            size=(length * 1.2, outer_rad * 2.5, outer_rad * 1.5),
            location=(center_x, -outer_rad * 0.6, 0.0)
        )
        mod = obj.modifiers.new("Cutaway", 'BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.solver = 'EXACT'
        mod.object = cutter
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Cutaway")
        bpy.data.objects.remove(cutter, do_unlink=True)

    return created_objs


def build_neuron_model(prefix="Full", is_section=False):
    """
    Constructs the complete NCERT-grade multipolar neuron hierarchy.
    """
    soma_mat = create_tissue_material(f"{prefix}_soma_mat", (0.92, 0.76, 0.56), subsurface=0.15, roughness=0.38)
    nucleus_mat = create_tissue_material(f"{prefix}_nucleus_mat", (0.64, 0.38, 0.72), subsurface=0.10, roughness=0.30)
    nucleolus_mat = create_tissue_material(f"{prefix}_nucleolus_mat", (0.36, 0.12, 0.44), subsurface=0.0, roughness=0.25)
    nissl_mat = create_tissue_material(f"{prefix}_nissl_mat", (0.38, 0.40, 0.65), subsurface=0.0, roughness=0.45)
    dendrite_mat = create_tissue_material(f"{prefix}_dendrite_mat", (0.90, 0.74, 0.54), subsurface=0.12, roughness=0.40)
    axon_mat = create_tissue_material(f"{prefix}_axon_mat", (0.28, 0.65, 0.90), subsurface=0.10, roughness=0.30)
    myelin_mat = create_tissue_material(f"{prefix}_myelin_mat", (0.95, 0.92, 0.85), subsurface=0.15, roughness=0.28)
    schwann_mat = create_tissue_material(f"{prefix}_schwann_mat", (0.58, 0.28, 0.65), subsurface=0.05, roughness=0.35)
    terminal_mat = create_tissue_material(f"{prefix}_terminal_mat", (0.86, 0.52, 0.44), subsurface=0.10, roughness=0.38)
    bouton_mat = create_tissue_material(f"{prefix}_bouton_mat", (0.92, 0.36, 0.30), subsurface=0.15, roughness=0.26)

    objects = []

    soma_center = (-0.052, 0.0, 0.0)
    soma_radius = 0.016
    hillock_exit = (-0.032, 0.0, 0.0)

    dendritic_specs = [
        {
            "root": (-0.065, 0.010, 0.008),
            "pri": [(-0.065, 0.010, 0.008), (-0.076, 0.018, 0.014), (-0.088, 0.024, 0.018)],
            "sec1": [(-0.088, 0.024, 0.018), (-0.098, 0.030, 0.025), (-0.106, 0.034, 0.030)],
            "sec2": [(-0.088, 0.024, 0.018), (-0.096, 0.018, 0.010), (-0.104, 0.015, 0.004)],
        },
        {
            "root": (-0.064, -0.011, 0.006),
            "pri": [(-0.064, -0.011, 0.006), (-0.075, -0.020, 0.012), (-0.086, -0.026, 0.016)],
            "sec1": [(-0.086, -0.026, 0.016), (-0.095, -0.032, 0.022), (-0.104, -0.036, 0.026)],
            "sec2": [(-0.086, -0.026, 0.016), (-0.092, -0.024, 0.006), (-0.100, -0.022, -0.002)],
        },
        {
            "root": (-0.066, 0.000, -0.011),
            "pri": [(-0.066, 0.000, -0.011), (-0.078, 0.002, -0.020), (-0.090, 0.004, -0.026)],
            "sec1": [(-0.090, 0.004, -0.026), (-0.100, 0.008, -0.032), (-0.108, 0.010, -0.038)],
            "sec2": [(-0.090, 0.004, -0.026), (-0.098, -0.006, -0.022), (-0.106, -0.012, -0.018)],
        },
        {
            "root": (-0.052, 0.013, -0.009),
            "pri": [(-0.052, 0.013, -0.009), (-0.058, 0.022, -0.018), (-0.066, 0.030, -0.024)],
            "sec1": [(-0.066, 0.030, -0.024), (-0.072, 0.036, -0.030), (-0.078, 0.040, -0.036)],
            "sec2": [(-0.066, 0.030, -0.024), (-0.062, 0.026, -0.016), (-0.060, 0.024, -0.010)],
        },
        {
            "root": (-0.050, -0.012, -0.009),
            "pri": [(-0.050, -0.012, -0.009), (-0.055, -0.022, -0.016), (-0.062, -0.030, -0.022)],
            "sec1": [(-0.062, -0.030, -0.022), (-0.068, -0.036, -0.028), (-0.074, -0.042, -0.032)],
            "sec2": [(-0.062, -0.030, -0.022), (-0.058, -0.024, -0.014), (-0.054, -0.020, -0.008)],
        },
        {
            "root": (-0.054, 0.002, 0.014),
            "pri": [(-0.054, 0.002, 0.014), (-0.060, 0.004, 0.024), (-0.068, 0.006, 0.032)],
            "sec1": [(-0.068, 0.006, 0.032), (-0.074, 0.010, 0.040), (-0.080, 0.012, 0.046)],
            "sec2": [(-0.068, 0.006, 0.032), (-0.064, -0.004, 0.028), (-0.060, -0.010, 0.024)],
        },
    ]

    dendrite_roots = [spec["root"] for spec in dendritic_specs]

    soma_obj = create_organic_soma(
        f"{prefix}_Soma", soma_center, soma_radius,
        dendrite_roots, hillock_exit, soma_mat
    )
    objects.append(soma_obj)

    for i, spec in enumerate(dendritic_specs):
        pri_obj = create_smooth_spline_tube(f"{prefix}_Dendrite_Pri_{i}", spec["pri"], radius=0.0018, material=dendrite_mat)
        sec1_obj = create_smooth_spline_tube(f"{prefix}_Dendrite_Sec1_{i}", spec["sec1"], radius=0.0012, material=dendrite_mat)
        sec2_obj = create_smooth_spline_tube(f"{prefix}_Dendrite_Sec2_{i}", spec["sec2"], radius=0.0010, material=dendrite_mat)
        objects.extend([pri_obj, sec1_obj, sec2_obj])

        spine_tip = spec["sec1"][-1]
        spine = kit.primitive_object(
            f"{prefix}_Spine_{i}", "uv_sphere", dendrite_mat,
            size=(0.0014, 0.0014, 0.0014),
            location=spine_tip
        )
        objects.append(spine)

    nucleus_center = (-0.052, 0.0, 0.0)
    nucleus_obj = kit.primitive_object(
        f"{prefix}_Nucleus", "uv_sphere", nucleus_mat,
        size=(0.009, 0.009, 0.009),
        location=nucleus_center
    )
    nucleolus_obj = kit.primitive_object(
        f"{prefix}_Nucleolus", "uv_sphere", nucleolus_mat,
        size=(0.0032, 0.0032, 0.0032),
        location=(-0.051, 0.002, 0.002)
    )
    objects.extend([nucleus_obj, nucleolus_obj])

    nissl_coords = [
        (-0.046, 0.006, 0.005),
        (-0.048, -0.005, 0.006),
        (-0.058, 0.005, -0.005),
        (-0.056, -0.006, -0.005),
        (-0.045, -0.004, -0.005),
        (-0.058, 0.007, 0.004),
        (-0.048, 0.008, -0.006),
        (-0.054, -0.008, 0.005),
    ]
    for n_idx, n_pos in enumerate(nissl_coords):
        n_granule = kit.primitive_object(
            f"{prefix}_Nissl_{n_idx}", "uv_sphere", nissl_mat,
            size=(0.0015, 0.0015, 0.0015),
            location=n_pos
        )
        objects.append(n_granule)

    hillock = create_tapered_branch(
        f"{prefix}_Axon_Hillock",
        start_pt=(-0.040, 0.0, 0.0),
        end_pt=(-0.024, 0.0, 0.0),
        start_radius=0.0065,
        end_radius=0.0022,
        material=soma_mat
    )
    if hillock:
        objects.append(hillock)

    axon_start_x = -0.024
    axon_end_x = 0.108
    axon_len = axon_end_x - axon_start_x
    axon_core = kit.primitive_object(
        f"{prefix}_Axon_Core", "cylinder", axon_mat,
        size=(0.0021, 0.0021, axon_len),
        location=((axon_start_x + axon_end_x) * 0.5, 0.0, 0.0),
        rotation_euler=(0.0, math.pi / 2, 0.0)
    )
    objects.append(axon_core)

    num_sheaths = 5
    sheath_len = 0.020
    sheath_spacing = 0.024
    start_sheath_x = -0.010

    for s_idx in range(num_sheaths):
        cx = start_sheath_x + s_idx * sheath_spacing
        is_cut = (is_section and s_idx == 2)
        sheath_objs = create_myelin_segment(
            f"{prefix}_Myelin_{s_idx}",
            center_x=cx,
            length=sheath_len,
            inner_rad=0.0021,
            outer_rad=0.0055,
            myelin_mat=myelin_mat,
            nuc_mat=schwann_mat,
            cutaway=is_cut
        )
        objects.extend(sheath_objs)

    term_start = Vector((axon_end_x, 0.0, 0.0))
    telodendria_specs = [
        (Vector((0.126, 0.012, 0.010)), Vector((1.0, 0.6, 0.5))),
        (Vector((0.128, -0.010, 0.008)), Vector((1.0, -0.5, 0.4))),
        (Vector((0.125, 0.008, -0.012)), Vector((1.0, 0.4, -0.6))),
        (Vector((0.127, -0.009, -0.010)), Vector((1.0, -0.4, -0.5))),
        (Vector((0.130, 0.000, 0.002)), Vector((1.0, 0.0, 0.1))),
    ]

    for t_idx, (t_end, t_dir) in enumerate(telodendria_specs):
        mid = (term_start + t_end) * 0.5
        t_pts = [term_start, mid + Vector((0.002, 0.002 * (t_idx % 2 - 0.5), 0)), t_end]
        t_tube = create_smooth_spline_tube(
            f"{prefix}_Telodendria_{t_idx}", t_pts, radius=0.0011, material=terminal_mat
        )
        bouton = create_synaptic_bouton(
            f"{prefix}_Synaptic_Bouton_{t_idx}", t_end, t_dir, material=bouton_mat, radius=0.0034
        )
        objects.extend([t_tube, bouton])

    if is_section:
        soma_cutter = kit.primitive_object(
            f"{prefix}_Soma_Cutter", "cube", None,
            size=(0.045, 0.035, 0.045),
            location=(-0.052, -0.018, 0.0)
        )
        mod_soma = soma_obj.modifiers.new("Coronal_Cut", 'BOOLEAN')
        mod_soma.operation = 'DIFFERENCE'
        mod_soma.solver = 'EXACT'
        mod_soma.object = soma_cutter
        bpy.context.view_layer.objects.active = soma_obj
        bpy.ops.object.modifier_apply(modifier="Coronal_Cut")
        bpy.data.objects.remove(soma_cutter, do_unlink=True)

    return objects


def build_neuron_dual_scene():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()

    coll_full = bpy.data.collections.new("Neuron_Full")
    coll_section = bpy.data.collections.new("Neuron_Section")
    root_coll = bpy.context.scene.collection
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)

    print("Building Neuron_Full...")
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Neuron_Full"]
    full_objs = build_neuron_model(prefix="Full", is_section=False)
    for obj in full_objs:
        if obj.name in root_coll.objects:
            root_coll.objects.unlink(obj)
        if obj.name not in coll_full.objects:
            coll_full.objects.link(obj)

    print("Building Neuron_Section...")
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Neuron_Section"]
    section_objs = build_neuron_model(prefix="Sec", is_section=True)
    for obj in section_objs:
        if obj.name in root_coll.objects:
            root_coll.objects.unlink(obj)
        if obj.name not in coll_section.objects:
            coll_section.objects.link(obj)

    world = bpy.data.worlds.new("Neuron_World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.015, 0.020, 0.028, 1.0)
    bg.inputs["Strength"].default_value = 0.40
    bpy.context.scene.world = world

    # Calibrated macro studio lighting (distances 0.45-0.65m for gentle macro highlights)
    key_data = bpy.data.lights.new("Neuron_KeyLight", 'AREA')
    key_data.energy = 8.5
    key_data.color = (1.0, 0.96, 0.92)
    key_data.size = 0.45
    key_light = bpy.data.objects.new("Neuron_KeyLight", key_data)
    key_light.location = (0.08, -0.55, 0.35)
    key_light.rotation_euler = (Vector((0.010, 0.0, 0.0)) - key_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(key_light)

    fill_data = bpy.data.lights.new("Neuron_FillLight", 'AREA')
    fill_data.energy = 4.5
    fill_data.color = (0.88, 0.93, 1.0)
    fill_data.size = 0.55
    fill_light = bpy.data.objects.new("Neuron_FillLight", fill_data)
    fill_light.location = (-0.35, -0.45, 0.25)
    fill_light.rotation_euler = (Vector((0.010, 0.0, 0.0)) - fill_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(fill_light)

    rim_data = bpy.data.lights.new("Neuron_RimLight", 'AREA')
    rim_data.energy = 7.0
    rim_data.color = (0.90, 0.95, 1.0)
    rim_data.size = 0.40
    rim_light = bpy.data.objects.new("Neuron_RimLight", rim_data)
    rim_light.location = (0.05, 0.50, 0.30)
    rim_light.rotation_euler = (Vector((0.010, 0.0, 0.0)) - rim_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(rim_light)

    bounce_data = bpy.data.lights.new("Neuron_BounceLight", 'AREA')
    bounce_data.energy = 2.2
    bounce_data.color = (1.0, 0.88, 0.82)
    bounce_data.size = 0.40
    bounce_light = bpy.data.objects.new("Neuron_BounceLight", bounce_data)
    bounce_light.location = (-0.02, -0.25, -0.25)
    bounce_light.rotation_euler = (Vector((0.010, 0.0, 0.0)) - bounce_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(bounce_light)

    bpy.context.scene.view_settings.view_transform = 'AgX'
    try:
        bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    except TypeError:
        bpy.context.scene.view_settings.look = 'High Contrast'

    cam_data = bpy.data.cameras.new("Neuron_Camera")
    cam_data.lens = 50.0
    cam_obj = bpy.data.objects.new("Neuron_Camera", cam_data)
    root_coll.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Full overview framing: captures dendritic tips (x=-0.11) through terminal knobs (x=+0.13)
    target = Vector((0.010, 0.0, 0.005))
    cam_obj.location = Vector((0.010, -0.42, 0.12))
    cam_dir = target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()

    kit.configure_render(width=1280, height=720, samples=24)

    blend_path = out / f"{ASSET_ID}.blend"
    print(f"Saving .blend: {blend_path}")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    glb_path = out / f"{ASSET_ID}.glb"
    print(f"Exporting GLB: {glb_path}")
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format='GLB',
        use_selection=False,
        export_apply=True
    )
    print(f"Exported GLB ({os.path.getsize(glb_path) / 1024:.1f} KB)")

    viewer_assets = Path(__file__).resolve().parents[3] / "apps" / "interactive-viewer" / "public" / "assets"
    if viewer_assets.exists():
        shutil.copy2(glb_path, viewer_assets / f"{ASSET_ID}.glb")
        print(f"Synchronized to viewer: {viewer_assets / f'{ASSET_ID}.glb'}")

    print("Rendering Full Preview...")
    bpy.context.view_layer.layer_collection.children["Neuron_Full"].exclude = False
    bpy.context.view_layer.layer_collection.children["Neuron_Section"].exclude = True
    kit.render_preview(out / "preview.png")
    print(f"Rendered: {out / 'preview.png'}")

    print("Rendering Section Preview...")
    bpy.context.view_layer.layer_collection.children["Neuron_Full"].exclude = True
    bpy.context.view_layer.layer_collection.children["Neuron_Section"].exclude = False
    # Zoomed in to Cyton + Axon Hillock + first myelin sheaths
    target_sec = Vector((-0.035, 0.0, 0.0))
    cam_obj.location = Vector((-0.035, -0.20, 0.07))
    cam_dir = target_sec - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()
    kit.render_preview(out / "preview_section.png")
    print(f"Rendered: {out / 'preview_section.png'}")

    bpy.context.view_layer.layer_collection.children["Neuron_Full"].exclude = False
    bpy.context.view_layer.layer_collection.children["Neuron_Section"].exclude = False
    cam_obj.location = Vector((0.010, -0.42, 0.12))
    cam_dir = target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print("=== NEURON BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    build_neuron_dual_scene()

