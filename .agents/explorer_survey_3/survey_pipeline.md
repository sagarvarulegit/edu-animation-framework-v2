# Pipeline & Validation Audit Report

**Auditor**: Pipeline & Validation Auditor (Explorer Survey 3)  
**Date**: 2026-09-09T02:55:00Z  
**Workspace**: `/home/sagarv/Projects/edu-animation-framework-v2`  
**Target Focus**: `tools/validate.mjs`, `schemas/`, `renderers/blender/`, `assets/python/`, `build_*.py` headless pipelines, and export workflows.

---

## Executive Summary

1. **Current Validation Baseline**: `node tools/validate.mjs` passes with **0 errors and 0 warnings** across all 57 registered assets, 44 OKF concepts, 3 lessons, 12 scene plans, and 1 design token file.
2. **Current Output Inventory**: All 57 assets in `assets/` currently have an associated `build_*.py` script and populated `out/<id>.blend`, `out/<id>.glb`, and `out/preview.png` files. Zero files have 0 bytes.
3. **Headless Blender Execution**: Headless execution via `blender --background --python <script>` is fully functional on Linux using Blender 4.2.0 LTS at `/home/sagarv/.local/bin/blender`. The trial run of `build_eye.py` completed with return code 0, generating `.blend`, `.glb` (0.75s export), and Cycles CPU ray-traced `preview.png` (2m19s).
4. **Critical Pipeline Gaps Identified**:
   - **Downstream Sync Disconnect**: `apps/interactive-viewer` loads models from `apps/interactive-viewer/public/assets/*.glb`. Generating a model via `build_*.py` writes only to `assets/<cat>/<id>/out/<id>.glb`; there is **no automated copy or synchronization tool**, leaving the web viewer showing stale models unless manually synchronized.
   - **Missing Build Orchestration**: `package.json` contains npm targets for only ~8 chemistry assets; 49 assets (including all Biology and Physics models) have no npm build scripts. There is no unified CLI tool (e.g., `tools/build_asset.py <id>` or `npm run build:assets`).
   - **Schema & Token Omissions for Subsurface Scattering (SSS)**: Neither `schemas/design-tokens.schema.json` nor `tools/validate.mjs` nor `assets/python/edu_asset_kit.py` supports Principled BSDF Subsurface Scattering sockets (`Subsurface Weight`, `Subsurface Radius`, `Subsurface Scale`), directly violating Requirement R3 for biological tissue shaders.
   - **Duplicated Procedural Geometry Helpers**: 3D Bezier tube extrusion (`create_smooth_tube`) is duplicated across `human-heart`, `nephron`, `human-respiratory-system`, and `human-excretory-system` instead of existing in the core kit `assets/python/edu_asset_kit.py`.
   - **Metadata Discrepancies**: In 6 assets (`brain`, `digestive-system`, `human-eye`, `human-heart`, `dna-double-helix`, `full-circuit`), `provenance.generator` in `asset.json` points to nonexistent scripts (e.g., `tools/extract_z_anatomy_*.py`), which `tools/validate.mjs` currently ignores.

---

## 1. Validation & Schema Architecture Survey

### 1.1 `tools/validate.mjs` Capabilities
`tools/validate.mjs` performs AST and structural schema validation across 6 artifact types:
- `visual/design-tokens.json`: Validates top-level keys (`colors`, `typography`, `materials`, `camera`, `lighting`, `labels`, `arrows`, `equations`, `particles`) and 6-digit hex color regex.
- `assets/**/asset.json`: Validates kebab-case ID matching directory name, version semver, categories, scale conventions, provenance structure, renderer compatibility booleans, and declared outputs.
- `lessons/**/lesson.json`: Validates curriculum, grade, learning objectives, scene references, and asset registry linkage.
- `knowledge/**/*.md`: Validates Open Knowledge Format (OKF v0.2) YAML frontmatter, types, citation sources, and cross-references.
- `lessons/**/narration.json`: Validates timestamp monotonically increasing cues and speakers.
- `lessons/**/<scene>.json`: Validates scene plans, camera shots, and timeline entries referencing implemented semantic primitives.

