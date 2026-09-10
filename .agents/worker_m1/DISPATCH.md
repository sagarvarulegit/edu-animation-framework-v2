# Worker M1 Dispatch

## Mission: Milestone 1 — Pipeline & Shared Primitives Infrastructure
You are Worker M1. Your mission is to implement the foundation utilities, schema extensions, token presets, metadata alignments, and web sync tool as specified in `PROJECT.md § Milestones` (Milestone 1).

### Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m1`

### Authoritative Context
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_3/handoff.md` and `survey_pipeline.md`

### Write Ownership (Exclusive to M1)
- `schemas/design-tokens.schema.json`
- `visual/design-tokens.json`
- `assets/python/edu_asset_kit.py`
- `tools/sync-web-assets.mjs`
- `assets/**/asset.json` (metadata alignment for generator paths)

### Tasks
1. **Design Tokens Schema & SSS Support**:
   - Update `schemas/design-tokens.schema.json` to allow `subsurfaceWeight` (0.0 to 1.0), `subsurfaceRadius` (array of 3 floats), and `subsurfaceScale` (float >= 0.0) in the `materials` definition.
2. **Biological Tissue Tokens**:
   - Register realistic biological tissue presets in `visual/design-tokens.json` (e.g. `tissueMuscle`, `tissueOrgan`, `tissueNerve`, `tissueFat`, `tissueSclera`, `tissueRetina`, `tissueCortex`, `tissueBone`).
3. **`edu_asset_kit.py` Extensions**:
   - Implement `add_tissue_material(name, base_color, roughness=0.35, subsurface_weight=0.3, subsurface_radius=(1.0, 0.2, 0.1), subsurface_scale=0.02)` using Blender 4.2 LTS Principled BSDF SSS sockets (`Subsurface Weight`, `Subsurface Radius`, `Subsurface Scale`).
   - Implement `create_smooth_tube(name, points, radius=0.003, resolution=16, material=None, cap_ends=True)` that generates clean, manifold geometry from 3D spline points, capping endpoints cleanly.
4. **Metadata Alignment**:
   - Fix obsolete generator paths in `asset.json` for `brain`, `digestive-system`, `dna-double-helix`, `human-eye`, `human-heart`, `full-circuit` to point to their actual `build_*.py` scripts, and set `provenance.method` to `"procedural-blender-python"`.
5. **Web Asset Sync Tool**:
   - Create `tools/sync-web-assets.mjs` that finds all `assets/**/out/*.glb` and copies them to `apps/interactive-viewer/public/assets/*.glb`.
6. **Verification**:
   - Run `node tools/validate.mjs` to ensure 0 errors.
   - Run `node tools/sync-web-assets.mjs` to verify synchronization.
   - Test `edu_asset_kit.py` extensions with Blender CLI.
   - Document results in `handoff.md`.

## 2026-09-09T02:57:04Z
You are Worker M1.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m1/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, and /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 1 (Pipeline & Shared Primitives Infrastructure):
1. Update schemas/design-tokens.schema.json for SSS fields.
2. Register biological tissue presets in visual/design-tokens.json.
3. Add add_tissue_material and create_smooth_tube to assets/python/edu_asset_kit.py.
4. Correct generator metadata and provenance in asset.json files.
5. Create tools/sync-web-assets.mjs.
6. Verify changes with `node tools/validate.mjs` (must pass with 0 errors).
7. Write progress.md and handoff.md in your directory (/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m1).
8. Send a message to the caller when complete.
