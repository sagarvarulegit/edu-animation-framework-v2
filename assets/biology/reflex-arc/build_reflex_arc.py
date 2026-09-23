"""
build_reflex_arc.py — Medical-Grade Reflex Arc Neural Circuit
NCERT / CBSE Class 10 Biology (Chapter 7: Control and Coordination, Fig 7.2)

Features:
- Stimulus: Detailed metal cooking pan with handle and heated edge.
- Receptor: Anatomical human finger pad touching hot pan, with cutaneous dermal receptors.
- Afferent Sensory Neuron: Curving luminescent cobalt-blue tract with dorsal root ganglion (DRG)
  entering the spinal cord through the dorsal nerve root.
- Spinal Cord Transverse Cross-Section: Anatomical transverse segment with anterior median fissure,
  posterior median sulcus, outer white matter funiculi, central butterfly gray matter (slender dorsal horn,
  broad ventral horn, central canal), and dorsal/ventral nerve roots.
- Interneuron (Relay Neuron): Synaptic relay in spinal gray matter with ascending collateral
  axon ("Message to brain" per NCERT Fig 7.2).
- Efferent Motor Neuron: Multipolar soma in ventral horn, axon exiting via ventral nerve root,
  luminescent crimson-red tract terminating at neuromuscular junction.
- Effector Organ: Fusiform arm flexor muscle with glistening tendinous ends and motor end-plates.
- Dual Collections:
    * ReflexArc_Full: Complete reflex circuit from pan/finger receptor to arm muscle.
    * ReflexArc_Section: Macro view focused on the spinal cord transverse section and synaptic relay.
- Calibrated 4-point studio lighting and AgX High Contrast rendering.
"""

import sys, math, os, shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector, Euler, Matrix

ASSET_ID = "reflex-arc"


