"""
build_bulb.py — High-Fidelity Incandescent Light Bulb (Edison Screw E27)
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bulb"


def build_bulb():
    # 1. Authentic Materials
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.98, 0.99, 1.0), ior=1.50, roughness=0.015)
    brass_mat = kit.add_machined_metal_material(f"{ASSET_ID}-brass-base", (0.86, 0.70, 0.28), metallic=0.92, roughness=0.28)
    tungsten_mat = kit.add_machined_metal_material(f"{ASSET_ID}-filament", (0.95, 0.85, 0.40), metallic=0.88, roughness=0.20)
    tungsten_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (1.0, 0.82, 0.40, 1.0)
    tungsten_mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3.5
    lead_wire_mat = kit.add_machined_metal_material(f"{ASSET_ID}-lead-wire", (0.75, 0.75, 0.78), metallic=0.95, roughness=0.25)
    insulator_mat = kit.add_material(f"{ASSET_ID}-black-glass", (0.05, 0.05, 0.06), metallic=0.1, roughness=0.25)

    objects = []

    # 2. Authentic Teardrop-Spherical Glass Envelope Profile
    # Parametric classic A19 / E27 bulb curve (r in meters, z in meters)
    globe_profile = [
        (0.000, 0.108),          # Closed rounded apex
        (0.004, 0.1078),
        (0.012, 0.105),
        (0.020, 0.098),
        (0.028, 0.086),          # Maximum globe diameter (60mm / r=30mm)
        (0.030, 0.075),
        (0.026, 0.060),          # Tapering neck
        (0.018, 0.046),
        (0.0145, 0.036),
        (0.0135, 0.028),         # Base transition into brass cap
        (0.000, 0.028)
    ]
    globe_obj = kit.lathe_object(f"{ASSET_ID}-globe", globe_profile, segments=64, material=glass_mat)
    objects.append(globe_obj)

    # 3. Threaded Edison Brass Screw Base (E27)
    base_profile = [
        (0.000, 0.003),
        (0.006, 0.003),          # Bottom contact point
        (0.008, 0.005),
        (0.013, 0.007),          # Black glass insulator ring
        (0.0132, 0.010),         # Thread start
        (0.0140, 0.013),         # Thread crest 1
        (0.0130, 0.016),         # Thread root 1
        (0.0140, 0.019),         # Thread crest 2
        (0.0130, 0.022),         # Thread root 2
        (0.0140, 0.025),         # Thread crest 3
        (0.0135, 0.028),
        (0.0142, 0.030),         # Upper collar
        (0.000, 0.030)
    ]
    base_obj = kit.lathe_object(f"{ASSET_ID}-screw-base", base_profile, segments=64, material=brass_mat)
    objects.append(base_obj)

    # 4. Central Glass Mount Stem & Exhaust Tube (Inside the bulb)
    stem_profile = [
        (0.000, 0.028),
        (0.005, 0.028),
        (0.0035, 0.048),
        (0.0065, 0.056),         # Stem press / pinch seal
        (0.000, 0.056)
    ]
    stem_obj = kit.lathe_object(f"{ASSET_ID}-glass-stem", stem_profile, segments=32, material=glass_mat)
    objects.append(stem_obj)

    # 5. Molybdenum / Copper Lead-in Support Wires
    for side in [-1, 1]:
        bm_wire = bmesh.new()
        bmesh.ops.create_cone(bm_wire, cap_ends=True, cap_tris=True, segments=16,
                              radius1=0.0005, radius2=0.0004, depth=0.024)
        mesh_wire = bpy.data.meshes.new(f"{ASSET_ID}-lead-wire-{side}")
        bm_wire.to_mesh(mesh_wire)
        bm_wire.free()
        for poly in mesh_wire.polygons:
            poly.use_smooth = True
        wire_obj = bpy.data.objects.new(f"{ASSET_ID}-lead-wire-{side}", mesh_wire)
        wire_obj.location = (side * 0.0055, 0.0, 0.066)
        wire_obj.rotation_euler = (0.0, side * -0.15, 0.0) # Slight outward angle
        bpy.context.collection.objects.link(wire_obj)
        wire_obj.data.materials.append(lead_wire_mat)
        objects.append(wire_obj)

    # 6. Double-Coiled Tungsten Filament Bridge
    bm_fil = bmesh.new()
    bmesh.ops.create_cone(bm_fil, cap_ends=True, cap_tris=True, segments=16,
                          radius1=0.00035, radius2=0.00035, depth=0.015)
    mesh_fil = bpy.data.meshes.new(f"{ASSET_ID}-filament")
    bm_fil.to_mesh(mesh_fil)
    bm_fil.free()
    for poly in mesh_fil.polygons:
        poly.use_smooth = True
    fil_obj = bpy.data.objects.new(f"{ASSET_ID}-filament", mesh_fil)
    fil_obj.location = (0.0, 0.0, 0.078)
    fil_obj.rotation_euler = (0.0, 1.5708, 0.0) # Horizontal bridge
    bpy.context.collection.objects.link(fil_obj)
    fil_obj.data.materials.append(tungsten_mat)
    objects.append(fil_obj)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_bulb()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
