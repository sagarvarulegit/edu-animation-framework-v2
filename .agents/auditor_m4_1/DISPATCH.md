# Dispatch — Forensic Auditor M4-1

## Mission
Forensic integrity audit for Milestone 4 (Chemistry Apparatus & Molecular Lattices).

## Mandatory Reading
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md`

## Forensic Audit Tasks
1. Verify genuine logic vs hardcoded test strings or dummy facade implementations:
   - Check `build_diamond_lattice.py`: Does it genuinely calculate and place atoms and bonds via BFS and vectors, or does it mock results?
   - Check `build_graphite_lattice.py`: Does it genuinely construct planar Bravais lattices and Bernal stacking?
   - Check `build_hydrogen_evolution.py` & `build_hydrogen_apparatus.py`: Does it authentically construct a continuous smooth delivery tube, flask, and thistle funnel?
   - Check `build_dropper.py`: Does it authentically revolve a 2D closed polygon with positive thickness?
   - Check `build_magnesium_atom.py` & `build_oxygen_atom.py`: Does it authentically place nucleons and concentric electron shells?
   - Check `build_bunsen_burner.py`: Does it authentically close profiles and add dual flame cones?
2. Verify test integrity:
   - Check `tests/e2e/tiers/` and `tests/e2e/run_all_tests.mjs`: Are the tests genuinely inspecting the generated `.blend`, `.glb`, or script code, or are they trivial passes?
3. Verify asset integrity:
   - Check `node tools/sync-web-assets.mjs` and verify sha256 sums match between source and destination GLBs.
   - Verify Blender builds exit 0 and produce non-empty files.
4. Report an explicit binary verdict: **CLEAN** or **INTEGRITY VIOLATION** with full evidence in `/home/sagarv/Projects/edu-animation-framework-v2/.agents/auditor_m4_1/handoff.md`.
5. Send a message to the caller with your verdict and evidence.

## 2026-09-09T13:13:21Z
You are the Forensic Auditor for Milestone 4.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/auditor_m4_1/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md.

Perform a forensic integrity audit on Milestone 4:
1. Verify authentic procedural synthesis without hardcoding, facade mocks, or shortcuts across all modified chemistry assets.
2. Check that E2E tests genuinely evaluate real assets and scripts.
3. Check web asset sync parity and zero non-manifold edges.
4. Report an explicit binary verdict: CLEAN or INTEGRITY VIOLATION with full evidence in /home/sagarv/Projects/edu-animation-framework-v2/.agents/auditor_m4_1/handoff.md.
5. Send a message to the caller with your verdict.
