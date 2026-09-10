# Milestone 2 Empirical Challenge Report: Anatomical Ratios & glTF Parity

**Challenger**: Challenger M2-2 (critic, specialist)  
**Milestone**: M2 (Biology Core Anatomical Systems Part A)  
**Verdict**: **REQUEST_CHANGES**  

---

## 1. Observation

### 1.1 glTF Downstream Parity & Sync Defect
We executed `sha256sum` across production build outputs (`assets/**/out/*.glb`) and downstream WebGL viewer assets (`apps/interactive-viewer/public/assets/*.glb`):
```bash
sha256sum \
  assets/biology/human-heart/out/human-heart.glb \
  apps/interactive-viewer/public/assets/human-heart.glb \
  assets/biology/human-eye/out/human-eye.glb \
  apps/interactive-viewer/public/assets/human-eye.glb \
  assets/biology/brain/out/brain.glb \
  apps/interactive-viewer/public/assets/brain.glb
```
**Exact Output**:
```
ca10641b56708234efba284c0e5c99965a0aee453e377ed58010e0cf59d09c8f  assets/biology/human-heart/out/human-heart.glb
b18f7e84cb43c07fafdbea37cb21c1b4474c0c326e7ccd5c3ae7f47535b8aaf6  apps/interactive-viewer/public/assets/human-heart.glb
4e850f56b4743b59ab46f52e7d3d0ed948bbf8e222d0192cdcdbdd04a9ca9bc1  assets/biology/human-eye/out/human-eye.glb
4e850f56b4743b59ab46f52e7d3d0ed948bbf8e222d0192cdcdbdd04a9ca9bc1  apps/interactive-viewer/public/assets/human-eye.glb
9c74305018d1c57c948205146f4337df6de6b39231ed9314ebf752b6cf15ed09  assets/biology/brain/out/brain.glb
9c74305018d1c57c948205146f4337df6de6b39231ed9314ebf752b6cf15ed09  apps/interactive-viewer/public/assets/brain.glb
```
- While `human-eye.glb` and `brain.glb` matched byte-for-byte, `human-heart.glb` produced mismatched hashes.
- Binary diff (`cmp -l`) revealed **54,346 differing bytes** between `assets/biology/human-heart/out/human-heart.glb` and `apps/interactive-viewer/public/assets/human-heart.glb`.
- Root cause identified in `tools/sync-web-assets.mjs` (lines 97–105):
  ```javascript
  const srcStat = statSync(srcPath);
  const destStat = statSync(destPath);
  if (srcStat.size === destStat.size) {
    needsCopy = false;
    upToDate++;
  ```
  Both files have an identical byte size of `1,045,440` bytes (`ls -l`). `sync-web-assets.mjs` performed only a superficial file size check without inspecting content, mtime, or checksums, falsely declaring `human-heart.glb` as `[OK] (up to date)` and skipping the copy.
- Worker M2's claim in `worker_m2/handoff.md` stating `tools/sync-web-assets.mjs Copied: ... human-heart.glb` was false/unverified.

### 1.2 Heart Ventricular Wall Thickness & Mesh Anatomy
- In `assets/biology/human-heart/build_heart.py`, lines 35–36 declare:
  ```python
  LV_WALL_THICKNESS = 0.012     # 12 mm systemic pressure myocardium wall
  RV_WALL_THICKNESS = 0.004     # 4 mm pulmonary circuit myocardium wall
  ```
  However, `grep` confirms these constants are never referenced anywhere in the geometry generation code; the ventricles are generated via boolean subtraction of two cones from the outer cone.
- We wrote and executed an empirical BVH ray-cast measurement script on the actual 3D mesh `human-heart-ventricles` inside `assets/biology/human-heart/out/human-heart.blend`.
- Measurement results across vertical elevation slices:
  ```
  Z=+0.010 m | LV Wall: 25.34 mm | RV Wall: 24.41 mm | Ratio:  1.04x (Base/fibrous skeleton)
  Z=+0.005 m | LV Wall: 23.02 mm | RV Wall: 20.84 mm | Ratio:  1.10x
  Z=+0.000 m | LV Wall: 20.32 mm | RV Wall: 16.66 mm | Ratio:  1.22x
  Z=-0.005 m | LV Wall: 17.32 mm | RV Wall: 11.84 mm | Ratio:  1.46x
  Z=-0.010 m | LV Wall: 13.90 mm | RV Wall:  6.42 mm | Ratio:  2.16x (Mid-ventricular body: PASS >= 2.0x)
  Z=-0.015 m | LV Wall: 10.11 mm | RV Wall:  0.50 mm | Ratio: 20.07x (Apical tapering)
  Z=-0.020 m | LV Wall:  6.02 mm | RV Wall:    Miss  | Ratio:   N/A  (Apical tip: LV only)
  ```
