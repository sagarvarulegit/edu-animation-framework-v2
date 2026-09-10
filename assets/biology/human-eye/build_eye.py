"""
build_eye.py — High-Fidelity Anatomical Section of the Human Eye
CBSE Class 10 Physics/Biology, Chapter 11: The Human Eye and the Colorful World
CBSE Class 11 Biology, Chapter 21: Neural Control and Coordination — Sensory Reception and Processing (Eye)

Anatomical Features:
- 3 Concentric Tunics:
  1. Outer fibrous tunic: Opaque white Sclera (posterior 5/6) transitioning to transparent bulging Cornea (anterior 1/6)
  2. Middle vascular tunic (Uvea): Dark pigmented Choroid layer, Ciliary Body with ciliary processes, and Iris diaphragm
  3. Inner sensory tunic: Sensory Retina with photoreceptors, Optic Disc (blind spot), and Macula Lutea / Fovea Centralis
- True open pupil aperture in the iris: An open central aperture hole (inner_radius = 0.0045 m) admitting light directly to the lens
- Crystalline biconvex lens: Refractive optical element (IOR ~1.406) with realistic anterior/posterior curvature
- Suspensory zonules (Zonules of Zinn): 32 radial fiber strands suspending the lens equator from the ciliary body
- Refractive humors: Transparent vitreous humor body (IOR ~1.336) in posterior cavity and aqueous humor in anterior chamber
- Optic nerve bundle: Cranial nerve II exiting posteromedially with central retinal vessel branches
- Clean quadrant cutaway revealing concentric tunic thicknesses and internal optical architecture
- Subsurface Scattering (SSS) for biological tissues and physical dielectric transmission for optical components
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector

ASSET_ID = "human-eye"

# Dimensional constants (eyeball radius ~40 mm in standard model space)
R_SCLERA_OUT = 0.0400
R_SCLERA_IN  = 0.0380
R_CHOROID_IN = 0.0370
R_RETINA_IN  = 0.0360

PUPIL_INNER_RADIUS = 0.0045 # True open aperture radius (9 mm aperture diameter)
IRIS_OUTER_RADIUS  = 0.0135 # Peripheral ciliary border of iris


def create_hollow_tunic_cutaway(name, r_outer, r_inner, cut_box_loc, cut_box_scale, material):
    """
    Creates a concentric hollow spherical shell representing an anatomical eye tunic
    with a clean quadrant cutaway exposing layer thickness.
    """
    bm_out = bmesh.new()
    bmesh.ops.create_uvsphere(bm_out, u_segments=48, v_segments=32, radius=r_outer)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm_out.to_mesh(mesh)
    bm_out.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Inner cavity void
    bm_in = bmesh.new()
    bmesh.ops.create_uvsphere(bm_in, u_segments=48, v_segments=32, radius=r_inner)
    mesh_in = bpy.data.meshes.new("void")
    bm_in.to_mesh(mesh_in)
    bm_in.free()
    void_obj = bpy.data.objects.new("void", mesh_in)
    bpy.context.collection.objects.link(void_obj)

    # Cutaway box (e.g. removes anterior-superior-right quadrant)
    bm_cut = bmesh.new()
    bmesh.ops.create_cube(bm_cut, size=1.0)
    mesh_cut = bpy.data.meshes.new("cut")
    bm_cut.to_mesh(mesh_cut)
    bm_cut.free()
    cut_obj = bpy.data.objects.new("cut", mesh_cut)
    bpy.context.collection.objects.link(cut_obj)
    cut_obj.scale = cut_box_scale
    cut_obj.location = cut_box_loc

    bpy.context.view_layer.update()

    for cutter in [void_obj, cut_obj]:
        mod = obj.modifiers.new("Cut", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = cutter
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Cut")
        bpy.data.objects.remove(cutter, do_unlink=True)

    for poly in obj.data.polygons:
        poly.use_smooth = True

    if material:
        obj.data.materials.append(material)

    return obj


def create_iris_with_pupil_aperture(name, inner_radius, outer_radius, thickness, iris_mat, pupil_margin_mat):
    """
    Creates an authentic iris diaphragm with a TRUE OPEN PUPIL APERTURE in the center.
    The geometry is an annular ring; the inner circle is a hollow aperture allowing light to pass.
    """
    bm = bmesh.new()
    num_pts = 48
    front_inner = []
    front_outer = []
    back_inner = []
    back_outer = []

    z_front = thickness * 0.5
    z_back = -thickness * 0.5

    for i in range(num_pts):
        th = 2.0 * math.pi * i / num_pts
        cos_t = math.cos(th)
        sin_t = math.sin(th)

        # Front face vertices
        front_inner.append(bm.verts.new((inner_radius * cos_t, inner_radius * sin_t, z_front)))
        front_outer.append(bm.verts.new((outer_radius * cos_t, outer_radius * sin_t, z_front)))
        # Back face vertices
        back_inner.append(bm.verts.new((inner_radius * cos_t, inner_radius * sin_t, z_back)))
        back_outer.append(bm.verts.new((outer_radius * cos_t, outer_radius * sin_t, z_back)))

    # Quads for front face (annular disc)
    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        bm.faces.new([front_inner[i], front_outer[i], front_outer[next_i], front_inner[next_i]])
        # Quads for back face
        bm.faces.new([back_inner[i], back_inner[next_i], back_outer[next_i], back_outer[i]])
        # Outer border rim
        bm.faces.new([front_outer[i], back_outer[i], back_outer[next_i], front_outer[next_i]])
        # Inner pupillary aperture rim
        bm.faces.new([front_inner[i], front_inner[next_i], back_inner[next_i], back_inner[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    iris_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(iris_obj)
    iris_obj.location = (0.0, -0.0315, 0.0)
    iris_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

    for poly in iris_obj.data.polygons:
        poly.use_smooth = True
    if iris_mat:
        iris_obj.data.materials.append(iris_mat)

    # Pupil sphincter boundary ring marker (aperture border)
    pupil_ring = kit.create_smooth_tube(
        f"{ASSET_ID}-pupil",
        [
            Vector((inner_radius * math.cos(2 * math.pi * i / 24), -0.0315, inner_radius * math.sin(2 * math.pi * i / 24)))
            for i in range(25)
        ],
        radius=0.00045,
        resolution=12,
        material=pupil_margin_mat,
        cap_ends=True
    )

    return iris_obj, pupil_ring


def create_suspensory_zonules(name, num_zonules, r_ciliary, r_lens, y_plane, zonule_mat):
    """
    Creates the delicate radial suspensory ligaments (Zonules of Zinn)
    suspending the crystalline lens equator from the ciliary body.
    """
    zonules = []
    for i in range(num_zonules):
        angle = 2.0 * math.pi * i / num_zonules
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Connect ciliary process to lens equator
        p_ciliary = Vector((r_ciliary * cos_a, y_plane, r_ciliary * sin_a))
        p_lens = Vector((r_lens * cos_a, y_plane, r_lens * sin_a))
        p_mid = (p_ciliary + p_lens) * 0.5 + Vector((0.0002 * cos_a, -0.0004, 0.0002 * sin_a))

        fiber = kit.create_smooth_tube(
            f"{name}-zonule-{i}",
            [p_ciliary, p_mid, p_lens],
            radius=0.00035,
            resolution=10,
            material=zonule_mat,
            cap_ends=True
        )
        zonules.append(fiber)
    return zonules


def build_eye():
    """Builds a museum-grade anatomical human eye with 3 tunics, biconvex lens, open pupil, and vitreous humor."""
    # === PBR & OPTICAL SHADERS ===
    sclera_mat = kit.add_material_from_token("eye-sclera", "tissueSclera")
    choroid_mat = kit.add_material("eye-choroid", (0.12, 0.06, 0.05), metallic=0.02, roughness=0.65)
    retina_mat = kit.add_material_from_token("eye-retina", "tissueRetina")

    cornea_mat = kit.add_glass_material("eye-cornea", tint=(0.96, 0.98, 1.0), ior=1.376, roughness=0.005)
    lens_mat = kit.add_glass_material("eye-lens", tint=(0.98, 0.99, 1.0), ior=1.406, roughness=0.008)
    vitreous_mat = kit.add_glass_material("eye-vitreous", tint=(0.95, 0.98, 1.0), ior=1.336, roughness=0.015)
    aqueous_mat = kit.add_glass_material("eye-aqueous", tint=(0.97, 0.99, 1.0), ior=1.333, roughness=0.005)

    iris_mat = kit.add_material("eye-iris", (0.15, 0.45, 0.75), metallic=0.08, roughness=0.45)
    pupil_margin_mat = kit.add_material("eye-pupil", (0.05, 0.05, 0.05), metallic=0.0, roughness=0.80)
    ciliary_mat = kit.add_material("eye-ciliary", (0.55, 0.20, 0.18), metallic=0.05, roughness=0.55)
    zonule_mat = kit.add_material("eye-zonules", (0.88, 0.92, 0.96), metallic=0.0, roughness=0.25)
    nerve_mat = kit.add_material_from_token("eye-nerve", "tissueNerve")
    macula_mat = kit.add_material("eye-macula", (0.92, 0.75, 0.15), metallic=0.05, roughness=0.50)
    optic_disc_mat = kit.add_material("eye-optic-disc", (0.94, 0.90, 0.82), metallic=0.02, roughness=0.40)
    art_mat = kit.add_material("eye-retinal-artery", (0.85, 0.08, 0.08), metallic=0.06, roughness=0.30)
    vein_mat = kit.add_material("eye-retinal-vein", (0.10, 0.20, 0.85), metallic=0.06, roughness=0.30)

    objects = []

    # Cutaway box specification (removes anterior-superior-right quadrant: X > 0, Z > 0, Y < 0.010)
    cut_box_loc = (0.035, -0.010, 0.035)
    cut_box_scale = (0.075, 0.090, 0.075)

    # 1. Outer Fibrous Tunic: Sclera Shell
    sclera = create_hollow_tunic_cutaway(
        f"{ASSET_ID}-sclera", R_SCLERA_OUT, R_SCLERA_IN,
        cut_box_loc, cut_box_scale, sclera_mat
    )
    objects.append(sclera)

    # 2. Middle Vascular Tunic: Choroid Shell
    choroid = create_hollow_tunic_cutaway(
        f"{ASSET_ID}-choroid", R_SCLERA_IN, R_CHOROID_IN,
        cut_box_loc, cut_box_scale, choroid_mat
    )
    objects.append(choroid)

    # 3. Inner Sensory Tunic: Retina Shell
    retina = create_hollow_tunic_cutaway(
        f"{ASSET_ID}-retina", R_CHOROID_IN, R_RETINA_IN,
        cut_box_loc, cut_box_scale, retina_mat
    )
    objects.append(retina)

    # 4. Vitreous Humor Body in Posterior Cavity
    bm_vit = bmesh.new()
    bmesh.ops.create_uvsphere(bm_vit, u_segments=48, v_segments=32, radius=R_RETINA_IN)
    vit_mesh = bpy.data.meshes.new(f"{ASSET_ID}-vitreous-mesh")
    bm_vit.to_mesh(vit_mesh)
    bm_vit.free()
    vitreous = bpy.data.objects.new(f"{ASSET_ID}-vitreous", vit_mesh)
    bpy.context.collection.objects.link(vitreous)

    # Cut vitreous with same quadrant cutaway
    bm_vit_cut = bmesh.new()
    bmesh.ops.create_cube(bm_vit_cut, size=1.0)
    vit_cut_mesh = bpy.data.meshes.new("vit_cut")
    bm_vit_cut.to_mesh(vit_cut_mesh)
    bm_vit_cut.free()
    vit_cut_box = bpy.data.objects.new("vit_cut_box", vit_cut_mesh)
    bpy.context.collection.objects.link(vit_cut_box)
    vit_cut_box.scale = cut_box_scale
    vit_cut_box.location = cut_box_loc
    bpy.context.view_layer.update()

    mod_vit = vitreous.modifiers.new("Cut", "BOOLEAN")
    mod_vit.operation = "DIFFERENCE"
    mod_vit.solver = "EXACT"
    mod_vit.object = vit_cut_box
    bpy.context.view_layer.objects.active = vitreous
    bpy.ops.object.modifier_apply(modifier="Cut")
    bpy.data.objects.remove(vit_cut_box, do_unlink=True)
    for poly in vitreous.data.polygons:
        poly.use_smooth = True
    vitreous.data.materials.append(vitreous_mat)
    objects.append(vitreous)

    # 5. Transparent Bulging Cornea (Anterior optical dome)
    cornea_profile = [
        (0.000, -0.048),
        (0.008, -0.047),
        (0.016, -0.044),
        (0.021, -0.038),
        (0.023, -0.032),
        (0.021, -0.032),
        (0.019, -0.037),
        (0.014, -0.043),
        (0.000, -0.046)
    ]
    cornea = kit.lathe_object(f"{ASSET_ID}-cornea", cornea_profile, segments=48, material=cornea_mat)
    cornea.rotation_euler = (math.pi / 2, 0.0, 0.0)
    objects.append(cornea)

    # 6. Aqueous Humor (Anterior Chamber Fluid)
    aqueous_profile = [
        (0.000, -0.045),
        (0.010, -0.042),
        (0.018, -0.036),
        (0.020, -0.032),
        (0.000, -0.032)
    ]
    aqueous = kit.lathe_object(f"{ASSET_ID}-aqueous", aqueous_profile, segments=36, material=aqueous_mat)
    aqueous.rotation_euler = (math.pi / 2, 0.0, 0.0)
    objects.append(aqueous)

    # 7. Iris Diaphragm with TRUE OPEN Pupil Aperture Hole
    iris, pupil = create_iris_with_pupil_aperture(
        f"{ASSET_ID}-iris",
        inner_radius=PUPIL_INNER_RADIUS,
        outer_radius=IRIS_OUTER_RADIUS,
        thickness=0.0012,
        iris_mat=iris_mat,
        pupil_margin_mat=pupil_margin_mat
    )
    objects.extend([iris, pupil])

    # 8. Crystalline Biconvex Lens (Equator radius 0.013, anterior/posterior curvature)
    lens_profile = [
        (0.000, 0.0035),   # Anterior pole
        (0.006, 0.0030),
        (0.011, 0.0018),
        (0.013, 0.0000),   # Equator (insertion of zonules)
        (0.011, -0.0022),
        (0.006, -0.0040),
        (0.000, -0.0048)   # Posterior pole (more sharply curved)
    ]
    lens = kit.lathe_object(f"{ASSET_ID}-lens", lens_profile, segments=48, material=lens_mat)
    lens.location = (0.0, -0.026, 0.0)
    lens.rotation_euler = (math.pi / 2, 0.0, 0.0)
    objects.append(lens)

    # 9. Ciliary Body Ring & Processes (Closed watertight torus)
    ciliary_profile = [
        (0.0138, -0.002),
        (0.0180, -0.002),
        (0.0240, 0.000),
        (0.0250, 0.004),
        (0.0180, 0.003),
        (0.0138, 0.001),
        (0.0138, -0.002) # Closed loop welded by remove_doubles
    ]
    ciliary_ring = kit.lathe_object(f"{ASSET_ID}-ciliary", ciliary_profile, segments=48, material=ciliary_mat)
    ciliary_ring.location = (0.0, -0.026, 0.0)
    ciliary_ring.rotation_euler = (math.pi / 2, 0.0, 0.0)
    objects.append(ciliary_ring)

    # 10. Suspensory Zonules of Zinn (32 radial fibers)
    zonules = create_suspensory_zonules(
        f"{ASSET_ID}-zonules",
        num_zonules=32,
        r_ciliary=0.0175,
        r_lens=0.0130,
        y_plane=-0.026,
        zonule_mat=zonule_mat
    )
    objects.extend(zonules)

    # 11. Optic Disc (Blind Spot) and Posterior Retinal Landmarks
    optic_disc = kit.primitive_object(
        f"{ASSET_ID}-optic-disc", "cylinder", optic_disc_mat,
        size=(0.005, 0.005, 0.001),
        location=(-0.012, 0.036, -0.004),
        rotation_euler=(0.2, 0.3, 0.0)
    )
    macula = kit.primitive_object(
        f"{ASSET_ID}-macula", "uv_sphere", macula_mat,
        size=(0.006, 0.004, 0.006),
        location=(0.005, 0.0365, 0.000)
    )
    objects.extend([optic_disc, macula])

    # 12. Posterior Optic Nerve Bundle (Exiting posteromedially)
    nerve_pts = [
        Vector((-0.012, 0.036, -0.004)),
        Vector((-0.015, 0.050, -0.006)),
        Vector((-0.018, 0.068, -0.008)),
    ]
    optic_nerve = kit.create_smooth_tube(
        f"{ASSET_ID}-optic-nerve",
        nerve_pts,
        radius=0.0052,
        resolution=18,
        material=nerve_mat,
        cap_ends=True
    )
    objects.append(optic_nerve)

    # 13. Retinal Blood Vessels (Artery & Vein branches radiating across retina)
    art_branch_1 = kit.create_smooth_tube(
        f"{ASSET_ID}-retinal-art-sup",
        [Vector((-0.012, 0.035, -0.004)), Vector((-0.010, 0.034, 0.014)), Vector((-0.006, 0.032, 0.024))],
        radius=0.0006, resolution=10, material=art_mat, cap_ends=True
    )
    art_branch_2 = kit.create_smooth_tube(
        f"{ASSET_ID}-retinal-art-inf",
        [Vector((-0.012, 0.035, -0.004)), Vector((-0.012, 0.034, -0.016)), Vector((-0.008, 0.032, -0.026))],
        radius=0.0006, resolution=10, material=art_mat, cap_ends=True
    )
    vein_branch_1 = kit.create_smooth_tube(
        f"{ASSET_ID}-retinal-vein-sup",
        [Vector((-0.013, 0.035, -0.003)), Vector((-0.018, 0.033, 0.012)), Vector((-0.022, 0.031, 0.022))],
        radius=0.0006, resolution=10, material=vein_mat, cap_ends=True
    )
    objects.extend([art_branch_1, art_branch_2, vein_branch_1])

    # Smooth shading across all objects
    for obj in objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            obj.select_set(True)
            bpy.ops.object.shade_smooth()

    return objects


def main():
    out = kit.output_dir(Path(__file__).resolve().parent / "out")
    kit.reset_scene()
    objects = build_eye()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=16)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
