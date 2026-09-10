"""
build_reflex_arc.py — Reflex Arc Neural Circuit (Receptor to Effector)
CBSE Class 10 Biology, Chapter 7: Control and Coordination (Fig 7.2)

Key Features:
- Stimulus & Receptor: Hot pan edge and human finger skin pain/heat receptor.
- Afferent Sensory Pathway: Smooth continuous blue sensory nerve tract with dorsal root ganglion (DRG)
  entering the spinal cord through the dorsal root.
- Spinal Cord Transverse Cross-Section: Oval white matter cylinder enclosing authentic
  butterfly-shaped gray matter (slender dorsal horn, broad ventral horn, central canal).
- Interneuron / Relay Neuron: Synaptic relay within spinal gray matter, including ascending
  relay branch transmitting messages superiorly to the brain.
- Efferent Motor Pathway: Smooth continuous red motor nerve tract exiting through the ventral root
  and terminating at the effector muscle neuromuscular junction.
- Effector Organ: Arm flexor muscle contracting to withdraw the hand from the painful stimulus.
- Clean manifold geometry throughout.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'reflex-arc'


def create_butterfly_gray_matter(name, cx, cy, cz, depth_y, mat):
    """
    Creates an anatomically authentic butterfly-shaped spinal gray matter mesh
    with slender dorsal horns (+Z), broad rounded ventral horns (-Z), and central canal.
    """
    bm = bmesh.new()

    # 2D contour points in (dx, dz) for Right Wing and Left Wing
    # Right half profile (closed clockwise loop)
    r_pts = [
        (0.002, 0.003),
        (0.005, 0.008),
        (0.010, 0.014),
        (0.014, 0.018),   # Dorsal horn apex
        (0.011, 0.018),
        (0.007, 0.011),
        (0.003, 0.003),   # Central commissure
        (0.003, -0.003),
        (0.008, -0.008),
        (0.015, -0.014),  # Ventral horn apex
        (0.016, -0.011),
        (0.012, -0.004),
        (0.007, -0.001),  # Lateral horn waist
        (0.004, 0.002),
    ]

    # Left half profile (mirrored across X)
    l_pts = [(-x, z) for x, z in r_pts]

    # Combine into single continuous butterfly perimeter
    perimeter = []
    # Right wing loop
    for x, z in r_pts:
        perimeter.append((x, z))
    # Left wing loop (reversed order for clean manifold face)
    for x, z in reversed(l_pts):
        perimeter.append((x, z))

    # Front slice (y = -depth_y / 2) and Back slice (y = depth_y / 2)
    front_verts = []
    back_verts = []
    y_front = cy - depth_y * 0.5
    y_back = cy + depth_y * 0.5

    for x, z in perimeter:
        front_verts.append(bm.verts.new((cx + x, y_front, cz + z)))
        back_verts.append(bm.verts.new((cx + x, y_back, cz + z)))

    # Connect side quads
    n_pts = len(perimeter)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm.faces.new([front_verts[i], front_verts[next_i], back_verts[next_i], back_verts[i]])

    # Cap front and back faces via fan or fill
    bm.faces.new(list(reversed(front_verts)))
    bm.faces.new(back_verts)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(mat)
    return obj


def build_reflex_arc():
    # Calibrated PBR Materials with emission for neural signal tracks
    skin_mat = kit.add_tissue_material('skin-receptor', base_color=(0.88, 0.72, 0.62, 1.0), roughness=0.45,
                                       subsurface_weight=0.25)
    sensory_mat = kit.add_material('nerve-sensory-blue', (0.15, 0.45, 0.95), metallic=0.2, roughness=0.3)
    sensory_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.15, 0.45, 0.95, 1.0)
    sensory_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.0

    motor_mat = kit.add_material('nerve-motor-red', (0.92, 0.18, 0.15), metallic=0.2, roughness=0.3)
    motor_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.92, 0.18, 0.15, 1.0)
    motor_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 2.0

    relay_mat = kit.add_material('nerve-relay-yellow', (0.95, 0.75, 0.15), metallic=0.1, roughness=0.3)
    relay_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].default_value = (0.95, 0.75, 0.15, 1.0)
    relay_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 1.8

    white_matter_mat = kit.add_tissue_material('cord-white-matter', base_color=(0.92, 0.90, 0.84, 1.0), roughness=0.40,
                                               subsurface_weight=0.30)
    gray_matter_mat = kit.add_tissue_material('cord-gray-matter', base_color=(0.68, 0.48, 0.45, 1.0), roughness=0.50,
                                              subsurface_weight=0.35)
    canal_mat = kit.add_material('central-canal', (0.35, 0.35, 0.40), metallic=0.1, roughness=0.3)
    muscle_mat = kit.add_tissue_material('effector-muscle', base_color=(0.78, 0.22, 0.25, 1.0), roughness=0.40,
                                         subsurface_weight=0.35)
    pan_mat = kit.add_machined_metal_material('hot-pan-metal', (0.15, 0.16, 0.18), metallic=0.9, roughness=0.3)

    objects = []

    # 1. Hot Stimulus (Hot pan at x = -0.10m, z = -0.05m)
    hot_pan = kit.primitive_object(
        f'{ASSET_ID}-hot-object', 'cube', pan_mat,
        size=(0.045, 0.045, 0.015),
        location=(-0.10, 0.0, -0.05)
    )
    objects.append(hot_pan)

    # 2. Skin Receptor (Finger pad touching hot stimulus)
    finger = kit.primitive_object(
        f'{ASSET_ID}-finger-receptor', 'uv_sphere', skin_mat,
        size=(0.024, 0.020, 0.032),
        location=(-0.10, 0.0, -0.030)
    )
    objects.append(finger)

    # 3. Spinal Cord Transverse Cross-Section at x = +0.07m, z = 0.04m
    cord_x = 0.070
    cord_z = 0.040
    cord_depth = 0.042

    # White matter outer cylinder
    cord_wm = kit.primitive_object(
        f'{ASSET_ID}-cord-wm', 'cylinder', white_matter_mat,
        size=(0.075, 0.055, cord_depth),
        location=(cord_x, 0.0, cord_z),
        rotation_euler=(math.pi / 2.0, 0.0, 0.0)
    )
    objects.append(cord_wm)

    # Authentic Butterfly-shaped gray matter interior
    gray_matter = create_butterfly_gray_matter(
        f'{ASSET_ID}-gray-matter-butterfly', cord_x, 0.0, cord_z, cord_depth + 0.0005, gray_matter_mat
    )
    objects.append(gray_matter)

    # Central Canal of spinal cord (small cerebrospinal fluid-filled lumen)
    central_canal = kit.primitive_object(
        f'{ASSET_ID}-central-canal', 'cylinder', canal_mat,
        size=(0.0028, 0.0028, cord_depth + 0.001),
        location=(cord_x, 0.0, cord_z),
        rotation_euler=(math.pi / 2.0, 0.0, 0.0)
    )
    objects.append(central_canal)

    # 4. Afferent Sensory Neuron (Smooth continuous blue tract from receptor to dorsal horn)
    sensory_pts = [
        (-0.100, 0.000, -0.020),
        (-0.070, 0.010,  0.010),
        (-0.030, -0.010, 0.040),
        ( 0.010, 0.010,  0.055),  # Dorsal root ganglion site
        ( 0.045, 0.005,  0.055),  # Enters dorsal root
        ( 0.060, 0.000,  0.052),  # Synapses in dorsal horn of gray matter
    ]
    sensory_nerve = kit.create_smooth_tube(
        f'{ASSET_ID}-sensory-nerve', sensory_pts, radius=0.0022, cap_ends=True, material=sensory_mat
    )
    objects.append(sensory_nerve)

    # Dorsal Root Ganglion (DRG) sensory neuron cell body swelling
    drg = kit.primitive_object(
        f'{ASSET_ID}-drg', 'uv_sphere', sensory_mat,
        size=(0.010, 0.010, 0.010),
        location=(0.010, 0.010, 0.055)
    )
    objects.append(drg)

    # 5. Relay Neuron / Interneuron (Synaptic relay inside gray matter)
    relay_pts = [
        (0.060, 0.0, 0.052),  # Synapse from sensory axon in dorsal horn
        (0.065, 0.0, 0.040),  # Interneuron body in gray commissure
        (0.060, 0.0, 0.028),  # Synapse onto motor neuron in ventral horn
    ]
    relay = kit.create_smooth_tube(
        f'{ASSET_ID}-relay-neuron', relay_pts, radius=0.0020, cap_ends=True, material=relay_mat
    )
    objects.append(relay)

    # Ascending tract to brain ("Message to brain" per NCERT Class 10 Fig 7.2)
    brain_pts = [
        (0.065, 0.0, 0.040),
        (0.066, 0.0, 0.062),
        (0.068, 0.0, 0.085),  # Ascends toward brain stem
    ]
    to_brain = kit.create_smooth_tube(
        f'{ASSET_ID}-message-to-brain', brain_pts, radius=0.0018, cap_ends=True, material=relay_mat
    )
    objects.append(to_brain)

    # 6. Efferent Motor Neuron (Smooth continuous red tract from ventral horn to effector muscle)
    motor_pts = [
        ( 0.060,  0.000, 0.028),  # Emerges from motor soma in ventral horn
        ( 0.045, -0.005, 0.026),  # Exits through ventral root
        ( 0.010, -0.010, 0.022),
        (-0.030,  0.010, 0.012),
        (-0.060,  0.000, 0.005),  # Reaches neuromuscular junction on muscle
    ]
    motor_nerve = kit.create_smooth_tube(
        f'{ASSET_ID}-motor-nerve', motor_pts, radius=0.0022, cap_ends=True, material=motor_mat
    )
    objects.append(motor_nerve)

    # 7. Effector Muscle (Arm flexor muscle contracting to withdraw hand)
    muscle = kit.primitive_object(
        f'{ASSET_ID}-effector-muscle', 'uv_sphere', muscle_mat,
        size=(0.045, 0.028, 0.028),
        location=(-0.065, 0.0, 0.005),
        rotation_euler=(0.0, 0.25, 0.0)
    )
    objects.append(muscle)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_reflex_arc()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')


if __name__ == '__main__':
    main()