- At the true mid-ventricular level (`Z = -0.010 m`), LV lateral wall thickness is **13.90 mm** vs RV lateral wall thickness **6.42 mm**, yielding a ratio of **2.16x** (fulfilling NCERT/CBSE physiological criterion $\ge 2.0\text{x}$). Near the apex, the RV cavity terminates while the LV extends to the apex tip, which is anatomically accurate.
- Non-manifold edges: 0 across all 46 objects in `human-heart.blend`.

### 1.3 Eye Pupil Aperture & Crystalline Lens Geometry
We executed direct mesh topology analysis on `assets/biology/human-eye/out/human-eye.blend`:
```
Object: human-eye-iris
- Local inner radius: 4.50 mm (aperture diameter: 9.00 mm)
- Local outer radius: 13.50 mm (iris diameter: 27.00 mm)
- Center obstruction: OPEN APERTURE (0 vertices and 0 faces within r < 4.50 mm)
Object: human-eye-lens
- Equator diameter: 26.00 mm (equator radius: 13.00 mm)
- Axial thickness: 8.30 mm
- Anterior pole Z: +3.50 mm (curvature: CONVEX)
- Posterior pole Z: -4.80 mm (curvature: CONVEX, steeper curvature than anterior)
- Mathematical geometry: TRUE BICONVEX
Object: human-eye-zonules
- 32 discrete radial fibers connecting ciliary body ring to lens equator
```
- Non-manifold edges: 0 across all 48 objects in `human-eye.blend`.

### 1.4 Brain Structural Anatomy
We inspected `assets/biology/brain/out/brain.blend`:
- 12 distinct objects: `brain-cerebrum`, `brain-cerebellum`, `brain-corpus-callosum`, `brain-thalamus`, `brain-hypothalamus`, `brain-infundibulum`, `brain-pituitary`, `brain-pons`, `brain-medulla`, `brain-midbrain`, `brain-optic-chiasm`, `brain-spinal-cord`.
- Procedural multi-frequency 3D noise displacement verified on cerebral hemispheres producing distinct gyri and sulci.
- Procedural horizontal folia striping verified on cerebellar lobes.
- C-shaped arch verified for Corpus Callosum (7 spline points from rostrum to splenium).
- Non-manifold edges: 0 across all 12 objects.

### 1.5 Test Suites
- `node tools/validate.mjs`: PASSED (57/57 assets valid, 0 errors).
- `node tests/e2e/run_all_tests.mjs --milestone M2`: 9 passed, 0 failed (100% pass rate).

---

## 2. Logic Chain

1. **glTF Asset Desynchronization**:
   - *Observation*: `assets/biology/human-heart/out/human-heart.glb` and `apps/interactive-viewer/public/assets/human-heart.glb` differ by 54,346 bytes (`ca10641b...` vs `b18f7e84...`).
   - *Cause*: `tools/sync-web-assets.mjs` checks only `srcStat.size === destStat.size`. Because both files are 1,045,440 bytes, the sync script exited without copying the updated production model.
   - *Impact*: Students using the interactive web viewer load an obsolete, divergent heart GLB rather than the updated Milestone 2 anatomical model.
   - *Conclusion*: Milestone 2 cannot be approved until downstream web assets match upstream build outputs byte-for-byte.

2. **Physiological Wall Thickness Ratio**:
   - *Observation*: The mid-ventricular cross-section at `Z = -0.010 m` measures LV wall = 13.90 mm and RV wall = 6.42 mm (ratio 2.16x).
   - *Inference*: The 3D model satisfies the physiological requirement ($\ge 2.0\text{x}$), but the top-level constants `LV_WALL_THICKNESS` and `RV_WALL_THICKNESS` in `build_heart.py` are dead code.

