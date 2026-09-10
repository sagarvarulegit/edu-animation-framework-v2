"""
build_neuron.py — High-Fidelity Multipolar Motor Neuron
CBSE Class 10 Biology, Chapter 7: Control and Coordination
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "neuron"


def build_neuron():
    # 1. Authentic Biological Materials
    soma_mat = kit.add_material("neuron-soma", (0.92, 0.78, 0.55), metallic=0.05, roughness=0.55)
    nucleus_mat = kit.add_material("neuron-nucleus", (0.55, 0.22, 0.58), metallic=0.1, roughness=0.45)
    nucleolus_mat = kit.add_material("neuron-nucleolus", (0.35, 0.10, 0.38), metallic=0.1, roughness=0.40)
    dendrite_mat = kit.add_material("neuron-dendrite", (0.88, 0.72, 0.50), metallic=0.05, roughness=0.60)
    axon_mat = kit.add_material("neuron-axon", (0.45, 0.70, 0.90), metallic=0.1, roughness=0.45)
    myelin_mat = kit.add_material("neuron-myelin", (0.96, 0.94, 0.88), metallic=0.05, roughness=0.35)
    terminal_mat = kit.add_material("neuron-terminal", (0.88, 0.45, 0.35), metallic=0.1, roughness=0.50)
    bouton_mat = kit.add_material("neuron-bouton", (0.92, 0.35, 0.28), metallic=0.15, roughness=0.40)

    objects = []

    # 2. Multipolar Cell Body (Soma) — Organic contoured shape
    soma_obj = kit.primitive_object(f"{ASSET_ID}-soma", "uv_sphere", soma_mat,
                                    size=(0.026, 0.024, 0.022),
                                    location=(-0.040, 0.0, 0.0))
    objects.append(soma_obj)

    # 3. Prominent Nucleus & Dark Nucleolus (Slightly protruding/visible through translucent cytoplasm)
    nucleus_obj = kit.primitive_object(f"{ASSET_ID}-nucleus", "uv_sphere", nucleus_mat,
                                       size=(0.012, 0.012, 0.012),
                                       location=(-0.040, -0.002, 0.003))
    nucleolus_obj = kit.primitive_object(f"{ASSET_ID}-nucleolus", "uv_sphere", nucleolus_mat,
                                         size=(0.0045, 0.0045, 0.0045),
                                         location=(-0.040, -0.004, 0.004))
    objects.extend([nucleus_obj, nucleolus_obj])

    # 4. Dendritic Arbor — Radiating tapering primary and secondary branches
    dendrite_branches = [
        # (angle_deg, elevation_deg, length, thickness)
        (130, 15, 0.032, 0.0032),
        (155, -20, 0.036, 0.0034),
        (180, 0, 0.038, 0.0035),
        (205, 25, 0.035, 0.0032),
        (230, -15, 0.030, 0.0030),
        (100, 30, 0.026, 0.0028),
        (260, -25, 0.028, 0.0028),
    ]

    for i, (az, el, length, thick) in enumerate(dendrite_branches):
        rad_az = math.radians(az)
        rad_el = math.radians(el)
        dx = length * math.cos(rad_el) * math.cos(rad_az)
        dy = length * math.cos(rad_el) * math.sin(rad_az)
        dz = length * math.sin(rad_el)
        mid_x = -0.040 + dx * 0.5
        mid_y = dy * 0.5
        mid_z = dz * 0.5
        
        # Primary dendrite branch
        dend = kit.primitive_object(f"{ASSET_ID}-dendrite-pri-{i}", "cylinder", dendrite_mat,
                                   size=(thick, thick, length),
                                   location=(mid_x, mid_y, mid_z))
        # Orient along direction
        dir_vec = Vector((dx, dy, dz)).normalized()
        dend.rotation_euler = dir_vec.to_track_quat("Z", "Y").to_euler()
        objects.append(dend)

        # Secondary sub-branch off primary
        sub_len = length * 0.55
        sub_thick = thick * 0.65
        sub_dx = sub_len * math.cos(rad_el + 0.3) * math.cos(rad_az + 0.35)
        sub_dy = sub_len * math.cos(rad_el + 0.3) * math.sin(rad_az + 0.35)
        sub_dz = sub_len * math.sin(rad_el + 0.3)
        sub_x = -0.040 + dx * 0.7 + sub_dx * 0.5
        sub_y = dy * 0.7 + sub_dy * 0.5
        sub_z = dz * 0.7 + sub_dz * 0.5
        sub_dend = kit.primitive_object(f"{ASSET_ID}-dendrite-sec-{i}", "cylinder", dendrite_mat,
                                       size=(sub_thick, sub_thick, sub_len),
                                       location=(sub_x, sub_y, sub_z))
        sub_dir = Vector((sub_dx, sub_dy, sub_dz)).normalized()
        sub_dend.rotation_euler = sub_dir.to_track_quat("Z", "Y").to_euler()
        objects.append(sub_dend)

    # 5. Axon Hillock (Smooth tapered transition from soma into axon)
    hillock = kit.primitive_object(f"{ASSET_ID}-hillock", "cone", soma_mat,
                                   size=(0.008, 0.008, 0.016),
                                   location=(-0.024, 0.0, 0.0),
                                   rotation_euler=(0.0, -math.pi / 2, 0.0))
    objects.append(hillock)

    # 6. Long Axon Core Fiber (Carries nerve impulses toward terminals)
    axon_len = 0.130
    axon_core = kit.primitive_object(f"{ASSET_ID}-axon-core", "cylinder", axon_mat,
                                     size=(0.0030, 0.0030, axon_len),
                                     location=(0.045, 0.0, 0.0),
                                     rotation_euler=(0.0, math.pi / 2, 0.0))
    objects.append(axon_core)

    # 7. Segmented Myelin Sheaths with Nodes of Ranvier (Cylindrical Schwann cell wrappings)
    num_sheaths = 6
    sheath_spacing = 0.018
    sheath_len = 0.014
    for i in range(num_sheaths):
        sx = -0.008 + i * sheath_spacing
        # Cylindrical Schwann cell sheath along axon (X-axis)
        sheath = kit.primitive_object(
            f"{ASSET_ID}-myelin-{i}", "cylinder", myelin_mat,
            size=(0.0075, 0.0075, sheath_len),
            location=(sx, 0.0, 0.0),
            rotation_euler=(0.0, math.pi / 2, 0.0)
        )
        # Flattened Schwann cell nucleus on outer sheath surface
        schwann_nuc = kit.primitive_object(
            f"{ASSET_ID}-schwann-nucleus-{i}", "uv_sphere", nucleus_mat,
            size=(0.0035, 0.0020, 0.0016),
            location=(sx, 0.0, 0.0038)
        )
        objects.extend([sheath, schwann_nuc])

    # 8. Axon Terminal Arborization (Telodendria) & Synaptic Boutons
    term_start_x = -0.008 + num_sheaths * sheath_spacing - 0.004
    terminals = [
        (0.016, 0.010, 0.008),
        (0.020, -0.008, 0.006),
        (0.018, 0.005, -0.010),
        (0.022, -0.006, -0.008),
    ]

    for i, (tx, ty, tz) in enumerate(terminals):
        end_x = term_start_x + tx
        end_y = ty
        end_z = tz
        mid_x = (term_start_x + end_x) / 2
        mid_y = end_y / 2
        mid_z = end_z / 2
        t_len = math.sqrt(tx**2 + ty**2 + tz**2)
        
        # Terminal branch wire
        t_branch = kit.primitive_object(f"{ASSET_ID}-terminal-{i}", "cylinder", terminal_mat,
                                       size=(0.0020, 0.0020, t_len),
                                       location=(mid_x, mid_y, mid_z))
        t_dir = Vector((tx, ty, tz)).normalized()
        t_branch.rotation_euler = t_dir.to_track_quat("Z", "Y").to_euler()
        objects.append(t_branch)

        # Bulbous Synaptic Bouton / Knob at the terminal tip
        bouton = kit.primitive_object(f"{ASSET_ID}-bouton-{i}", "uv_sphere", bouton_mat,
                                      size=(0.0055, 0.0055, 0.0055),
                                      location=(end_x, end_y, end_z))
        objects.append(bouton)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_neuron()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
