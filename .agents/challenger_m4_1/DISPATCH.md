# Dispatch — Challenger M4-1

## Mission
Empirical mesh topology and manifoldness verification for Milestone 4 (Chemistry Apparatus & Molecular Lattices).

## Mandatory Reading
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md`

## Challenge Tasks
1. Write and execute a Python script inspecting Blender `.blend` files in headless mode (`blender -b <file> --python-expr ...`):
   - Check all modified chemistry assets: `diamond-lattice`, `graphite-lattice`, `hydrogen-evolution-apparatus`, `dropper`, `magnesium-atom`, `oxygen-atom`, `bunsen-burner`, `beaker`, `conical-flask`, `watch-glass`, `magnesium-burning-setup`.
   - Calculate non-manifold edge counts via BMesh:
     Every modified asset must have **strictly 0 non-manifold edges**.
2. Empirically verify:
   - In `diamond-lattice.blend`, check that bonds connect atoms into closed 6-membered cycles.
   - In `graphite-lattice.blend`, check planar coordinates and ABAB spacing.
   - In `dropper.blend`, check lathe geometry is solid (manifold).
3. Run `node tools/validate.mjs` and `node tests/e2e/run_all_tests.mjs --milestone M4`.
4. Issue an explicit verdict (APPROVE or REQUEST_CHANGES) with empirical evidence in `/home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_1/handoff.md`.
5. Send a message to the caller with your verdict.

## 2026-09-09T13:13:20Z
You are Challenger M4-1.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_1/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md.

Empirically verify mesh topology and non-manifold edge counts across all Milestone 4 chemistry assets in Blender:
1. Run a headless Blender python script inspecting .blend files in assets/chemistry/*/out/*.blend for non-manifold edges.
2. Verify that non-manifold edge count is strictly 0 across all modified assets.
3. Run `node tools/validate.mjs` and `node tests/e2e/run_all_tests.mjs --milestone M4`.
4. Issue an explicit verdict (APPROVE or REQUEST_CHANGES) with empirical data in /home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_1/handoff.md.
5. Send a message to the caller with your verdict.
