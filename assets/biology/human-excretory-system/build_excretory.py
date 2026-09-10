"""
build_excretory.py — Anatomical Human Excretory System (Kidneys, Ureters, Bladder, Vessels)
CBSE Class 10 Biology, Chapter 5: Life Processes — Excretion in Human Beings (Fig 5.13)
CBSE Class 11 Biology, Chapter 19: Excretory Products and their Elimination (Fig 19.1, 19.2)

Key Anatomical Features:
- Paired bean-shaped kidneys with concave medial hilum (right kidney slightly lower due to liver).
- Suprarenal (adrenal) pyramidal glands capping the superior poles.
- Funnel-shaped renal pelvis at the hilum transitioning into bilateral curving ureters.
- Great abdominal blood vessels:
  * Abdominal aorta with renal arteries and common iliac artery bifurcations.
  * Inferior vena cava with renal veins (left renal vein crossing anterior to aorta!)
    and common iliac vein convergence.
- Bilateral ureters descending retroperitoneally into the posterolateral base of the urinary bladder.
- Pear-shaped muscular urinary bladder with detrusor muscle, tapering bladder neck, and urethra.
- ZERO non-manifold edges: all tubular vessels and ureters capped cleanly via kit.create_smooth_tube(..., cap_ends=True).
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'human-excretory-system'


def create_bean_kidney(name, sign, kz, kidney_mat):
    """
    Creates an anatomically authentic bean-shaped kidney with concave medial hilum indentation.
    sign = -1 for Anatomical Right Kidney (viewer's left).
    sign = +1 for Anatomical Left Kidney (viewer's right).
    """
    bm = bmesh.new()
    num_z = 24
    num_pts = 24
    z_min = -0.032
    z_max = 0.032

    slices = []
    for s in range(num_z):
        tz = s / (num_z - 1)  # 0 to 1
        z = z_min + tz * (z_max - z_min)

        r_scale = math.cos((tz - 0.5) * math.pi * 0.88)
        r_scale = max(r_scale, 0.15)

        rx = 0.020 * r_scale
        ry = 0.015 * r_scale

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            ct = math.cos(theta)
            st = math.sin(theta)

            px = rx * ct
            py = ry * st

            # Medial hilum indentation: medial border is where (ct * sign) < 0
            if (ct * sign) < 0 and 0.28 < tz < 0.72:
                hilum_depth = 0.010 * math.sin((tz - 0.28) / 0.44 * math.pi) * abs(ct)
                px += sign * hilum_depth

            v = bm.verts.new((px, py, z))
            ring.append(v)
        slices.append(ring)

    for s in range(num_z - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            v1 = slices[s][i]
            v2 = slices[s][next_i]
            v3 = slices[s + 1][next_i]
            v4 = slices[s + 1][i]
            bm.faces.new([v1, v2, v3, v4])

    base_center = bm.verts.new((0.0, 0.0, z_min))
    top_center = bm.verts.new((0.0, 0.0, z_max))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][next_i], slices[0][i], base_center])
        bm.faces.new([slices[-1][i], slices[-1][next_i], top_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (sign * 0.054, 0.0, kz)
    obj.rotation_euler = (0.0, -sign * 0.08, 0.0)

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(kidney_mat)
    return obj


def build_excretory():
    # 1. Calibrated PBR Materials with tissue subsurface scattering
    kidney_mat = kit.add_tissue_material('kidney-cortex', base_color=(0.35, 0.08, 0.08, 1.0), roughness=0.32,
                                         subsurface_weight=0.30, subsurface_radius=(0.7, 0.2, 0.1))
    adrenal_mat = kit.add_tissue_material('adrenal-gland', base_color=(0.65, 0.44, 0.12, 1.0), roughness=0.40,
                                          subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.1))
    aorta_mat = kit.add_material('renal-aorta', (0.75, 0.08, 0.10), metallic=0.15, roughness=0.25)
    vena_cava_mat = kit.add_material('renal-cava', (0.08, 0.22, 0.65), metallic=0.15, roughness=0.25)
    ureter_mat = kit.add_tissue_material('ureter-tube', base_color=(0.78, 0.72, 0.45, 1.0), roughness=0.38,
                                         subsurface_weight=0.20, subsurface_radius=(0.4, 0.3, 0.2))
    bladder_mat = kit.add_tissue_material('urinary-bladder', base_color=(0.55, 0.16, 0.20, 1.0), roughness=0.35,
                                          subsurface_weight=0.30, subsurface_radius=(0.6, 0.2, 0.1))
    pelvis_mat = kit.add_tissue_material('renal-pelvis', base_color=(0.70, 0.62, 0.38, 1.0), roughness=0.40,
                                         subsurface_weight=0.20, subsurface_radius=(0.4, 0.3, 0.2))

    objects = []

    # 2. Great Abdominal Blood Vessels (Abdominal Aorta & Inferior Vena Cava)
    # Abdominal Aorta: Left of midline (viewer's right, x = +0.007m)
    aorta = kit.primitive_object(
        f'{ASSET_ID}-aorta', 'cylinder', aorta_mat,
        size=(0.012, 0.012, 0.15),
        location=(0.007, -0.004, 0.145)
    )
    # Inferior Vena Cava: Right of midline (viewer's left, x = -0.007m)
    vena_cava = kit.primitive_object(
        f'{ASSET_ID}-vena-cava', 'cylinder', vena_cava_mat,
        size=(0.014, 0.014, 0.15),
        location=(-0.007, 0.002, 0.145)
    )
    objects.extend([aorta, vena_cava])

    # Common Iliac Vessel Bifurcations at base (NCERT Class 10 Fig 5.13)
    iliac_art_r = kit.create_smooth_tube(
        f'{ASSET_ID}-iliac-artery-r', [(0.007, -0.004, 0.070), (-0.010, -0.003, 0.045), (-0.020, -0.002, 0.025)],
        radius=0.0042, cap_ends=True, material=aorta_mat
    )
    iliac_art_l = kit.create_smooth_tube(
        f'{ASSET_ID}-iliac-artery-l', [(0.007, -0.004, 0.070), (0.018, -0.003, 0.045), (0.028, -0.002, 0.025)],
        radius=0.0042, cap_ends=True, material=aorta_mat
    )
    iliac_vein_r = kit.create_smooth_tube(
        f'{ASSET_ID}-iliac-vein-r', [(-0.007, 0.002, 0.070), (-0.018, 0.003, 0.045), (-0.026, 0.003, 0.025)],
        radius=0.0048, cap_ends=True, material=vena_cava_mat
    )
    iliac_vein_l = kit.create_smooth_tube(
        f'{ASSET_ID}-iliac-vein-l', [(-0.007, 0.002, 0.070), (0.010, 0.003, 0.045), (0.022, 0.003, 0.025)],
        radius=0.0048, cap_ends=True, material=vena_cava_mat
    )
    objects.extend([iliac_art_r, iliac_art_l, iliac_vein_r, iliac_vein_l])

    # 3. Paired Authentic Bean-Shaped Kidneys (Right kidney lower at z=0.126; Left higher at z=0.138)
    for sign, name, kz in [(-1, 'right', 0.126), (1, 'left', 0.138)]:
        kidney = create_bean_kidney(f'{ASSET_ID}-kidney-{name}', sign, kz, kidney_mat)
        objects.append(kidney)

        # Adrenal Glands (Suprarenal pyramidal caps on superior pole)
        adrenal = kit.primitive_object(
            f'{ASSET_ID}-adrenal-{name}', 'cone', adrenal_mat,
            size=(0.018, 0.014, 0.015),
            location=(sign * 0.052, 0.002, kz + 0.033),
            rotation_euler=(0.0, sign * 0.15, 0.0)
        )
        objects.append(adrenal)

        # Renal Pelvis Funnel at Hilum
        pelvis = kit.primitive_object(
            f'{ASSET_ID}-pelvis-{name}', 'cone', pelvis_mat,
            size=(0.012, 0.009, 0.018),
            location=(sign * 0.042, 0.0, kz - 0.004),
            rotation_euler=(0.0, 0.0, sign * (math.pi / 2 + 0.2))
        )
        objects.append(pelvis)

    # 4. Renal Arteries & Veins (All capped cleanly with ZERO non-manifold edges)
    # Right Renal Artery: emerges from aorta, passes behind IVC to right hilum
    r_art_pts = [
        (0.007, -0.004, 0.128),
        (-0.002, -0.008, 0.127),
        (-0.025, -0.006, 0.125),
        (-0.043, 0.0, 0.124),
    ]
    r_art = kit.create_smooth_tube(f'{ASSET_ID}-renal-artery-right', r_art_pts, radius=0.0030, cap_ends=True, material=aorta_mat)

    # Left Renal Artery: short direct branch to left hilum
    l_art_pts = [
        (0.007, -0.004, 0.136),
        (0.024, -0.004, 0.136),
        (0.043, 0.0, 0.136),
    ]
    l_art = kit.create_smooth_tube(f'{ASSET_ID}-renal-artery-left', l_art_pts, radius=0.0030, cap_ends=True, material=aorta_mat)

    # Right Renal Vein: short direct branch from right hilum to IVC
    r_vein_pts = [
        (-0.043, 0.002, 0.126),
        (-0.025, 0.003, 0.126),
        (-0.007, 0.002, 0.126),
    ]
    r_vein = kit.create_smooth_tube(f'{ASSET_ID}-renal-vein-right', r_vein_pts, radius=0.0038, cap_ends=True, material=vena_cava_mat)

    # Left Renal Vein: crosses anterior to aorta (+Y) to reach IVC on opposite side
    l_vein_pts = [
        (0.043, 0.002, 0.138),
        (0.024, 0.005, 0.137),
        (0.007, 0.008, 0.135),    # Arches anteriorly over aorta!
        (-0.007, 0.002, 0.134),
    ]
    l_vein = kit.create_smooth_tube(f'{ASSET_ID}-renal-vein-left', l_vein_pts, radius=0.0038, cap_ends=True, material=vena_cava_mat)
    objects.extend([r_art, l_art, r_vein, l_vein])

    # 5. Bilateral Curving Ureters (Conducting urine down into posterolateral bladder base)
    # Right Ureter
    u_right_pts = [
        (-0.038, 0.0, 0.118),
        (-0.034, 0.004, 0.090),
        (-0.028, 0.006, 0.060),
        (-0.020, 0.006, 0.036),
        (-0.014, 0.002, 0.020),  # Enters posterolateral bladder wall
    ]
    u_right = kit.create_smooth_tube(f'{ASSET_ID}-ureter-right', u_right_pts, radius=0.0024, cap_ends=True, material=ureter_mat)

    # Left Ureter
    u_left_pts = [
        (0.038, 0.0, 0.130),
        (0.034, 0.004, 0.095),
        (0.028, 0.006, 0.062),
        (0.020, 0.006, 0.036),
        (0.014, 0.002, 0.020),  # Enters posterolateral bladder wall
    ]
    u_left = kit.create_smooth_tube(f'{ASSET_ID}-ureter-left', u_left_pts, radius=0.0024, cap_ends=True, material=ureter_mat)
    objects.extend([u_right, u_left])

    # 6. Muscular Pear-Shaped Urinary Bladder
    bladder = kit.primitive_object(
        f'{ASSET_ID}-bladder', 'uv_sphere', bladder_mat,
        size=(0.044, 0.038, 0.046),
        location=(0.0, 0.004, 0.016)
    )
    bladder_neck = kit.primitive_object(
        f'{ASSET_ID}-bladder-neck', 'cone', bladder_mat,
        size=(0.022, 0.020, 0.016),
        location=(0.0, 0.004, -0.006),
        rotation_euler=(math.pi, 0.0, 0.0)
    )
    objects.extend([bladder, bladder_neck])

    # 7. Urethra (Outflow canal exiting inferior bladder)
    urethra = kit.primitive_object(
        f'{ASSET_ID}-urethra', 'cylinder', ureter_mat,
        size=(0.006, 0.006, 0.022),
        location=(0.0, 0.004, -0.018)
    )
    objects.append(urethra)

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_excretory()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')


if __name__ == '__main__':
    main()
