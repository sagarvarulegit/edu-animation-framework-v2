# Handoff Report — Pipeline & Validation Audit

**Agent**: Pipeline & Validation Auditor (Explorer Survey 3)  
**Date**: 2026-09-09T02:56:00Z  
**Directory**: `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_3`  
**Handoff Type**: Hard (Task Complete)

---

## 1. Observation

1. **Validation Status**:
   Executed `node tools/validate.mjs` at repository root. Command exited with code 0:
   ```
   Design Tokens     : 1 (visual/design-tokens.json validated)
   OKF Concepts      : 44
   Lessons checked   : 3
   Assets checked    : 57
   Scene plans       : 12
   Narration scripts : 1
   Asset registry    : brain, digestive-system, dna-double-helix, flower-anatomy, human-excretory-system, human-eye, human-heart, human-respiratory-system, nephron, neuron, reflex-arc, stoma, trophic-level-pyramid, beaker, bunsen-burner, conical-flask, diamond-lattice, displacement-reaction-setup, dropper, graphite-lattice, hydrogen-evolution-apparatus, laboratory-tongs, magnesium-atom, magnesium-burning-setup, magnesium-oxide, magnesium-oxide-lattice, magnesium-ribbon, methane-molecule, oxygen-atom, retort-stand, soap-micelle, test-tube, tripod-wire-gauze, watch-glass, water-electrolysis-apparatus, ammeter, bar-magnet, battery, bulb, concave-lens, concave-mirror, connecting-wire, convex-lens, convex-mirror, electric-motor, full-circuit, galvanometer, glass-prism, glass-prism-refraction, glass-slab, optical-bench, plane-mirror, resistor, rheostat, solenoid, switch, voltmeter

   Validation passed.
   ```

2. **Asset Artifact Completeness**:
   Audited all 57 asset directories under `assets/` via Node script:
   - All 57 assets contain an active `build_*.py` script.
   - All 57 assets contain `out/<id>.blend`, `out/<id>.glb`, and `out/preview.png`.
   - Zero files have 0 bytes.

3. **Blender CLI Environment & Headless Run**:
   - Host binary: `/home/sagarv/.local/bin/blender` (version 4.2.0 LTS, release commit `a51f293548ad`).
   - Executed `blender --background --python assets/biology/human-eye/build_eye.py`.
   - Result: Exited with code 0. Generated `human-eye.blend` (2.4MB), exported `human-eye.glb` in 0.75s (186KB), rendered `preview.png` via Cycles CPU (24 samples) in 2m19s.

4. **Schema Omission for Subsurface Scattering (SSS)**:
   In `schemas/design-tokens.schema.json:96-112`:
   ```json
   "materials": {
     "type": "object",
     "additionalProperties": {
       "type": "object",
       "required": ["baseColor", "metallic", "roughness"],
       "properties": {
         "baseColor": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" },
         "metallic": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
         "roughness": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
         "transmission": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
         "ior": { "type": "number", "minimum": 1.0, "maximum": 3.0 },
         "emissionColor": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" },
         "emissionStrength": { "type": "number", "minimum": 0.0 }
       }
     }
   }
   ```
   Blender 4.2 Principled BSDF inputs (`Subsurface Weight`, `Subsurface Radius`, `Subsurface Scale`) are not included in the schema or validated in `tools/validate.mjs`.

5. **Code Duplication in Procedural Scripts**:
   `create_smooth_tube` or `create_smooth_curved_tube` is duplicated across:
   - `assets/biology/human-heart/build_heart.py:16-46`
   - `assets/biology/nephron/build_nephron.py:14-37`
   - `assets/biology/human-respiratory-system/build_respiratory.py:151-174`
   - `assets/biology/human-excretory-system/build_excretory.py:14-37`
   It is missing from `assets/python/edu_asset_kit.py`.

6. **Generator Metadata Divergence**:
   Six assets in `assets/**/asset.json` specify obsolete generator paths that do not exist:
   - `brain`: `"tools/extract_z_anatomy_brain.py"` (actual: `build_brain.py`)
   - `digestive-system`: `"tools/extract_z_anatomy_digestive.py"` (actual: `build_digestive.py`)
   - `dna-double-helix`: `"build_dna_double_helix.py"` (actual: `build_dna.py`)
   - `human-eye`: `"tools/extract_z_anatomy_eye.py"` (actual: `build_eye.py`)
   - `human-heart`: `"tools/extract_z_anatomy_heart.py"` (actual: `build_heart.py`)
   - `full-circuit`: `"build_full_circuit.py"` (actual: `build_circuit.py`)

7. **Downstream Web Assets Disconnect**:
   - `apps/interactive-viewer/src/components/AssetStudioInspector.tsx:75` loads `/assets/${asset.id}.glb`, resolved from `apps/interactive-viewer/public/assets/`.
   - Asset build scripts output to `assets/<cat>/<id>/out/<id>.glb`.
   - No script or build rule exists to copy or sync updated `.glb` files to `apps/interactive-viewer/public/assets/`.
   - `package.json` only contains scripts for 8 chemistry assets; 49 assets have no npm build entries.

