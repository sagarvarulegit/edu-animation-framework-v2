# Test Infrastructure & Methodology — Educational Animation Framework

## 1. Overview & Test Philosophy

This document defines the automated, requirement-driven end-to-end (E2E) test infrastructure for the Educational Animation Framework (`edu-animation-framework-v2`).

The test suite provides an **opaque-box, requirement-driven verification harness** covering all 32 features inventoried in `PROJECT.md § Feature Inventory` across Tiers 1 through 4.

### Core Testing Principles

1. **Requirement-Driven Assertions**: Every test case derives its expected outcomes directly from authoritative specifications:
   - `ORIGINAL_REQUEST.md` (Scientific accuracy, procedural generation, material polish, multi-format delivery)
   - `AGENTS.md` (Scientific correctness, pedagogical clarity, deterministic automation, coordinate/scale conventions)
   - `PROJECT.md` (32 feature requirements, interface contracts, milestone deliverables)
   - NCERT / CBSE Class 9–12 Science Textbooks (Anatomical structures, chemical equations, physical laws)

2. **Zero Facade Testing**: Tests exercise authentic system behavior, filesystem artifacts, schema definitions, mathematical relations, and binary signatures. No tests are written to trivially pass without validating actual requirements.

3. **Deterministic & Fast Execution**: The test suite runs in standard Node.js (v18.19.1+) without third-party dependencies or external service requirements. Headless binary inspections and validation steps run deterministically in seconds.

4. **Progressive Testability & Defect Isolation**: Tests verify requirements incrementally by Milestone (M1 through M6) and by Tier (Tier 1 through Tier 4). When a milestone feature is not yet implemented or contains a defect, the test fails with an explicit diagnostic message pinpointing the exact requirement and source file.

---

## 2. Test Suite Architecture

```
tests/e2e/
├── harness.mjs                   # Shared test runner harness, assertions, and reporting engine
├── tier1_feature_coverage.test.mjs # Tier 1: Feature presence, schema validity, output artifacts
├── tier2_boundary_cases.test.mjs   # Tier 2: Boundary conditions, degenerate inputs, constraint limits
├── tier3_cross_feature.test.mjs    # Tier 3: Cross-feature combinations, metadata/mesh/token parity
├── tier4_real_world.test.mjs       # Tier 4: Pipeline execution, schema validator pass, web readiness
└── run_all_tests.mjs             # Unified CLI test runner entrypoint
```

### Module Responsibilities

