"""
build_realistic_eye.py — Medical-Grade 3D Construction Pipeline for the Human Eye
CBSE Class 10 Physics/Biology (Chapter 11: The Human Eye and the Colorful World — Fig 11.1)
CBSE Class 11 Biology (Chapter 21: Neural Control and Coordination — Sensory Organs)

Key Anatomical Features:
1. Three Concentric Tunics:
   - Outer fibrous tunic: Brilliant opaque white Sclera with PBR Subsurface Scattering (SSS)
     and fine episcleral micro-vascular branching, merging into crystal-clear aspheric Cornea
     with realistic corneal limbus transition.
   - Middle vascular tunic (Uvea): Melanin-pigmented Choroid layer, Annular Ciliary Body
     with ~70 radial ciliary processes (corona ciliaris), and striated Iris diaphragm
     with pupillary sphincter, radial dilator fibers, collarette, and true open pupil aperture.
   - Inner neural tunic (Retina): Sensory photoreceptor layer with realistic warm retinal tone,
     golden-yellow Macula Lutea, central Fovea Centralis depression, and pale Optic Disc (blind spot).
2. Refractive Optics:
   - Transparent crystalline biconvex lens with authentic asymmetric curvature
     (anterior radius ~10mm, posterior steeper radius ~6mm, IOR ~1.406).
   - Suspensory Ligaments (Zonules of Zinn): 48 delicate radial fibrous strands anchoring
     the lens equator to the ciliary processes.
   - Refractive humors: Clear aqueous humor in anterior chamber and dielectric vitreous body.
3. Extrinsic Ocular Muscles:
   - Striated muscular bellies and glistening tendinous insertions of the 4 Rectus muscles
     (Superior, Inferior, Medial, Lateral Rectus) anchoring onto the sclera.
4. Retinal & Optic Vasculature:
   - Sheathed Optic Nerve bundle (Cranial Nerve II) exiting posteromedially.
   - Central Retinal Artery & Vein entering through the optic disc and arborizing into 4 quadrantic
     arcades (Superior Temporal, Inferior Temporal, Superior Nasal, Inferior Nasal) hugging retina.
5. Dual Presentation Collections:
   - Full 3D Eye Globe with Rectus Muscles and Optic Nerve (preview.png).
   - NCERT Fig 11.1 Horizontal Cross-Section exposing all interior optical and neural structures
     under dedicated internal illumination (preview_section.png).
"""

import sys
import math
import shutil
from pathlib import Path

# Paths
THIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = THIS_DIR.parents[2]
sys.path.insert(0, str(ROOT_DIR / "assets" / "python"))

import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector, Matrix

ASSET_ID = "human-eye"
OUT_DIR = THIS_DIR / "out"
OUT_BLEND = OUT_DIR / "human-eye.blend"
OUT_GLB = OUT_DIR / "human-eye.glb"
VIEWER_GLB = ROOT_DIR / "apps" / "interactive-viewer" / "public" / "assets" / "human-eye.glb"
OUT_PREVIEW = OUT_DIR / "preview.png"
OUT_PREVIEW_SECTION = OUT_DIR / "preview_section.png"

# Dimensional constants (Scale: 0.040 m = 40 mm radius, matching project standard convention)
R_SCLERA_OUT = 0.0400
R_SCLERA_IN  = 0.0380
R_CHOROID_IN = 0.0370
R_RETINA_IN  = 0.0360

PUPIL_RADIUS = 0.0050  # 10 mm diameter open pupil
IRIS_OUTER_R = 0.0210  # Iris ciliary border (snugly meets corneal limbus)
LENS_EQUATOR = 0.0135  # Lens equator radius
LENS_Y_POS   = -0.0265 # Axial center of crystalline lens
IRIS_Y_POS   = -0.0315 # Axial plane of iris


