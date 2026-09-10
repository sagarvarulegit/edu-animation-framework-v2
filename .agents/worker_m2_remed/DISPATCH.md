# Worker M2 Remediation Dispatch

## Mission: Milestone 2 Remediation (Iteration 2)
You are Worker M2 (Remediation). Your mission is to fix the issues identified by Reviewer 2 and Challenger 2 in Milestone 2 Gate Iteration 1.

### Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m2_remed`

### Issues to Fix (From GATE_STATUS.md)
1. **Fix `tools/sync-web-assets.mjs` caching logic**:
   - The script currently relies solely on `srcStat.size === destStat.size`.
   - Update it so that if sizes are equal, it compares modification times (`srcStat.mtimeMs > destStat.mtimeMs`) or compares file buffer hashes (e.g. SHA-256 or `fs.readFileSync(src).equals(fs.readFileSync(dest))`). If buffers differ or source is newer, copy the file.
   - Also add a `--force` flag to force-copy all files regardless of size/timestamp.
2. **Fix `assets/biology/human-heart/build_heart.py`**:
   - Wire `LV_WALL_THICKNESS` and `RV_WALL_THICKNESS` directly into the chamber cutter scaling and positioning math in `build_heart.py` so they are active functional parameters, not unused dead variables.
3. **Re-run Headless Build & Sync**:
   - Run `blender -b -P assets/biology/human-heart/build_heart.py`.
   - Run `node tools/sync-web-assets.mjs --force`.
   - Verify with `sha256sum`:
     `sha256sum assets/biology/human-heart/out/human-heart.glb apps/interactive-viewer/public/assets/human-heart.glb`
     Confirm that both hashes are 100% IDENTICAL.
4. **Validation**:
   - Run `node tools/validate.mjs` (must pass 0 errors).
   - Run `node tests/e2e/run_all_tests.mjs --milestone M2` (all 9 tests must pass).
   - Document changes and verification commands in `handoff.md`.


## 2026-09-09T07:54:22Z
You are Worker M2 (Remediation).
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m2_remed/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/orchestrator_1/GATE_STATUS.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
1. Fix tools/sync-web-assets.mjs (replace naive size check with buffer/hash comparison or mtime, add --force).
2. Wire LV_WALL_THICKNESS and RV_WALL_THICKNESS in assets/biology/human-heart/build_heart.py into the cutter math.
3. Re-run headless build for human-heart, run sync-web-assets.mjs, and verify sha256sum parity between out/human-heart.glb and apps/interactive-viewer/public/assets/human-heart.glb.
4. Run node tools/validate.mjs and node tests/e2e/run_all_tests.mjs --milestone M2.
5. Write progress.md and handoff.md in /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m2_remed.
6. Send a message to the caller when complete.