### 1.2 Current Baseline Test Execution
```bash
$ node tools/validate.mjs
Design Tokens     : 1 (visual/design-tokens.json validated)
OKF Concepts      : 44
Lessons checked   : 3
Assets checked    : 57
Scene plans       : 12
Narration scripts : 1
Asset registry    : brain, digestive-system, dna-double-helix, flower-anatomy, human-excretory-system, human-eye, human-heart, human-respiratory-system, nephron, neuron, reflex-arc, stoma, trophic-level-pyramid, beaker, bunsen-burner, conical-flask, diamond-lattice, displacement-reaction-setup, dropper, graphite-lattice, hydrogen-evolution-apparatus, laboratory-tongs, magnesium-atom, magnesium-burning-setup, magnesium-oxide, magnesium-oxide-lattice, magnesium-ribbon, methane-molecule, oxygen-atom, retort-stand, soap-micelle, test-tube, tripod-wire-gauze, watch-glass, water-electrolysis-apparatus, ammeter, bar-magnet, battery, bulb, concave-lens, concave-mirror, connecting-wire, convex-lens, convex-mirror, electric-motor, full-circuit, galvanometer, glass-prism, glass-prism-refraction, glass-slab, optical-bench, plane-mirror, resistor, rheostat, solenoid, switch, voltmeter

Validation passed.
```

### 1.3 Schema & Validation Blind Spots
1. **No Validation of Generator Script Existence**:
   In `tools/validate.mjs:326`:
   ```javascript
   strField(prov, "generator", file);
   ```
   The validator merely asserts that `provenance.generator` is a string. Six assets have invalid generator paths pointing to deleted or non-existent extraction scripts:
   - `assets/biology/brain/asset.json` -> `tools/extract_z_anatomy_brain.py` (actual: `build_brain.py`)
   - `assets/biology/digestive-system/asset.json` -> `tools/extract_z_anatomy_digestive.py` (actual: `build_digestive.py`)
   - `assets/biology/dna-double-helix/asset.json` -> `build_dna_double_helix.py` (actual: `build_dna.py`)
   - `assets/biology/human-eye/asset.json` -> `tools/extract_z_anatomy_eye.py` (actual: `build_eye.py`)
   - `assets/biology/human-heart/asset.json` -> `tools/extract_z_anatomy_heart.py` (actual: `build_heart.py`)
   - `assets/physics/full-circuit/asset.json` -> `build_full_circuit.py` (actual: `build_circuit.py`)
2. **Outputs Check is Warning-Only**:
   In `tools/validate.mjs:356-358`:
   ```javascript
   if (!existsSync(join(dirname(file), out.file))) {
     warnFile(file, `declared output "${out.file}" not found yet (run the build script)`);
   }
   ```
   Missing outputs do not fail `npm test` or `tools/validate.mjs`, making it possible for unbuilt assets to pass CI.
3. **No File Integrity / Non-Zero-Byte Check**:
   Neither the validator nor the build scripts check that `.blend`, `.glb`, or `preview.png` are non-empty valid binary files.
4. **Schema Omission for Subsurface Scattering (SSS)**:
   In `schemas/design-tokens.schema.json:96-112`:
   Only `baseColor`, `metallic`, `roughness`, `transmission`, `ior`, `emissionColor`, `emissionStrength` are permitted. Any attempt to add `subsurfaceWeight`, `subsurfaceRadius`, or `subsurfaceColor` to `design-tokens.json` will fail schema validation unless the schema is updated.

---

## 2. Headless Blender CLI Execution Survey

### 2.1 Blender Environment Verification
- **Host Binary**: `/home/sagarv/.local/bin/blender` (symlinked or directly accessible on PATH).
- **Version**: Blender 4.2.0 LTS (Release build `a51f293548ad`, built 2024-07-16).
- **Python Runtime**: Python 3.11 bundled inside Blender.
- **Draco Compression**: Available via `libextern_draco.so`.

### 2.2 Execution Command Patterns
Individual asset scripts can be executed via:
```bash
blender --background --python assets/<category>/<asset_id>/build_<script>.py
# or with explicit output redirection
blender --background --python assets/<category>/<asset_id>/build_<script>.py -- --out assets/<category>/<asset_id>/out
```

### 2.3 Headless Trial Execution Details (`build_eye.py`)
Execution telemetry from background execution task:
- **Status**: Return Code 0, cleanly terminated.
- **Phase 1: Scene & Geometry Assembly**: 0.08 seconds (BMesh lathe, primitive instantiation, and Boolean cutaway).
- **Phase 2: Master `.blend` Save**: `human-eye.blend` (2.4 MB) written via `kit.save_blend`.
- **Phase 3: Web GLB Export**: `human-eye.glb` (186 KB) exported in 0.75 seconds via `kit.export_glb(export_apply=True)`.
- **Phase 4: Cycles Preview Render**:
  - Engine: Cycles CPU with OpenImageDenoise.
  - Samples: 24.
  - Resolution: 1280x720.
  - Render time: 2 minutes 19 seconds.
- **Artifacts Verified**:
  - `assets/biology/human-eye/out/human-eye.blend` (2,416,244 bytes)
  - `assets/biology/human-eye/out/human-eye.glb` (186,788 bytes)
  - `assets/biology/human-eye/out/preview.png` (870,412 bytes)

