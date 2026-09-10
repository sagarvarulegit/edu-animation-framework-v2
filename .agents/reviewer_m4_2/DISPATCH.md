# Dispatch — Reviewer M4-2

## Mission
Independent and adversarial review of Milestone 4 (Chemistry Apparatus & Molecular Lattices).

## Mandatory Reading
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md`

## Review Tasks
1. Adversarial edge case inspection:
   - Check whether `diamond-lattice` actually closes rings without dangling non-bonded vertices.
   - Check `graphite-lattice` strictly maintains z-variance = 0 on layers and layer_gap / bond_r > 2.0.
   - Check `hydrogen-evolution-apparatus` continuous tube has non-zero bore radius and passes through stopper into flask.
   - Check `dropper` has genuine physical wall thickness ($r_{\text{outer}} > r_{\text{inner}} > 0$).
   - Check `bunsen-burner` flame has genuine dual cones with emission colors and strengths matching design tokens.
2. Run validation and tests:
   - `node tools/validate.mjs`
   - `node tests/e2e/run_all_tests.mjs --milestone M4`
   - `node tests/e2e/run_all_tests.mjs`
3. Verify headless builds and manifoldness (0 non-manifold edges).
4. Record your explicit verdict (APPROVE or REQUEST_CHANGES) in `/home/sagarv/Projects/edu-animation-framework-v2/.agents/reviewer_m4_2/handoff.md`.
5. Send a message to the caller with your verdict.

## 2026-09-09T13:13:20Z
You are Reviewer M4-2.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/reviewer_m4_2/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4/handoff.md.

Review Milestone 4 independently and adversarially:
1. Check edge cases, boundaries, dropper wall thickness, diamond chair rings, graphite z-variance, and bunsen flame cones.
2. Run `node tools/validate.mjs` and `node tests/e2e/run_all_tests.mjs --milestone M4` and `node tests/e2e/run_all_tests.mjs`.
3. Issue an explicit verdict (APPROVE or REQUEST_CHANGES) with rationale in /home/sagarv/Projects/edu-animation-framework-v2/.agents/reviewer_m4_2/handoff.md.
4. Send a message to the caller with your verdict.

