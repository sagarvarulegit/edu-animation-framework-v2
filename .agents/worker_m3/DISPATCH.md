# Worker M3 Dispatch

## Mission: Milestone 3 — Biology Core Anatomical Systems Part B & Microscopic
You are Worker M3. Your mission is to implement anatomical enhancements, procedural geometry fixes, and topological cleanup for:
- `nephron` (`assets/biology/nephron/`)
- `human-respiratory-system` (`assets/biology/human-respiratory-system/`)
- `digestive-system` (`assets/biology/digestive-system/`)
- `dna-double-helix` (`assets/biology/dna-double-helix/`)
- Other biology assets: `human-excretory-system`, `stoma`, `trophic-level-pyramid`, `neuron`, `reflex-arc`

### Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m3`

### Authoritative Files
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/survey_biology.md` (detailed benchmarks for Nephron, Respiratory, Digestive, DNA, etc.)
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/handoff.md`

### Write Ownership (Exclusive to M3)
- `assets/biology/nephron/*`
- `assets/biology/human-respiratory-system/*`
- `assets/biology/digestive-system/*`
- `assets/biology/dna-double-helix/*`
- `assets/biology/human-excretory-system/*`
- `assets/biology/stoma/*`
- `assets/biology/trophic-level-pyramid/*`
- `assets/biology/neuron/*`
- `assets/biology/reflex-arc/*`

### Technical Tasks
1. **Nephron (`build_nephron.py`)**:
   - Model Bowman's capsule enclosing the glomerulus tuft.
   - Model the proximal convoluted tubule (PCT) with winding loops.
   - Model the hairpin Loop of Henle: thin descending limb transitioning to thicker ascending limb.
   - Model distal convoluted tubule (DCT) curving back into macula densa contact with Bowman's vascular pole.
   - Model the collecting duct receiving multiple DCT connections.
   - Use `create_smooth_tube(..., cap_ends=True)` to weld/cap all tubule and capillary segments, eliminating the 576 non-manifold boundary edges.
   - Run headless build: `blender -b -P assets/biology/nephron/build_nephron.py`.

2. **Respiratory System (`build_respiratory.py`)**:
   - Make lungs transparent/cutaway (dielectric transmission with slight tissue color) to reveal the internal bronchial tree: primary bronchi branching into lobar and segmental bronchioles.
   - Replace closed complete cylinders for tracheal rings with anatomically accurate C-shaped hyaline cartilages.
   - Model terminal alveolar clusters.
   - Eliminate 280 non-manifold edges across tubes.
   - Run headless build: `blender -b -P assets/biology/human-respiratory-system/build_respiratory.py`.

3. **Digestive System (`build_digestive.py`)**:
   - Replace the 7 disconnected spheres for the small intestine with a continuous looping coiled tube (duodenum, jejunum, ileum).
   - Ensure the GI tract is continuous from mouth/pharynx, esophagus, stomach (fundus, body, pylorus), small intestine, large intestine (cecum with appendix, ascending/transverse/descending/sigmoid colon with haustra, rectum).
   - Model hepatopancreatic duct convergence (common bile duct from liver/gallbladder + pancreatic duct from pancreas entering the C-loop of the duodenum).
   - Run headless build: `blender -b -P assets/biology/digestive-system/build_digestive.py`.

4. **DNA Double Helix (`build_dna.py`)**:
   - Fix cylinder rotation math (`rotation_euler`) so base pair cylinders connect the two antiparallel helical backbones horizontally (perpendicular to helical axis).
   - Apply skin modifier to convert 1D wireframes to manifold geometry (eliminating 80 non-manifold elements).
   - Represent major and minor grooves.
   - Sync base pair colors with `design-tokens.json` (Adenine=Green, Thymine=Red, Guanine=Amber, Cytosine=Blue).
   - Run headless build: `blender -b -P assets/biology/dna-double-helix/build_dna.py`.

5. **Other Biology Asset Polish**:
   - `human-excretory-system`: cap renal vessels/ureters, eliminating 168 non-manifold edges.
   - `stoma`: eliminate 64 non-manifold edges on inner wall tubes.
   - `trophic-level-pyramid`: fix zero-thickness degenerate cone in arrow head.
   - `neuron`: cylindrical Schwann cells and Nodes of Ranvier.
   - `reflex-arc`: butterfly gray matter contour in spinal cord cross-section.
   - Run headless builds for any modified assets.

6. **Web Sync & Validation**:
   - Run `node tools/sync-web-assets.mjs --force`.
   - Run `node tools/validate.mjs` (must pass with 0 errors).
   - Run `node tests/e2e/run_all_tests.mjs --milestone M3` (all M3 tests must pass).
   - Write progress.md and handoff.md in your directory.

## 2026-09-09T08:05:36Z
You are Worker M3 (Biology Anatomical Systems Part B & Microscopic).
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m3/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_1/survey_biology.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 3:
1. Nephron (Bowman's capsule + glomerulus, PCT, loop of Henle, DCT with macula densa contact, collecting duct, weld tubes to eliminate 576 non-manifold edges).
2. Respiratory System (cutaway/transparent lungs revealing branching bronchial tree, C-shaped tracheal rings, alveoli clusters, eliminate 280 non-manifold edges).
3. Digestive System (continuous looping small intestine, continuous GI tract mouth to rectum, hepatopancreatic duct entering duodenum).
4. DNA Double Helix (horizontal base pair cylinders connecting strands, applied skin modifier, major/minor grooves, sync base colors with design-tokens.json).
5. Other biology assets (human-excretory-system, stoma, trophic-level-pyramid, neuron, reflex-arc).
6. Run headless Blender builds for all modified assets.
7. Run `node tools/sync-web-assets.mjs --force`.
8. Verify: `node tools/validate.mjs` (0 errors) and `node tests/e2e/run_all_tests.mjs --milestone M3`.
9. Write progress.md and handoff.md in your directory (/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m3).
10. Send a message to the caller when complete.