- **`harness.mjs`**: Provides the lightweight test runner framework with `describe`, `test`, `assert`, tier tagging, execution timing, colorized ANSI console reporting, and milestone filtering.
- **`tier1_feature_coverage.test.mjs`**: Verifies that every feature has its required schema properties, Python utilities, token definitions, asset metadata files, and build scripts in place.
- **`tier2_boundary_cases.test.mjs`**: Stress-tests constraints, negative/zero dimensions, out-of-range physical values, degenerate shapes, malformed inputs, and schema rejection behavior.
- **`tier3_cross_feature.test.mjs`**: Verifies relational integrity between components: `asset.json` metadata matching build script file outputs, design tokens matching shader parameters, glTF models in sync with web viewer directories, and chemical/physical laws (tetrahedral angles, planar graphene sheets, Snell's law).
- **`tier4_real_world.test.mjs`**: Executes real-world end-to-end integration workflows: running the full framework validator (`node tools/validate.mjs`), validating all 57 glTF/GLB binaries, verifying all 57 Blender scenes and rendered previews, and checking web viewer asset readiness.
- **`run_all_tests.mjs`**: Top-level executable that dispatches all tiers or targeted subsets via CLI arguments.

---

## 3. Test Tier Definitions

| Tier | Name | Focus | Scope |
|------|------|-------|-------|
| **Tier 1** | Feature Coverage | Presence & Structural Correctness | Verifies schemas, code interfaces, token registries, and required file paths exist and comply with structure. |
| **Tier 2** | Boundary & Corner Cases | Limits & Error Rejection | Tests edge cases: non-zero wall thickness, valid angle ranges, degenerate geometries, invalid token rejection. |
| **Tier 3** | Cross-Feature Combinations | Multi-Component Parity & Laws | Cross-validates metadata against build outputs, shader tokens against python kit, and scientific laws. |
| **Tier 4** | Real-World Application Scenarios | Full Pipeline & Delivery Readiness | Runs framework validation, binary integrity audits, web sync verification, and end-to-end workflows. |

---

## 4. Feature-to-Test Mapping Table

The 32 features from `PROJECT.md § Feature Inventory` are mapped across Tiers 1–4:

| # | Feature | Milestone | Tier 1 Test | Tier 2 Test | Tier 3 Test | Tier 4 Test |
|---|---------|-----------|-------------|-------------|-------------|-------------|
| 1 | SSS Schema Support | M1 | Schema defines `subsurfaceWeight`, `Radius`, `Scale` | Rejects weight > 1.0, radius != 3 items | Design tokens validate against SSS schema | Full schema validation passes |
| 2 | SSS Tissue Shaders in Kit | M1 | `edu_asset_kit.py` defines `add_tissue_material` | Validates default SSS parameters and bounds | Principled BSDF socket connections | Python compilation & import in Blender |
| 3 | Shared Spline Tube Utility | M1 | `edu_asset_kit.py` defines `create_smooth_tube` | Handles minimum points, non-zero radius, capping | Biology build scripts import shared kit | Asset build scripts compile cleanly |
| 4 | Biological Tissue Tokens | M1 | Tissue tokens present in `design-tokens.json` | Validates hex color regex, metallic <= 0.1 | Biology scripts reference token keys | Web viewer loads token styles |
| 5 | Metadata Alignment | M1 | `asset.json` has `provenance.generator` | Generator path syntax & traversal safety | Generator script file exists on disk | Validator verifies all 57 asset.json |
| 6 | Web Asset Sync Tool | M1 | `tools/sync-web-assets.mjs` exists | Missing destination directory auto-creation | `assets/**/out/*.glb` parity with web dir | Web viewer glb assets up to date |
| 7 | Heart Internal Anatomy | M2 | `build_heart.py` defines 4 chambers, septa, valves | LV wall thicker than RV wall ($t_{LV} > t_{RV}$) | Cutaway objects match `asset.json` labels | `human-heart.glb` valid glTF binary |
| 8 | Heart Vessels & Manifold Ends | M2 | Vena cava, aorta, pulmonary vessels defined | Capped vessel ends (0 open boundary edges) | Arterial red vs venous blue materials | Binary integrity of heart outputs |
| 9 | Eye 3-Layer Structure | M2 | Sclera, choroid, retina, vitreous defined | Layer radii: $r_{vit} < r_{ret} < r_{chor} < r_{scl}$ | Vitreous transmission >= 0.9 | `human-eye.glb` valid glTF binary |
| 10 | Eye Iris & Aperture Pupil | M2 | Annular iris mesh with light-admitting aperture | $0 < r_{pupil} < r_{iris}$ | Light transmission through pupil | Binary integrity of eye outputs |
| 11 | Brain Gyri & Sulci Detailing | M2 | Cerebral cortex with surface convolutions | Displacement amplitude > 0 within bounds | Left & right hemisphere division | `brain.glb` valid glTF binary |
| 12 | Brainstem & Cerebellar Folia | M2 | Cerebellum, corpus callosum, pons, medulla | Anatomical positioning bounds | Cerebrum/cerebellum/stem distinction | Binary integrity of brain outputs |
| 13 | Nephron Loop of Henle & Welding | M3 | Bowman's capsule, PCT, Henle loop, DCT, duct | Hairpin $U$-bend continuity, wall diameter > 0 | Vascular vs tubular color distinction | `nephron.glb` valid glTF binary |
| 14 | Respiratory Bronchial Tree & C-Rings | M3 | Trachea, C-rings, bronchial tree, alveoli | C-rings arc < 360° (open posteriorly) | Lung transmission allows internal view | `respiratory.glb` valid glTF binary |
| 15 | Continuous Digestive Tract & Ducts | M3 | Continuous GI tract & hepatopancreatic ducts | Continuous lumen endpoints matching | C-loop duodenum encloses pancreas | `digestive.glb` valid glTF binary |
| 16 | DNA Double Helix Geometry | M3 | Complementary base pairs and helical backbones | Horizontal base pair rungs ($z$-slope = 0) | AT and GC base pair color consistency | `dna.glb` valid glTF binary |
| 17 | Other Biology Topological Fixes | M3 | Build scripts for 13 biology assets exist | Coordinate validity, non-zero mesh volume | Biology asset metadata completeness | All 13 biology assets valid GLB |
| 18 | Diamond Lattice Crystallography | M4 | Tetrahedral sp3 carbon lattice defined | Tetrahedral angle $\approx 109.47^\circ$, uniform bonds | Closed 6-membered chair rings | `diamond-lattice.glb` valid GLB |
| 19 | Graphite Planar Hexagonal Lattice | M4 | Planar hexagonal graphene sheets defined | Planar $z$-variance = 0, $120^\circ$ angles | Interlayer spacing > bond length (~2.36x) | `graphite-lattice.glb` valid GLB |
| 20 | Hydrogen Evolution Delivery Tube | M4 | Continuous curved glass delivery tube | Tangent continuity $C^1$, constant tube bore | Borosilicate glass material applied | `hydrogen-apparatus.glb` valid GLB |
| 21 | Dropper Glass Wall Thickness | M4 | Lathe profile with inner & outer wall contours | $r_{outer}(z) > r_{inner}(z) > 0$ along body | Glass body vs rubber teat materials | `dropper.glb` valid GLB |
| 22 | Atom Electron Styling Unification | M4 | Mg and O atoms model nucleus & shells | Mg=12 (2,8,2), O=8 (2,6), increasing shell $r$ | Shared electron & nucleon styling | Atom `.glb` valid binaries |
| 23 | Chemistry Materials Polish | M4 | Glassware shaders use transmission & IOR | Meniscus curvature concave for water | Flame inner cool vs outer hot zones | Chemistry `.glb` valid binaries |
| 24 | Full Circuit Physics Consistency | M5 | Battery, switch, bulb, resistor modeled | Open switch -> bulb emission == 0 | Closed circuit continuity loop | `full-circuit.glb` valid GLB |
| 25 | DC Motor Split-Ring Commutator | M5 | Split rings, insulation gap, brushes modeled | Commutator gap angle > 0° and < 45° | N/S magnetic pole color coding | `electric-motor.glb` valid GLB |
| 26 | Glass Slab Emergent Rays & Pins | M5 | Slab, incident/refracted/emergent rays, pins | Snell's law: $\sin(i)/\sin(r) = n$, $e = i$ | Collinear pins P1-P2 and P3-P4 | `glass-slab.glb` valid GLB |
| 27 | Optics & Physics Materials | M5 | Crown glass IOR 1.52, meter dials, coils | Mirror metallic=1.0, roughness <= 0.05 | Red (+)/Black (-) terminal convention | Physics `.glb` valid binaries |
| 28 | Headless Batch Generation | M6 | All 57 assets have build scripts & out dirs | All 57 scripts compile without SyntaxError | Non-empty outputs: blend, glb, preview | Binary format verification |
| 29 | Full Schema & Catalog Validation | M6 | `tools/validate.mjs` executes cleanly | Validator detects invalid schemas / IDs | All 57 assets registered in catalog | 0 errors across entire workspace |
| 30 | Downstream Web Sync | M6 | 57 `.glb` files in web public directory | All web `.glb` files non-zero bytes | Parity between asset out/ and web dir | Interactive viewer loads without 404 |
| 31 | Full E2E Test Suite (Tiers 1-4) | M6 | All tiers execute via single test runner | Fast execution (< 10s), zero test defects | Cross-tier status reporting | Exit code matches pass/fail state |
| 32 | Adversarial Hardening (Tier 5) | M6 | Mesh integrity, manifoldness, scale checks | Reject NaN/Inf coordinates, zero area faces | Structural consistency under mutation | Complete forensic audit verification |

---

## 5. Test Runner Invocation & CLI Usage

### Basic Execution
Run all E2E test tiers (Tiers 1–4):
```bash
node tests/e2e/run_all_tests.mjs
```

### Targeted Execution by Tier
```bash
# Run Tier 1 only (Feature Coverage)
node tests/e2e/run_all_tests.mjs --tier 1

# Run Tier 2 only (Boundary & Corner Cases)
node tests/e2e/run_all_tests.mjs --tier 2

# Run Tier 3 only (Cross-Feature Combinations)
node tests/e2e/run_all_tests.mjs --tier 3

# Run Tier 4 only (Real-World Application Scenarios)
node tests/e2e/run_all_tests.mjs --tier 4

# Run multiple tiers
node tests/e2e/run_all_tests.mjs --tier 1,2
```

### Targeted Execution by Milestone
```bash
# Run tests relevant to Milestone 1
node tests/e2e/run_all_tests.mjs --milestone M1

# Run tests relevant to Milestone 2
node tests/e2e/run_all_tests.mjs --milestone M2
```

### Targeted Execution by Feature
```bash
# Run tests covering Feature 1 (SSS Schema Support)
node tests/e2e/run_all_tests.mjs --feature 1

# Run tests covering Feature 5 (Metadata Alignment)
node tests/e2e/run_all_tests.mjs --feature 5
```

### Options & Flags
- `--tier <list>`: Comma-separated list of tiers to run (`1`, `2`, `3`, `4`). Default: all.
- `--milestone <id>`: Filter tests by milestone (`M1` through `M6`).
- `--feature <id>`: Filter tests by feature number (1 through 32).
- `--verbose`: Enable detailed per-assertion logging.
- `--json`: Output test results in machine-readable JSON format.
- `--help`: Display CLI usage documentation.

---

## 6. Pass/Fail Semantics & Exit Codes

- **Exit Code 0**: All executed tests passed.
- **Exit Code 1**: One or more executed tests failed. Detailed diagnostic information (expected vs. actual, failing assertion, file path, line number) is printed to `stderr` / `stdout`.

### Diagnostic Output Example
```text
======================================================================
EDUCATIONAL ANIMATION FRAMEWORK — E2E TEST SUITE REPORT
======================================================================
[TIER 1] Feature Coverage Tests
  ✓ [F01] [M1] SSS Schema Support: schemas/design-tokens.schema.json defines subsurface properties
  ✓ [F02] [M1] SSS Shaders: edu_asset_kit.py exports add_tissue_material
  ...
[TIER 2] Boundary & Corner Cases
  ✓ [F18] [M4] Diamond Lattice: tetrahedral bond angles match 109.47 deg
  ...
[TIER 3] Cross-Feature Combinations
  ✓ [F05] [M1] Metadata Alignment: all 57 asset.json provenance.generator files exist
  ...
[TIER 4] Real-World Application Scenarios
  ✓ [F29] [M6] Framework Validator: tools/validate.mjs passes with 0 errors
  ✓ [F30] [M6] Web Sync: all 57 glb files present in interactive-viewer with valid glTF header
======================================================================
Summary: 32/32 Features Checked | Passed: 32 | Failed: 0 | Execution Time: 2.14s
======================================================================
```

---

## 7. Authoritative Sources of Expected Output

Every test case derives its assertions from documented specifications:

1. **glTF 2.0 Binary Specification** (Khronos Group):
   - Magic: `0x46546C67` (`glTF` in ASCII)
   - Version: `2`
   - Header length: 12 bytes
2. **NCERT Class 10/11 Science Standards**:
   - Human Heart: 4 chambers, tricuspid/bicuspid valves, coronal cutaway view.
   - Human Eye: Cornea -> pupil aperture -> crystalline lens -> vitreous -> retina -> choroid -> sclera.
   - Human Nephron: Bowman's capsule -> proximal tubule -> loop of Henle -> distal tubule -> collecting duct.
   - Diamond vs Graphite: Diamond $sp^3$ tetrahedral $\approx 109.47^\circ$ chair rings; Graphite $sp^2$ planar sheets $120.0^\circ$ with interlayer van der Waals spacing.
   - Glass Slab Refraction: Snell's Law $n_1 \sin(i) = n_2 \sin(r)$, emergent angle $e = i$, lateral ray displacement.
   - Electric Circuit: Light emission only when circuit is closed ($I = V/R > 0$).
3. **Repository Design System**:
   - `schemas/design-tokens.schema.json`
   - `visual/design-tokens.json`
   - `schemas/asset.schema.json`
