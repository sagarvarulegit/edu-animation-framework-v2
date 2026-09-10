"""
build_respiratory.py — Anatomical Human Respiratory System & Alveoli Cluster
CBSE Class 10 Biology, Chapter 5: Life Processes — Respiration in Human Beings (Fig 5.9)
CBSE Class 11 Biology, Chapter 17: Breathing and Exchange of Gases (Fig 17.1)

Key Anatomical Features:
- Larynx: Thyroid cartilage with Adam's apple laryngeal prominence, cricoid cartilage ring, and epiglottis.
- Trachea (Windpipe): Transparent/cutaway lumen surrounded by authentic C-shaped hyaline cartilaginous
  rings, open posteriorly (< 360 deg arc) where the smooth trachealis muscle abuts the esophagus.
- Carina & Bronchial Tree: Primary bronchi bifurcating at carina (T5 level), branching into secondary
  lobar bronchi (3 right: superior, middle, inferior; 2 left: superior, inferior) and tertiary
  segmental bronchioles penetrating deeply into lung segments.
- Bilateral Lungs: Transparent lung parenchyma (dielectric transmission with tissue scattering)
  revealing the internal bronchial tree. Right lung has 3 lobes (oblique and horizontal fissures),
  left lung has 2 lobes with cardiac notch indentation.
- Muscular Diaphragm: Conforming double-domed sheet with central tendon beneath the lungs.
- Magnified Alveoli Cluster: Terminal respiratory bronchiole, alveolar duct, grape-like cluster
  of spherical alveoli sacs, and anastomosing capillary plexus (oxygenated red and deoxygenated blue).
- ZERO non-manifold edges: all tubular structures capped cleanly via kit.create_smooth_tube(..., cap_ends=True).
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = 'human-respiratory-system'


def create_anatomical_lung(name, sign, lung_mat, fissure_mat):
    """
    Creates an authentic, anatomically contoured lung with concave diaphragmatic base,
    convex costal wall, flat mediastinal surface, and interlobar fissures.
    sign = +1 for Right Lung (3 lobes: superior, middle, inferior).
    sign = -1 for Left Lung (2 lobes with prominent medial cardiac notch).
    """
    bm = bmesh.new()
    num_z = 24
    num_pts = 24

    z_min = 0.012
    z_max = 0.125

    slices = []
    for s in range(num_z):
        tz = s / (num_z - 1)  # 0 to 1
        z = z_min + tz * (z_max - z_min)

        # Anatomical profile: tapered apex at top, widest in lower third, concave at base
        if tz < 0.15:
            width_factor = 0.85 + tz * 1.0
        elif tz < 0.6:
            width_factor = 1.0 + 0.15 * math.sin(tz * math.pi)
        else:
            width_factor = 1.15 * math.cos((tz - 0.6) * (math.pi / 0.9))
        width_factor = max(width_factor, 0.18)

        rx = 0.024 * width_factor
        ry = 0.028 * width_factor

        # Center of cross-section
        center_x = sign * (0.042 - 0.005 * tz)
        center_y = -0.002 * tz

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            ct = math.cos(theta)
            st = math.sin(theta)

            px = rx * ct
            py = ry * st

            # Medial surface flattening (facing spine & mediastinum, where ct * sign < 0)
            if (ct * sign) < 0:
                px *= 0.68

            # Cardiac notch indentation for Left Lung (sign = -1) on antero-medial face
            if sign == -1 and 0.25 < tz < 0.65:
                cardiac_depth = 0.011 * math.sin((tz - 0.25) / 0.40 * math.pi)
                if ct > -0.2 and st > -0.2:
                    px -= cardiac_depth * 0.7
                    py -= cardiac_depth * 0.5

            # Concave diaphragmatic base underside
            vz = z
            if s == 0:
                vz = z_min + 0.004 * (1.0 - math.sqrt(ct * ct + st * st))

            v = bm.verts.new((center_x + px, center_y + py, vz))
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

    # Cap apex and base
    base_center = bm.verts.new((sign * 0.042, 0.0, z_min + 0.004))
    apex_center = bm.verts.new((sign * 0.037, 0.0, z_max))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][next_i], slices[0][i], base_center])
        bm.faces.new([slices[-1][i], slices[-1][next_i], apex_center])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    sub.render_levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(lung_mat)

    # Interlobar Fissures with clean manifold capping
    fissure_objs = []
    if sign == 1:
        # Right lung: Oblique fissure and Horizontal fissure
        f1_pts = [
            (0.022, -0.018, 0.092),
            (0.046, -0.012, 0.070),
            (0.065, 0.005, 0.045),
            (0.042, 0.016, 0.030),
            (0.024, 0.005, 0.035),
        ]
        fissure_objs.append(kit.create_smooth_tube(f'{name}-oblique-fissure', f1_pts, radius=0.0014, cap_ends=True, material=fissure_mat))
        f2_pts = [
            (0.026, 0.005, 0.058),
            (0.048, 0.015, 0.058),
            (0.064, 0.008, 0.056),
            (0.060, -0.010, 0.055),
        ]
        fissure_objs.append(kit.create_smooth_tube(f'{name}-horizontal-fissure', f2_pts, radius=0.0014, cap_ends=True, material=fissure_mat))
    else:
        # Left lung: Oblique fissure
        f_left_pts = [
            (-0.020, -0.018, 0.090),
            (-0.042, -0.012, 0.068),
            (-0.062, 0.004, 0.042),
            (-0.038, 0.014, 0.026),
            (-0.022, 0.004, 0.032),
        ]
        fissure_objs.append(kit.create_smooth_tube(f'{name}-oblique-fissure', f_left_pts, radius=0.0014, cap_ends=True, material=fissure_mat))

    return obj, fissure_objs


def build_respiratory():
    # 1. PBR Materials with realistic optical transmission for lung cutaway
    lung_mat = kit.add_material('lung-tissue', (0.76, 0.32, 0.36), metallic=0.02, roughness=0.24)
    bsdf_lung = lung_mat.node_tree.nodes["Principled BSDF"]
    if "Transmission Weight" in bsdf_lung.inputs:
        bsdf_lung.inputs["Transmission Weight"].default_value = 0.78
    elif "Transmission" in bsdf_lung.inputs:
        bsdf_lung.inputs["Transmission"].default_value = 0.78
    if "IOR" in bsdf_lung.inputs:
        bsdf_lung.inputs["IOR"].default_value = 1.34

    fissure_mat = kit.add_material('interlobar-fissure', (0.35, 0.10, 0.14), metallic=0.06, roughness=0.40)
    cartilage_mat = kit.add_tissue_material('hyaline-cartilage', base_color=(0.82, 0.86, 0.84, 1.0), roughness=0.30,
                                            subsurface_weight=0.35, subsurface_radius=(0.4, 0.3, 0.2))
    larynx_mat = kit.add_material('thyroid-cartilage', (0.75, 0.70, 0.62), metallic=0.04, roughness=0.35)
    airway_mat = kit.add_tissue_material('airway-tube', base_color=(0.58, 0.20, 0.22, 1.0), roughness=0.35,
                                         subsurface_weight=0.25, subsurface_radius=(0.5, 0.2, 0.1))
    bronchiole_mat = kit.add_tissue_material('bronchiole-tube', base_color=(0.65, 0.28, 0.30, 1.0), roughness=0.35,
                                             subsurface_weight=0.20, subsurface_radius=(0.4, 0.2, 0.1))
    diaphragm_mat = kit.add_material('diaphragm-muscle', (0.42, 0.10, 0.12), metallic=0.06, roughness=0.38)
    tendon_mat = kit.add_material('central-tendon', (0.78, 0.80, 0.76), metallic=0.02, roughness=0.32)
    oxy_mat = kit.add_material('capillary-oxy', (0.85, 0.08, 0.10), metallic=0.15, roughness=0.22)
    deoxy_mat = kit.add_material('capillary-deoxy', (0.12, 0.28, 0.80), metallic=0.15, roughness=0.22)
    alveolus_mat = kit.add_tissue_material('alveolar-sac', base_color=(0.82, 0.60, 0.62, 1.0), roughness=0.32,
                                           subsurface_weight=0.30, subsurface_radius=(0.6, 0.3, 0.2))

    objects = []

    # 2. Larynx (Anatomical Thyroid, Cricoid, Prominence, Epiglottis at z = 0.19m)
    thyroid = kit.primitive_object(
        f'{ASSET_ID}-larynx-thyroid', 'cube', larynx_mat,
        size=(0.024, 0.020, 0.024),
        location=(0.0, 0.004, 0.192)
    )
    adam_prom = kit.primitive_object(
        f'{ASSET_ID}-larynx-prominence', 'cone', larynx_mat,
        size=(0.014, 0.012, 0.016),
        location=(0.0, 0.014, 0.195),
        rotation_euler=(-math.pi / 2, 0.0, 0.0)
    )
    cricoid = kit.primitive_object(
        f'{ASSET_ID}-larynx-cricoid', 'cylinder', cartilage_mat,
        size=(0.020, 0.020, 0.008),
        location=(0.0, 0.0, 0.176)
    )
    epiglottis = kit.primitive_object(
        f'{ASSET_ID}-epiglottis', 'cube', cartilage_mat,
        size=(0.016, 0.005, 0.016),
        location=(0.0, -0.006, 0.208),
        rotation_euler=(-0.35, 0.0, 0.0)
    )
    objects.extend([thyroid, adam_prom, cricoid, epiglottis])

    # 3. Trachea & Authentic C-Shaped Cartilaginous Rings (Open posteriorly)
    trachea_tube = kit.primitive_object(
        f'{ASSET_ID}-trachea-lumen', 'cylinder', airway_mat,
        size=(0.015, 0.015, 0.065),
        location=(0.0, 0.0, 0.140)
    )
    objects.append(trachea_tube)

    # Posterior trachealis muscle (connecting the open ends of the C-rings)
    trachealis = kit.primitive_object(
        f'{ASSET_ID}-trachealis-muscle', 'cube', airway_mat,
        size=(0.011, 0.0025, 0.065),
        location=(0.0, -0.0075, 0.140)
    )
    objects.append(trachealis)

    # 8 C-shaped Cartilage Rings (Open posteriorly at -Y, arc covers ~260 degrees)
    ring_radius = 0.0088
    for i in range(8):
        rz = 0.112 + i * 0.0078
        c_ring_pts = []
        for deg in range(-130, 131, 20):
            rad = math.radians(deg)
            # Anterior is +Y (deg = 0 => x=0, y=ring_radius)
            # Posterior is -Y (deg = +/- 130 => x = +/- R*sin(130), y = -R*cos(50))
            rx = ring_radius * math.sin(rad)
            ry = ring_radius * math.cos(rad)
            c_ring_pts.append((rx, ry, rz))

        c_ring = kit.create_smooth_tube(
            f'{ASSET_ID}-cartilage-c-ring-{i}', c_ring_pts, radius=0.0016, cap_ends=True, material=cartilage_mat
        )
        objects.append(c_ring)

    # 4. Carina & Primary Bronchi Bifurcation (Bifurcates at z = 0.108m)
    r_bronchus_pts = [
        (0.000, 0.0, 0.108),
        (0.014, 0.0, 0.096),
        (0.026, 0.0, 0.082),
    ]
    r_bronchus = kit.create_smooth_tube(f'{ASSET_ID}-bronchus-r', r_bronchus_pts, radius=0.0048, cap_ends=True, material=airway_mat)

    l_bronchus_pts = [
        (0.000, 0.0, 0.108),
        (-0.016, 0.0, 0.094),
        (-0.030, 0.0, 0.080),
    ]
    l_bronchus = kit.create_smooth_tube(f'{ASSET_ID}-bronchus-l', l_bronchus_pts, radius=0.0044, cap_ends=True, material=airway_mat)
    objects.extend([r_bronchus, l_bronchus])

    # 5. Secondary Lobar Bronchi (Right: 3 lobes; Left: 2 lobes)
    # Right Lobar: Superior, Middle, Inferior
    r_lobar_specs = [
        ([(0.026, 0.0, 0.082), (0.033, 0.006, 0.096), (0.038, 0.008, 0.108)], 'sup', 0.0034),
        ([(0.026, 0.0, 0.082), (0.038, 0.010, 0.075), (0.048, 0.008, 0.062)], 'mid', 0.0032),
        ([(0.026, 0.0, 0.082), (0.034, -0.006, 0.060), (0.040, -0.004, 0.038)], 'inf', 0.0035),
    ]
    for pts, tag, rad in r_lobar_specs:
        b_obj = kit.create_smooth_tube(f'{ASSET_ID}-bronchus-r-lobar-{tag}', pts, radius=rad, cap_ends=True, material=airway_mat)
        objects.append(b_obj)

    # Left Lobar: Superior and Inferior
    l_lobar_specs = [
        ([(-0.030, 0.0, 0.080), (-0.036, 0.006, 0.094), (-0.038, 0.008, 0.106)], 'sup', 0.0034),
        ([(-0.030, 0.0, 0.080), (-0.038, -0.006, 0.060), (-0.042, -0.004, 0.036)], 'inf', 0.0035),
    ]
    for pts, tag, rad in l_lobar_specs:
        b_obj = kit.create_smooth_tube(f'{ASSET_ID}-bronchus-l-lobar-{tag}', pts, radius=rad, cap_ends=True, material=airway_mat)
        objects.append(b_obj)

    # 6. Tertiary Segmental Bronchioles (Arborizing throughout lung lobes)
    segmental_specs = [
        # Right Superior Lobe segments (apical, anterior, posterior)
        ([(0.038, 0.008, 0.108), (0.037, 0.004, 0.118)], 'r-apical'),
        ([(0.038, 0.008, 0.108), (0.048, 0.012, 0.102)], 'r-anterior'),
        # Right Middle Lobe segments (lateral, medial)
        ([(0.048, 0.008, 0.062), (0.058, 0.010, 0.060)], 'r-lateral'),
        ([(0.048, 0.008, 0.062), (0.044, 0.014, 0.052)], 'r-medial'),
        # Right Inferior Lobe segments (superior, basal)
        ([(0.040, -0.004, 0.038), (0.052, -0.008, 0.032)], 'r-basal-lat'),
        ([(0.040, -0.004, 0.038), (0.036, 0.006, 0.024)], 'r-basal-med'),
        # Left Superior Lobe segments (apicoposterior, anterior)
        ([(-0.038, 0.008, 0.106), (-0.037, 0.004, 0.116)], 'l-apicopost'),
        ([(-0.038, 0.008, 0.106), (-0.048, 0.012, 0.098)], 'l-anterior'),
        # Left Inferior Lobe segments
        ([(-0.042, -0.004, 0.036), (-0.052, -0.008, 0.028)], 'l-basal-lat'),
        ([(-0.042, -0.004, 0.036), (-0.036, 0.006, 0.022)], 'l-basal-med'),
    ]
    for pts, tag in segmental_specs:
        seg_obj = kit.create_smooth_tube(f'{ASSET_ID}-bronchiole-{tag}', pts, radius=0.0020, cap_ends=True, material=bronchiole_mat)
        objects.append(seg_obj)

    # 7. Authentically Contoured Lungs (Transparent tissue reveals internal bronchial tree)
    r_lung, r_fissures = create_anatomical_lung(f'{ASSET_ID}-lung-right', 1, lung_mat, fissure_mat)
    l_lung, l_fissures = create_anatomical_lung(f'{ASSET_ID}-lung-left', -1, lung_mat, fissure_mat)
    objects.extend([r_lung, *r_fissures, l_lung, *l_fissures])

    # 8. Muscular Diaphragm (Double-domed sheet directly beneath lungs)
    diaphragm_bm = bmesh.new()
    d_rows = 18
    d_cols = 28
    for r in range(d_rows):
        v = r / (d_rows - 1)  # 0 to 1 (front to back)
        y = -0.040 + v * 0.080
        for c in range(d_cols):
            u = c / (d_cols - 1)  # 0 to 1 (left to right)
            x = -0.080 + u * 0.160

            # Double-dome height profile: peaks under right and left lungs
            r_peak = math.exp(-((x - 0.040) ** 2 / 0.0014 + y ** 2 / 0.0012))
            l_peak = math.exp(-((x + 0.040) ** 2 / 0.0014 + y ** 2 / 0.0012))
            z_dome = 0.002 + 0.016 * r_peak + 0.013 * l_peak

            # Downward flare at margins
            margin_dist = math.sqrt((x / 0.080) ** 2 + (y / 0.040) ** 2)
            if margin_dist > 0.7:
                z_dome -= (margin_dist - 0.7) * 0.035

            diaphragm_bm.verts.new((x, y, z_dome))

    diaphragm_bm.verts.ensure_lookup_table()
    for r in range(d_rows - 1):
        for c in range(d_cols - 1):
            v1 = diaphragm_bm.verts[r * d_cols + c]
            v2 = diaphragm_bm.verts[r * d_cols + (c + 1)]
            v3 = diaphragm_bm.verts[(r + 1) * d_cols + (c + 1)]
            v4 = diaphragm_bm.verts[(r + 1) * d_cols + c]
            diaphragm_bm.faces.new([v1, v2, v3, v4])

    bmesh.ops.recalc_face_normals(diaphragm_bm, faces=diaphragm_bm.faces)
    d_mesh = bpy.data.meshes.new(f'{ASSET_ID}-diaphragm-mesh')
    diaphragm_bm.to_mesh(d_mesh)
    diaphragm_bm.free()

    diaphragm_obj = bpy.data.objects.new(f'{ASSET_ID}-diaphragm', d_mesh)
    bpy.context.collection.objects.link(diaphragm_obj)

    sol = diaphragm_obj.modifiers.new("Solidify", type='SOLIDIFY')
    sol.thickness = 0.004
    sol.use_rim = True
    bpy.context.view_layer.objects.active = diaphragm_obj
    diaphragm_obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Solidify")
    sub = diaphragm_obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 1
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    diaphragm_obj.data.materials.append(diaphragm_mat)
    objects.append(diaphragm_obj)

    # Central tendon of diaphragm
    tendon = kit.primitive_object(
        f'{ASSET_ID}-central-tendon', 'uv_sphere', tendon_mat,
        size=(0.030, 0.024, 0.004),
        location=(0.0, 0.0, 0.010)
    )
    objects.append(tendon)

    # 9. Magnified Alveoli Sac Cluster (Microscopic inset showing grape-like alveolar sacs & capillaries)
    alv_origin = Vector((0.090, -0.032, 0.040))
    alv_duct_pts = [
        (alv_origin.x - 0.020, alv_origin.y, alv_origin.z - 0.014),
        (alv_origin.x - 0.010, alv_origin.y, alv_origin.z - 0.008),
        (alv_origin.x, alv_origin.y, alv_origin.z),
    ]
    alv_duct = kit.create_smooth_tube(f'{ASSET_ID}-alveolar-duct', alv_duct_pts, radius=0.0026, cap_ends=True, material=airway_mat)
    objects.append(alv_duct)

    # 10 clustered alveoli sacs (grape-like spherical clusters)
    alv_offsets = [
        (0.000, 0.000, 0.000),
        (0.010, 0.005, 0.006),
        (-0.007, 0.008, 0.004),
        (0.003, -0.008, 0.005),
        (-0.006, -0.006, 0.010),
        (0.007, -0.003, 0.012),
        (-0.002, 0.007, 0.014),
        (0.002, 0.002, 0.018),
        (0.008, 0.006, 0.016),
        (-0.008, -0.002, 0.016),
    ]
    for idx, off in enumerate(alv_offsets):
        sac = kit.primitive_object(
            f'{ASSET_ID}-alveolus-{idx}', 'uv_sphere', alveolus_mat,
            size=(0.012, 0.012, 0.012),
            location=(alv_origin.x + off[0], alv_origin.y + off[1], alv_origin.z + off[2])
        )
        objects.append(sac)

    # Pulmonary capillary network loops entwining the alveolar sacs
    cap_loop_1 = [
        (alv_origin.x - 0.008, alv_origin.y - 0.008, alv_origin.z + 0.002),
        (alv_origin.x - 0.004, alv_origin.y - 0.010, alv_origin.z + 0.008),
        (alv_origin.x + 0.006, alv_origin.y - 0.006, alv_origin.z + 0.012),
        (alv_origin.x + 0.010, alv_origin.y + 0.002, alv_origin.z + 0.008),
    ]
    cap1 = kit.create_smooth_tube(f'{ASSET_ID}-cap-oxy-1', cap_loop_1, radius=0.0011, cap_ends=True, material=oxy_mat)

    cap_loop_2 = [
        (alv_origin.x - 0.008, alv_origin.y + 0.008, alv_origin.z + 0.004),
        (alv_origin.x - 0.002, alv_origin.y + 0.010, alv_origin.z + 0.010),
        (alv_origin.x + 0.006, alv_origin.y + 0.008, alv_origin.z + 0.014),
        (alv_origin.x + 0.004, alv_origin.y - 0.002, alv_origin.z + 0.018),
    ]
    cap2 = kit.create_smooth_tube(f'{ASSET_ID}-cap-deoxy-1', cap_loop_2, radius=0.0011, cap_ends=True, material=deoxy_mat)
    objects.extend([cap1, cap2])

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / 'out')
    kit.reset_scene()
    objects = build_respiratory()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f'{ASSET_ID}.blend')
    kit.export_glb(out / f'{ASSET_ID}.glb')
    kit.render_preview(out / 'preview.png')
    print(f'[OK] High-fidelity {ASSET_ID} built and rendered.')


if __name__ == '__main__':
    main()