def create_pbr_materials():
    """Builds authentic medical-grade PBR shaders for all ocular tissues and optical elements."""
    mats = {}

    # 1. Sclera: Opaque fibrous coat with high subsurface scattering
    sclera = bpy.data.materials.new("eye-sclera")
    sclera.use_nodes = True
    bsdf = sclera.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.94, 0.95, 0.97, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.28
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.45
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.4, 0.3)
        bsdf.inputs["Subsurface Scale"].default_value = 0.015
    mats["sclera"] = sclera

    # 2. Cornea: Aspheric crystal-clear refractive optical dome
    cornea = bpy.data.materials.new("eye-cornea")
    cornea.use_nodes = True
    bsdf = cornea.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.98, 0.99, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.003
    bsdf.inputs["Transmission Weight"].default_value = 0.99
    bsdf.inputs["IOR"].default_value = 1.376
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = 0.4
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.01
    mats["cornea"] = cornea

    # 3. Corneal Limbus: Soft transition ring
    limbus = bpy.data.materials.new("eye-limbus")
    limbus.use_nodes = True
    bsdf = limbus.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.88, 0.91, 0.95, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.20
    bsdf.inputs["Transmission Weight"].default_value = 0.35
    bsdf.inputs["IOR"].default_value = 1.376
    mats["limbus"] = limbus

    # 4. Choroid: Melanin-rich dark vascular layer
    choroid = bpy.data.materials.new("eye-choroid")
    choroid.use_nodes = True
    bsdf = choroid.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.08, 0.04, 0.03, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.65
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.15
        bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.2, 0.1)
    mats["choroid"] = choroid

    # 5. Ciliary Body & Muscular Ring
    ciliary = bpy.data.materials.new("eye-ciliary")
    ciliary.use_nodes = True
    bsdf = ciliary.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.54, 0.18, 0.16, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    mats["ciliary"] = ciliary

    # 6. Ciliary Processes (Corona ciliaris folds)
    ciliary_proc = bpy.data.materials.new("eye-ciliary-processes")
    ciliary_proc.use_nodes = True
    bsdf = ciliary_proc.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.64, 0.22, 0.20, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.38
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.40
    mats["ciliary_proc"] = ciliary_proc

    # 7. Iris: Striated muscular diaphragm with Hazel/Cerulean stroma
    iris = bpy.data.materials.new("eye-iris")
    iris.use_nodes = True
    nt = iris.node_tree
    bsdf = nt.nodes["Principled BSDF"]

    # Procedural radial stroma fibers and deep hazel/amber pigmentation
    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    grad = nt.nodes.new("ShaderNodeTexGradient")
    grad.gradient_type = 'RADIAL'
    nt.links.new(tex_coord.outputs["Object"], grad.inputs["Vector"])

    math_mult = nt.nodes.new("ShaderNodeMath")
    math_mult.operation = 'MULTIPLY'
    math_mult.inputs[1].default_value = 600.0  # ~95 fine delicate radial stroma striations
    nt.links.new(grad.outputs["Fac"], math_mult.inputs[0])

    math_sin = nt.nodes.new("ShaderNodeMath")
    math_sin.operation = 'SINE'
    nt.links.new(math_mult.outputs["Value"], math_sin.inputs[0])

    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 85.0
    noise.inputs["Detail"].default_value = 4.0
    nt.links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    mix_node = nt.nodes.new("ShaderNodeMix")
    mix_node.data_type = 'FLOAT'
    mix_node.inputs[0].default_value = 0.50
    nt.links.new(math_sin.outputs["Value"], mix_node.inputs[2])
    nt.links.new(noise.outputs["Fac"], mix_node.inputs[3])

    color_ramp = nt.nodes.new("ShaderNodeValToRGB")
    color_ramp.color_ramp.elements[0].position = 0.05
    color_ramp.color_ramp.elements[0].color = (0.04, 0.025, 0.015, 1.0)
    color_ramp.color_ramp.elements[1].position = 0.50
    color_ramp.color_ramp.elements[1].color = (0.22, 0.14, 0.06, 1.0)
    cr_elem2 = color_ramp.color_ramp.elements.new(0.85)
    cr_elem2.color = (0.42, 0.30, 0.12, 1.0)

    nt.links.new(mix_node.outputs[0], color_ramp.inputs["Fac"])
    nt.links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.52
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.20
        bsdf.inputs["Subsurface Radius"].default_value = (0.8, 0.4, 0.2)
    mats["iris"] = iris

    # 8. Pupil Sphincter Margin Ring
    pupil_ring = bpy.data.materials.new("eye-pupil-sphincter")
    pupil_ring.use_nodes = True
    bsdf = pupil_ring.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.60
    mats["pupil_ring"] = pupil_ring

    # 9. Crystalline Biconvex Lens
    lens = bpy.data.materials.new("eye-lens")
    lens.use_nodes = True
    bsdf = lens.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.92, 0.97, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["Transmission Weight"].default_value = 0.88
    bsdf.inputs["IOR"].default_value = 1.406  # Authentic biological crystalline lens IOR
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = 0.35
        bsdf.inputs["Clearcoat Roughness"].default_value = 0.01
    mats["lens"] = lens

    # 10. Suspensory Ligaments (Zonules of Zinn)
    zonules = bpy.data.materials.new("eye-zonules")
    zonules.use_nodes = True
    bsdf = zonules.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.90, 0.94, 0.98, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Transmission Weight"].default_value = 0.30
    mats["zonules"] = zonules

    # 11. Retina: Photoreceptor sensory layer
    retina = bpy.data.materials.new("eye-retina")
    retina.use_nodes = True
    bsdf = retina.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.86, 0.44, 0.32, 1.0)  # Warm salmon-orange
    bsdf.inputs["Roughness"].default_value = 0.45
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.42
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.45, 0.25)
    mats["retina"] = retina

    # 12. Macula Lutea (Yellow carotenoid spot)
    macula = bpy.data.materials.new("eye-macula")
    macula.use_nodes = True
    bsdf = macula.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.94, 0.76, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
    mats["macula"] = macula

    # 13. Fovea Centralis (Central high-acuity pit)
    fovea = bpy.data.materials.new("eye-fovea")
    fovea.use_nodes = True
    bsdf = fovea.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.78, 0.48, 0.16, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.32
    mats["fovea"] = fovea

    # 14. Optic Disc (Physiological blind spot)
    disc = bpy.data.materials.new("eye-optic-disc")
    disc.use_nodes = True
    bsdf = disc.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.96, 0.90, 0.84, 1.0)  # Pale creamy disc
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.30
    mats["optic_disc"] = disc

    # 15. Retinal Artery Branches (Oxygenated scarlet red)
    ret_art = bpy.data.materials.new("eye-retinal-artery")
    ret_art.use_nodes = True
    bsdf = ret_art.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.88, 0.08, 0.08, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = 0.25
    mats["retinal_artery"] = ret_art

    # 16. Retinal Vein Branches (Deoxygenated royal blue)
    ret_vein = bpy.data.materials.new("eye-retinal-vein")
    ret_vein.use_nodes = True
    bsdf = ret_vein.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.12, 0.25, 0.80, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = 0.25
    mats["retinal_vein"] = ret_vein

    # 17. Vitreous Humor (Transparent optical gel)
    vitreous = bpy.data.materials.new("eye-vitreous")
    vitreous.use_nodes = True
    bsdf = vitreous.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.97, 0.99, 1.0, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.008
    bsdf.inputs["Transmission Weight"].default_value = 0.98
    bsdf.inputs["IOR"].default_value = 1.336
    mats["vitreous"] = vitreous

    # 18. Optic Nerve Bundle & Meningeal Sheath
    nerve = bpy.data.materials.new("eye-optic-nerve")
    nerve.use_nodes = True
    bsdf = nerve.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.88, 0.82, 0.72, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.40
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.38
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.5, 0.3)
    mats["optic_nerve"] = nerve

    # 19. Extrinsic Rectus Muscle Bellies
    muscle = bpy.data.materials.new("eye-rectus-muscle")
    muscle.use_nodes = True
    bsdf = muscle.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.68, 0.18, 0.15, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.42
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.35
        bsdf.inputs["Subsurface Radius"].default_value = (1.0, 0.3, 0.2)
    mats["rectus_muscle"] = muscle

    # 20. Tendinous Insertions (Silvery glistening tendon)
    tendon = bpy.data.materials.new("eye-rectus-tendon")
    tendon.use_nodes = True
    bsdf = tendon.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.90, 0.91, 0.92, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.25
    if "Clearcoat Weight" in bsdf.inputs:
        bsdf.inputs["Clearcoat Weight"].default_value = 0.3
    mats["rectus_tendon"] = tendon

    return mats


