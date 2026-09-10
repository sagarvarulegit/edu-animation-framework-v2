"""
build_digestive.py — High-Fidelity Human Digestive System (Alimentary Canal & Accessory Organs)
CBSE Class 10 Biology, Chapter 5: Life Processes — Nutrition in Human Beings (Fig 5.6)
CBSE Class 11 Biology, Chapter 16: Digestion and Absorption (Fig 16.1, 16.2, 16.3)

Key Anatomical Features:
- Complete Continuous Gastrointestinal (GI) Tract from mouth to rectum:
  * Mouth / oral cavity with teeth/tongue space
  * Pharynx and continuous muscular esophagus
  * J-shaped muscular stomach: cardiac notch, fundus, body with greater/lesser curvatures, pyloric sphincter
  * C-shaped duodenal loop embracing the head of the pancreas
  * Continuous looping small intestine (jejunum & ileum) as a serpentine mesenteric coil
  * Large intestine (colon): ileocecal valve, caecum with vermiform appendix, ascending colon,
    hepatic flexure, transverse colon, splenic flexure, descending colon, sigmoid colon,
    rectum, and anal canal.
- Accessory Organs & Hepatopancreatic Duct Convergence:
  * Liver: right and left lobes separated by falciform groove
  * Gallbladder: green bile storage sac with cystic duct
  * Common bile duct uniting with main pancreatic duct (Duct of Wirsung) from pancreas
  * Convergence into the Hepatopancreatic Ampulla (Ampulla of Vater) entering duodenal C-loop
- ZERO non-manifold edges: all tubular segments and organs capped cleanly.
"""

import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy, bmesh
from mathutils import Vector

ASSET_ID = "digestive-system"


def create_j_stomach(name, stomach_mat):
    """
    Creates an anatomically authentic J-shaped stomach with convex greater curvature,
    concave lesser curvature, rounded superior fundus, and tapering pylorus.
    """
    bm = bmesh.new()
    num_rings = 24
    num_pts = 24

    # Trajectory of gastric midline axis: starts at cardiac orifice, dips through body, rises to pylorus
    gastric_axis = [
        # (t, center_x, center_y, center_z, scale_x, scale_y)
        (0.00, -0.005, 0.002, 0.064, 0.006, 0.006),  # Cardiac entrance from esophagus
        (0.12, -0.012, 0.004, 0.068, 0.012, 0.010),  # Fundus dome expansion
        (0.25, -0.016, 0.005, 0.062, 0.015, 0.012),  # Upper body
        (0.45, -0.014, 0.005, 0.048, 0.016, 0.013),  # Mid gastric body (widest)
        (0.65, -0.008, 0.005, 0.038, 0.014, 0.012),  # Lower body / incisura angularis
        (0.80,  0.002, 0.004, 0.036, 0.010, 0.009),  # Pyloric antrum
        (0.92,  0.008, 0.003, 0.038, 0.007, 0.007),  # Pyloric canal
        (1.00,  0.012, 0.003, 0.040, 0.006, 0.006),  # Pyloric sphincter into duodenum
    ]

    # Interpolate along gastric axis
    slices = []
    for r in range(num_rings):
        tr = r / (num_rings - 1)
        # Find segment
        idx = 0
        while idx < len(gastric_axis) - 2 and gastric_axis[idx + 1][0] < tr:
            idx += 1
        p0 = gastric_axis[idx]
        p1 = gastric_axis[idx + 1]
        span = p1[0] - p0[0]
        u = (tr - p0[0]) / span if span > 0 else 0.0
        # Smooth hermite interpolation
        u_s = u * u * (3.0 - 2.0 * u)

        cx = p0[1] + (p1[1] - p0[1]) * u_s
        cy = p0[2] + (p1[2] - p0[2]) * u_s
        cz = p0[3] + (p1[3] - p0[3]) * u_s
        sx = p0[4] + (p1[4] - p0[4]) * u_s
        sy = p0[5] + (p1[5] - p0[5]) * u_s

        ring = []
        for i in range(num_pts):
            theta = 2.0 * math.pi * i / num_pts
            # Gastric asymmetry: greater curvature (+X left) vs lesser curvature (-X right)
            px = sx * math.cos(theta)
            py = sy * math.sin(theta)
            ring.append(bm.verts.new((cx + px, cy + py, cz)))
        slices.append(ring)

    # Faces between slices
    for r in range(num_rings - 1):
        for i in range(num_pts):
            next_i = (i + 1) % num_pts
            bm.faces.new([slices[r][i], slices[r][next_i], slices[r + 1][next_i], slices[r + 1][i]])

    # Cap both ends
    cardiac_cap = bm.verts.new((-0.005, 0.002, 0.064))
    pylorus_cap = bm.verts.new((0.012, 0.003, 0.040))
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([slices[0][next_i], slices[0][i], cardiac_cap])
        bm.faces.new([slices[-1][i], slices[-1][next_i], pylorus_cap])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    sub = obj.modifiers.new("Subsurf", type='SUBSURF')
    sub.levels = 2
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    bpy.ops.object.shade_smooth()
    obj.data.materials.append(stomach_mat)
    return obj


