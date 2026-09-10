# Worker M2 Dispatch

## Mission: Milestone 2 — Biology Core Anatomical Systems Part A (Heart, Eye, Brain)
You are Worker M2. Your mission is to implement the anatomical enhancements, procedural geometry, and realistic pedagogical shaders for `human-heart`, `human-eye`, and `brain` as defined in `PROJECT.md § Milestones` (Milestone 2) and `ORIGINAL_REQUEST.md`.

### Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m2`

### Authoritative Files
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/survey_biology.md` (detailed benchmarks for Heart, Eye, Brain)
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/handoff.md`

### Write Ownership (Exclusive to M2)
- `assets/biology/human-heart/*`
- `assets/biology/human-eye/*`
- `assets/biology/brain/*`

### Technical Requirements
1. **Human Heart (`assets/biology/human-heart/build_heart.py` and `asset.json`)**:
   - Model an anatomical coronal cutaway revealing 4 distinct chambers: Right Atrium (RA), Right Ventricle (RV), Left Atrium (LA), and Left Ventricle (LV with thicker muscular wall).
   - Model the interatrial septum and interventricular septum.
   - Model atrioventricular valves: Tricuspid valve (between RA & RV) and Bicuspid/Mitral valve (between LA & LV); Semilunar valves (aortic and pulmonary valves).
   - Model the great vessels with anatomically accurate attachments: Superior Vena Cava (SVC) & Inferior Vena Cava (IVC) into RA; Pulmonary Artery (trunk + left/right branches) from RV; Pulmonary Veins into LA; Aorta with aortic arch and 3 systemic branches (brachiocephalic, left common carotid, left subclavian) from LV.
   - Use `create_smooth_tube(..., cap_ends=True)` from `assets/python/edu_asset_kit.py` for all vessels to eliminate open non-manifold boundary edges.
   - Apply realistic biological tissue materials with Subsurface Scattering (`tissue_myocardium` or `add_tissue_material`).
   - Run headless build: `blender -b -P assets/biology/human-heart/build_heart.py`. Ensure exit code 0 and non-empty outputs in `out/`.
   - Document anatomical conventions/simplifications in `assets/biology/human-heart/asset.json`.

2. **Human Eye (`assets/biology/human-eye/build_eye.py` and `asset.json`)**:
   - Model the 3 concentric tunics: Outer fibrous tunic (opaque white Sclera transitioning to clear domed Cornea); Middle vascular tunic (dark pigmented Choroid layer, Ciliary Body with ciliary processes, and Iris); Inner sensory tunic (pigmented & neural Retina with optic disc / blind spot and fovea).
   - Model a true open pupil aperture in the iris (NOT a solid black cylinder token!).
   - Model the crystalline biconvex lens with suspensory zonules (Zonules of Zinn) connecting to the ciliary body.
   - Model the vitreous humor transparent body in the posterior cavity and aqueous humor in the anterior chamber.
   - Model the optic nerve bundle exiting posteromedially.
   - Use clean hollow geometry with a cross-sectional cutout (e.g. 90° or 120° quadrant cutaway) that reveals the internal cavity rather than flat slicing planes.
   - Apply realistic optical materials: glass/cornea transmission (IOR ~1.376), crystalline lens transmission (gradient or IOR ~1.406), and SSS for sclera and retina.
   - Run headless build: `blender -b -P assets/biology/human-eye/build_eye.py`. Ensure exit code 0 and non-empty outputs in `out/`.
   - Document conventions in `assets/biology/human-eye/asset.json`.

3. **Brain (`assets/biology/brain/build_brain.py` and `asset.json`)**:
   - Model the Cerebrum with left and right cerebral hemispheres, longitudinal fissure, and procedural displacement / noise forming distinct cortical gyri ridges and sulci furrows (resolving Feature 11).
   - Model the Cerebellum with horizontal folia striping and distinct left/right hemispheres.
   - Model the Brainstem with Differentiated Midbrain, prominent rounded Pons, and Medulla Oblongata tapering into the spinal cord.
   - Model deep commissural anatomy: C-shaped arch of the Corpus Callosum (NOT a straight cylinder!), Thalamus, and Hypothalamus with infundibulum.
   - Apply `tissueCortex` and `tissueNerve` shaders with Subsurface Scattering.
   - Run headless build: `blender -b -P assets/biology/brain/build_brain.py`. Ensure exit code 0 and non-empty outputs in `out/`.
   - Document conventions in `assets/biology/brain/asset.json`.

4. **Validation & Sync**:
   - Run `node tools/validate.mjs` (must pass 0 errors).
   - Run `node tests/e2e/run_all_tests.mjs --milestone M2` (all M2 tests must pass).
   - Run `node tools/sync-web-assets.mjs` to sync updated `.glb` files to `apps/interactive-viewer/public/assets/`.
   - Document all changes and verification outputs in `handoff.md`.

## 2026-09-09T03:30:00Z
**From**: Parent (40c9ff71-e711-4e13-b090-171086460054)
**Context**: Milestone 2 (Heart, Eye, Brain) Implementation
**Content**: Status check on Milestone 2 procedural generation scripts: Have build_heart.py, build_eye.py, and build_brain.py completed their test runs? Please provide current status and update progress.md.
**Action**: Provide update and update progress.md