### 2.4 Performance Bottlenecks & Optimization Needs
- **CPU Render Overhead**: Rendering 24 Cycles samples at 720p takes ~1.5 to 2.5 minutes per asset on CPU.
- **Full Suite Build Time**: Rebuilding all 57 assets headlessly with preview renders would take ~90–120 minutes sequentially.
- **Recommendation**:
  - Add a `--skip-preview` or `--fast` flag to `edu_asset_kit.py` / `build_*.py` for rapid geometry and `.glb` iteration.
  - Allow lowering render samples (e.g. 8 samples) or using Blender Workbench / EEVEE Next for quick test renders during development.

---

## 3. Shared Utilities & Asset Kit Architecture

### 3.1 Existing `assets/python/edu_asset_kit.py` Modules
The shared kit currently provides:
- `output_dir(default)`: CLI `--out` parser.
- `reset_scene()`: Cleans scene with `bpy.ops.wm.read_factory_settings(use_empty=True)`.
- `add_material(name, color, metallic, roughness)`: Basic Principled BSDF node setup.
- `add_material_from_token(name, key)`: Reads basic PBR properties from `design-tokens.json`.
- `add_glass_material(name, tint, ior, roughness)`: Optical/borosilicate glass shader.
- `add_machined_metal_material(name, color, metallic, roughness)`: Steel/aluminum shader.
- `lathe_object(name, profile_points, segments, material, location, rotation_euler)`: 360° rotational sweep of 2D profile.
- `mesh_object(name, verts, faces, material)`: Raw polygonal mesh creation from vertices and faces.
- `primitive_object(name, kind, material, size, location, rotation_euler)`: Cube, cylinder, cone, UV sphere.
- `text_mesh_object(name, text, material, size, extrude, location, rotation_euler)`: 3D font converted to mesh.
- `setup_world_and_light()`: Deep slate world background + 3-point Sun light rig.
- `frame_camera(objects, lens)`: Bounding-box automatic framing camera.
- `configure_render(width, height, samples)`: Cycles CPU setup.
- `save_blend(path)`: Saves current `.blend`.
- `export_glb(path)`: Exports `.glb` with modifiers applied.
- `render_preview(path)`: Renders still frame to disk.

### 3.2 Key Gaps & Missing Reusable Primitives
1. **Smooth 3D Spline / Tube Generator (`create_smooth_tube`)**:
   - Currently copy-pasted in:
     - `assets/biology/human-heart/build_heart.py:16` (`create_smooth_curved_tube`)
     - `assets/biology/nephron/build_nephron.py:14` (`create_smooth_tube`)
     - `assets/biology/human-respiratory-system/build_respiratory.py:151` (`create_smooth_tube`)
     - `assets/biology/human-excretory-system/build_excretory.py:14` (`create_smooth_tube`)
   - **Required Action**: Factor this into `edu_asset_kit.py`:
     ```python
     def smooth_tube_object(name, points, radius, material=None, segments=24, ring_verts=16):
         ...
     ```
2. **Subsurface Scattering Biological Material Helper (`add_tissue_material`)**:
   - Currently nonexistent in `edu_asset_kit.py`.
   - In Blender 4.2 LTS, the Principled BSDF SSS sockets are:
     - `bsdf.inputs["Subsurface Weight"].default_value = sss_weight` (e.g., 0.25 - 0.45)
     - `bsdf.inputs["Subsurface Radius"].default_value = Vector(sss_radius)` (e.g., (1.0, 0.2, 0.1) for fleshy tissue)
     - `bsdf.inputs["Subsurface Scale"].default_value = sss_scale` (e.g., 0.05)
     - `bsdf.inputs["Subsurface IOR"].default_value = 1.40`
   - **Required Action**: Add `add_tissue_material(name, base_color, sss_weight=0.3, sss_radius=(1.0, 0.2, 0.1), sss_scale=0.05, roughness=0.35)` to `edu_asset_kit.py`.
3. **Lighting Token Disconnect**:
   - `visual/design-tokens.json` specifies `energyWatts` for key (120W), fill (45W), and rim (75W) with specified radii.
   - `edu_asset_kit.py:253` ignores tokens and builds 3 Sun lights (`3.0`, `1.2`, `2.2` strength).
   - This should be reconciled so `setup_world_and_light()` respects design tokens.
4. **Organic Surface Displacement / Gyri-Sulci / Folia Helper**:
   - Assets like `brain` currently use simple UV spheres for cerebrum, cerebellum, and brainstem because there is no procedural displacement helper in `edu_asset_kit.py`.
   - A helper applying procedural Voronoi or Musgrave noise texture displacement to a subdivided BMesh would allow high-fidelity biological detailing.

---

## 4. Export & Downstream Consumption Pipeline