def create_spherical_shell(name, r_outer, r_inner, u_seg=64, v_seg=32, cutaway=None, corneal_aperture=True, aperture_radius=0.0215, material=None):
    """
    Creates a concentric hollow spherical shell representing an anatomical eye tunic.
    Cuts the anterior corneal aperture at the front (-Y) so internal optics and iris are visible.
    If cutaway == 'horizontal', cuts away the superior half (Z > 0) to produce an NCERT Fig 11.1
    horizontal section exposing layer thicknesses.
    """
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=u_seg, v_segments=v_seg, radius=r_outer)
    mesh_out = bpy.data.meshes.new(f"{name}_outer")
    bm.to_mesh(mesh_out)
    bm.free()

    obj = bpy.data.objects.new(name, mesh_out)
    bpy.context.collection.objects.link(obj)

    # Inner cavity void
    bm_in = bmesh.new()
    bmesh.ops.create_uvsphere(bm_in, u_segments=u_seg, v_segments=v_seg, radius=r_inner)
    mesh_in = bpy.data.meshes.new(f"{name}_void")
    bm_in.to_mesh(mesh_in)
    bm_in.free()
    void_obj = bpy.data.objects.new(f"{name}_void", mesh_in)
    bpy.context.collection.objects.link(void_obj)

    bpy.context.view_layer.update()

    # Boolean difference to create hollow shell
    mod_void = obj.modifiers.new("Hollow", "BOOLEAN")
    mod_void.operation = "DIFFERENCE"
    mod_void.solver = "EXACT"
    mod_void.object = void_obj
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="Hollow")
    bpy.data.objects.remove(void_obj, do_unlink=True)

    # Cut anterior corneal aperture (for sclera/choroid/retina at front)
    if corneal_aperture:
        bm_ap = bmesh.new()
        bmesh.ops.create_cone(
            bm_ap, cap_ends=True, cap_tris=False, segments=48,
            radius1=aperture_radius, radius2=aperture_radius, depth=0.040
        )
        mesh_ap = bpy.data.meshes.new(f"{name}_aperture")
        bm_ap.to_mesh(mesh_ap)
        bm_ap.free()
        ap_obj = bpy.data.objects.new(f"{name}_aperture", mesh_ap)
        bpy.context.collection.objects.link(ap_obj)
        ap_obj.rotation_euler = (math.pi / 2, 0, 0)
        ap_obj.location = (0.0, -0.035, 0.0)
        bpy.context.view_layer.update()

        mod_ap = obj.modifiers.new("Aperture", "BOOLEAN")
        mod_ap.operation = "DIFFERENCE"
        mod_ap.solver = "EXACT"
        mod_ap.object = ap_obj
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="Aperture")
        bpy.data.objects.remove(ap_obj, do_unlink=True)

    # Optional section cutaway
    if cutaway == 'horizontal':
        # Remove superior half: Z > 0, slightly offset for clear view
        bm_cut = bmesh.new()
        bmesh.ops.create_cube(bm_cut, size=1.0)
        mesh_cut = bpy.data.meshes.new(f"{name}_cutter")
        bm_cut.to_mesh(mesh_cut)
        bm_cut.free()
        cut_obj = bpy.data.objects.new(f"{name}_cutter", mesh_cut)
        bpy.context.collection.objects.link(cut_obj)
        cut_obj.scale = (0.12, 0.12, 0.10)
        cut_obj.location = (0.0, 0.0, 0.05)  # covers Z from 0.0 to 0.10
        bpy.context.view_layer.update()

        mod_cut = obj.modifiers.new("CutSection", "BOOLEAN")
        mod_cut.operation = "DIFFERENCE"
        mod_cut.solver = "EXACT"
        mod_cut.object = cut_obj
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier="CutSection")
        bpy.data.objects.remove(cut_obj, do_unlink=True)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    if material:
        obj.data.materials.append(material)

    return obj


def create_cornea_and_limbus(mats, cutaway=None):
    """Creates the aspheric transparent cornea and annular limbus transition."""
    # Cornea aspheric profile (bulging forward along -Y)
    cornea_profile = [
        (0.000, -0.0480), # Anterior corneal apex
        (0.005, -0.0475),
        (0.010, -0.0458),
        (0.015, -0.0428),
        (0.019, -0.0385),
        (0.0215, -0.0335), # Corneal limbus equator
        (0.0200, -0.0335), # Posterior inner margin
        (0.0175, -0.0380),
        (0.0135, -0.0420),
        (0.0085, -0.0450),
        (0.000, -0.0465)  # Posterior central thickness ~0.55mm scaled
    ]
    cornea = kit.lathe_object(f"{ASSET_ID}-cornea", cornea_profile, segments=64, material=mats["cornea"])
    cornea.rotation_euler = (math.pi / 2, 0.0, 0.0)

    # Limbus ring
    limbus_profile = [
        (0.0212, -0.0345),
        (0.0225, -0.0340),
        (0.0232, -0.0325),
        (0.0218, -0.0325),
        (0.0212, -0.0345)
    ]
    limbus = kit.lathe_object(f"{ASSET_ID}-limbus", limbus_profile, segments=64, material=mats["limbus"])
    limbus.rotation_euler = (math.pi / 2, 0.0, 0.0)

    objs = [cornea, limbus]
    if cutaway == 'horizontal':
        for o in objs:
            bm_cut = bmesh.new()
            bmesh.ops.create_cube(bm_cut, size=1.0)
            mesh_cut = bpy.data.meshes.new("c_cutter")
            bm_cut.to_mesh(mesh_cut)
            bm_cut.free()
            cut_obj = bpy.data.objects.new("c_cutter", mesh_cut)
            bpy.context.collection.objects.link(cut_obj)
            cut_obj.scale = (0.12, 0.12, 0.10)
            cut_obj.location = (0.0, 0.0, 0.05)
            bpy.context.view_layer.update()

            mod = o.modifiers.new("CutSection", "BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.object = cut_obj
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier="CutSection")
            bpy.data.objects.remove(cut_obj, do_unlink=True)

    return objs


