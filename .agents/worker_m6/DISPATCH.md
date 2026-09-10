# Dispatch Instructions — Worker M6 (Full Integration & Batch Generation)

## Mission
Execute Milestone 6 Phase 1: Full Pipeline Integration, Headless Multi-Format Batch Generation, Downstream Web Synchronization, Validation, E2E Testing, and Web Build Verification across all 57 assets in `edu-animation-framework-v2`.

## Mandatory References
1. `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md` (Read in full)
2. `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md` (Read in full)
3. `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md` (Update M5 and M6 status)
4. `/home/sagarv/Projects/edu-animation-framework-v2/TEST_READY.md` (Check test runner command and checklist)

## Mandatory Integrity Warning
> DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.
> Every command and output in your handoff must be reproduced verbatim from actual terminal execution. DO NOT invent file names or hashes.

## Tasks
1. **Update `PROJECT.md`**:
   - In `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`, update the Milestones table:
     - M5 status: `DONE`
     - M6 status: `IN_PROGRESS`
2. **Headless Batch Generation Across All 57 Assets**:
   - Locate and run headless Blender builds (`blender -b -P <build_script>`) for all 57 assets in the repository:
     - 14 Biology assets under `assets/biology/`
     - 21 Chemistry assets under `assets/chemistry/`
     - 22 Physics assets under `assets/physics/`
   - Ensure every asset has generated in its `out/` folder:
     - Non-empty `<asset-id>.blend`
     - Valid `<asset-id>.glb`
     - Non-empty `preview.png`
3. **Web Asset Synchronization**:
   - Run `node tools/sync-web-assets.mjs --force`.
   - Verify 100% SHA-256 and byte parity between `assets/**/out/*.glb` and `apps/interactive-viewer/public/assets/*.glb` for all 57 assets.
4. **Full Schema & Catalog Validation**:
   - Run `node tools/validate.mjs`
   - Must pass with strictly 0 errors across 57 assets, 44 OKF concepts, 3 lessons, and 12 scene plans.
5. **Full E2E Test Suite (Tiers 1-4)**:
   - Run `node tests/e2e/run_all_tests.mjs`
   - Must pass 64/64 tests (100% across all 4 tiers).
6. **Web Applications Production Build**:
   - Run `npm run build --prefix apps/interactive-viewer` (must build cleanly with Vite).
   - Run `npm run build --prefix apps/video-composer` (must build cleanly with Vite).
7. **Comprehensive BMesh Topology Audit**:
   - Execute a Blender Python audit script inspecting all `.blend` files across all 57 assets.
   - Confirm strictly 0 non-manifold edges AND 0 degenerate zero-area faces across all mesh objects in the entire project.
8. **Documentation & Handoff**:
   - In `.agents/worker_m6/handoff.md`, provide:
     - Complete table of all 57 assets (ID, Category, .blend status, .glb SHA-256, web sync status, mesh count, non-manifold edges, degenerate faces).
     - Verbatim terminal outputs from all verification commands.
     - Summary of results.

## 2026-09-09T18:18:53Z

You are Worker M6 (Full Integration, Batch Generation & Web Verification Specialist).
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m6/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/TEST_READY.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 6 Phase 1:
1. Update /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md milestones table: set M5 to DONE, and M6 to IN_PROGRESS.
2. Execute headless Blender builds (`blender -b -P <build_script>`) across all 57 assets in the repository, verifying non-empty .blend, .glb, and preview.png in out/ for each asset.
3. Run `node tools/sync-web-assets.mjs --force` and verify 100% SHA-256 and byte parity between production `assets/**/out/*.glb` and web delivery `apps/interactive-viewer/public/assets/*.glb` for all 57 assets.
4. Run `node tools/validate.mjs` (must pass 0 errors across 57 assets, 44 OKF concepts, 3 lessons, 12 scene plans).
5. Run `node tests/e2e/run_all_tests.mjs` (must pass 64/64 tests, 100% across Tiers 1-4).
6. Run `npm run build --prefix apps/interactive-viewer` and `npm run build --prefix apps/video-composer` (both must succeed cleanly with Vite).
7. Run a BMesh topology audit across all 57 .blend files confirming strictly 0 non-manifold edges AND 0 degenerate zero-area faces.
8. Write an authentic, genuine handoff report in /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m6/handoff.md with all 57 asset hashes, manifold statuses, and verbatim CLI execution outputs.
9. Send a message to the caller when complete.