def create_pbr_mat(name, base_color, roughness=0.4, metallic=0.0, emission=None, emission_strength=1.0, subsurface=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if subsurface > 0.0 and "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    if emission and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def create_smooth_tube(name, points, radius, material, bevel_resolution=4):
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


def create_anatomical_spinal_cord(prefix, cx, cy, cz, depth, wm_mat, gm_mat, canal_mat):
    """
    Creates an anatomically accurate spinal cord segment in transverse section:
    - Anterior median fissure (deep anterior ventral notch)
    - Posterior median sulcus (shallow dorsal slit)
    - Oval white matter cylinder
    - Butterfly gray matter with slender dorsal horns and broad ventral horns
    - Central canal with ependymal lumen
    """
    objs = []

    # 1. White Matter Perimeter with Anterior Median Fissure (-Z) and Posterior Median Sulcus (+Z)
    bm_wm = bmesh.new()
    wm_pts_2d = [
        # (x, z) points defining half profile of spinal cord
        (0.001, 0.026),   # Posterior median sulcus notch
        (0.006, 0.027),
        (0.016, 0.026),
        (0.026, 0.021),   # Posterior-lateral funiculus
        (0.033, 0.012),
        (0.035, 0.000),   # Lateral funiculus
        (0.033, -0.012),
        (0.025, -0.021),  # Anterior-lateral funiculus
        (0.014, -0.026),
        (0.004, -0.026),
        (0.001, -0.018),  # Deep anterior median fissure notch
    ]
    # Mirror for left half
    wm_left = [(-x, z) for x, z in wm_pts_2d]
    wm_perimeter = []
    for pt in wm_pts_2d:
        wm_perimeter.append(pt)
    for pt in reversed(wm_left):
        wm_perimeter.append(pt)

    y_f = cy - depth * 0.5
    y_b = cy + depth * 0.5
    vf_wm = [bm_wm.verts.new((cx + x, y_f, cz + z)) for x, z in wm_perimeter]
    vb_wm = [bm_wm.verts.new((cx + x, y_b, cz + z)) for x, z in wm_perimeter]

    n_wm = len(wm_perimeter)
    for i in range(n_wm):
        ni = (i + 1) % n_wm
        bm_wm.faces.new([vf_wm[i], vf_wm[ni], vb_wm[ni], vb_wm[i]])
    bm_wm.faces.new(list(reversed(vf_wm)))
    bm_wm.faces.new(vb_wm)

    bmesh.ops.recalc_face_normals(bm_wm, faces=bm_wm.faces)
    mesh_wm = bpy.data.meshes.new(f"{prefix}_Spinal_Cord_WM_mesh")
    bm_wm.to_mesh(mesh_wm)
    bm_wm.free()

    for poly in mesh_wm.polygons:
        poly.use_smooth = True
    mesh_wm.update()

    obj_wm = bpy.data.objects.new(f"{prefix}_Spinal_Cord_White_Matter", mesh_wm)
    bpy.context.collection.objects.link(obj_wm)
    obj_wm.data.materials.append(wm_mat)
    sub_wm = obj_wm.modifiers.new("Subsurf", 'SUBSURF')
    sub_wm.levels = 2
    objs.append(obj_wm)

    # 2. Butterfly Gray Matter
    bm_gm = bmesh.new()
    r_gm = [
        (0.002, 0.003),
        (0.005, 0.007),
        (0.009, 0.013),
        (0.013, 0.019),   # Slender dorsal horn apex (+Z)
        (0.010, 0.019),
        (0.006, 0.011),
        (0.003, 0.003),   # Gray commissure
        (0.003, -0.003),
        (0.008, -0.008),
        (0.014, -0.015),  # Broad ventral horn apex (-Z)
        (0.016, -0.011),
        (0.012, -0.005),
        (0.007, -0.001),  # Lateral horn waist
        (0.004, 0.002),
    ]
    l_gm = [(-x, z) for x, z in r_gm]
    gm_perimeter = []
    for pt in r_gm:
        gm_perimeter.append(pt)
    for pt in reversed(l_gm):
        gm_perimeter.append(pt)

    # Gray matter is slightly extruded to sit flush on the cut face
    y_gm_f = cy - (depth * 0.5 + 0.0003)
    y_gm_b = cy + (depth * 0.5 + 0.0003)
    vf_gm = [bm_gm.verts.new((cx + x, y_gm_f, cz + z)) for x, z in gm_perimeter]
    vb_gm = [bm_gm.verts.new((cx + x, y_gm_b, cz + z)) for x, z in gm_perimeter]

    n_gm = len(gm_perimeter)
    for i in range(n_gm):
        ni = (i + 1) % n_gm
        bm_gm.faces.new([vf_gm[i], vf_gm[ni], vb_gm[ni], vb_gm[i]])
    f_front = bm_gm.faces.new(list(reversed(vf_gm)))
    f_back = bm_gm.faces.new(vb_gm)
    bmesh.ops.triangulate(bm_gm, faces=[f_front, f_back], quad_method='BEAUTY', ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(bm_gm, faces=bm_gm.faces)
    mesh_gm = bpy.data.meshes.new(f"{prefix}_Spinal_Cord_GM_mesh")
    bm_gm.to_mesh(mesh_gm)
    bm_gm.free()

    for poly in mesh_gm.polygons:
        poly.use_smooth = True
    mesh_gm.update()

    obj_gm = bpy.data.objects.new(f"{prefix}_Spinal_Cord_Gray_Matter", mesh_gm)
    bpy.context.collection.objects.link(obj_gm)
    obj_gm.data.materials.append(gm_mat)
    objs.append(obj_gm)

    # 3. Central Canal (Cerebrospinal Fluid Lumen)
    canal = kit.primitive_object(
        f"{prefix}_Central_Canal", "cylinder", canal_mat,
        size=(0.0024, 0.0024, depth + 0.001),
        location=(cx, cy, cz),
        rotation_euler=(math.pi / 2.0, 0.0, 0.0)
    )
    objs.append(canal)

    # 4. Dorsal and Ventral Nerve Roots (Bilateral rootlets exiting spinal cord)
    root_mat = wm_mat
    # Right dorsal rootlet (+X, +Z)
    r_dorsal_pts = [(cx + 0.013, cy, cz + 0.019), (cx + 0.026, cy, cz + 0.022), (cx + 0.038, cy, cz + 0.020)]
    # Right ventral rootlet (+X, -Z)
    r_ventral_pts = [(cx + 0.014, cy, cz - 0.015), (cx + 0.025, cy, cz - 0.018), (cx + 0.038, cy, cz - 0.012)]
    d_root = create_smooth_tube(f"{prefix}_Dorsal_Root", r_dorsal_pts, radius=0.0016, material=root_mat)
    v_root = create_smooth_tube(f"{prefix}_Ventral_Root", r_ventral_pts, radius=0.0016, material=root_mat)
    objs.extend([d_root, v_root])

    return objs


def build_stimulus_and_receptor(prefix, mats):
    """
    Creates the hot cooking pan with handle and anatomical finger pad with dermal receptors.
    """
    objs = []

    # 1. Hot Cooking Pan
    pan_mat = mats["pan"]
    heat_mat = mats["heat"]

    # Pan base & rim
    pan_body = kit.primitive_object(
        f"{prefix}_Pan_Body", "cylinder", pan_mat,
        size=(0.065, 0.065, 0.022),
        location=(-0.115, 0.0, -0.055)
    )
    # Pan inner cavity (recessed cylinder)
    pan_rim = kit.primitive_object(
        f"{prefix}_Pan_Hot_Rim", "cylinder", heat_mat,
        size=(0.068, 0.068, 0.004),
        location=(-0.115, 0.0, -0.044)
    )
    # Pan handle
    pan_handle = kit.primitive_object(
        f"{prefix}_Pan_Handle", "cylinder", pan_mat,
        size=(0.010, 0.010, 0.075),
        location=(-0.170, 0.0, -0.050),
        rotation_euler=(0.0, math.pi / 2.0, 0.0)
    )
    objs.extend([pan_body, pan_rim, pan_handle])

    # 2. Human Finger Pad & Dermal Receptors
    finger_mat = mats["skin"]
    # Finger body (phalanx)
    finger = kit.primitive_object(
        f"{prefix}_Finger_Receptor", "uv_sphere", finger_mat,
        size=(0.022, 0.018, 0.032),
        location=(-0.108, 0.0, -0.028),
        rotation_euler=(0.0, 0.22, 0.0)
    )
    # Fingernail plate
    nail = kit.primitive_object(
        f"{prefix}_Fingernail", "cylinder", mats["nail"],
        size=(0.011, 0.009, 0.003),
        location=(-0.112, 0.0, -0.017),
        rotation_euler=(0.0, 0.22, 0.0)
    )
    objs.extend([finger, nail])

    # Dermal pain/temperature sensory receptor terminals inside skin
    receptor_bulb = kit.primitive_object(
        f"{prefix}_Dermal_Receptor_Knob", "uv_sphere", mats["sensory"],
        size=(0.0045, 0.0045, 0.0045),
        location=(-0.106, 0.0, -0.036)
    )
    objs.append(receptor_bulb)

    return objs


def build_effector_muscle(prefix, mats):
    """
    Creates an anatomical fusiform arm flexor muscle (biceps brachii) with tendinous ends.
    """
    objs = []
    muscle_mat = mats["muscle"]
    tendon_mat = mats["tendon"]

    # Central belly (contracting flexor muscle)
    belly = kit.primitive_object(
        f"{prefix}_Muscle_Belly", "uv_sphere", muscle_mat,
        size=(0.042, 0.024, 0.024),
        location=(-0.058, 0.0, 0.008),
        rotation_euler=(0.0, 0.28, 0.0)
    )
    # Tendon at distal end
    tendon_dist = kit.primitive_object(
        f"{prefix}_Tendon_Distal", "cylinder", tendon_mat,
        size=(0.007, 0.007, 0.018),
        location=(-0.076, 0.0, -0.002),
        rotation_euler=(0.0, 0.45, 0.0)
    )
    # Tendon at proximal end
    tendon_prox = kit.primitive_object(
        f"{prefix}_Tendon_Proximal", "cylinder", tendon_mat,
        size=(0.007, 0.007, 0.018),
        location=(-0.040, 0.0, 0.018),
        rotation_euler=(0.0, 0.45, 0.0)
    )
    objs.extend([belly, tendon_dist, tendon_prox])

    # Neuromuscular junction (motor end-plate branching onto muscle fibers)
    nmj = kit.primitive_object(
        f"{prefix}_Neuromuscular_End_Plate", "uv_sphere", mats["motor"],
        size=(0.0055, 0.004, 0.004),
        location=(-0.052, 0.004, 0.012)
    )
    objs.append(nmj)

    return objs


def build_neural_pathways(prefix, cord_x, cord_y, cord_z, mats):
    """
    Builds the complete sensory, relay, and motor nerve tracts with DRG and brain message branch.
    """
    objs = []

    # 1. Afferent Sensory Nerve Tract (Cobalt Blue)
    # Pathway: Finger dermal receptor -> arm nerve bundle -> dorsal root ganglion -> dorsal root -> dorsal horn
    sensory_pts = [
        (-0.106, 0.0, -0.036),  # From cutaneous receptor
        (-0.082, 0.008, -0.008),
        (-0.045, -0.006, 0.028),
        ( 0.005, 0.008, 0.050),
        ( 0.038, 0.002, 0.056),  # Dorsal root entry
        (cord_x + 0.013, cord_y, cord_z + 0.019),  # Synapse in dorsal horn
    ]
    sensory_nerve = create_smooth_tube(
        f"{prefix}_Sensory_Nerve_Tract", sensory_pts, radius=0.0018, material=mats["sensory"]
    )
    objs.append(sensory_nerve)

    # Dorsal Root Ganglion (DRG): Swollen ganglion containing sensory pseudounipolar cell bodies
    drg = kit.primitive_object(
        f"{prefix}_Dorsal_Root_Ganglion", "uv_sphere", mats["sensory"],
        size=(0.0085, 0.0075, 0.0075),
        location=(0.016, 0.006, 0.053)
    )
    objs.append(drg)

    # Directional impulse indicators on sensory nerve (impulse toward spinal cord)
    s_chevron1 = kit.primitive_object(
        f"{prefix}_Sensory_Impulse_1", "cone", mats["sensory_pulse"],
        size=(0.004, 0.004, 0.006),
        location=(-0.065, 0.002, 0.010),
        rotation_euler=(0.0, -math.pi / 3.2, 0.0)
    )
    objs.append(s_chevron1)

    # 2. Interneuron (Relay Neuron, Amber-Yellow)
    # Synaptic connection from dorsal horn to ventral horn within gray matter
    relay_pts = [
        (cord_x + 0.013, cord_y, cord_z + 0.019),  # Dorsal horn synapse
        (cord_x + 0.008, cord_y, cord_z + 0.005),  # Relay soma in gray matter
        (cord_x + 0.014, cord_y, cord_z - 0.015),  # Ventral horn motor synapse
    ]
    relay_nerve = create_smooth_tube(
        f"{prefix}_Relay_Interneuron", relay_pts, radius=0.0016, material=mats["relay"]
    )
    relay_soma = kit.primitive_object(
        f"{prefix}_Relay_Soma", "uv_sphere", mats["relay"],
        size=(0.0042, 0.0042, 0.0042),
        location=(cord_x + 0.008, cord_y, cord_z + 0.005)
    )
    objs.extend([relay_nerve, relay_soma])

    # Ascending axon tract ("Message to brain" per NCERT Fig 7.2)
    brain_pts = [
        (cord_x + 0.008, cord_y, cord_z + 0.005),
        (cord_x + 0.008, cord_y, cord_z + 0.024),
        (cord_x + 0.008, cord_y, cord_z + 0.046),  # Ascends superiorly to brainstem
    ]
    to_brain = create_smooth_tube(
        f"{prefix}_Message_To_Brain_Tract", brain_pts, radius=0.0015, material=mats["brain_tract"]
    )
    brain_arrow = kit.primitive_object(
        f"{prefix}_Brain_Arrow", "cone", mats["brain_tract"],
        size=(0.004, 0.004, 0.007),
        location=(cord_x + 0.008, cord_y, cord_z + 0.046),
        rotation_euler=(0.0, 0.0, 0.0)
    )
    objs.extend([to_brain, brain_arrow])

    # 3. Efferent Motor Nerve Tract (Crimson Red)
    # Pathway: Ventral horn motor soma -> ventral root -> spinal nerve trunk -> muscle neuromuscular junction
    motor_pts = [
        (cord_x + 0.014, cord_y, cord_z - 0.015),  # Ventral horn motor soma
        ( 0.038, -0.002, 0.015),  # Ventral root exit
        ( 0.008, -0.008, 0.018),
        (-0.025,  0.006, 0.016),
        (-0.052,  0.004, 0.012),  # Neuromuscular end-plate on muscle
    ]
    motor_nerve = create_smooth_tube(
        f"{prefix}_Motor_Nerve_Tract", motor_pts, radius=0.0018, material=mats["motor"]
    )
    motor_soma = kit.primitive_object(
        f"{prefix}_Motor_Soma", "uv_sphere", mats["motor"],
        size=(0.0045, 0.0045, 0.0045),
        location=(cord_x + 0.014, cord_y, cord_z - 0.015)
    )
    objs.extend([motor_nerve, motor_soma])

    # Directional impulse indicator on motor nerve (impulse toward effector muscle)
    m_chevron1 = kit.primitive_object(
        f"{prefix}_Motor_Impulse_1", "cone", mats["motor_pulse"],
        size=(0.004, 0.004, 0.006),
        location=(-0.010, -0.002, 0.017),
        rotation_euler=(0.0, math.pi / 2.2, 0.0)
    )
    objs.append(m_chevron1)

    return objs


def build_reflex_arc_model(prefix="Full", is_section=False):
    """
    Constructs the complete Reflex Arc hierarchy.
    """
    # Materials
    mats = {
        "pan": create_pbr_mat(f"{prefix}_mat_pan", (0.16, 0.17, 0.19), roughness=0.32, metallic=0.88),
        "heat": create_pbr_mat(f"{prefix}_mat_heat", (0.95, 0.28, 0.12), roughness=0.25, emission=(1.0, 0.35, 0.12), emission_strength=2.5),
        "skin": create_pbr_mat(f"{prefix}_mat_skin", (0.88, 0.72, 0.60), roughness=0.42, subsurface=0.25),
        "nail": create_pbr_mat(f"{prefix}_mat_nail", (0.94, 0.82, 0.78), roughness=0.22),
        "sensory": create_pbr_mat(f"{prefix}_mat_sensory", (0.15, 0.48, 0.95), roughness=0.30, emission=(0.15, 0.48, 0.95), emission_strength=1.6),
        "sensory_pulse": create_pbr_mat(f"{prefix}_mat_sensory_pulse", (0.40, 0.75, 1.0), roughness=0.20, emission=(0.40, 0.75, 1.0), emission_strength=3.0),
        "relay": create_pbr_mat(f"{prefix}_mat_relay", (0.96, 0.76, 0.16), roughness=0.28, emission=(0.96, 0.76, 0.16), emission_strength=1.8),
        "brain_tract": create_pbr_mat(f"{prefix}_mat_brain", (0.98, 0.85, 0.30), roughness=0.25, emission=(0.98, 0.85, 0.30), emission_strength=2.2),
        "motor": create_pbr_mat(f"{prefix}_mat_motor", (0.92, 0.18, 0.15), roughness=0.30, emission=(0.92, 0.18, 0.15), emission_strength=1.6),
        "motor_pulse": create_pbr_mat(f"{prefix}_mat_motor_pulse", (1.0, 0.45, 0.40), roughness=0.20, emission=(1.0, 0.45, 0.40), emission_strength=3.0),
        "cord_wm": create_pbr_mat(f"{prefix}_mat_cord_wm", (0.92, 0.90, 0.84), roughness=0.38, subsurface=0.20),
        "cord_gm": create_pbr_mat(f"{prefix}_mat_cord_gm", (0.68, 0.48, 0.46), roughness=0.45, subsurface=0.22),
        "canal": create_pbr_mat(f"{prefix}_mat_canal", (0.28, 0.30, 0.35), roughness=0.25),
        "muscle": create_pbr_mat(f"{prefix}_mat_muscle", (0.80, 0.20, 0.24), roughness=0.38, subsurface=0.28),
        "tendon": create_pbr_mat(f"{prefix}_mat_tendon", (0.94, 0.92, 0.86), roughness=0.25, subsurface=0.15),
    }

    objects = []

    cord_x = 0.065
    cord_y = 0.0
    cord_z = 0.032
    cord_depth = 0.038

    # 1. Spinal Cord Transverse Cross-Section
    cord_objs = create_anatomical_spinal_cord(
        prefix, cord_x, cord_y, cord_z, cord_depth,
        mats["cord_wm"], mats["cord_gm"], mats["canal"]
    )
    objects.extend(cord_objs)

    # 2. Stimulus and Receptor (Pan + Finger)
    stim_objs = build_stimulus_and_receptor(prefix, mats)
    objects.extend(stim_objs)

    # 3. Effector Muscle
    muscle_objs = build_effector_muscle(prefix, mats)
    objects.extend(muscle_objs)

    # 4. Neural Circuit Pathways (Sensory, Relay, Brain, Motor)
    neural_objs = build_neural_pathways(prefix, cord_x, cord_y, cord_z, mats)
    objects.extend(neural_objs)

    return objects


def build_reflex_arc_dual_scene():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()

    coll_full = bpy.data.collections.new("ReflexArc_Full")
    coll_section = bpy.data.collections.new("ReflexArc_Section")
    root_coll = bpy.context.scene.collection
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)

    print("Building ReflexArc_Full...")
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["ReflexArc_Full"]
    full_objs = build_reflex_arc_model(prefix="Full", is_section=False)
    for obj in full_objs:
        if obj.name in root_coll.objects:
            root_coll.objects.unlink(obj)
        if obj.name not in coll_full.objects:
            coll_full.objects.link(obj)

    print("Building ReflexArc_Section...")
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["ReflexArc_Section"]
    section_objs = build_reflex_arc_model(prefix="Sec", is_section=True)
    for obj in section_objs:
        if obj.name in root_coll.objects:
            root_coll.objects.unlink(obj)
        if obj.name not in coll_section.objects:
            coll_section.objects.link(obj)

    # Studio World & Environment
    world = bpy.data.worlds.new("ReflexArc_World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.015, 0.020, 0.028, 1.0)
    bg.inputs["Strength"].default_value = 0.40
    bpy.context.scene.world = world

    # Macro Studio Lighting (calibrated energies for ~0.25m neural circuit)
    key_data = bpy.data.lights.new("Reflex_KeyLight", 'AREA')
    key_data.energy = 8.5
    key_data.color = (1.0, 0.96, 0.92)
    key_data.size = 0.45
    key_light = bpy.data.objects.new("Reflex_KeyLight", key_data)
    key_light.location = (0.05, -0.55, 0.35)
    key_light.rotation_euler = (Vector((0.0, 0.0, 0.01)) - key_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(key_light)

    fill_data = bpy.data.lights.new("Reflex_FillLight", 'AREA')
    fill_data.energy = 4.5
    fill_data.color = (0.88, 0.93, 1.0)
    fill_data.size = 0.55
    fill_light = bpy.data.objects.new("Reflex_FillLight", fill_data)
    fill_light.location = (-0.35, -0.45, 0.25)
    fill_light.rotation_euler = (Vector((0.0, 0.0, 0.01)) - fill_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(fill_light)

    rim_data = bpy.data.lights.new("Reflex_RimLight", 'AREA')
    rim_data.energy = 7.0
    rim_data.color = (0.90, 0.95, 1.0)
    rim_data.size = 0.40
    rim_light = bpy.data.objects.new("Reflex_RimLight", rim_data)
    rim_light.location = (0.02, 0.50, 0.30)
    rim_light.rotation_euler = (Vector((0.0, 0.0, 0.01)) - rim_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(rim_light)

    bounce_data = bpy.data.lights.new("Reflex_BounceLight", 'AREA')
    bounce_data.energy = 2.2
    bounce_data.color = (1.0, 0.88, 0.82)
    bounce_data.size = 0.40
    bounce_light = bpy.data.objects.new("Reflex_BounceLight", bounce_data)
    bounce_light.location = (-0.02, -0.25, -0.25)
    bounce_light.rotation_euler = (Vector((0.0, 0.0, 0.01)) - bounce_light.location).to_track_quat("-Z", "Y").to_euler()
    root_coll.objects.link(bounce_light)

    bpy.context.scene.view_settings.view_transform = 'AgX'
    try:
        bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    except TypeError:
        bpy.context.scene.view_settings.look = 'High Contrast'

    cam_data = bpy.data.cameras.new("Reflex_Camera")
    cam_data.lens = 48.0
    cam_obj = bpy.data.objects.new("Reflex_Camera", cam_data)
    root_coll.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Full overview framing: captures hot pan on left (-0.15) to spinal cord on right (+0.10)
    target = Vector((-0.025, 0.0, 0.005))
    cam_obj.location = Vector((-0.025, -0.44, 0.14))
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
    bpy.context.view_layer.layer_collection.children["ReflexArc_Full"].exclude = False
    bpy.context.view_layer.layer_collection.children["ReflexArc_Section"].exclude = True
    kit.render_preview(out / "preview.png")
    print(f"Rendered: {out / 'preview.png'}")

    print("Rendering Section Preview...")
    bpy.context.view_layer.layer_collection.children["ReflexArc_Full"].exclude = True
    bpy.context.view_layer.layer_collection.children["ReflexArc_Section"].exclude = False
    # Zoomed directly onto the spinal cord transverse section and relay synapse
    target_sec = Vector((0.065, 0.0, 0.032))
    cam_obj.location = Vector((0.065, -0.22, 0.09))
    cam_dir = target_sec - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()
    kit.render_preview(out / "preview_section.png")
    print(f"Rendered: {out / 'preview_section.png'}")

    bpy.context.view_layer.layer_collection.children["ReflexArc_Full"].exclude = False
    bpy.context.view_layer.layer_collection.children["ReflexArc_Section"].exclude = False
    cam_obj.location = Vector((-0.025, -0.44, 0.14))
    cam_dir = target - cam_obj.location
    cam_obj.rotation_euler = cam_dir.to_track_quat("-Z", "Y").to_euler()
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print("=== REFLEX ARC BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    build_reflex_arc_dual_scene()
