"""
build_test_tube.py — High-Fidelity Borosilicate Test Tube with Hemispherical Base
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "test-tube"


def build_test_tube():
    # 1. Borosilicate Glass & Solutions
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.96, 0.98, 1.0), ior=1.52, roughness=0.015)
    liquid_mat = kit.add_glass_material(f"{ASSET_ID}-liquid", tint=(0.90, 0.45, 0.12), ior=1.333, roughness=0.01)

    # 2. Standard 16x150mm Test Tube Profile with True Hemispherical Bottom
    # Radius (r in meters), Height (z in meters)
    r_outer = 0.008   # 16mm outer diameter
    r_inner = 0.0068  # 1.2mm wall thickness
    r_rim   = 0.0094  # Flared beaded top rim
    h_total = 0.140   # 140mm total length

    tube_profile = []
    
    # Outer Hemispherical Bottom Curve (z = 0 to z = r_outer)
    num_hemi = 16
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_outer * math.sin(angle)
        z = r_outer * (1.0 - math.cos(angle))
        tube_profile.append((r, z))

    # Outer Cylindrical Wall to Flared Rim
    tube_profile.extend([
        (r_outer, h_total - 0.006),
        (r_rim - 0.0005, h_total - 0.0015),
        (r_rim, h_total),
        (r_rim - 0.001, h_total + 0.0008),
        # Inner Rim & Wall
        (r_inner + 0.0008, h_total - 0.0015),
        (r_inner, h_total - 0.006),
        (r_inner, r_outer)
    ])

    # Inner Hemispherical Bottom Curve (down to inner center)
    for i in range(num_hemi, -1, -1):
        angle = math.pi / 2 * (i / num_hemi)
        r = r_inner * math.sin(angle)
        z = r_outer + (r_inner - 0.0012) - r_inner * math.cos(angle)
        if z < 0.0015:
            z = 0.0015
        tube_profile.append((r, z))

    tube_body = kit.lathe_object(f"{ASSET_ID}-body", tube_profile, segments=48, material=glass_mat)

    # 3. Meniscus Liquid Fill (Iodine solution / reddish-amber)
    liquid_h = 0.065
    liquid_profile = []
    for i in range(num_hemi + 1):
        angle = math.pi / 2 * (i / num_hemi)
        r = (r_inner - 0.0002) * math.sin(angle)
        z = 0.0018 + (r_inner - 0.0002) * (1.0 - math.cos(angle))
        liquid_profile.append((r, z))

    liquid_profile.extend([
        (r_inner - 0.0002, liquid_h - 0.001),
        (r_inner - 0.0010, liquid_h + 0.0008), # Meniscus
        (0.000, liquid_h)
    ])

    liquid_body = kit.lathe_object(f"{ASSET_ID}-liquid", liquid_profile, segments=48, material=liquid_mat)

    return [tube_body, liquid_body]


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_test_tube()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
