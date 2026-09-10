"""
build_nephron.py — Microscopic Functional Nephron Architecture
CBSE Class 10 Biology, Chapter 5: Life Processes — Excretion in Human Beings (Fig 5.14)
CBSE Class 11 Biology, Chapter 19: Excretory Products and their Elimination (Fig 19.3)

Key Anatomical Features:
- Renal Corpuscle: Bowman's capsule (double-walled calyx) enclosing the Glomerulus capillary tuft.
- Afferent arteriole (wider lumen) and efferent arteriole (narrower lumen) at the vascular pole.
- Proximal Convoluted Tubule (PCT): tortuous cortical winding loops emerging from urinary pole.
- Hairpin Loop of Henle: thin descending limb dipping into renal medulla, hairpin U-turn,
  transitioning to thick ascending limb (TAL) ascending back to cortex.
- Juxtaglomerular Apparatus (JGA) & Macula Densa: thick ascending limb / early DCT curves directly
  into intimate contact with Bowman's vascular pole between afferent and efferent arterioles.
- Distal Convoluted Tubule (DCT): cortical convolutions connecting into the collecting duct.
- Collecting Duct: vertical collecting trunk receiving DCT and multiple tributary branches.
- Peritubular capillary network & Vasa Recta: capillary plexus entwining PCT/DCT and descending
  alongside Loop of Henle for countercurrent exchange.
- Corticomedullary Boundary: demarcation plane distinguishing Renal Cortex (z > 0) and Medulla (z < 0).
- ZERO non-manifold edges: all tubular structures capped cleanly via kit.create_smooth_tube(..., cap_ends=True).
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'nephron'


def build_nephron():
    # Anatomical PBR Materials with realistic tissue shading
    capsule_mat = kit.add_tissue_material(
        'bowman-capsule', base_color=(0.88, 0.70, 0.62, 1.0), roughness=0.35,
        subsurface_weight=0.30, subsurface_radius=(0.8, 0.2, 0.1)
    )
    art_blood_mat = kit.add_material('arterial-blood', (0.88, 0.10, 0.12), metallic=0.15, roughness=0.25)
    ven_blood_mat = kit.add_material('venous-blood', (0.16, 0.35, 0.82), metallic=0.15, roughness=0.25)
    capillary_mat = kit.add_material('capillary-purple', (0.65, 0.18, 0.48), metallic=0.12, roughness=0.28)
    tubule_mat = kit.add_tissue_material(
        'renal-tubule', base_color=(0.92, 0.82, 0.58, 1.0), roughness=0.40,
        subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2)
    )
    henle_thin_mat = kit.add_tissue_material(
        'loop-henle-thin', base_color=(0.88, 0.76, 0.52, 1.0), roughness=0.45,
        subsurface_weight=0.25, subsurface_radius=(0.4, 0.3, 0.2)
    )
    duct_mat = kit.add_tissue_material(
        'collecting-duct', base_color=(0.94, 0.72, 0.32, 1.0), roughness=0.38,
        subsurface_weight=0.25, subsurface_radius=(0.6, 0.4, 0.2)
    )
    macula_mat = kit.add_material('macula-densa', (0.78, 0.62, 0.42), metallic=0.04, roughness=0.35)
    boundary_mat = kit.add_material('corticomedullary-boundary', (0.80, 0.82, 0.88), metallic=0.0, roughness=0.5)
    bsdf_b = boundary_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in bsdf_b.inputs:
        bsdf_b.inputs["Transmission Weight"].default_value = 0.80

    objects = []

    # 1. Bowman's Capsule (Double-walled spherical calyx with open vascular pole at top)
    cup_bm = bmesh.new()
    num_lat = 18
    num_lon = 32
    radius = 0.016
    for i in range(num_lat):
        lat = (i / (num_lat - 1)) * (math.pi * 0.72)  # 0 to 130 deg (open cup)
        for j in range(num_lon):
            lon = (j / num_lon) * 2.0 * math.pi
            x = -0.055 + radius * math.sin(lat) * math.cos(lon)
            y = radius * math.sin(lat) * math.sin(lon)
            z = 0.088 - radius * math.cos(lat)
            cup_bm.verts.new((x, y, z))
    cup_bm.verts.ensure_lookup_table()
    for i in range(num_lat - 1):
        for j in range(num_lon):
            next_j = (j + 1) % num_lon
            v1 = cup_bm.verts[i * num_lon + j]
            v2 = cup_bm.verts[i * num_lon + next_j]
            v3 = cup_bm.verts[(i + 1) * num_lon + next_j]
            v4 = cup_bm.verts[(i + 1) * num_lon + j]
            cup_bm.faces.new([v1, v2, v3, v4])
    bmesh.ops.recalc_face_normals(cup_bm, faces=cup_bm.faces)
    cup_mesh = bpy.data.meshes.new(f'{ASSET_ID}-capsule-cup-mesh')
    cup_bm.to_mesh(cup_mesh)
    cup_bm.free()
    capsule_cup = bpy.data.objects.new(f'{ASSET_ID}-capsule-cup', cup_mesh)
    bpy.context.collection.objects.link(capsule_cup)

    # Solidify modifier for anatomical wall thickness, creating closed manifold geometry
    sol = capsule_cup.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.0022
    sol.use_rim = True
    sol.use_rim_only = False
    bpy.context.view_layer.objects.active = capsule_cup
    capsule_cup.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    sub = capsule_cup.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    capsule_cup.data.materials.append(capsule_mat)
    objects.append(capsule_cup)

    # 2. Glomerulus: Knot of convoluted capillary loops nestled in Bowman's cup
    glom_center = Vector((-0.055, 0.0, 0.088))
    glom_pts = []
    num_glom_steps = 36
    for g in range(num_glom_steps):
        t = g / (num_glom_steps - 1)
        theta = t * math.pi * 6.0
        r = 0.009 * math.sin(t * math.pi)
        gx = glom_center.x + r * math.cos(theta) * 0.9
        gy = glom_center.y + r * math.sin(theta) * 0.9
        gz = glom_center.z + (t - 0.5) * 0.012 + 0.003 * math.cos(theta * 1.5)
        glom_pts.append((gx, gy, gz))
    glom_knot = kit.create_smooth_tube(f'{ASSET_ID}-glomerulus-knot', glom_pts, radius=0.0018, cap_ends=True, material=art_blood_mat)
    objects.append(glom_knot)

    # Central glomerulus core
    glom_core = kit.primitive_object(f'{ASSET_ID}-glom-core', 'uv_sphere', art_blood_mat,
                                      size=(0.016, 0.016, 0.016),
                                      location=(glom_center.x, glom_center.y, glom_center.z))
    objects.append(glom_core)

    # Afferent Arteriole (Inflow: wider diameter, entering vascular pole)
    aff_pts = [
        (-0.080, -0.010, 0.125),
        (-0.068, -0.006, 0.108),
        (-0.058, -0.003, 0.096),
    ]
    aff_art = kit.create_smooth_tube(f'{ASSET_ID}-afferent-arteriole', aff_pts, radius=0.0028, cap_ends=True, material=art_blood_mat)
    objects.append(aff_art)

    # Efferent Arteriole (Outflow: narrower diameter, emerging from vascular pole)
    eff_pts = [
        (-0.052, 0.003, 0.096),
        (-0.046, 0.008, 0.105),
        (-0.038, 0.012, 0.098),
        (-0.034, 0.006, 0.075),
    ]
    eff_art = kit.create_smooth_tube(f'{ASSET_ID}-efferent-arteriole', eff_pts, radius=0.0020, cap_ends=True, material=art_blood_mat)
    objects.append(eff_art)

    # 3. Proximal Convoluted Tubule (PCT: Organic convoluted S-curve emerging from urinary pole)
    pct_pts = [
        (-0.055, 0.0, 0.072),       # Neck from urinary pole
        (-0.052, 0.012, 0.060),
        (-0.042, 0.018, 0.052),
        (-0.032, 0.008, 0.062),
        (-0.026, -0.012, 0.068),
        (-0.034, -0.020, 0.055),
        (-0.044, -0.014, 0.042),
        (-0.036, 0.004, 0.032),
        (-0.024, 0.006, 0.022),
        (-0.018, 0.000, 0.008),     # Transition to descending limb at corticomedullary border
    ]
    pct = kit.create_smooth_tube(f'{ASSET_ID}-pct', pct_pts, radius=0.0032, cap_ends=True, material=tubule_mat)
    objects.append(pct)

    # 4. Loop of Henle (Hairpin countercurrent loop dipping deeply into medulla)
    # Descending thin limb (thin-walled, water permeable segment)
    henle_desc_pts = [
        (-0.018, 0.000, 0.008),
        (-0.016, -0.003, -0.020),
        (-0.015, -0.002, -0.045),
        (-0.014, 0.000, -0.065),
    ]
    henle_desc = kit.create_smooth_tube(f'{ASSET_ID}-henle-desc', henle_desc_pts, radius=0.0019, cap_ends=True, material=henle_thin_mat)
    objects.append(henle_desc)

    # Hairpin U-turn bend in inner medulla
    turn_pts = [
        (-0.014, 0.000, -0.065),
        (-0.012, 0.003, -0.076),
        (-0.006, 0.002, -0.080),
        (0.000, -0.002, -0.076),
        (0.004, 0.000, -0.065),
    ]
    henle_turn = kit.create_smooth_tube(f'{ASSET_ID}-henle-turn', turn_pts, radius=0.0022, cap_ends=True, material=henle_thin_mat)
    objects.append(henle_turn)

    # Ascending thick limb (TAL: thick active transport segment)
    # Ascends out of medulla, enters cortex, and heads directly toward vascular pole of Bowman's capsule!
    henle_asc_pts = [
        (0.004, 0.000, -0.065),
        (0.005, 0.002, -0.040),
        (0.006, -0.002, -0.015),
        (0.006, 0.000, 0.010),
        (0.002, 0.004, 0.035),
        (-0.012, 0.008, 0.060),
        (-0.032, 0.006, 0.082),
        (-0.054, 0.001, 0.096),     # Direct anatomical contact with vascular pole: MACULA DENSA / JGA!
    ]
    henle_asc = kit.create_smooth_tube(f'{ASSET_ID}-henle-asc', henle_asc_pts, radius=0.0028, cap_ends=True, material=tubule_mat)
    objects.append(henle_asc)

    # Macula Densa / Juxtaglomerular Apparatus (JGA) contact node
    macula_densa = kit.primitive_object(
        f'{ASSET_ID}-macula-densa', 'uv_sphere', macula_mat,
        size=(0.0055, 0.0055, 0.0055),
        location=(-0.054, 0.001, 0.096)
    )
    objects.append(macula_densa)

    # 5. Distal Convoluted Tubule (DCT: Convoluted cortical segment emerging from macula densa)
    # Loops tortuously through cortex before draining into collecting duct
    dct_pts = [
        (-0.054, 0.001, 0.096),     # Emerges from macula densa contact
        (-0.045, -0.010, 0.102),
        (-0.030, -0.014, 0.098),
        (-0.012, -0.008, 0.092),
        (0.005, 0.006, 0.088),
        (0.020, 0.012, 0.084),
        (0.035, 0.006, 0.076),
        (0.045, 0.000, 0.070),      # Drains into collecting duct
    ]
    dct = kit.create_smooth_tube(f'{ASSET_ID}-dct', dct_pts, radius=0.0030, cap_ends=True, material=tubule_mat)
    objects.append(dct)

    # 6. Collecting Duct (Broad vertical trunk collecting urine from multiple nephrons)
    duct_pts = [
        (0.045, 0.0, 0.120),        # Upper cortical collecting duct
        (0.045, 0.0, 0.080),
        (0.046, 0.0, 0.030),        # Corticomedullary border
        (0.046, 0.0, -0.020),       # Outer medullary duct
        (0.047, 0.0, -0.070),       # Inner medullary duct
        (0.048, 0.0, -0.095),       # Renal papilla base discharging into minor calyx
    ]
    duct = kit.create_smooth_tube(f'{ASSET_ID}-collecting-duct', duct_pts, radius=0.0048, cap_ends=True, material=duct_mat)
    objects.append(duct)

    # Tributary branches from adjacent nephrons entering collecting duct
    for tz, sign in [(0.105, 1), (0.042, -1), (0.010, 1), (-0.035, -1)]:
        trib_pts = [
            (0.056 * sign if sign > 0 else 0.034, 0.012 * sign, tz + 0.012),
            (0.050 if sign > 0 else 0.040, 0.006 * sign, tz + 0.005),
            (0.0455, 0.0, tz)
        ]
        trib = kit.create_smooth_tube(f'{ASSET_ID}-trib-{tz}', trib_pts, radius=0.0024, cap_ends=True, material=duct_mat)
        objects.append(trib)

    # 7. Peritubular Capillary Network & Vasa Recta (Selective Reabsorption System)
    # Capillaries entwined around PCT (arterial blood transitioning to capillary)
    cap_pct_pts1 = [
        (-0.034, 0.006, 0.075),
        (-0.024, 0.015, 0.065),
        (-0.026, -0.008, 0.052),
        (-0.038, -0.012, 0.046),
        (-0.030, 0.008, 0.036),
    ]
    cap_pct1 = kit.create_smooth_tube(f'{ASSET_ID}-cap-pct-1', cap_pct_pts1, radius=0.0014, cap_ends=True, material=art_blood_mat)
    objects.append(cap_pct1)

    cap_pct_pts2 = [
        (-0.038, 0.012, 0.098),
        (-0.048, 0.020, 0.075),
        (-0.046, -0.005, 0.062),
        (-0.030, -0.018, 0.058),
        (-0.020, -0.006, 0.040),
    ]
    cap_pct2 = kit.create_smooth_tube(f'{ASSET_ID}-cap-pct-2', cap_pct_pts2, radius=0.0013, cap_ends=True, material=capillary_mat)
    objects.append(cap_pct2)

    # Vasa Recta: Straight hairpin capillary plexus descending alongside Loop of Henle into medulla
    vasa_desc_pts = [
        (-0.030, 0.008, 0.036),
        (-0.022, 0.005, 0.005),
        (-0.020, 0.004, -0.030),
        (-0.018, 0.003, -0.058),
        (-0.014, 0.004, -0.072),
        (-0.006, 0.004, -0.075),     # Hairpin loop around Henle turn
        (0.001, 0.004, -0.068),
        (0.008, 0.003, -0.045),
        (0.009, 0.004, -0.010),
        (0.012, 0.005, 0.025),      # Ascends as venule into cortex
        (0.018, 0.008, 0.060),
    ]
    vasa_recta = kit.create_smooth_tube(f'{ASSET_ID}-vasa-recta', vasa_desc_pts, radius=0.0014, cap_ends=True, material=ven_blood_mat)
    objects.append(vasa_recta)

    # Capillaries around DCT leading to interlobular renal venule
    cap_dct_pts = [
        (0.018, 0.008, 0.060),
        (0.008, -0.008, 0.076),
        (0.015, -0.014, 0.084),
        (0.026, 0.002, 0.088),
        (0.032, -0.010, 0.070),
    ]
    cap_dct = kit.create_smooth_tube(f'{ASSET_ID}-cap-dct', cap_dct_pts, radius=0.0013, cap_ends=True, material=ven_blood_mat)
    objects.append(cap_dct)

    # Renal Venule (Return outflow from peritubular capillary bed)
    venule_pts = [
        (0.032, -0.010, 0.070),
        (0.022, -0.016, 0.095),
        (0.010, -0.018, 0.120),
        (-0.005, -0.020, 0.135),
    ]
    venule = kit.create_smooth_tube(f'{ASSET_ID}-renal-venule', venule_pts, radius=0.0026, cap_ends=True, material=ven_blood_mat)
    objects.append(venule)

    # 8. Corticomedullary Boundary Plane (Demarcating Renal Cortex z > 0 and Renal Medulla z < 0)
    boundary = kit.primitive_object(
        f'{ASSET_ID}-corticomedullary-boundary', 'cube', boundary_mat,
        size=(0.150, 0.070, 0.0006),
        location=(-0.010, 0.0, 0.0)
    )
    objects.append(boundary)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_nephron()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')


if __name__ == '__main__':
    main()
