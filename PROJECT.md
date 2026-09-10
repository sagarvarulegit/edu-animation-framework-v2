# Project: Educational Animation Framework — 3D Asset Scientific Polish & Verification

## Architecture

The framework decouples lesson specifications from rendering backends. 3D models live under `assets/<discipline>/<asset-id>/` and are generated deterministically via headless Blender scripts (`build_*.py`).

```
assets/
├── python/
│   └── edu_asset_kit.py         # Shared Blender procedural geometry & shader library
├── biology/
│   ├── human-heart/             # Coronal section, 4 chambers, septa, valves
│   ├── human-eye/               # 3 layers (sclera, choroid, retina), lens, pupil aperture
│   ├── brain/                   # Gyri/sulci convolutions, folia, C-arch corpus callosum
│   ├── nephron/                 # Glomerulus, PCT, loop of Henle, DCT, collecting duct
│   ├── human-respiratory-system/# Transparent lungs, bronchial tree, C-rings, alveoli
│   ├── digestive-system/        # Continuous GI tract, duodenal loop, hepatopancreatic duct
│   └── dna-double-helix/        # Antiparallel strands, horizontal base pairs, major/minor grooves
├── chemistry/
│   ├── diamond-lattice/         # Inverted tetrahedral branching, 6-member chair rings
│   ├── graphite-lattice/        # Planar hexagonal graphene sheets (valency 3)
│   ├── hydrogen-evolution-apparatus/ # Continuous curved delivery tube
│   └── dropper/                 # Manifold glass lathe profile with wall thickness
└── physics/
    ├── full-circuit/            # Consistent switch-bulb state (no open-circuit emission)
    ├── electric-motor/          # True split-ring commutator and brushes
    └── glass-slab/              # Emergent refraction pins and ray paths
```

Data Flow:
1. `build_*.py` uses `assets/python/edu_asset_kit.py` and `visual/design-tokens.json`.
2. Headless execution: `blender -b -P build_<id>.py`.
3. Outputs: `out/<id>.blend`, `out/<id>.glb`, `out/preview.png`.
4. Downstream Sync: `tools/sync-web-assets.mjs` copies `.glb` into `apps/interactive-viewer/public/assets/`.
5. Schema & Catalog Validation: `node tools/validate.mjs` ensures 100% integrity.

---

## Feature Inventory

Every requirement and survey finding is mapped directly to a milestone:

| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | SSS Schema Support | Add `subsurfaceWeight`, `subsurfaceRadius`, `subsurfaceScale` to `schemas/design-tokens.schema.json` | M1 | Survey 3 |
| 2 | SSS Tissue Shaders in Kit | Implement Blender 4.2 Principled BSDF Subsurface Scattering in `edu_asset_kit.py:add_tissue_material` | M1 | Survey 3 |
| 3 | Shared Spline Tube Utility | Add robust manifold `create_smooth_tube` / `smooth_tube_object` to `edu_asset_kit.py` | M1 | Survey 1, 3 |
| 4 | Biological Tissue Tokens | Register tissue material presets (`tissueMuscle`, `tissueOrgan`, `tissueNerve`, etc.) in `visual/design-tokens.json` | M1 | Survey 1, 3 |
| 5 | Metadata Alignment | Fix obsolete `provenance.generator` and method paths across `asset.json` files | M1 | Survey 1, 3 |
| 6 | Web Asset Sync Tool | Create `tools/sync-web-assets.mjs` to keep `apps/interactive-viewer/public/assets/` synchronized with `out/*.glb` | M1 | Survey 3 |
| 7 | Heart Internal Anatomy | Model 4 distinct chambers (RA, LA, RV, LV), septa, tricuspid/bicuspid/semilunar valves in coronal cutaway | M2 | Request R2, Survey 1 |
| 8 | Heart Vessels & Manifold Ends | Correct vena cava / aorta / pulmonary attachments; cap open ends to eliminate 508 non-manifold edges | M2 | Request R2, Survey 1 |
| 9 | Eye 3-Layer Structure | Add choroid layer, transparent vitreous body, suspensory zonules of Zinn | M2 | Request R2, Survey 1 |
| 10 | Eye Iris & Aperture Pupil | Replace solid black cylinder token with true light-admitting aperture in iris | M2 | Request R2, Survey 1 |
| 11 | Brain Gyri & Sulci Detailing | Procedural noise displacement on cerebral cortex to form anatomically distinct gyri and sulci | M2 | Request R2, Survey 1 |
| 12 | Brainstem & Cerebellar Folia | Sculpt folia on cerebellum, C-shaped corpus callosum arch, realistic pons/medulla brainstem | M2 | Request R2, Survey 1 |
| 13 | Nephron Loop of Henle & Welding | Proper descending/ascending limbs, DCT macula densa contact, welded junctions eliminating 576 non-manifold edges | M3 | Request R2, Survey 1 |
| 14 | Respiratory Bronchial Tree & C-Rings | Cutaway/transparency on lungs revealing bronchial tree; C-shaped cartilaginous tracheal rings | M3 | Request R2, Survey 1 |
| 15 | Continuous Digestive Tract & Ducts | Continuous looping small intestine; continuous tract; hepatopancreatic duct convergence at duodenum | M3 | Request R2, Survey 1 |
| 16 | DNA Double Helix Geometry | Fix cylinder rotation so base pairs connect horizontally; apply skin modifier; major/minor grooves; sync colors | M3 | Survey 1 |
| 17 | Other Biology Topological Fixes | Fix non-manifold edges and degenerate geometries in excretory, stoma, pyramid, reflex-arc, neuron | M3 | Survey 1 |
| 18 | Diamond Lattice Crystallography | Invert child tetrahedral vectors ($\vec{d}_{\text{child}} = -\vec{d}_{\text{parent}}$) to form closed 6-membered chair rings | M4 | Survey 2 |
| 19 | Graphite Planar Hexagonal Lattice | Correct 2D hexagonal lattice coordinates to generate planar graphene sheets with 3-coordinated carbons | M4 | Survey 2 |
| 20 | Hydrogen Evolution Delivery Tube | Replace disjoint 90° cylinders with smooth continuous bent glass tube | M4 | Survey 2 |
| 21 | Dropper Glass Wall Thickness | Add inner return wall to lathe profile for physical wall thickness and correct refraction | M4 | Survey 2 |
| 22 | Atom Electron Styling Unification | Unify electron colors and orbital visuals between magnesium-atom and oxygen-atom | M4 | Survey 2 |
| 23 | Chemistry Materials Polish | Glass transmission with volume absorption, liquid meniscus, multi-zone bunsen flame | M4 | Request R3, Survey 2 |
| 24 | Full Circuit Physics Consistency | Ensure bulb filament emits light only when knife switch is closed ($I = V/R$) | M5 | Survey 2 |
| 25 | DC Motor Split-Ring Commutator | Semicircular split rings with insulation gap and contact brushes | M5 | Survey 2 |
| 26 | Glass Slab Emergent Rays & Pins | Refraction pins (P1-P4) and ray paths for CBSE Class 10 glass slab demonstration | M5 | Survey 2 |
| 27 | Optics & Physics Materials | Crown glass IOR (1.52), metallic conductors, realistic meter dials and coil windings | M5 | Request R3, Survey 2 |
| 28 | Headless Batch Generation | Headless execution of all updated build scripts generating `.blend`, `.glb`, and `preview.png` | M6 | Request R4 |
| 29 | Full Schema & Catalog Validation | Pass `node tools/validate.mjs` with 0 errors across all 57 assets | M6 | Request System Validation |
| 30 | Downstream Web Sync | Copy all production `.glb` assets to `apps/interactive-viewer/public/assets/` | M6 | Survey 3 |
| 31 | Full E2E Test Suite (Tiers 1-4) | Comprehensive requirement-driven opaque-box test suite verifying all 57 assets and pipeline | M6 | Dual Track / Original Request |
| 32 | Adversarial Hardening (Tier 5) | White-box stress-testing, mesh integrity audit, and Forensic Audit verification | M6 | Project Pattern Phase 2 |

---

## Milestones

| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Pipeline & Shared Primitives Infrastructure | SSS schema, `edu_asset_kit.py` SSS & tube utilities, `design-tokens.json`, metadata alignment, web sync tool | none | DONE |
| M2 | Biology Core Anatomical Systems Part A | `human-heart`, `human-eye`, `brain` procedural scripts, meshes, and materials | M1 | DONE |
| M3 | Biology Core Anatomical Systems Part B & Microscopic | `nephron`, `human-respiratory-system`, `digestive-system`, `dna-double-helix`, other biology fixes | M1 | DONE |
| M4 | Chemistry Apparatus & Molecular Lattices | `diamond-lattice`, `graphite-lattice`, `hydrogen-evolution-apparatus`, `dropper`, atoms, glassware shaders | M1 | DONE |
| M5 | Physics Apparatus & Demonstration Models | `full-circuit`, `electric-motor`, `glass-slab`, optics, circuit components | M1 | DONE |
| M6 | E2E Integration, Multi-Format Generation & Victory Audit | Run headless builds, sync web assets, pass `node tools/validate.mjs` 0 errors, pass 100% E2E tests, Tier 5 audit | M2, M3, M4, M5 | IN_PROGRESS |

---

## Interface Contracts

### 1. `edu_asset_kit.py` Shared Library
```python
def create_smooth_tube(name, points, radius=0.003, resolution=16, material=None, cap_ends=True):
    """Generates a smooth 3D bevel tube from 3D spline control points.
    If cap_ends is True, caps endpoints with manifold hemispherical or planar geometry."""

def add_tissue_material(name, base_color=(0.85, 0.25, 0.25, 1.0), roughness=0.35,
                        subsurface_weight=0.3, subsurface_radius=(1.0, 0.2, 0.1), subsurface_scale=0.02):
    """Creates a Principled BSDF material configured for biological tissue with Subsurface Scattering
    compatible with Blender 4.2 LTS sockets."""
```

### 2. `visual/design-tokens.json` & `schemas/design-tokens.schema.json`
```json
"properties": {
  "subsurfaceWeight": { "type": "number", "minimum": 0.0, "maximum": 1.0 },
  "subsurfaceRadius": { "type": "array", "items": { "type": "number" }, "minItems": 3, "maxItems": 3 },
  "subsurfaceScale": { "type": "number", "minimum": 0.0 }
}
```

### 3. Headless Build Execution Contract
Every asset `assets/<category>/<asset-id>/build_<name>.py` must execute via:
```bash
blender -b -P assets/<category>/<asset-id>/build_<name>.py
```
Outputs produced deterministically in `assets/<category>/<asset-id>/out/`:
- `<asset-id>.blend` (non-empty production Blender scene)
- `<asset-id>.glb` (web-ready glTF 2.0 binary)
- `preview.png` (high-resolution rendered preview)

### 4. Downstream Web Sync Contract
```bash
node tools/sync-web-assets.mjs
```
Copies `assets/**/out/*.glb` into `apps/interactive-viewer/public/assets/*.glb`.

---

## Code Layout

- `assets/python/edu_asset_kit.py`: Shared Blender procedural library (Owned by M1)
- `schemas/design-tokens.schema.json`: Schema for design tokens (Owned by M1)
- `visual/design-tokens.json`: Design token values (Owned by M1)
- `tools/sync-web-assets.mjs`: Automated asset sync tool (Owned by M1)
- `assets/biology/human-heart/*`: Heart asset files (Owned by M2)
- `assets/biology/human-eye/*`: Eye asset files (Owned by M2)
- `assets/biology/brain/*`: Brain asset files (Owned by M2)
- `assets/biology/nephron/*`: Nephron asset files (Owned by M3)
- `assets/biology/human-respiratory-system/*`: Respiratory asset files (Owned by M3)
- `assets/biology/digestive-system/*`: Digestive asset files (Owned by M3)
- `assets/biology/dna-double-helix/*`: DNA asset files (Owned by M3)
- `assets/biology/human-excretory-system/*`, `stoma/*`, `trophic-level-pyramid/*`: (Owned by M3)
- `assets/chemistry/diamond-lattice/*`: Diamond asset files (Owned by M4)
- `assets/chemistry/graphite-lattice/*`: Graphite asset files (Owned by M4)
- `assets/chemistry/hydrogen-evolution-apparatus/*`: Hydrogen asset files (Owned by M4)
- `assets/chemistry/dropper/*`: Dropper asset files (Owned by M4)
- `assets/chemistry/magnesium-atom/*`, `oxygen-atom/*`: Atomic asset files (Owned by M4)
- `assets/physics/full-circuit/*`: Circuit asset files (Owned by M5)
- `assets/physics/electric-motor/*`: Motor asset files (Owned by M5)
- `assets/physics/glass-slab/*`: Glass slab asset files (Owned by M5)
- `tests/e2e/*`: E2E test suite (Owned by E2E Testing Track)
