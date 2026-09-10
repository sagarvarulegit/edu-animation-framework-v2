# Original User Request

## 2026-09-09T02:47:25Z

Audit, research, and polish the 3D educational models in the repository to align with real-world scientific and anatomical reality, prioritizing Biology anatomical systems (Heart, Brain, Eye, Nephron, Respiratory, Digestive) followed by Chemistry and Physics apparatus, while balancing realistic materials and proportions with educational clarity.

Working directory: /home/sagarv/Projects/edu-animation-framework-v2
Integrity mode: development

## Requirements

### R1. Scientific and Anatomical Accuracy Audit
Review and research existing 3D models against authoritative scientific benchmarks (NCERT/CBSE Class 9–12 textbooks and anatomical/physical references). Document all discrepancies in anatomical structure, missing features, incorrect connections, and unrealistic proportions or orientations, beginning with core Biology models (Heart, Brain, Eye, Nephron, Respiratory, Digestive) and extending to Chemistry and Physics assets.

### R2. Procedural Blender Geometry & Topology Enhancement
Refine the procedural Blender generation scripts (`build_*.py` under `assets/`) to fix identified anatomical and physical errors. Enhance geometric fidelity (e.g., proper chamber/vessel connections in Heart, sulci/gyri detailing in Brain, accurate layers in Eye, proper nephron tubule looping), eliminate non-manifold geometry or mesh artifacts, and ensure clean procedural modifier stacks.

### R3. Realistic Pedagogical Shaders & Material Polish
Upgrade procedural materials and lighting to reflect physical reality (subsurface scattering, realistic roughness/specularity, accurate tissue/glass/metal shaders) while strictly maintaining pedagogical color-coding and visibility for educational demonstrations.

### R4. Pipeline Integration & Multi-Format Generation
Ensure all updated build scripts deterministically generate production `.blend` files, web-ready `.glb` models, and high-resolution `preview.png` renderings without manual Blender intervention, maintaining full compatibility with the interactive viewer and video composer.

## Verification Resources

- Framework schema and integrity validator: `node tools/validate.mjs`
- Linux Blender CLI: `blender` (v4.2 LTS at `/home/sagarv/.local/bin/blender`)
- Asset directories: `assets/biology/`, `assets/chemistry/`, `assets/physics/`
- Reference standards: `AGENTS.md` (scientific correctness, pedagogical clarity, deterministic automation)

## Acceptance Criteria

### Scientific Correctness & Anatomy
- [ ] Heart model features 4 anatomically distinct chambers, correct vena cava / pulmonary artery / aorta orientations and attachments, and septal division.
- [ ] Eye model features correct layered anatomy (cornea, iris, pupil, biconvex crystalline lens, ciliary body, retina, optic nerve exit).
- [ ] Brain model features anatomically distinct cerebrum (with gyri/sulci convolutions), cerebellum (with folia texturing), and brainstem (pons & medulla oblongata).
- [ ] Nephron model accurately represents Bowman's capsule with glomerulus, proximal convoluted tubule, hairpin loop of Henle (descending/ascending limbs), distal convoluted tubule, and collecting duct.
- [ ] Human respiratory and digestive systems accurately portray branching airways/alveoli and connected gastrointestinal tract segments with proportional scaling.
- [ ] All scientific simplifications or pedagogical conventions are explicitly documented in corresponding `asset.json` descriptions.

### Procedural Script & Mesh Quality
- [ ] All updated `build_*.py` scripts execute headlessly via `blender -b -P <script>` exiting with return code 0 and no unhandled Python exceptions.
- [ ] Generated meshes have clean normals, no inverted faces, and no severe self-intersections.

### Material & Visual Polish
- [ ] Shaders utilize Principled BSDF with realistic physical attributes (subsurface scattering on biological tissues, transmission/roughness on glass apparatus, metallic properties on conductors/stands).
- [ ] Visual clarity and pedagogical color distinctions are preserved under neutral three-point studio lighting.

### System Validation & Build Outputs
- [ ] `node tools/validate.mjs` passes with 0 errors across all assets, schemas, and catalogs.
- [ ] Every modified asset directory contains verified, non-empty `out/*.blend`, `out/*.glb`, and `out/preview.png` files.
