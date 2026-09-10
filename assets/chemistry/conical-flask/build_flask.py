"""
build_flask.py — High-Fidelity Borosilicate Erlenmeyer Conical Flask (250ml)
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "conical-flask"


def build_flask():
    # 1. Authentic Borosilicate Glass Shader (Pyrex IOR 1.52)
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.96, 0.98, 1.0), ior=1.52, roughness=0.015)
    
    # 2. Golden-Amber Dilute Acid Solution
    liquid_mat = kit.add_glass_material(f"{ASSET_ID}-liquid", tint=(0.96, 0.82, 0.25), ior=1.333, roughness=0.01)
    
    # 3. White Enamel Markings
    enamel_mat = kit.add_material(f"{ASSET_ID}-enamel", (0.95, 0.95, 0.95), metallic=0.0, roughness=0.35)

    # 4. Standard 250ml Erlenmeyer Flask Lathe Profile
    # Wide conical base tapering smoothly into a narrow reinforced neck and flared beaded rim
    # Radius (r in meters), Height (z in meters)
    r_base_outer = 0.042   # 84mm diameter flat bottom
    r_base_inner = 0.0405  # 1.5mm wall thickness
    r_neck_outer = 0.017   # 34mm neck diameter
    r_neck_inner = 0.0155
    r_rim_outer  = 0.0195  # Flared rim bead
    h_body       = 0.095   # Conical body height
    h_total      = 0.140   # 140mm total height

    flask_profile = [
        # Outer surface
        (0.000, 0.000),
        (r_base_outer - 0.006, 0.000),      # Flat base
        (r_base_outer - 0.001, 0.002),      # Heel fillet
        (r_base_outer, 0.008),              # Bottom corner
        (r_neck_outer, h_body),             # Conical wall slope
        (r_neck_outer, h_total - 0.008),    # Straight cylindrical neck
        (r_rim_outer - 0.001, h_total - 0.002), # Flared rim transition
        (r_rim_outer, h_total),             # Rim bead apex
        (r_rim_outer - 0.0015, h_total + 0.001), # Rounded lip
        # Inner surface
        (r_neck_inner + 0.001, h_total - 0.002),
        (r_neck_inner, h_total - 0.008),    # Inner neck
        (r_neck_inner, h_body),             # Inner transition
        (r_base_inner, 0.008),              # Inner conical wall
        (r_base_inner - 0.004, 0.0025),     # Inner bottom fillet
        (0.000, 0.0025)                     # Inner base center
    ]

    flask_body = kit.lathe_object(f"{ASSET_ID}-body", flask_profile, segments=64, material=glass_mat)

    # 5. Liquid Fill (Partial 100ml fill in conical base)
    liquid_h = 0.042
    r_liq_top = r_base_inner - (r_base_inner - r_neck_inner) * (liquid_h / h_body)
    
    liquid_profile = [
        (0.000, 0.003),
        (r_base_inner - 0.003, 0.003),
        (r_base_inner - 0.0003, 0.008),
        (r_liq_top - 0.0003, liquid_h - 0.001),
        (r_liq_top - 0.0015, liquid_h + 0.001), # Meniscus
        (0.000, liquid_h)
    ]
    liquid_body = kit.lathe_object(f"{ASSET_ID}-liquid", liquid_profile, segments=64, material=liquid_mat)

    # 6. Front Graduation Lines (50ml, 100ml, 150ml, 200ml)
    grad_objects = []
    for i, ml in enumerate([50, 100, 150, 200]):
        z_mark = 0.024 + (i * 0.018)
        r_at_z = r_base_outer - (r_base_outer - r_neck_outer) * (z_mark / h_body)
        is_major = (ml % 100 == 0)
        arc_angle = 0.32 if is_major else 0.18

        # Create a narrow 3D manifold curved strip on the outer conical glass surface (0 non-manifold edges)
        bm_mark = bmesh.new()
        seg_mark = 12
        r1 = r_at_z + 0.0001
        r2 = r_at_z + 0.0004
        z_low = z_mark - 0.0004
        z_high = z_mark + 0.0004

        verts_in_low = []
        verts_in_high = []
        verts_out_low = []
        verts_out_high = []

        for s in range(seg_mark + 1):
            theta = -arc_angle / 2 + (arc_angle * s / seg_mark)
            st = math.sin(theta)
            ct = math.cos(theta)
            verts_in_low.append(bm_mark.verts.new((r1 * st, -r1 * ct, z_low)))
            verts_in_high.append(bm_mark.verts.new((r1 * st, -r1 * ct, z_high)))
            verts_out_low.append(bm_mark.verts.new((r2 * st, -r2 * ct, z_low)))
            verts_out_high.append(bm_mark.verts.new((r2 * st, -r2 * ct, z_high)))

        for s in range(seg_mark):
            # Outer face (+r)
            bm_mark.faces.new([verts_out_low[s], verts_out_low[s + 1], verts_out_high[s + 1], verts_out_high[s]])
            # Inner face (-r)
            bm_mark.faces.new([verts_in_low[s + 1], verts_in_low[s], verts_in_high[s], verts_in_high[s + 1]])
            # Top face (+z)
            bm_mark.faces.new([verts_in_high[s], verts_out_high[s], verts_out_high[s + 1], verts_in_high[s + 1]])
            # Bottom face (-z)
            bm_mark.faces.new([verts_in_low[s + 1], verts_out_low[s + 1], verts_out_low[s], verts_in_low[s]])

        # Side caps
        bm_mark.faces.new([verts_in_low[0], verts_in_high[0], verts_out_high[0], verts_out_low[0]])
        bm_mark.faces.new([verts_in_low[-1], verts_out_low[-1], verts_out_high[-1], verts_in_high[-1]])
        bmesh.ops.recalc_face_normals(bm_mark, faces=bm_mark.faces)

        mesh_mark = bpy.data.meshes.new(f"{ASSET_ID}-tick-{ml}")
        bm_mark.to_mesh(mesh_mark)
        bm_mark.free()
        mark_obj = bpy.data.objects.new(f"{ASSET_ID}-tick-{ml}", mesh_mark)
        bpy.context.collection.objects.link(mark_obj)
        mark_obj.data.materials.append(enamel_mat)
        grad_objects.append(mark_obj)

    return [flask_body, liquid_body] + grad_objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_flask()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
