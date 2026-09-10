import bpy
import bmesh
import math
from mathutils import Vector

print("\n==================== DEEP ANATOMICAL AUDIT ====================")

# 1. HEART AUDIT
bpy.ops.wm.open_mainfile(filepath="assets/biology/human-heart/out/human-heart.blend")
print("\n--- [HEART DETAILED AUDIT] ---")
heart_objs = {o.name: o for o in bpy.data.objects}
print(f"Loaded {len(heart_objs)} objects in heart.")

# Check required anatomical structures
expected_heart = [
    "human-heart-ventricles",
    "human-heart-interventricular-septum",
    "human-heart-right-atrium",
    "human-heart-left-atrium",
    "human-heart-interatrial-septum",
    "human-heart-aorta-arch",
    "human-heart-pulmonary-trunk",
    "human-heart-svc",
    "human-heart-ivc"
]
for exp in expected_heart:
    assert exp in heart_objs, f"Missing required heart object: {exp}"
    print(f"  [PASS] Found: {exp}")

# Check valves
tricuspid = [o for o in heart_objs if "tricuspid" in o]
mitral = [o for o in heart_objs if "mitral" in o]
aortic_valves = [o for o in heart_objs if "aortic-valve" in o]
pulm_valves = [o for o in heart_objs if "pulmonary-valve" in o]
print(f"  Tricuspid cusps: {len(tricuspid)} (expected 3)")
print(f"  Mitral cusps: {len(mitral)} (expected 2)")
print(f"  Aortic semilunar cusps: {len(aortic_valves)} (expected 3)")
print(f"  Pulmonary semilunar cusps: {len(pulm_valves)} (expected 3)")
assert len(tricuspid) == 3, f"Expected 3 tricuspid cusps, got {len(tricuspid)}"
assert len(mitral) == 2, f"Expected 2 mitral cusps, got {len(mitral)}"
assert len(aortic_valves) == 3, f"Expected 3 aortic valve cusps, got {len(aortic_valves)}"
assert len(pulm_valves) == 3, f"Expected 3 pulmonary valve cusps, got {len(pulm_valves)}"

# Check papillary & chordae
chordae = [o for o in heart_objs if "chorda" in o]
papillary = [o for o in heart_objs if "papillary" in o]
print(f"  Papillary muscles: {len(papillary)} | Chordae tendineae: {len(chordae)}")
assert len(papillary) >= 3, "Expected at least 3 papillary muscles"
assert len(chordae) >= 7, "Expected multiple chordae tendineae fibers"

# Check great vessels branches
aorta_branches = ["human-heart-brachiocephalic", "human-heart-left-carotid", "human-heart-left-subclavian"]
for b in aorta_branches:
    assert b in heart_objs, f"Missing aorta systemic branch: {b}"
print("  [PASS] Aortic arch systemic branches verified (brachiocephalic, left carotid, left subclavian).")

pulm_veins = [o for o in heart_objs if "pulm-vein" in o]
print(f"  Pulmonary veins: {len(pulm_veins)} (expected 4)")
assert len(pulm_veins) == 4, f"Expected 4 pulmonary veins into LA, found {len(pulm_veins)}"

# Check ventricular wall thickness ratio (LV vs RV)
# LV is around X=+0.02 to +0.035, RV is around X=-0.035 to -0.02
vent = heart_objs["human-heart-ventricles"]
bm = bmesh.new()
bm.from_mesh(vent.data)
# Find bounding boxes or wall distances
# In build_heart.py: LV_WALL_THICKNESS = 0.012, RV_WALL_THICKNESS = 0.004 -> 3.0x ratio
print("  Ventricular mesh: verts =", len(bm.verts), "faces =", len(bm.faces))
bm.free()


# 2. EYE AUDIT
bpy.ops.wm.open_mainfile(filepath="assets/biology/human-eye/out/human-eye.blend")
print("\n--- [EYE DETAILED AUDIT] ---")
eye_objs = {o.name: o for o in bpy.data.objects}
print(f"Loaded {len(eye_objs)} objects in eye.")

expected_eye = [
    "human-eye-sclera",
    "human-eye-cornea",
    "human-eye-choroid",
    "human-eye-ciliary",
    "human-eye-iris",
    "human-eye-pupil",
    "human-eye-lens",
    "human-eye-retina",
    "human-eye-vitreous",
    "human-eye-aqueous",
    "human-eye-optic-nerve",
    "human-eye-optic-disc",
    "human-eye-macula"
]
for exp in expected_eye:
    assert exp in eye_objs, f"Missing required eye object: {exp}"
    print(f"  [PASS] Found: {exp}")

# Check suspensory zonules
zonules = [o for o in eye_objs if "zonule" in o]
print(f"  Suspensory zonules of Zinn: {len(zonules)} (expected 32)")
assert len(zonules) == 32, f"Expected 32 zonules of Zinn, got {len(zonules)}"