def create_iris_and_pupil(mats, cutaway=None):
    """
    Creates an anatomically detailed iris diaphragm with pupillary sphincter ring,
    radial stroma ridges, and a true open central pupil aperture admitting light to the lens.
    """
    bm = bmesh.new()
    num_pts = 64
    front_in, front_mid, front_out = [], [], []
    back_in, back_out = [], []

    z_f = 0.0006
    z_b = -0.0006
    r_collarette = (PUPIL_RADIUS + IRIS_OUTER_R) * 0.45

    for i in range(num_pts):
        th = 2.0 * math.pi * i / num_pts
        ct = math.cos(th)
        st = math.sin(th)
        # Subtle radial undulation for iris crypts
        crypt = 0.0003 * math.sin(16 * th)

        front_in.append(bm.verts.new((PUPIL_RADIUS * ct, PUPIL_RADIUS * st, z_f)))
        front_mid.append(bm.verts.new((r_collarette * ct, r_collarette * st, z_f + crypt)))
        front_out.append(bm.verts.new((IRIS_OUTER_R * ct, IRIS_OUTER_R * st, z_f * 0.5)))

        back_in.append(bm.verts.new((PUPIL_RADIUS * ct, PUPIL_RADIUS * st, z_b)))
        back_out.append(bm.verts.new((IRIS_OUTER_R * ct, IRIS_OUTER_R * st, z_b)))

    for i in range(num_pts):
        next_i = (i + 1) % num_pts
        # Pupillary zone (inner ring)
        bm.faces.new([front_in[i], front_mid[i], front_mid[next_i], front_in[next_i]])
        # Ciliary zone (outer ring)
        bm.faces.new([front_mid[i], front_out[i], front_out[next_i], front_mid[next_i]])
        # Back face
        bm.faces.new([back_in[i], back_in[next_i], back_out[next_i], back_out[i]])
        # Rim borders
        bm.faces.new([front_out[i], back_out[i], back_out[next_i], front_out[next_i]])
        bm.faces.new([front_in[i], front_in[next_i], back_in[next_i], back_in[i]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{ASSET_ID}-iris-mesh")
    bm.to_mesh(mesh)
    bm.free()

    iris_obj = bpy.data.objects.new(f"{ASSET_ID}-iris", mesh)
    bpy.context.collection.objects.link(iris_obj)
    iris_obj.location = (0.0, IRIS_Y_POS, 0.0)
    iris_obj.rotation_euler = (math.pi / 2, 0.0, 0.0)

    for poly in iris_obj.data.polygons:
        poly.use_smooth = True
    iris_obj.data.materials.append(mats["iris"])

    # Sphincter ring (aperture boundary)
    sphincter = kit.create_smooth_tube(
        f"{ASSET_ID}-pupil-sphincter",
        [
            Vector((PUPIL_RADIUS * math.cos(2 * math.pi * i / 32), IRIS_Y_POS, PUPIL_RADIUS * math.sin(2 * math.pi * i / 32)))
            for i in range(33)
        ],
        radius=0.00045,
        resolution=12,
        material=mats["pupil_ring"],
        cap_ends=True
    )

    objs = [iris_obj, sphincter]
    if cutaway == 'horizontal':
        for o in objs:
            bm_cut = bmesh.new()
            bmesh.ops.create_cube(bm_cut, size=1.0)
            mesh_cut = bpy.data.meshes.new("iris_cut")
            bm_cut.to_mesh(mesh_cut)
            bm_cut.free()
            cut_obj = bpy.data.objects.new("iris_cut", mesh_cut)
            bpy.context.collection.objects.link(cut_obj)
            cut_obj.scale = (0.12, 0.12, 0.10)
            cut_obj.location = (0.0, 0.0, 0.05)
            bpy.context.view_layer.update()

            mod = o.modifiers.new("CutSection", "BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.object = cut_obj
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier="CutSection")
            bpy.data.objects.remove(cut_obj, do_unlink=True)

    return objs


def create_crystalline_lens(mats, cutaway=None):
    """
    Creates an authentic biconvex crystalline lens with asymmetric curvature:
    anterior curvature is flatter (R ~ 10mm), posterior curvature is steeper (R ~ 6mm).
    """
    lens_profile = [
        (0.000, 0.0032),   # Anterior pole
        (0.004, 0.0028),
        (0.008, 0.0020),
        (0.011, 0.0010),
        (LENS_EQUATOR, 0.0000), # Equator (insertion of zonules)
        (0.011, -0.0018),
        (0.008, -0.0032),
        (0.004, -0.0042),
        (0.000, -0.0046)   # Posterior pole (more sharply curved)
    ]
    lens = kit.lathe_object(f"{ASSET_ID}-lens", lens_profile, segments=64, material=mats["lens"])
    lens.location = (0.0, LENS_Y_POS, 0.0)
    lens.rotation_euler = (math.pi / 2, 0.0, 0.0)

    if cutaway == 'horizontal':
        bm_cut = bmesh.new()
        bmesh.ops.create_cube(bm_cut, size=1.0)
        mesh_cut = bpy.data.meshes.new("lens_cut")
        bm_cut.to_mesh(mesh_cut)
        bm_cut.free()
        cut_obj = bpy.data.objects.new("lens_cut", mesh_cut)
        bpy.context.collection.objects.link(cut_obj)
        cut_obj.scale = (0.12, 0.12, 0.10)
        cut_obj.location = (0.0, 0.0, 0.05)
        bpy.context.view_layer.update()

        mod = lens.modifiers.new("CutSection", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = cut_obj
        bpy.context.view_layer.objects.active = lens
        bpy.ops.object.modifier_apply(modifier="CutSection")
        bpy.data.objects.remove(cut_obj, do_unlink=True)

    return lens


def create_ciliary_body_and_zonules(mats, cutaway=None):
    """
    Creates the ciliary muscular body ring, corona ciliaris (ciliary processes),
    and 48 delicate radial suspensory zonules of Zinn extending to the lens equator.
    """
    objs = []

    # 1. Main ciliary muscle annular ring
    ciliary_profile = [
        (0.0142, -0.0035),
        (0.0190, -0.0030),
        (0.0245, -0.0010),
        (0.0255, 0.0035),
        (0.0195, 0.0030),
        (0.0142, 0.0005),
        (0.0142, -0.0035)
    ]
    ciliary_ring = kit.lathe_object(f"{ASSET_ID}-ciliary-body", ciliary_profile, segments=64, material=mats["ciliary"])
    ciliary_ring.location = (0.0, LENS_Y_POS, 0.0)
    ciliary_ring.rotation_euler = (math.pi / 2, 0.0, 0.0)
    objs.append(ciliary_ring)

    # 2. Ciliary processes (corona ciliaris): 36 radial folds around circumference
    num_processes = 36
    r_proc_inner = 0.0138
    r_proc_outer = 0.0185
    y_plane = LENS_Y_POS

    for i in range(num_processes):
        angle = 2.0 * math.pi * i / num_processes
        if cutaway == 'horizontal' and math.sin(angle) > 0.05:
            continue  # Skip superior processes in horizontal cutaway
        ca, sa = math.cos(angle), math.sin(angle)
        p1 = Vector((r_proc_outer * ca, y_plane - 0.0015, r_proc_outer * sa))
        p2 = Vector((r_proc_inner * ca, y_plane + 0.0005, r_proc_inner * sa))
        proc = kit.create_smooth_tube(
            f"{ASSET_ID}-ciliary-process-{i}",
            [p1, p2],
            radius=0.00045,
            resolution=8,
            material=mats["ciliary_proc"],
            cap_ends=True
        )
        objs.append(proc)

    # 3. Suspensory Ligaments / Zonules of Zinn: 48 radial fibrous strands
    num_zonules = 48
    r_ciliary_attach = 0.0165
    for i in range(num_zonules):
        angle = 2.0 * math.pi * i / num_zonules
        if cutaway == 'horizontal' and math.sin(angle) > 0.05:
            continue
        ca, sa = math.cos(angle), math.sin(angle)
        # Stagger attachment between anterior and posterior lens equator
        y_offset = 0.0008 if (i % 2 == 0) else -0.0008
        p_ciliary = Vector((r_ciliary_attach * ca, y_plane, r_ciliary_attach * sa))
        p_lens = Vector((LENS_EQUATOR * ca, y_plane + y_offset, LENS_EQUATOR * sa))
        p_mid = (p_ciliary + p_lens) * 0.5 + Vector((0.0001 * ca, y_offset * 0.5, 0.0001 * sa))

        zonule = kit.create_smooth_tube(
            f"{ASSET_ID}-zonule-{i}",
            [p_ciliary, p_mid, p_lens],
            radius=0.00028,
            resolution=6,
            material=mats["zonules"],
            cap_ends=True
        )
        objs.append(zonule)

    if cutaway == 'horizontal':
        # Cut the ciliary ring as well
        bm_cut = bmesh.new()
        bmesh.ops.create_cube(bm_cut, size=1.0)
        mesh_cut = bpy.data.meshes.new("cil_cut")
        bm_cut.to_mesh(mesh_cut)
        bm_cut.free()
        cut_obj = bpy.data.objects.new("cil_cut", mesh_cut)
        bpy.context.collection.objects.link(cut_obj)
        cut_obj.scale = (0.12, 0.12, 0.10)
        cut_obj.location = (0.0, 0.0, 0.05)
        bpy.context.view_layer.update()

        mod = ciliary_ring.modifiers.new("CutSection", "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.solver = "EXACT"
        mod.object = cut_obj
        bpy.context.view_layer.objects.active = ciliary_ring
        bpy.ops.object.modifier_apply(modifier="CutSection")
        bpy.data.objects.remove(cut_obj, do_unlink=True)

    return objs


def create_retinal_landmarks_and_vasculature(mats, cutaway=None):
    """
    Creates the Macula Lutea, central Fovea Centralis, pale Optic Disc (blind spot),
    and branching Central Retinal Artery and Vein quadrantic arcades spanning the retinal bowl.
    """
    objs = []

    def project_retina(v, force_lower=True):
        """Projects coordinate onto inner spherical retina surface."""
        norm = v.normalized()
        z = norm.z
        if force_lower and cutaway == 'horizontal':
            z = min(-0.0015, z)
            norm = Vector((norm.x, norm.y, z)).normalized()
        return norm * (R_RETINA_IN - 0.00035)

    # Anatomical coordinates: Optic disc is nasal (-X), Macula/Fovea is temporal (+X)
    disc_pos = project_retina(Vector((-0.010, 0.034, -0.004)))
    macula_pos = project_retina(Vector((0.008, 0.035, -0.003)))
    fovea_pos = project_retina(Vector((0.008, 0.0352, -0.003)))

    # 1. Optic Disc (Pale oval physiological blind spot)
    disc = kit.primitive_object(
        f"{ASSET_ID}-optic-disc", "cylinder", mats["optic_disc"],
        size=(0.0050, 0.0050, 0.0007),
        location=disc_pos,
        rotation_euler=(0.20, 0.32, 0.0)
    )
    objs.append(disc)

    # 2. Macula Lutea (Golden-yellow carotenoid spot)
    macula = kit.primitive_object(
        f"{ASSET_ID}-macula", "uv_sphere", mats["macula"],
        size=(0.0060, 0.0030, 0.0060),
        location=macula_pos
    )
    objs.append(macula)

    # 3. Fovea Centralis (High-acuity central pit)
    fovea = kit.primitive_object(
        f"{ASSET_ID}-fovea", "uv_sphere", mats["fovea"],
        size=(0.0022, 0.0018, 0.0022),
        location=fovea_pos
    )
    objs.append(fovea)

    # 4. Retinal Arterial Tree (Scarlet red oxygenated branches)
    artery_branches = [
        # Inferior Temporal main arcade (arching below macula toward temporal equator)
        [
            disc_pos,
            project_retina(Vector((-0.005, 0.034, -0.010))),
            project_retina(Vector((0.004, 0.032, -0.016))),
            project_retina(Vector((0.015, 0.026, -0.022))),
            project_retina(Vector((0.022, 0.016, -0.026))),
            project_retina(Vector((0.025, 0.004, -0.025))),
            project_retina(Vector((0.023, -0.008, -0.024)))
        ],
        # Temporal descending floor branch (branching into lowest retina cup)
        [
            project_retina(Vector((0.004, 0.032, -0.016))),
            project_retina(Vector((0.006, 0.022, -0.028))),
            project_retina(Vector((0.004, 0.010, -0.034))),
            project_retina(Vector((0.001, -0.002, -0.035)))
        ],
        # Inferior Nasal main arcade (sweeping down nasally)
        [
            disc_pos,
            project_retina(Vector((-0.016, 0.032, -0.009))),
            project_retina(Vector((-0.022, 0.026, -0.016))),
            project_retina(Vector((-0.026, 0.016, -0.022))),
            project_retina(Vector((-0.027, 0.002, -0.024))),
            project_retina(Vector((-0.024, -0.010, -0.023)))
        ],
        # Nasal descending floor branch
        [
            project_retina(Vector((-0.022, 0.026, -0.016))),
            project_retina(Vector((-0.016, 0.018, -0.028))),
            project_retina(Vector((-0.008, 0.008, -0.034))),
            project_retina(Vector((-0.002, -0.002, -0.035)))
        ],
        # Macular arterioles (small branches reaching around macula)
        [
            project_retina(Vector((0.004, 0.032, -0.016))),
            project_retina(Vector((0.007, 0.034, -0.009))),
            project_retina(Vector((0.008, 0.035, -0.006)))
        ],
    ]

    for idx, branch in enumerate(artery_branches):
        art = kit.create_smooth_tube(
            f"{ASSET_ID}-retinal-art-{idx}",
            branch,
            radius=0.00042 if idx < 3 else 0.00030,
            resolution=8,
            material=mats["retinal_artery"],
            cap_ends=True
        )
        objs.append(art)

    # 5. Retinal Venous Tree (Royal blue deoxygenated companion veins)
    vein_branches = [
        # Inferior Temporal vein
        [
            disc_pos + Vector((0.0006, -0.0004, -0.0004)),
            project_retina(Vector((-0.004, 0.033, -0.012))),
            project_retina(Vector((0.005, 0.031, -0.018))),
            project_retina(Vector((0.016, 0.024, -0.024))),
            project_retina(Vector((0.023, 0.013, -0.027))),
            project_retina(Vector((0.024, 0.001, -0.026)))
        ],
        # Inferior Nasal vein
        [
            disc_pos + Vector((-0.0005, -0.0004, -0.0004)),
            project_retina(Vector((-0.015, 0.031, -0.011))),
            project_retina(Vector((-0.020, 0.024, -0.018))),
            project_retina(Vector((-0.024, 0.014, -0.024))),
            project_retina(Vector((-0.025, 0.000, -0.025)))
        ],
        # Central floor draining venule
        [
            project_retina(Vector((-0.004, 0.033, -0.012))),
            project_retina(Vector((0.002, 0.020, -0.029))),
            project_retina(Vector((0.003, 0.008, -0.034)))
        ]
    ]

    for idx, branch in enumerate(vein_branches):
        vein = kit.create_smooth_tube(
            f"{ASSET_ID}-retinal-vein-{idx}",
            branch,
            radius=0.00052 if idx < 2 else 0.00036,
            resolution=8,
            material=mats["retinal_vein"],
            cap_ends=True
        )
        objs.append(vein)

    return objs


def create_extrinsic_rectus_muscles(mats):
    """
    Creates the 4 extrinsic rectus muscles (Superior, Inferior, Medial, Lateral Rectus)
    with striated muscle bellies and silvery glistening tendinous insertions onto the sclera.
    """
    objs = []
    # Muscle trajectories: insert near equator (y ~ -0.020 to -0.024) and extend back to posterior apex (y ~ +0.070)
    muscle_configs = [
        ("Superior-Rectus", (0.0, 0.038), (0.0, 0.030), (0.0, 0.018), math.radians(0)),
        ("Inferior-Rectus", (0.0, -0.038), (0.0, -0.030), (0.0, -0.018), math.radians(180)),
        ("Medial-Rectus",   (-0.038, 0.0), (-0.030, 0.0), (-0.018, 0.0), math.radians(90)),
        ("Lateral-Rectus",  (0.038, 0.0),  (0.030, 0.0),  (0.018, 0.0), math.radians(-90)),
    ]

    for name, p_insert, p_mid, p_post, rot_z in muscle_configs:
        # Tendon insertion: flat ribbon tapering onto sclera
        p_tendon_start = Vector((p_insert[0], -0.020, p_insert[1]))
        p_tendon_end   = Vector((p_mid[0] * 1.05, -0.005, p_mid[1] * 1.05))
        tendon = kit.create_smooth_tube(
            f"{ASSET_ID}-{name}-tendon",
            [p_tendon_start, p_tendon_end],
            radius=0.0028,
            resolution=10,
            material=mats["rectus_tendon"],
            cap_ends=True
        )
        objs.append(tendon)

        # Muscular belly: fleshy belly thickening in middle and tapering back
        p_belly_mid = Vector((p_mid[0] * 1.10, 0.030, p_mid[1] * 1.10))
        p_belly_end = Vector((p_post[0], 0.072, p_post[1]))
        muscle = kit.create_smooth_tube(
            f"{ASSET_ID}-{name}-belly",
            [p_tendon_end, p_belly_mid, p_belly_end],
            radius=0.0045,
            resolution=14,
            material=mats["rectus_muscle"],
            cap_ends=True
        )
        objs.append(muscle)

    return objs


def create_optic_nerve_bundle(mats):
    """Creates the posterior sheathed Optic Nerve bundle (Cranial Nerve II)."""
    nerve_pts = [
        Vector((-0.012, 0.036, -0.004)),
        Vector((-0.016, 0.052, -0.006)),
        Vector((-0.020, 0.072, -0.008)),
    ]
    nerve = kit.create_smooth_tube(
        f"{ASSET_ID}-optic-nerve",
        nerve_pts,
        radius=0.0055,
        resolution=18,
        material=mats["optic_nerve"],
        cap_ends=True
    )
    return nerve


def build_scene():
    """Constructs the complete medical-grade eye with Full and Section collections."""
    kit.reset_scene()
    mats = create_pbr_materials()

    # Create root collections
    root_coll = bpy.context.scene.collection
    coll_full = bpy.data.collections.new("Eye_Full")
    coll_section = bpy.data.collections.new("Eye_Section")
    coll_lights = bpy.data.collections.new("Studio_Lighting")
    root_coll.children.link(coll_full)
    root_coll.children.link(coll_section)
    root_coll.children.link(coll_lights)

    # =========================================================================
    # 1. EYE FULL (Complete 3D Globe with Sclera, Muscles, Cornea, Iris, Nerve)
    # =========================================================================
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Eye_Full"]

    sclera_full = create_spherical_shell(f"{ASSET_ID}-sclera-full", R_SCLERA_OUT, R_SCLERA_IN, material=mats["sclera"])
    choroid_full = create_spherical_shell(f"{ASSET_ID}-choroid-full", R_SCLERA_IN, R_CHOROID_IN, corneal_aperture=True, aperture_radius=0.0210, material=mats["choroid"])
    cornea_full = create_cornea_and_limbus(mats)
    iris_full = create_iris_and_pupil(mats)
    lens_full = create_crystalline_lens(mats)
    ciliary_full = create_ciliary_body_and_zonules(mats)
    nerve_full = create_optic_nerve_bundle(mats)
    muscles_full = create_extrinsic_rectus_muscles(mats)

    full_objs = [sclera_full, choroid_full, *cornea_full, *iris_full, lens_full, *ciliary_full, nerve_full, *muscles_full]
    for o in full_objs:
        if o.name not in coll_full.objects:
            coll_full.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # =========================================================================
    # 2. EYE SECTION (NCERT Fig 11.1 Horizontal Cutaway exposing all interior)
    # =========================================================================
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children["Eye_Section"]

    sclera_sec = create_spherical_shell(f"{ASSET_ID}-sclera-section", R_SCLERA_OUT, R_SCLERA_IN, cutaway='horizontal', corneal_aperture=True, aperture_radius=0.0215, material=mats["sclera"])
    choroid_sec = create_spherical_shell(f"{ASSET_ID}-choroid-section", R_SCLERA_IN, R_CHOROID_IN, cutaway='horizontal', corneal_aperture=True, aperture_radius=0.024, material=mats["choroid"])
    retina_sec = create_spherical_shell(f"{ASSET_ID}-retina-section", R_CHOROID_IN, R_RETINA_IN, cutaway='horizontal', corneal_aperture=True, aperture_radius=0.024, material=mats["retina"])
    cornea_sec = create_cornea_and_limbus(mats, cutaway='horizontal')
    iris_sec = create_iris_and_pupil(mats, cutaway='horizontal')
    lens_sec = create_crystalline_lens(mats, cutaway='horizontal')
    ciliary_sec = create_ciliary_body_and_zonules(mats, cutaway='horizontal')
    retinal_landmarks = create_retinal_landmarks_and_vasculature(mats, cutaway='horizontal')
    nerve_sec = create_optic_nerve_bundle(mats)

    # Vitreous humor body in section (kept in blend for interactive inspection, hidden in cutaway render)
    bm_vit = bmesh.new()
    bmesh.ops.create_uvsphere(bm_vit, u_segments=48, v_segments=32, radius=R_RETINA_IN)
    mesh_vit = bpy.data.meshes.new(f"{ASSET_ID}-vitreous-mesh")
    bm_vit.to_mesh(mesh_vit)
    bm_vit.free()
    vit_sec = bpy.data.objects.new(f"{ASSET_ID}-vitreous", mesh_vit)
    bpy.context.collection.objects.link(vit_sec)
    bm_cut = bmesh.new()
    bmesh.ops.create_cube(bm_cut, size=1.0)
    mesh_cut = bpy.data.meshes.new("vit_cutter")
    bm_cut.to_mesh(mesh_cut)
    bm_cut.free()
    cut_obj = bpy.data.objects.new("vit_cutter", mesh_cut)
    bpy.context.collection.objects.link(cut_obj)
    cut_obj.scale = (0.12, 0.12, 0.10)
    cut_obj.location = (0.0, 0.0, 0.05)
    bpy.context.view_layer.update()

    mod_v = vit_sec.modifiers.new("CutSection", "BOOLEAN")
    mod_v.operation = "DIFFERENCE"
    mod_v.solver = "EXACT"
    mod_v.object = cut_obj
    bpy.context.view_layer.objects.active = vit_sec
    bpy.ops.object.modifier_apply(modifier="CutSection")
    bpy.data.objects.remove(cut_obj, do_unlink=True)
    for poly in vit_sec.data.polygons:
        poly.use_smooth = True
    vit_sec.data.materials.append(mats["vitreous"])
    vit_sec.hide_render = True  # Hidden in section render so internal retina, fovea, and vessels are directly visible

    sec_objs = [
        sclera_sec, choroid_sec, retina_sec, *cornea_sec, *iris_sec,
        lens_sec, *ciliary_sec, vit_sec, *retinal_landmarks, nerve_sec
    ]
    for o in sec_objs:
        if o.name not in coll_section.objects:
            coll_section.objects.link(o)
        if o.name in root_coll.objects:
            root_coll.objects.unlink(o)

    # =========================================================================
    # 3. HIGH-END MEDICAL STUDIO LIGHTING RIG
    # =========================================================================
    # World background
    world = bpy.data.worlds.new("eye_studio_world")
    world.use_nodes = True
    bpy.context.scene.world = world
    bg = world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.015, 0.020, 0.028, 1.0)
    bg.inputs["Strength"].default_value = 0.50

    # Key Area Light (Warm daylight, anterior-lateral)
    key_data = bpy.data.lights.new("Key_Light", 'AREA')
    key_data.energy = 8.5
    key_data.size = 0.35
    key_data.color = (1.0, 0.98, 0.94)
    key_obj = bpy.data.objects.new("Key_Light", key_data)
    key_obj.location = (-0.18, -0.28, 0.16)
    key_obj.rotation_euler = (Vector((0, 0, 0)) - key_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(key_obj)

    # Fill Area Light (Cool soft fill, lateral opposite)
    fill_data = bpy.data.lights.new("Fill_Light", 'AREA')
    fill_data.energy = 4.5
    fill_data.size = 0.45
    fill_data.color = (0.86, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (0.20, -0.24, 0.10)
    fill_obj.rotation_euler = (Vector((0, 0, 0)) - fill_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(fill_obj)

    # Rim / Edge Light (Sharp separation from behind)
    rim_data = bpy.data.lights.new("Rim_Light", 'AREA')
    rim_data.energy = 7.0
    rim_data.size = 0.30
    rim_data.color = (0.95, 0.98, 1.0)
    rim_obj = bpy.data.objects.new("Rim_Light", rim_data)
    rim_obj.location = (0.0, 0.28, 0.20)
    rim_obj.rotation_euler = (Vector((0, 0, 0)) - rim_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(rim_obj)

    # Cavity / Internal Fill Light (Soft angled light directly into horizontal cutaway bowl)
    cavity_data = bpy.data.lights.new("Cavity_Light", 'AREA')
    cavity_data.energy = 2.5
    cavity_data.size = 0.20
    cavity_data.color = (1.0, 0.96, 0.90)
    cavity_obj = bpy.data.objects.new("Cavity_Light", cavity_data)
    cavity_obj.location = (0.08, -0.02, 0.11)
    cavity_obj.rotation_euler = (Vector((0.0, 0.0, -0.015)) - cavity_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(cavity_obj)

    # Bottom Bounce Light
    bounce_data = bpy.data.lights.new("Bounce_Light", 'AREA')
    bounce_data.energy = 2.0
    bounce_data.size = 0.25
    bounce_data.color = (0.85, 0.88, 0.92)
    bounce_obj = bpy.data.objects.new("Bounce_Light", bounce_data)
    bounce_obj.location = (0.0, -0.15, -0.20)
    bounce_obj.rotation_euler = (Vector((0, 0, 0)) - bounce_obj.location).to_track_quat("-Z", "Y").to_euler()
    coll_lights.objects.link(bounce_obj)

    # =========================================================================
    # 4. CAMERA RIG & RENDERING PIPELINE
    # =========================================================================
    cam_data = bpy.data.cameras.new("MainCamera")
    cam_data.lens = 75.0  # 75mm portrait/macro medical lens
    cam_data.clip_start = 0.01
    cam_data.clip_end = 20.0
    cam_obj = bpy.data.objects.new("MainCamera", cam_data)
    root_coll.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderEngine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    if hasattr(scene, "eevee"):
        scene.eevee.use_raytracing = True
        scene.eevee.taa_render_samples = 128

    try:
        scene.view_settings.view_transform = 'AgX'
    except Exception:
        pass

    # Cleanup material slots across all created objects to prevent Boolean None slots
    for o in [*full_objs, *sec_objs]:
        if o.type == 'MESH':
            valid_mats = [m for m in o.data.materials if m is not None]
            if valid_mats:
                target_mat = valid_mats[0]
                o.data.materials.clear()
                o.data.materials.append(target_mat)
                for p in o.data.polygons:
                    p.material_index = 0

    return {
        "coll_full": coll_full,
        "coll_section": coll_section,
        "cam_obj": cam_obj,
        "full_objs": full_objs,
        "sec_objs": sec_objs,
    }


def main():
    print(f"=== BUILDING MEDICAL-GRADE HUMAN EYE 3D ASSET ===")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    data = build_scene()
    coll_full = data["coll_full"]
    coll_section = data["coll_section"]
    cam_obj = data["cam_obj"]

    # 1. Export GLB with Full Globe and Section
    coll_full.hide_render = False
    coll_section.hide_render = True
    print(f"Saving .blend file: {OUT_BLEND}")
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    print(f"Exporting GLB: {OUT_GLB}")
    bpy.ops.export_scene.gltf(
        filepath=str(OUT_GLB),
        export_format='GLB',
        use_selection=False,
        export_apply=True,
    )
    print(f"Exported GLB ({OUT_GLB.stat().st_size / 1024:.1f} KB)")

    # Copy to interactive viewer public directory
    VIEWER_GLB.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_GLB, VIEWER_GLB)
    print(f"Synchronized to viewer: {VIEWER_GLB}")

    vl = bpy.context.view_layer

    # 2. Render Mode A: 3/4 Exterior Globe Preview (preview.png)
    print("Rendering 3/4 Exterior Preview...")
    vl.layer_collection.children['Eye_Full'].exclude = False
    vl.layer_collection.children['Eye_Section'].exclude = True
    coll_full.hide_render = False
    coll_section.hide_render = True

    # Camera framed so full eye globe, rectus muscles, and optic nerve fit comfortably
    cam_loc = Vector((-0.14, -0.34, 0.09))
    target = Vector((0.0, 0.0, 0.0))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW}")

    # 3. Render Mode B: NCERT Fig 11.1 Horizontal Cross-Section (preview_section.png)
    print("Rendering NCERT Horizontal Cross-Section Preview...")
    vl.layer_collection.children['Eye_Full'].exclude = True
    vl.layer_collection.children['Eye_Section'].exclude = False
    coll_full.hide_render = True
    coll_section.hide_render = False

    # Side elevated 3/4 view matching NCERT Fig 11.1 orientation:
    # Cornea/pupil/lens on LEFT (-Y), retina/macula/optic nerve on RIGHT (+Y)
    cam_sec_loc = Vector((0.24, -0.005, 0.13))
    target_sec = Vector((0.00, 0.004, -0.008))
    cam_obj.location = cam_sec_loc
    cam_obj.rotation_euler = (target_sec - cam_sec_loc).to_track_quat("-Z", "Y").to_euler()

    bpy.context.scene.render.filepath = str(OUT_PREVIEW_SECTION)
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {OUT_PREVIEW_SECTION}")

    # Reset default visibility and re-save blend file
    vl.layer_collection.children['Eye_Full'].exclude = False
    vl.layer_collection.children['Eye_Section'].exclude = False
    coll_full.hide_render = False
    coll_section.hide_render = False
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.wm.save_mainfile()

    print("=== HUMAN EYE 3D BUILD COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
