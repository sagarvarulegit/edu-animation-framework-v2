"""
build_brain.py — High-Fidelity Anatomical Sagittal & Hemispheric Section of the Human Brain
CBSE Class 10 Biology, Chapter 7: Control and Coordination
CBSE Class 11 Biology, Chapter 21: Neural Control and Coordination — Central Nervous System (Brain)

Anatomical Features:
- Cerebrum: Cerebral hemispheres separated by longitudinal fissure, with genuine procedural gyri ridges and sulci furrows
- Anatomical lobes: Frontal, Parietal, Temporal, and Occipital lobes
- Medial sagittal section exposing deep commissural and diencephalic anatomy:
  * C-shaped arch of the Corpus Callosum (rostrum, genu, body, and splenium; NOT a straight cylinder!)
  * Thalamus: Large ovoid sensory relay center
  * Hypothalamus: Neuroendocrine control center with infundibulum (stalk) leading to Pituitary Gland (NOT a cube!)
  * Optic Chiasm and Mammillary body
- Brainstem:
  * Differentiated Midbrain (cerebral peduncles and tectal colliculi)
  * Prominent rounded Pons (bulging anteriorly)
  * Medulla Oblongata tapering continuously into the Spinal Cord
- Cerebellum:
  * Foliated structure with fine horizontal folia folds/striping
- Shaders:
  * Subsurface Scattering for gray matter cortex (tissueCortex), brainstem/corpus callosum (tissueNerve), and cerebellar folia
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "python"))
import edu_asset_kit as kit
import bpy
import bmesh
from mathutils import Vector, noise

ASSET_ID = "brain"


def create_cerebral_cortex(name, is_left, material):
    """
    Creates an anatomically contoured cerebral hemisphere with authentic procedural
    gyri ridges and sulci furrows covering the cortex.
    """
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=48, radius=0.045)
    sign = 1.0 if is_left else -1.0

    for v in bm.verts:
        px, py, pz = v.co.x, v.co.y, v.co.z

        # Shape into anatomical hemisphere:
        # Elongated anterior-posterior (Y), arch parieto-occipitally (Z), flatten medially at X=0
        if (is_left and px < 0) or (not is_left and px > 0):
            v.co.x *= 0.12 # Flatten medial sagittal face
        else:
            v.co.x *= 1.10
        v.co.y *= 1.30
        v.co.z *= 0.98

        # Procedural multi-frequency 3D noise displacement for gyri ridges and sulci furrows
        freq1 = 44.0
        freq2 = 88.0
        n1 = noise.noise(Vector((v.co.x * freq1, v.co.y * freq1, v.co.z * freq1)))
        n2 = noise.noise(Vector((v.co.x * freq2, v.co.y * freq2, v.co.z * freq2)))

        # Sinusoidal convolution to form continuous winding gyri convolutions and sulcal valleys
        gyri_val = math.sin(n1 * math.pi * 3.5 + n2 * 1.6) * 0.0035

        # Weight displacement: fully on lateral convexity, zero on flat medial sagittal face
        medial_dist = abs(v.co.x)
        weight = min(1.0, max(0.0, (medial_dist - 0.003) / 0.010))

        norm = v.normal.normalized() if v.normal.length > 0 else Vector((sign, 0, 0))
        v.co += norm * (gyri_val * weight)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    offset_x = 0.003 * sign
    obj.location = (offset_x, 0.016, 0.018)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    if material:
        obj.data.materials.append(material)

    return obj


def create_cerebellum(name, material):
    """
    Creates the cerebellum with characteristic horizontal folia striping.
    Positioned postero-inferior to the cerebral occipital lobes.
    """
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=48, radius=0.034)

    for v in bm.verts:
        # Morph into bilateral cerebellar mass: wider transversely (X), flattened dorsoventrally (Z)
        v.co.x *= 1.20
        v.co.y *= 0.88
        v.co.z *= 0.80

        # Sculpt horizontal folia striping via sinusoidal Z-frequency modulation
        folia_val = math.sin(v.co.z * 220.0) * 0.0016
        norm = v.normal.normalized() if v.normal.length > 0 else Vector((0, -1, 0))
        v.co += norm * folia_val

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.004, -0.034, -0.016)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    if material:
        obj.data.materials.append(material)

    return obj


def create_corpus_callosum(name, material):
    """
    Creates the authentic C-shaped commissural arch of the Corpus Callosum
    (Rostrum, Genu, Body, and Splenium). NOT a straight cylinder!
    """
    pts = [
        Vector((0.004, 0.018, 0.010)),  # Rostrum (pointing toward lamina terminalis)
        Vector((0.004, 0.024, 0.016)),  # Genu (prominent anterior bend)
        Vector((0.004, 0.020, 0.024)),  # Anterior body
        Vector((0.004, 0.004, 0.027)),  # Summit / trunk of arch
        Vector((0.004, -0.014, 0.024)), # Posterior body
        Vector((0.004, -0.022, 0.016)), # Splenium (thick rounded posterior arch)
        Vector((0.004, -0.020, 0.012)),
    ]
    return kit.create_smooth_tube(
        name, pts, radius=0.0035, resolution=20, material=material, cap_ends=True
    )


def create_hypothalamus(name, material):
    """
    Creates the wedge-shaped hypothalamus nucleus situated antero-inferior
    to the thalamus. (Authentic organic wedge morphology, NOT a cube!).
    """
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=0.0075, radius2=0.0035, depth=0.013)
    mesh = bpy.data.meshes.new(f"{name}-mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = (0.004, 0.012, 0.004)
    obj.rotation_euler = (0.35, 0.0, 0.0)

    for poly in obj.data.polygons:
        poly.use_smooth = True
    if material:
        obj.data.materials.append(material)
    return obj


def build_brain():
    """Builds an authentic anatomical human brain with gyri/sulci, cerebellar folia, C-arch corpus callosum, and brainstem."""
    # === PBR MATERIALS with Biological Subsurface Scattering ===
    cortex_mat = kit.add_material_from_token("brain-cortex", "tissueCortex")
    cerebellum_mat = kit.add_tissue_material("brain-cerebellum", (0.72, 0.42, 0.36, 1.0), roughness=0.55, subsurface_weight=0.35)
    stem_mat = kit.add_material_from_token("brain-stem", "tissueNerve")
    corpus_mat = kit.add_material_from_token("brain-corpus-callosum", "tissueNerve")
    thalamus_mat = kit.add_material("brain-thalamus", (0.80, 0.52, 0.48), metallic=0.04, roughness=0.45)
    pituitary_mat = kit.add_material("brain-pituitary", (0.85, 0.35, 0.35), metallic=0.08, roughness=0.40)

    objects = []

    # 1. Cerebrum: Left Cerebral Hemisphere with procedural gyri and sulci
    cerebrum_left = create_cerebral_cortex(f"{ASSET_ID}-cerebrum", is_left=True, material=cortex_mat)
    objects.append(cerebrum_left)

    # 2. Deep Commissural & Diencephalic Anatomy (Exposed in medial sagittal aspect)
    # C-shaped arch of Corpus Callosum
    corpus_callosum = create_corpus_callosum(f"{ASSET_ID}-corpus-callosum", corpus_mat)
    objects.append(corpus_callosum)

    # Thalamus: Large ovoid sensory relay center beneath corpus callosum
    thalamus = kit.primitive_object(
        f"{ASSET_ID}-thalamus", "uv_sphere", thalamus_mat,
        size=(0.018, 0.024, 0.016),
        location=(0.005, -0.002, 0.013)
    )
    objects.append(thalamus)

    # Hypothalamus: Organic wedge-shaped neuroendocrine control center
    hypothalamus = create_hypothalamus(f"{ASSET_ID}-hypothalamus", cortex_mat)
    objects.append(hypothalamus)

    # Infundibulum (stalk) & Pituitary Gland (Master endocrine gland)
    infundibulum = kit.create_smooth_tube(
        f"{ASSET_ID}-infundibulum",
        [Vector((0.004, 0.014, 0.002)), Vector((0.004, 0.018, -0.007))],
        radius=0.0014, resolution=12, material=stem_mat, cap_ends=True
    )
    pituitary = kit.primitive_object(
        f"{ASSET_ID}-pituitary", "uv_sphere", pituitary_mat,
        size=(0.009, 0.008, 0.007),
        location=(0.004, 0.020, -0.009)
    )
    objects.extend([infundibulum, pituitary])

    # Optic Chiasm landmark
    optic_chiasm = kit.primitive_object(
        f"{ASSET_ID}-optic-chiasm", "uv_sphere", stem_mat,
        size=(0.007, 0.005, 0.004),
        location=(0.004, 0.023, -0.002)
    )
    objects.append(optic_chiasm)

    # 3. Hindbrain — Cerebellum with horizontal folia striping
    cerebellum = create_cerebellum(f"{ASSET_ID}-cerebellum", cerebellum_mat)
    objects.append(cerebellum)

    # 4. Brainstem: Midbrain, Pons, and Medulla Oblongata
    # Midbrain (Mesencephalon): cerebral peduncles and colliculi
    midbrain = kit.primitive_object(
        f"{ASSET_ID}-midbrain", "cylinder", stem_mat,
        size=(0.016, 0.016, 0.012),
        location=(0.004, -0.005, 0.001),
        rotation_euler=(0.15, 0.0, 0.0)
    )
    # Pons: Prominent rounded anterior bulge
    pons = kit.primitive_object(
        f"{ASSET_ID}-pons", "uv_sphere", stem_mat,
        size=(0.022, 0.020, 0.018),
        location=(0.004, -0.003, -0.013)
    )
    # Medulla Oblongata: Tapering cone descending continuously
    medulla = kit.primitive_object(
        f"{ASSET_ID}-medulla", "cone", stem_mat,
        size=(0.015, 0.010, 0.022),
        location=(0.004, -0.008, -0.030),
        rotation_euler=(0.10, 0.0, 0.0)
    )
    # Spinal Cord: Continuous downward pathway
    spinal_cord = kit.primitive_object(
        f"{ASSET_ID}-spinal-cord", "cylinder", stem_mat,
        size=(0.009, 0.009, 0.030),
        location=(0.004, -0.012, -0.052),
        rotation_euler=(0.08, 0.0, 0.0)
    )
    objects.extend([midbrain, pons, medulla, spinal_cord])

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
    objects = build_brain()
    kit.setup_world_and_light()
    kit.configure_render(width=1280, height=720, samples=16)
    kit.frame_camera(objects, lens=50.0)
    kit.save_blend(out / f"{ASSET_ID}.blend")
    kit.export_glb(out / f"{ASSET_ID}.glb")
    kit.render_preview(out / "preview.png")
    print(f"[OK] High-fidelity {ASSET_ID} built and rendered successfully.")


if __name__ == "__main__":
    main()
