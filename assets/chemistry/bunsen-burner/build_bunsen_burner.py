"""
build_bunsen_burner.py — High-Fidelity Laboratory Bunsen Burner
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "bunsen-burner"


def build_burner(include_flame=True):
    # 1. Authentic Materials
    cast_iron_mat = kit.add_material(f"{ASSET_ID}-cast-iron", (0.12, 0.12, 0.14), metallic=0.75, roughness=0.55)
    brass_mat = kit.add_machined_metal_material(f"{ASSET_ID}-brass", (0.85, 0.65, 0.22), metallic=0.92, roughness=0.25)
    nickel_mat = kit.add_machined_metal_material(f"{ASSET_ID}-nickel-stem", (0.82, 0.84, 0.86), metallic=0.95, roughness=0.22)
    hose_rubber_mat = kit.add_material(f"{ASSET_ID}-rubber-hose", (0.85, 0.45, 0.15), metallic=0.0, roughness=0.6)

    objects = []

    # 2. Heavy Cast-Iron Base (Flanged, Chamfered Hexagonal/Circular Base with recess)
    base_profile = [
        (0.000, 0.000),
        (0.045, 0.000),      # 90mm diameter base footprint
        (0.045, 0.003),      # Bottom chamfer
        (0.042, 0.006),      # Stepped foot
        (0.040, 0.008),      # Sloped top shoulder
        (0.016, 0.012),      # Neck taper
        (0.014, 0.018),      # Central threaded boss
        (0.000, 0.018)
    ]
    base_obj = kit.lathe_object(f"{ASSET_ID}-base", base_profile, segments=64, material=cast_iron_mat)
    objects.append(base_obj)

    # 3. Gas Inlet Hose Barb (Side inlet brass nipple)
    barb_bm = bmesh.new()
    bmesh.ops.create_cone(barb_bm, cap_ends=True, cap_tris=True, segments=32,
                          radius1=0.004, radius2=0.0035, depth=0.028)
    barb_mesh = bpy.data.meshes.new(f"{ASSET_ID}-gas-inlet")
    barb_bm.to_mesh(barb_mesh)
    barb_bm.free()
    for poly in barb_mesh.polygons:
        poly.use_smooth = True
    barb_obj = bpy.data.objects.new(f"{ASSET_ID}-gas-inlet", barb_mesh)
    barb_obj.location = (-0.025, 0.0, 0.010)
    barb_obj.rotation_euler = (0.0, 1.5708, 0.0) # Horizontal pointing left
    bpy.context.collection.objects.link(barb_obj)
    barb_obj.data.materials.append(brass_mat)
    objects.append(barb_obj)

    # 4. Rotatable Brass Air Collar with Dual Intake Ports (Closed solid manifold loop)
    collar_profile = [
        (0.0082, 0.018),
        (0.0115, 0.018),
        (0.0120, 0.020), # Knurled rim
        (0.0120, 0.038), # Collar body
        (0.0115, 0.040), # Upper knurl
        (0.0082, 0.040),
        (0.0082, 0.018)  # Closes inner cylindrical wall
    ]
    collar_obj = kit.lathe_object(f"{ASSET_ID}-air-collar", collar_profile, segments=48, material=brass_mat)
    objects.append(collar_obj)

    # Air intake slots (Boolean or visual cutouts on the brass collar)
    for i in [-1, 1]:
        hole_bm = bmesh.new()
        bmesh.ops.create_cone(hole_bm, cap_ends=True, cap_tris=True, segments=24,
                              radius1=0.0035, radius2=0.0035, depth=0.030)
        hole_mesh = bpy.data.meshes.new(f"{ASSET_ID}-air-hole-{i}")
        hole_bm.to_mesh(hole_mesh)
        hole_bm.free()
        for poly in hole_mesh.polygons:
            poly.use_smooth = True
        hole_obj = bpy.data.objects.new(f"{ASSET_ID}-air-hole-{i}", hole_mesh)
        hole_obj.location = (0.0, 0.0, 0.029)
        hole_obj.rotation_euler = (1.5708, 0.0, 0.0)
        bpy.context.collection.objects.link(hole_obj)
        hole_obj.data.materials.append(cast_iron_mat) # Appears as dark internal hole
        hole_obj.scale = (1.0, 1.0, 0.8)
        objects.append(hole_obj)

    # 5. Nickel-Plated Brass Mixing Chimney/Barrel (Closed solid manifold loop)
    barrel_h = 0.125 # 125mm standard laboratory height
    barrel_profile = [
        # Outer surface
        (0.0065, 0.038),
        (0.0072, 0.044),  # Lower flare
        (0.0068, 0.048),
        (0.0068, barrel_h - 0.006), # Main cylindrical barrel
        (0.0078, barrel_h - 0.002), # Top flame stabilizer flare
        (0.0080, barrel_h),         # Top rim apex
        (0.0070, barrel_h + 0.0005),# Inner lip
        # Inner bore (Hollow central mixing tube)
        (0.0055, barrel_h - 0.002),
        (0.0055, 0.038),
        (0.0065, 0.038)  # Closes bottom annular face
    ]
    barrel_obj = kit.lathe_object(f"{ASSET_ID}-stem", barrel_profile, segments=64, material=nickel_mat)
    objects.append(barrel_obj)

    # 6. Multi-zone Bunsen Burner Flame (Dual-zone blue flame)
    if include_flame:
        # Inner reducing core cone (#38bdf8, emission strength 10.0)
        inner_flame_mat = bpy.data.materials.new(f"{ASSET_ID}-flame-inner")
        inner_flame_mat.use_nodes = True
        bsdf_fi = inner_flame_mat.node_tree.nodes["Principled BSDF"]
        bsdf_fi.inputs["Base Color"].default_value = (0.22, 0.74, 0.97, 1.0)
        bsdf_fi.inputs["Emission Color"].default_value = (0.22, 0.74, 0.97, 1.0)
        bsdf_fi.inputs["Emission Strength"].default_value = 10.0
        bsdf_fi.inputs["Roughness"].default_value = 0.2

        # Outer oxidizing flame cone (#60a5fa, emission strength 6.0)
        outer_flame_mat = bpy.data.materials.new(f"{ASSET_ID}-flame-outer")
        outer_flame_mat.use_nodes = True
        bsdf_fo = outer_flame_mat.node_tree.nodes["Principled BSDF"]
        bsdf_fo.inputs["Base Color"].default_value = (0.38, 0.65, 0.98, 1.0)
        bsdf_fo.inputs["Emission Color"].default_value = (0.38, 0.65, 0.98, 1.0)
        bsdf_fo.inputs["Emission Strength"].default_value = 6.0
        bsdf_fo.inputs["Roughness"].default_value = 0.2

        outer_flame_h = 0.045
        outer_flame = kit.primitive_object(
            f"{ASSET_ID}-flame-outer", "cone", outer_flame_mat,
            size=(0.015, 0.002, outer_flame_h),
            location=(0.0, 0.0, barrel_h + outer_flame_h / 2)
        )
        objects.append(outer_flame)

        inner_flame_h = 0.024
        inner_flame = kit.primitive_object(
            f"{ASSET_ID}-flame-inner", "cone", inner_flame_mat,
            size=(0.011, 0.001, inner_flame_h),
            location=(0.0, 0.0, barrel_h + inner_flame_h / 2)
        )
        objects.append(inner_flame)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_burner()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
