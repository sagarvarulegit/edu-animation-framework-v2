# E2E Test Writer Dispatch

## Mission: Build Comprehensive Requirement-Driven E2E Test Suite
You are the E2E Test Writer. Your mission is to create a complete, requirement-driven, opaque-box test suite for the educational animation framework, covering all 32 features inventoried in `PROJECT.md § Feature Inventory` across Tiers 1–4.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/test_writer_e2e`

### Authoritative Files
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_3/survey_pipeline.md`

### Deliverables
1. `TEST_INFRA.md` at project root:
   - Document test philosophy, architecture, runner invocation, pass/fail semantics.
   - Map all features to test cases across Tiers 1-4.
2. Test Suite Implementation:
   - Create tests under `tests/e2e/` (e.g. Node.js test runner `tests/e2e/run_all_tests.mjs` or separate test scripts).
   - The test suite must be runnable via a single deterministic command (e.g. `node tests/e2e/run_all_tests.mjs`).
   - Test Tiers:
     - Tier 1: Feature Coverage (verify presence, structural correctness, output files, schema validity for all features).
     - Tier 2: Boundary & Corner Cases (missing files, malformed fields, zero-thickness/degenerate dimensions, non-manifold checks, invalid rotations).
     - Tier 3: Cross-Feature Combinations (e.g. asset.json metadata matching build_*.py outputs, design token color codes matching build script shaders, web sync directory parity).
     - Tier 4: Real-World Application Scenarios (verify headless generation pipeline, schema validator passes 0 errors, interactive viewer asset readiness).
3. `TEST_READY.md` at project root:
   - Published once the test harness and test cases are verified and runnable.
   - Contains exact test runner command, tier breakdown table, and feature checklist.
4. Working memory: `progress.md` and `handoff.md` in your directory.

## 2026-09-09T02:57:04Z
You are the E2E Test Writer.
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/test_writer_e2e/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, and /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md.

Your objective:
1. Create TEST_INFRA.md at project root with test architecture, methodology, and feature mapping.
2. Build an automated requirement-driven test suite under tests/e2e/ covering Tiers 1-4 for all features in PROJECT.md.
3. Test your runner so it executes deterministically.
4. Publish TEST_READY.md at project root once the test suite is ready.
5. Write progress.md and handoff.md in your working directory (/home/sagarv/Projects/edu-animation-framework-v2/.agents/test_writer_e2e).
6. Send a message to the caller when complete.