def build_digestive():
    # 1. Biological Tissue Shaders with Subsurface Scattering
    mouth_mat = kit.add_tissue_material("digest-mouth", base_color=(0.85, 0.55, 0.50, 1.0), roughness=0.45,
                                        subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2))
    esophagus_mat = kit.add_tissue_material("digest-esophagus", base_color=(0.78, 0.52, 0.48, 1.0), roughness=0.50,
                                            subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2))
    stomach_mat = kit.add_tissue_material("digest-stomach", base_color=(0.80, 0.42, 0.36, 1.0), roughness=0.45,
                                          subsurface_weight=0.35, subsurface_radius=(0.7, 0.3, 0.2))
    liver_mat = kit.add_tissue_material("digest-liver", base_color=(0.48, 0.18, 0.14, 1.0), roughness=0.40,
                                        subsurface_weight=0.30, subsurface_radius=(0.8, 0.2, 0.1))
    gall_mat = kit.add_material("digest-gallbladder", (0.24, 0.58, 0.22), metallic=0.08, roughness=0.30)
    pancreas_mat = kit.add_tissue_material("digest-pancreas", base_color=(0.88, 0.72, 0.40, 1.0), roughness=0.50,
                                           subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2))
    duct_mat = kit.add_material("digest-duct", (0.35, 0.70, 0.30), metallic=0.05, roughness=0.35)
    small_int_mat = kit.add_tissue_material("digest-small-int", base_color=(0.84, 0.58, 0.50, 1.0), roughness=0.45,
                                            subsurface_weight=0.30, subsurface_radius=(0.6, 0.3, 0.2))
    large_int_mat = kit.add_tissue_material("digest-large-int", base_color=(0.72, 0.50, 0.44, 1.0), roughness=0.50,
                                            subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2))
    rectum_mat = kit.add_tissue_material("digest-rectum", base_color=(0.65, 0.42, 0.38, 1.0), roughness=0.55,
                                         subsurface_weight=0.25, subsurface_radius=(0.5, 0.3, 0.2))

    objects = []

    # 2. Oral Cavity & Pharynx (Buccal cavity, tongue, and swallowing pharynx)
    mouth = kit.primitive_object(
        f"{ASSET_ID}-mouth", "uv_sphere", mouth_mat,
        size=(0.024, 0.022, 0.016),
        location=(0.0, 0.005, 0.125)
    )
    pharynx = kit.primitive_object(
        f"{ASSET_ID}-pharynx", "cylinder", esophagus_mat,
        size=(0.010, 0.010, 0.014),
        location=(0.0, 0.002, 0.112)
    )
    objects.extend([mouth, pharynx])

    # 3. Continuous Muscular Esophagus (Gullet descending down through thorax)
    esoph_pts = [
        (0.000, 0.002, 0.112),
        (0.000, 0.001, 0.090),
        (-0.002, 0.000, 0.076),
        (-0.005, 0.002, 0.064),  # Enters cardiac sphincter of stomach
    ]
    esophagus = kit.create_smooth_tube(f"{ASSET_ID}-esophagus", esoph_pts, radius=0.0042, cap_ends=True, material=esophagus_mat)
    objects.append(esophagus)

    # 4. J-Shaped Muscular Stomach (Fundus dome, gastric body, greater/lesser curvatures, pylorus)
    stomach = create_j_stomach(f"{ASSET_ID}-stomach", stomach_mat)
    objects.append(stomach)

    # 5. Liver (Large multi-lobed metabolic gland dominating right upper quadrant)
    # Right Lobe (large triangular mass)
    liver_r = kit.primitive_object(
        f"{ASSET_ID}-liver-right", "cube", liver_mat,
        size=(0.034, 0.020, 0.026),
        location=(0.022, 0.008, 0.062),
        rotation_euler=(0.0, 0.12, -0.18)
    )
    mod_r = liver_r.modifiers.new("subsurf", type="SUBSURF")
    mod_r.levels = 2
    # Left Lobe (smaller triangular mass extending across midline)
    liver_l = kit.primitive_object(
        f"{ASSET_ID}-liver-left", "cube", liver_mat,
        size=(0.020, 0.014, 0.018),
        location=(-0.002, 0.009, 0.065),
        rotation_euler=(0.0, -0.10, 0.15)
    )
    mod_l = liver_l.modifiers.new("subsurf", type="SUBSURF")
    mod_l.levels = 2
    objects.extend([liver_r, liver_l])

    # 6. Gallbladder & Hepatobiliary Ducts
    # Gallbladder (Pear-shaped green bile sac under inferior liver surface)
    gallbladder = kit.primitive_object(
        f"{ASSET_ID}-gallbladder", "uv_sphere", gall_mat,
        size=(0.008, 0.008, 0.014),
        location=(0.016, 0.012, 0.048),
        rotation_euler=(0.35, 0.0, 0.0)
    )
    objects.append(gallbladder)

    # Cystic duct from gallbladder
    cystic_pts = [
        (0.016, 0.012, 0.048),
        (0.018, 0.008, 0.042),
        (0.019, 0.005, 0.036),
    ]
    cystic_duct = kit.create_smooth_tube(f"{ASSET_ID}-cystic-duct", cystic_pts, radius=0.0012, cap_ends=True, material=duct_mat)

    # Hepatic ducts from liver lobes uniting to common hepatic duct
    hepatic_r_pts = [(0.022, 0.008, 0.050), (0.019, 0.005, 0.040)]
    hepatic_l_pts = [(0.006, 0.008, 0.052), (0.019, 0.005, 0.040)]
    hep_r = kit.create_smooth_tube(f"{ASSET_ID}-hepatic-duct-r", hepatic_r_pts, radius=0.0011, cap_ends=True, material=duct_mat)
    hep_l = kit.create_smooth_tube(f"{ASSET_ID}-hepatic-duct-l", hepatic_l_pts, radius=0.0011, cap_ends=True, material=duct_mat)

    # Common Bile Duct (Ductus Choledochus): descends to join pancreatic duct
    bile_duct_pts = [
        (0.019, 0.005, 0.036),
        (0.021, 0.003, 0.032),
        (0.022, 0.002, 0.026),  # Converges into hepatopancreatic ampulla at duodenum
    ]
    bile_duct = kit.create_smooth_tube(f"{ASSET_ID}-common-bile-duct", bile_duct_pts, radius=0.0013, cap_ends=True, material=duct_mat)
    objects.extend([cystic_duct, hep_r, hep_l, bile_duct])

    # 7. Pancreas & Pancreatic Duct (Gland nestled in duodenal loop)
    pancreas = kit.primitive_object(
        f"{ASSET_ID}-pancreas", "cylinder", pancreas_mat,
        size=(0.009, 0.008, 0.034),
        location=(0.002, -0.002, 0.036),
        rotation_euler=(0.0, 1.45, 0.0)
    )
    # Pancreatic Duct (Duct of Wirsung) running along pancreas and converging with bile duct
    panc_duct_pts = [
        (-0.012, -0.002, 0.038),  # Pancreas tail
        (0.002, -0.002, 0.034),   # Pancreas body
        (0.014, 0.000, 0.028),    # Pancreas head
        (0.022, 0.002, 0.026),    # Converges with bile duct!
    ]
    panc_duct = kit.create_smooth_tube(f"{ASSET_ID}-pancreatic-duct", panc_duct_pts, radius=0.0011, cap_ends=True, material=duct_mat)

    # Hepatopancreatic Ampulla (Ampulla of Vater) entering the C-loop of duodenum
    ampulla = kit.primitive_object(
        f"{ASSET_ID}-ampulla-vater", "uv_sphere", duct_mat,
        size=(0.0035, 0.0035, 0.0035),
        location=(0.0225, 0.002, 0.026)
    )
    objects.extend([pancreas, panc_duct, ampulla])

    # 8. Duodenum (C-shaped duodenal loop receiving chyme and hepatopancreatic juices)
    duodenum_pts = [
        (0.012, 0.003, 0.040),   # Emerges from pylorus
        (0.020, 0.003, 0.041),   # Superior duodenal flexure
        (0.025, 0.002, 0.033),   # Descending duodenum
        (0.023, 0.002, 0.025),   # Major duodenal papilla site
        (0.014, 0.002, 0.020),   # Horizontal/inferior duodenal limb
        (0.004, 0.003, 0.020),   # Ascending duodenum
        (-0.005, 0.004, 0.023),  # Duodenojejunal flexure transitioning into jejunum
    ]
    duodenum = kit.create_smooth_tube(f"{ASSET_ID}-duodenum", duodenum_pts, radius=0.0046, cap_ends=True, material=small_int_mat)
    objects.append(duodenum)

    # 9. Small Intestine (Continuous Serpentine Looping Coils: Jejunum & Ileum)
    # Replaces primitive spheres with an authentic continuous lumen tube
    small_int_pts = [
        (-0.005, 0.004, 0.023),  # Duodenojejunal flexure start
        (-0.012, 0.006, 0.026),
        (-0.016, 0.007, 0.018),
        (-0.008, 0.007, 0.014),
        (0.004, 0.006, 0.016),
        (0.014, 0.005, 0.013),
        (0.012, 0.006, 0.005),
        (0.000, 0.007, 0.006),
        (-0.010, 0.007, 0.008),
        (-0.016, 0.006, 0.000),
        (-0.008, 0.006, -0.006),
        (0.005, 0.006, -0.004),
        (0.014, 0.005, -0.006),
        (0.020, 0.003, -0.004),  # Enters caecum at ileocecal valve!
    ]
    small_intestine = kit.create_smooth_tube(
        f"{ASSET_ID}-small-intestine-coil", small_int_pts, radius=0.0040, cap_ends=True, material=small_int_mat
    )
    objects.append(small_intestine)

    # 10. Large Intestine / Colon with Haustra (Framing the small intestine perimeter)
    # Caecum (Dilated pouch in right iliac fossa)
    caecum = kit.primitive_object(
        f"{ASSET_ID}-caecum", "uv_sphere", large_int_mat,
        size=(0.016, 0.014, 0.016),
        location=(0.022, 0.002, -0.005)
    )
    # Vermiform Appendix (Slender blind-ended diverticulum)
    app_pts = [
        (0.024, 0.002, -0.011),
        (0.027, 0.001, -0.018),
        (0.024, 0.000, -0.023),
    ]
    appendix = kit.create_smooth_tube(f"{ASSET_ID}-appendix", app_pts, radius=0.0018, cap_ends=True, material=large_int_mat)
    objects.extend([caecum, appendix])

    # Continuous Colon Pathway: Ascending, Transverse, Descending, Sigmoid, Rectum
    colon_pts = [
        (0.022, 0.002, -0.005),  # From caecum
        (0.024, 0.002, 0.014),   # Ascending colon
        (0.023, 0.003, 0.030),   # Hepatic flexure (right colic flexure)
        (0.012, 0.006, 0.033),   # Transverse colon right
        (0.000, 0.007, 0.032),   # Transverse colon mid (crosses anterior abdomen)
        (-0.012, 0.006, 0.033),  # Transverse colon left
        (-0.022, 0.003, 0.030),  # Splenic flexure (left colic flexure)
        (-0.023, 0.002, 0.014),  # Descending colon
        (-0.021, 0.002, -0.004), # Left iliac fossa
        (-0.015, 0.003, -0.010), # Sigmoid colon S-loop
        (-0.006, 0.002, -0.012), # Sigmoid colon toward midline
        (0.000, 0.001, -0.015),  # Rectum entrance
        (0.000, 0.000, -0.024),  # Rectum terminal ampulla
        (0.000, 0.000, -0.028),  # Anal canal & anus
    ]
    colon_trunk = kit.create_smooth_tube(f"{ASSET_ID}-colon-trunk", colon_pts, radius=0.0060, cap_ends=True, material=large_int_mat)
    objects.append(colon_trunk)

    # Anatomical Haustral Sacculations (Bulging segments giving the colon its characteristic puckered look)
    haustra_locs = [
        (0.024, 0.002, 0.005),
        (0.024, 0.002, 0.022),
        (0.016, 0.006, 0.033),
        (0.006, 0.007, 0.033),
        (-0.006, 0.007, 0.033),
        (-0.016, 0.006, 0.033),
        (-0.023, 0.002, 0.022),
        (-0.023, 0.002, 0.005),
        (-0.018, 0.003, -0.007),
    ]
    for h_idx, (hx, hy, hz) in enumerate(haustra_locs):
        h_obj = kit.primitive_object(
            f"{ASSET_ID}-haustrum-{h_idx}", "uv_sphere", large_int_mat,
            size=(0.014, 0.013, 0.012),
            location=(hx, hy, hz)
        )
        objects.append(h_obj)

    # Rectum & Anal Sphincter Canal
    rectum = kit.primitive_object(
        f"{ASSET_ID}-rectum", "cylinder", rectum_mat,
        size=(0.012, 0.012, 0.016),
        location=(0.0, 0.0, -0.020)
    )
    anus = kit.primitive_object(
        f"{ASSET_ID}-anus", "cylinder", rectum_mat,
        size=(0.008, 0.008, 0.006),
        location=(0.0, 0.0, -0.028)
    )
    objects.extend([rectum, anus])

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_digestive()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=24)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered.")


if __name__ == "__main__":
    main()