### 4.1 GLB Export Standards
All `build_*.py` scripts invoke:
```python
bpy.ops.export_scene.gltf(
    filepath=str(path),
    export_format="GLB",
    export_cameras=False,
    export_lights=False,
    export_apply=True
)
```
- `export_apply=True` ensures all modifiers (Subdivision Surface, Solidify, Bevel, Boolean) are baked into geometry before export.
- Cameras and lighting are excluded so the downstream Three.js / React Three Fiber scene controls the lighting environment and camera movement.

### 4.2 Downstream Viewer Disconnect (Critical Finding)
- `apps/interactive-viewer/src/components/AssetStudioInspector.tsx` line 75 loads:
  ```typescript
  const { scene } = useGLTF(`/assets/${asset.id}.glb`);
  ```
- Vite serves this from `apps/interactive-viewer/public/assets/${asset.id}.glb`.
- However, building an asset writes to:
  `assets/<category>/<asset_id>/out/<asset_id>.glb`.
- **There is currently NO build script, npm target, or watcher that copies generated `.glb` files into `apps/interactive-viewer/public/assets/`**.
- **Impact**: Updating an asset via `build_*.py` leaves the interactive viewer displaying stale geometry unless an agent or developer manually copies the file.

### 4.3 Build Automation Gaps in `package.json`
`package.json` contains:
```json
"build:magnesium-ribbon": "blender --background --python assets/chemistry/magnesium-ribbon/build_magnesium_ribbon.py",
"build:laboratory-tongs": "blender --background --python assets/chemistry/laboratory-tongs/build_laboratory_tongs.py",
"build:bunsen-burner": "blender --background --python assets/chemistry/bunsen-burner/build_bunsen_burner.py",
"build:watch-glass": "blender --background --python assets/chemistry/watch-glass/build_watch_glass.py",
"build:magnesium-oxide": "blender --background --python assets/chemistry/magnesium-oxide/build_magnesium_oxide.py",
"build:magnesium-atom": "blender --background --python assets/chemistry/magnesium-atom/build_magnesium_atom.py",
"build:oxygen-atom": "blender --background --python assets/chemistry/oxygen-atom/build_oxygen_atom.py",
"build:magnesium-oxide-lattice": "blender --background --python assets/chemistry/magnesium-oxide-lattice/build_magnesium_oxide_lattice.py",
"build:chemistry-atoms": "npm run build:magnesium-atom && npm run build:oxygen-atom && npm run build:magnesium-oxide-lattice",
"build:dropper": "blender --background --python assets/chemistry/dropper/build_dropper.py",
"build:lab-core-kit": "npm run build:bunsen-burner && ..."
```
- **Zero Biology Build Scripts**: `heart`, `brain`, `eye`, `nephron`, `respiratory`, `digestive` have no npm script entries.
- **Zero Physics Build Scripts**: `prism`, `magnet`, `circuit`, `lens`, `motor` have no npm script entries.
- **No Master Build Tool**: No `npm run build:assets` or `node tools/build-assets.mjs` exists.

---

## 5. Architectural Recommendations & Action Plan

### Recommended Changes

| Component | Current State | Proposed Enhancement |
|---|---|---|
| `assets/python/edu_asset_kit.py` | Lacks tube generator and SSS shader | Add `smooth_tube_object(...)` and `add_tissue_material(...)` with Blender 4.2 SSS inputs |
| `schemas/design-tokens.schema.json` | Rejects SSS material attributes | Add optional `subsurfaceWeight`, `subsurfaceRadius`, `subsurfaceColor`, `subsurfaceScale` to material properties |
| `visual/design-tokens.json` | Only 1 biological tissue (`tissue_myocardium`) with no SSS | Add anatomical tissue tokens for brain, eye, nephron, respiratory, digestive with SSS |
| `tools/validate.mjs` | Ignores generator file existence, warns only on missing outputs | Verify `provenance.generator` exists on disk; add non-zero byte check for outputs |
| 6 Desynchronized `asset.json` files | Point to `tools/extract_z_anatomy_*.py` | Update `generator` to match `build_*.py` scripts |
| Downstream Sync Tool | No sync mechanism for `public/assets/` | Create `tools/sync-web-assets.mjs` and hook into build workflow |
| Build Automation | Only 8 chemistry scripts in `package.json` | Create `tools/build-assets.mjs` supporting `--asset <id>`, `--category <cat>`, `--fast`, and auto-sync to `public/assets/` |

---

## Conclusion
The core headless Blender pipeline and validation infrastructure are fundamentally solid and functional on Linux with Blender 4.2.0. However, critical gaps in **reusable procedural utilities (spline tubes and SSS shaders)**, **schema support for subsurface scattering**, **metadata synchronization**, and **automated web asset synchronization** must be resolved to fulfill the requirements of the 3D educational model enhancement project.