---

## 2. Logic Chain

1. **From Observation 1 & 2**:
   The existing asset library and validation pipeline currently pass all structural tests, with all 57 assets having populated output folders. Therefore, changes made during anatomical enhancement can be regression-tested directly with `node tools/validate.mjs`.

2. **From Observation 3**:
   Blender 4.2.0 LTS on Linux successfully executes procedural Python scripts headlessly and generates valid production artifacts without user interaction. However, each Cycles 24-sample render takes ~2 minutes on CPU, indicating that a batch rebuild of all 57 models would take ~2 hours unless optimized or run with preview generation disabled during development.

3. **From Observation 4 & 5**:
   The user request specifically mandates realistic biological materials (subsurface scattering) and procedural anatomical enhancements across Heart, Brain, Eye, Nephron, Respiratory, and Digestive models. Because `edu_asset_kit.py` lacks an SSS tissue shader and a reusable 3D tube/spline generator, and `design-tokens.schema.json` disallows SSS fields, multiple scripts duplicate spline logic and rely on generic flat shaders. Adding `smooth_tube_object` and `add_tissue_material` to `edu_asset_kit.py` and updating `design-tokens.schema.json` is a prerequisite for clean, compliant model enhancement.

4. **From Observation 6**:
   The divergence between `asset.json` generator paths and actual `build_*.py` files reveals that `tools/validate.mjs` has a blind spot: it does not verify that the generator file exists. Aligning these fields prevents confusing downstream AI agents or developers.

5. **From Observation 7**:
   Because `apps/interactive-viewer` reads from `apps/interactive-viewer/public/assets/`, rebuilding an asset in `assets/<cat>/<id>/` will have zero visual impact on the interactive web viewer until the `.glb` is copied. An automated synchronization step or script (`tools/sync-web-assets.mjs`) is required to ensure that model improvements appear in the interactive viewer.

---

## 3. Caveats

1. **Rendering Performance**: Headless rendering was timed only on `build_eye.py`. Complex scenes with higher polygon counts or multiple boolean modifiers may take longer than 2m19s per asset.
2. **GPU Acceleration**: Blender was tested with CPU Cycles rendering (`device = "CPU"` in `configure_render`). CUDA/OptiX hardware acceleration was not configured or tested in this headless environment.
3. **Web Viewer Automation**: Headless browser viewport testing (`tools/batch_fast.mjs`) relies on Google Chrome at `/usr/bin/google-chrome` and an active Vite server at `http://localhost:5173`. We verified the script logic, but did not start the Vite dev server during this read-only survey.

---

## 4. Conclusion

The build and validation pipeline is intact and functional, but has four critical architectural gaps that should be addressed before or during the anatomical model polish phase:
1. Promote `create_smooth_tube` to `edu_asset_kit.py` and implement `add_tissue_material` with Blender 4.2 Principled BSDF Subsurface Scattering sockets.
2. Expand `schemas/design-tokens.schema.json` to allow SSS properties and add anatomical tissue presets to `visual/design-tokens.json`.
3. Correct the 6 desynchronized `provenance.generator` values in `asset.json` and enforce generator file existence in `tools/validate.mjs`.
4. Create an automated sync tool to copy generated `out/*.glb` files to `apps/interactive-viewer/public/assets/` and provide a unified asset build runner in `tools/`.

---

## 5. Verification Method

To independently verify the observations and findings in this report:

1. **Run Integrity Validation**:
   ```bash
   node tools/validate.mjs
   ```
   *Expected result*: Exits with code 0; logs 57 assets, 44 OKF concepts, 3 lessons, 12 scenes.

2. **Verify Blender CLI and Headless Execution**:
   ```bash
   blender --version
   blender --background --python assets/biology/human-eye/build_eye.py
   ```
   *Expected result*: Blender 4.2.0 prints version and runs `build_eye.py` to completion, writing to `assets/biology/human-eye/out/`.

3. **Verify Generator Discrepancies**:
   Inspect `assets/biology/human-heart/asset.json:53` vs actual file `assets/biology/human-heart/build_heart.py`:
   ```bash
   grep -n "generator" assets/biology/human-heart/asset.json
   ls assets/biology/human-heart/build_*.py
   ```
   *Expected result*: `generator` is `"tools/extract_z_anatomy_heart.py"`, whereas the local script is `build_heart.py`.

4. **Verify SSS Absence in Schema**:
   Inspect `schemas/design-tokens.schema.json:96-112`:
   *Expected result*: `properties` for materials contains only `baseColor`, `metallic`, `roughness`, `transmission`, `ior`, `emissionColor`, `emissionStrength`.
