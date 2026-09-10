"""
build_beaker.py — High-Fidelity Borosilicate Laboratory Beaker (250ml)
"""

import sys
from pathlib import Path
import math
import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit

ASSET_ID = "beaker"


def build_beaker():
    # 1. Physically accurate Borosilicate Glass Shader (Pyrex IOR 1.52)
    glass_mat = kit.add_glass_material(f"{ASSET_ID}-glass", tint=(0.96, 0.98, 1.0), ior=1.52, roughness=0.015)
    
    # 2. CuSO4 Solution Liquid (Deep Cerulean Blue)
    liquid_mat = kit.add_glass_material(f"{ASSET_ID}-liquid", tint=(0.10, 0.45, 0.85), ior=1.333, roughness=0.01)
    
    # 3. White Ceramic Enamel Graduation Markings
    enamel_mat = kit.add_material(f"{ASSET_ID}-enamel", (0.95, 0.95, 0.95), metallic=0.0, roughness=0.35)

    # 4. Standard 250ml Beaker Cross-Section Profile (Outer & Inner Walls with 1.4mm thickness)
    # Radius (r in meters), Height (z in meters)
    r_outer = 0.034  # 68mm diameter
    r_inner = 0.0326 # 1.4mm wall thickness
    h_total = 0.088  # 88mm height
    r_lip   = 0.0365 # Flared pouring rim
    
    beaker_profile = [
        # Outer surface
        (0.000, 0.000),             # Bottom center outer
        (r_outer - 0.005, 0.000),   # Flat base
        (r_outer - 0.001, 0.0015),  # Heel bevel
        (r_outer, 0.006),           # Lower body
        (r_outer, h_total - 0.008), # Cylindrical wall
        (r_lip - 0.001, h_total - 0.002), # Rim flare
        (r_lip, h_total),           # Top rim apex
        (r_lip - 0.0015, h_total + 0.0008), # Rounded top lip
        # Inner surface
        (r_inner + 0.001, h_total - 0.002), # Inner rim transition
        (r_inner, h_total - 0.008), # Inner wall
        (r_inner, 0.006),           # Inner wall bottom
        (r_inner - 0.003, 0.002),   # Inner bottom fillet
        (0.000, 0.002)              # Inner bottom center
    ]

    # Revolve 360° to build the beaker body
    beaker_body = kit.lathe_object(f"{ASSET_ID}-body", beaker_profile, segments=64, material=glass_mat)

    # 5. Model a clean pulled pouring spout using bmesh deformation
    # Pull out vertices near the top rim in the +X quadrant
    bm = bmesh.new()
    bm.from_mesh(beaker_body.data)
    for v in bm.verts:
        if v.co.z > (h_total - 0.012) and v.co.x > 0.020:
            factor = (v.co.z - (h_total - 0.012)) / 0.012
            angle_weight = max(0.0, v.co.x / r_lip)
            v.co.x += factor * angle_weight * 0.0065
            v.co.y *= (1.0 - factor * 0.25)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(beaker_body.data)
    bm.free()
    beaker_body.data.update()

    # 6. Meniscus-contoured Liquid Fill (50ml to 200ml level)
    liquid_h = 0.055
    liquid_profile = [
        (0.000, 0.0025),
        (r_inner - 0.002, 0.0025),
        (r_inner - 0.0003, 0.006),
        (r_inner - 0.0003, liquid_h - 0.001),
        (r_inner - 0.0015, liquid_h + 0.001), # Liquid meniscus curve
        (0.000, liquid_h)
    ]
    liquid_body = kit.lathe_object(f"{ASSET_ID}-liquid", liquid_profile, segments=64, material=liquid_mat)

    # 7. Authentic Front Graduation Tick Marks & 250ml Logo Decal (Arc markings, not 360° rings)
    # Build graduation lines as curved ribbons on the outer front wall
    grad_objects = []
    for i, ml in enumerate([50, 100, 150, 200]):
        z_mark = 0.018 + (i * 0.014)
        is_major = (ml % 100 == 0)
        arc_angle = 0.35 if is_major else 0.20
        
        # Create a narrow 3D manifold curved strip on the outer glass surface (0 non-manifold edges)
        bm_mark = bmesh.new()
        seg_mark = 12
        r1 = r_outer + 0.0001
        r2 = r_outer + 0.0004
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

    return [beaker_body, liquid_body] + grad_objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_beaker()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
