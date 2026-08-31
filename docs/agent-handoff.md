# AI Agent Handoff Guide

This repository is designed for multiple AI coding agents.

## First action

Read:

1. `AGENTS.md`
2. `README.md`

Then inspect the current repository.

## Never assume

Do not assume:

- Blender is the only renderer;
- every lesson needs Blender;
- every object needs a new model;
- a generated scene is visually correct;
- scientific details can be inferred;
- the previous agent implemented the ideal architecture.

## Before editing

Answer internally:

- What is the current architecture?
- Which files own this behavior?
- Can an existing primitive be reused?
- Is this lesson-specific or framework-level?
- Does this change affect other renderers?

## After editing

Run appropriate validation and document:

- what changed;
- what was tested;
- what was visually inspected;
- known limitations;
- what should happen next.

## If blocked

Do not invent a workaround that silently changes educational meaning.

Document the blocker and propose alternatives.

## If replacing an implementation

Preserve behavior unless the task explicitly changes behavior.

Do not perform unrelated refactors.

## Visual work

For visual changes, code execution is insufficient.

Generate a preview if possible and inspect:

- composition;
- framing;
- readability;
- scientific interpretation;
- animation timing;
- materials;
- lighting.

## Scientific work

When a lesson involves:

- equations;
- reactions;
- measurements;
- physical laws;
- biological processes;

validate the content against reliable sources where necessary.

If a simplification is used, document it.

## Current State & Handoff Summary (2026-08-31)

### Completed:
- Full 3-mode architecture fully functional:
  1. **Mode A (Interactive 3D)**: `apps/interactive-viewer` running Three.js / React Three Fiber with 36 assets in 3D Studio Inspector + Virtual Lab Game World (FPS exploration between optics, chemistry, biology stations).
  2. **Mode B (Cinematic 3D)**: Blender 4.2 LTS headless automation pipeline in `renderers/blender/render_scene.py` and `assets/*/*/build_*.py` generating deterministic `.blend`, `.glb`, and Cycles preview renders.
  3. **Mode C (Video Composer)**: `apps/video-composer` Remotion studio with 88s CBSE Class 10 Chemistry Burning of Magnesium Ribbon lesson (Intro Title, 3D lab setup, flame heating, dazzling combustion, Bohr atom electron transfer diagram, balanced equation with KaTeX, outro recap, and synchronized karaoke captions).
- **Open Knowledge Format (OKF v0.2)**: 23 verified concepts across Physics, Chemistry, Biology, and NCERT curriculum with provenance, citations, equations, and misconception traps.
- **Node.js 18 Compatibility**: Migrated web apps to stable `vite@^6.2.0` and `@vitejs/plugin-react@^4.3.4`, verifying 100% clean builds with `tsc -b && vite build`.
- **Validation**: Zero schema/lint errors via `node tools/validate.mjs` checking design tokens, 36 assets, 12 scene plans, 23 OKF concepts, and 3 lessons.

### Validation Commands:
- `node tools/validate.mjs` / `npm test`
- `node tools/okf/compile-okf.mjs`
- `npm run build --prefix apps/interactive-viewer`
- `npm run build --prefix apps/video-composer`
- `blender --background --python assets/chemistry/bunsen-burner/build_bunsen_burner.py`

### Next Recommended Steps:
- Add additional CBSE chapters (e.g., Electricity circuits, Optics lens refraction) to the video composer suite as new master compositions.
- Expand interactive physics simulations (e.g., Ohm's law circuit builder) in the Interactive Viewer.

