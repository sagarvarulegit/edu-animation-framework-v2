# 3dviz-pro-max Integration Design Specification

**Date**: 2026-10-07  
**Status**: Draft / Pending Review  
**Context**: CBSE Educational Animation Framework (`edu-animation-framework-v2`)

---

## 1. Executive Summary & Problem Context

The Educational Animation Framework requires rigorous scientific accuracy, visual fidelity, and clean separation between Blender cinematic rendering and Three.js interactive applications. 

[`viettranx/3dviz-pro-max`](https://github.com/viettranx/3dviz-pro-max) is an open-source agent skill and knowledge system providing:
- 223 domain recipes and 440 knowledge records with calibrated numeric defaults.
- A formalized Blender-to-Three.js handoff architecture.
- An empirical, headless GPU frame capture and view-quality inspection harness (evaluating contrast, clipping, and motion).

Currently in `edu-animation-framework-v2`:
1. Agent sessions lack a unified 3D visualization and spatial reasoning skill for procedural geometries and PBR materials.
2. The existing capture script ([`tools/capture_viewport.mjs`](../../tools/capture_viewport.mjs)) has a hardcoded Linux Google Chrome path (`/usr/bin/google-chrome`), preventing visual regression testing on Windows.
3. Complex scientific visualizations (e.g. crystal lattices, unit cells, ray optics) are authored ad-hoc rather than inheriting structured physical/material knowledge records.

This project integrates `3dviz-pro-max` into the framework in three structured, sequential phases.

---

## 2. Goals & Non-Goals

### Goals
- **G1**: Install `3dviz-pro-max` as a fully operational local agent skill in `.agents/skills/3dviz-pro-max`, with functional Python search and resolution scripts on Windows.
- **G2**: Upgrade framework visual validation with a cross-platform (Windows & Linux) headless Chromium capture harness (`tools/capture.py`) capable of computing view-quality metrics (luminance, contrast, wall collisions).
- **G3**: Mine relevant domain recipes (Molecules & Materials, Physical Optics, Circuits, PBR Lighting Profiles) into Open Knowledge Format (OKF) concepts and framework asset tokens.
- **G4**: Ensure all existing tests (`node tools/validate.mjs`) continue to pass with zero regressions.

### Non-Goals
- **NG1**: Replacing the core OKF compiler or lesson schema. `3dviz-pro-max` serves as an authoring skill and verification harness, not a replacement for our semantic lesson pipeline.
- **NG2**: Modifying working Blender scene files or rewriting existing asset geometry unless specifically targeted in Phase 3.

---

## 3. Phased Architectural Roadmap

```mermaid
flowchart TD
    subgraph Phase 1: Skill Installation
        A1["Clone/Download 3dviz-pro-max"] --> A2["Populate .agents/skills/3dviz-pro-max"]
        A2 --> A3["Verify Python CLI scripts on Windows"]
    end

    subgraph Phase 2: Frame Capture Harness
        B1["Port capture.py & capture_view_quality.py"] --> B2["Configure Windows ANGLE D3D11"]
        B2 --> B3["Expose npm run test:visual & integrate into validation"]
    end

    subgraph Phase 3: Science & Material Mining
        C1["Extract Molecular Lattices & Lighting Records"] --> C2["Map to OKF concepts & visual/design-tokens.json"]
        C2 --> C3["Verify with node tools/validate.mjs"]
    end

    Phase 1 --> Phase 2 --> Phase 3
```

---

## 4. Phase Detailed Specifications

### Phase 1: Skill Installation & Tooling (`.agents/skills/3dviz-pro-max`)

* **Target Directory**: `.agents/skills/3dviz-pro-max/`
* **Artifacts**:
  - `SKILL.md`: Main instructions and workflow contract.
  - `data/`:
    - `catalog-summary.json`: Index of all 223 recipes, 440 records, 24 directions.
    - `catalog-knowledge/`: Structured JSON records containing calibrated defaults.
    - `catalog-directions/`: Direction taxonomies.
  - `scripts/`:
    - `search.py`: Lexical and semantic query engine over records and recipes.
    - `resolve.py`: Record resolver printing applicability, limits, and defaults.
    - `catalog.py`: Catalog inspection CLI.
    - `design-context.py`: Scene design context synthesizer.
    - `host-probe.py`: Tool and environment discovery (Blender, Three.js, GPU).
  - `references/`:
    - `blender-threejs-handoff.md`: PBR material parity, baking, and modifier management.
    - `research-and-truth.md`: Fact-checking guidelines for educational visualization.
    - `lighting-direction-and-scale.md`: Calibrated light ratios and camera conventions.
    - `object-craft.md`: Surface continuity and silhouette guidelines.

### Phase 2: Frame Capture & View-Quality Verification Harness

* **Target Directory**: `tools/`
* **Components**:
  - `tools/capture.py`: Headless browser frame capture with ANGLE GPU flags (`--use-angle=d3d11` on Windows, `--use-angle=gl` on Linux).
  - `tools/capture_view_quality.py`: Image metric analysis checking:
    - Under-exposure / near-black frames.
    - Camera near-plane clipping (wall occlusion).
    - Contrast distribution and frame variance.
    - Motion diff between subsequent animation ticks.
  - Script update or replacement for `tools/capture_viewport.mjs` ensuring cross-platform support via Playwright or Puppeteer with dynamic browser discovery.
* **Testing Command**: Added to `package.json` as `npm run test:visual`.

### Phase 3: Science Pipeline & Knowledge Integration

* **Target Concepts**:
  - **Chemistry**: Ionic vs covalent representations, crystal lattices (Magnesium Oxide rock-salt lattice [NaCl structure], Diamond/Graphite allotropes).
  - **Physics**: Light ray refraction in prisms, lens conventions, circuit schematic-to-3D representation.
  - **Visual System**: PBR token refinement in `visual/design-tokens.json` (metallic, roughness, laboratory glass transmission, Bunsen flame emissive values).
* **Validation**: Run `node tools/validate.mjs` to ensure OKF concepts, asset schemas, and token definitions validate cleanly.

---

## 5. Risk Assessment & Mitigations

| Risk | Impact | Mitigation |
| :--- | :--- | :--- |
| Missing Python dependencies for Playwright | Phase 2 capture fails | Script provides clear diagnostic message and fallback to software renderer / existing node tools. |
| Path separator issues on Windows (`\` vs `/`) | Scripts fail in PowerShell | All python scripts in `3dviz-pro-max` use `pathlib.Path` with POSIX normalizations. |
| Incompatible schema changes | Schema tests fail | No existing schemas in `schemas/` will be altered without corresponding updates in `validate.mjs`. |

---

## 6. Success Criteria

1. `python .agents/skills/3dviz-pro-max/scripts/search.py "crystal lattice"` returns relevant records with zero errors.
2. `tools/capture.py` captures a rendered 3D viewport on Windows without Linux path errors.
3. `node tools/validate.mjs` passes with 0 errors across all 57 assets and 44 OKF concepts.
4. All work committed and pushed to git remote origin per workspace conventions.