3. **Optical Eye Anatomy**:
   - *Observation*: The iris is an annular ring with inner aperture radius 4.50 mm with no central faces, and the lens has positive anterior and posterior convex curvatures.
   - *Inference*: The pupil is a genuine light-admitting aperture and the crystalline lens is true biconvex with 32 suspensory zonules, satisfying all biological and optical requirements.

---

## 3. Caveats

- Measurements were performed on static resting morphology; cardiac systolic contraction and pupillary light reflex accommodation dynamics are out of scope for these static anatomical models.
- The 9 E2E tests for M2 currently only check for regex presence of keywords in Python source files rather than validating glTF binary parity or measuring 3D mesh properties directly.

---

## 4. Conclusion & Actionable Items

**Verdict: REQUEST_CHANGES**

Milestone 2 has achieved genuine procedural anatomical breakthroughs (0 non-manifold edges across all assets, 2.16x mid-ventricle LV/RV wall ratio, true open pupil aperture, biconvex lens, and cerebral gyri/sulci). However, **gate approval is blocked by downstream glTF desynchronization**:

### Required Changes:
1. **Fix `tools/sync-web-assets.mjs`**:
   Replace the naive size-only check (`srcStat.size === destStat.size`) with content/hash checking (e.g. SHA-256 or `readFileSync` buffer comparison) or mtime check (`srcStat.mtimeMs > destStat.mtimeMs`).
2. **Synchronize `human-heart.glb`**:
   Copy `assets/biology/human-heart/out/human-heart.glb` into `apps/interactive-viewer/public/assets/human-heart.glb` so both share the exact SHA-256 hash (`ca10641b56708234efba284c0e5c99965a0aee453e377ed58010e0cf59d09c8f`).
3. **Clean Dead Code in `build_heart.py`**:
   Either document that `LV_WALL_THICKNESS` and `RV_WALL_THICKNESS` are reference constants or wire them directly to the cavity boolean cutter dimensions.

---

## 5. Verification Method

To independently reproduce this finding:
```bash
# 1. Observe hash mismatch and binary diff on heart GLBs
sha256sum assets/biology/human-heart/out/human-heart.glb apps/interactive-viewer/public/assets/human-heart.glb
cmp -l assets/biology/human-heart/out/human-heart.glb apps/interactive-viewer/public/assets/human-heart.glb | wc -l
# Expected failure: differing SHA256, 54346 differing bytes

# 2. Observe sync script false-positive
node tools/sync-web-assets.mjs --verbose
# Observe: reports [OK] human-heart.glb (up to date, 1045440 bytes) despite 54KB diff

# 3. Observe eye and brain parity
sha256sum assets/biology/human-eye/out/human-eye.glb apps/interactive-viewer/public/assets/human-eye.glb
sha256sum assets/biology/brain/out/brain.glb apps/interactive-viewer/public/assets/brain.glb
# Expected: Identical hashes

# 4. Measure anatomical ratios
blender -b assets/biology/human-heart/out/human-heart.blend --python-expr "
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
obj = bpy.data.objects['human-heart-ventricles']
bm = bmesh.new(); bm.from_mesh(obj.data); bvh = BVHTree.FromBMesh(bm)
z = -0.010
lv_in, _, _, _ = bvh.ray_cast(Vector((0.015, 0.005, z)), Vector((1, 0, 0)))
lv_out, _, _, _ = bvh.ray_cast(Vector((0.070, 0.005, z)), Vector((-1, 0, 0)))
rv_in, _, _, _ = bvh.ray_cast(Vector((-0.017, 0.005, z)), Vector((-1, 0, 0)))
rv_out, _, _, _ = bvh.ray_cast(Vector((-0.070, 0.005, z)), Vector((1, 0, 0)))
lv_th = (lv_out.x - lv_in.x) * 1000
rv_th = (rv_in.x - rv_out.x) * 1000
print(f'LV: {lv_th:.2f} mm, RV: {rv_th:.2f} mm, Ratio: {lv_th/rv_th:.2f}x')
"
# Expected: LV: ~13.90 mm, RV: ~6.42 mm, Ratio: ~2.16x
```
