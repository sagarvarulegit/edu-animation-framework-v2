# Dispatch — Challenger M4-2

## Mission
Empirical parameter testing, web synchronization verification, and curriculum fidelity challenge for Milestone 4.

## Mandatory Reading
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md`

## Challenge Tasks
1. Verify exact byte / SHA-256 parity between `assets/chemistry/*/out/*.glb` and `apps/interactive-viewer/public/assets/*.glb` for all modified chemistry assets (`diamond-lattice`, `graphite-lattice`, `hydrogen-evolution-apparatus`, `dropper`, `magnesium-atom`, `oxygen-atom`, `bunsen-burner`, `beaker`, `conical-flask`, `watch-glass`, `magnesium-burning-setup`).
2. Verify crystallographic and physical parameters:
   - Diamond C-C-C tetrahedral bond angle: compute vectors from vertex positions, confirm $\theta \approx 109.47^\circ$.
   - Graphite interlayer gap to bond length ratio > 2.0.
   - Dropper physical wall thickness: verify $r_{\text{outer}} - r_{\text{inner}} \ge 1.0\text{ mm}$.
   - Atomic model electron shells: verify radius sequence increases monotonically for Mg (2, 8, 2) and O (2, 6).
   - Glassware transmission: verify Principled BSDF Transmission Weight = 1.0, IOR = 1.52.
3. Run `node tools/validate.mjs` and `node tests/e2e/run_all_tests.mjs --milestone M4`.
4. Issue an explicit verdict (APPROVE or REQUEST_CHANGES) with empirical data in `/home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_2/handoff.md`.
5. Send a message to the caller with your verdict.

## 2026-09-09T13:13:20Z
You are Challenger M4-2.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_2/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md.

Empirically verify boundary parameters, web GLB synchronization, and curriculum accuracy:
1. Verify exact byte / SHA-256 parity between assets/chemistry/*/out/*.glb and apps/interactive-viewer/public/assets/*.glb for all modified chemistry assets.
2. Verify Diamond tetrahedral angle (~109.47 deg), Graphite interlayer ratio (>2.0), Dropper wall thickness (>=1.0 mm), and atom electron shell radii.
3. Run `node tools/validate.mjs` and `node tests/e2e/run_all_tests.mjs --milestone M4`.
4. Issue an explicit verdict (APPROVE or REQUEST_CHANGES) in /home/sagarv/Projects/edu-animation-framework-v2/.agents/challenger_m4_2/handoff.md.
5. Send a message to the caller with your verdict.