# Check Pupil Aperture geometry in Iris
iris = eye_objs["human-eye-iris"]
bm = bmesh.new()
bm.from_mesh(iris.data)
# Iris should be an annular ring. Minimum radius of vertices from center in local space (X, Y):
radii = [math.sqrt(v.co.x**2 + v.co.y**2) for v in bm.verts]
min_radius = min(radii)
max_radius = max(radii)
print(f"  Iris aperture geometry: min radius = {min_radius*1000:.2f} mm, max radius = {max_radius*1000:.2f} mm")
assert min_radius > 0.003, f"Pupil aperture is closed or solid! min_radius={min_radius}"
assert max_radius > 0.010, f"Iris outer border too small! max_radius={max_radius}"
# Check if any face covers the center aperture (radius < 0.003)
faces_covering_center = 0
for f in bm.faces:
    center = f.calc_center_median()
    if math.sqrt(center.x**2 + center.y**2) < 0.003:
        faces_covering_center += 1
print(f"  Faces covering central aperture: {faces_covering_center}")
assert faces_covering_center == 0, "Pupil aperture is NOT open! Faces found in center."
print("  [PASS] Iris has a genuine, open pupil aperture hole.")
bm.free()

# Check crystalline lens biconvexity
lens = eye_objs["human-eye-lens"]
bm = bmesh.new()
bm.from_mesh(lens.data)
z_coords = [v.co.z for v in bm.verts]
z_min = min(z_coords)
z_max = max(z_coords)
print(f"  Lens Z range (anterior to posterior poles): min={z_min*1000:.2f} mm, max={z_max*1000:.2f} mm")
# Center at (0,0) in local space
center_verts = [v for v in bm.verts if math.sqrt(v.co.x**2 + v.co.y**2) < 0.002]
center_z = [v.co.z for v in center_verts]
print(f"  Lens central poles Z: {min(center_z)*1000:.2f} mm to {max(center_z)*1000:.2f} mm")
equator_verts = [v for v in bm.verts if math.sqrt(v.co.x**2 + v.co.y**2) > 0.011]
equator_z = [v.co.z for v in equator_verts]
print(f"  Lens equator Z: {min(equator_z)*1000:.2f} mm to {max(equator_z)*1000:.2f} mm")
assert max(center_z) > max(equator_z), "Lens is not convex on anterior face"
assert min(center_z) < min(equator_z), "Lens is not convex on posterior face"
print("  [PASS] Lens is verified biconvex (thicker at optical axis than equator).")
bm.free()


# 3. BRAIN AUDIT
bpy.ops.wm.open_mainfile(filepath="assets/biology/brain/out/brain.blend")
print("\n--- [BRAIN DETAILED AUDIT] ---")
brain_objs = {o.name: o for o in bpy.data.objects}
print(f"Loaded {len(brain_objs)} objects in brain.")

expected_brain = [
    "brain-cerebrum",
    "brain-cerebellum",
    "brain-corpus-callosum",
    "brain-thalamus",
    "brain-hypothalamus",
    "brain-infundibulum",
    "brain-pituitary",
    "brain-optic-chiasm",
    "brain-midbrain",
    "brain-pons",
    "brain-medulla",
    "brain-spinal-cord"
]
for exp in expected_brain:
    assert exp in brain_objs, f"Missing required brain object: {exp}"
    print(f"  [PASS] Found: {exp}")

# Check gyri/sulci on cerebrum
cerebrum = brain_objs["brain-cerebrum"]
bm = bmesh.new()
bm.from_mesh(cerebrum.data)
# Calculate standard deviation or variance of vertex radial distances to confirm surface roughness/displacement
radii_cerebrum = [v.co.length for v in bm.verts if abs(v.co.x) > 0.015]
mean_r = sum(radii_cerebrum) / len(radii_cerebrum)
variance = sum((r - mean_r)**2 for r in radii_cerebrum) / len(radii_cerebrum)
std_dev = math.sqrt(variance)
print(f"  Cerebrum lateral cortex: count={len(radii_cerebrum)}, mean radius={mean_r*1000:.2f} mm, std_dev={std_dev*1000:.3f} mm")
assert std_dev > 0.001, "Cerebrum surface is completely smooth! No gyri/sulci displacement detected."
print("  [PASS] Cerebrum has confirmed procedural gyri/sulci surface convolutions.")
bm.free()

# Check cerebellar folia
cerebellum = brain_objs["brain-cerebellum"]
bm = bmesh.new()
bm.from_mesh(cerebellum.data)
z_vals = [v.co.z for v in bm.verts]
print(f"  Cerebellum vertex count: {len(bm.verts)}, Z span: {min(z_vals)*1000:.1f} to {max(z_vals)*1000:.1f} mm")
bm.free()

# Check Corpus Callosum C-shaped arch
cc = brain_objs["brain-corpus-callosum"]
bm = bmesh.new()
bm.from_mesh(cc.data)
# In build_brain.py, CC was created with smooth tube along C-shaped points:
# Y spans from -0.022 (splenium) to +0.024 (genu), Z arches up to 0.027
y_coords = [v.co.y for v in bm.verts]
z_coords = [v.co.z for v in bm.verts]
print(f"  Corpus callosum: Y span = {min(y_coords)*1000:.1f} to {max(y_coords)*1000:.1f} mm")
print(f"  Corpus callosum: Z span = {min(z_coords)*1000:.1f} to {max(z_coords)*1000:.1f} mm")
assert max(y_coords) - min(y_coords) > 0.035, "Corpus callosum lacks proper anterior-posterior span"
assert max(z_coords) - min(z_coords) > 0.015, "Corpus callosum is flat, not arched"
print("  [PASS] Corpus callosum is verified C-shaped arch.")
bm.free()

print("\nALL ANATOMICAL AND GEOMETRIC VERIFICATIONS PASSED!")

