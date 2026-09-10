/**
 * Empirical Stress Test Harness for tools/sync-web-assets.mjs (Challenger M1-1)
 */

import { existsSync, mkdirSync, rmSync, writeFileSync, chmodSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import assert from 'node:assert';

const ROOT_DIR = resolve('.');
const SYNC_SCRIPT = join(ROOT_DIR, 'tools', 'sync-web-assets.mjs');
const REAL_TARGET = join(ROOT_DIR, 'apps', 'interactive-viewer', 'public', 'assets');

console.log('='.repeat(70));
console.log('RUNNING SYNC-WEB-ASSETS STRESS TESTS');
console.log('='.repeat(70));

const results = [];
function report(name, passed, details = '') {
  const status = passed ? 'PASS' : 'FAIL';
  console.log(`[${status}] ${name}`);
  if (details) console.log(`       Details: ${details}`);
  results.append ? results.append({ name, passed }) : results.push({ name, passed, details });
}

// Test S1: Baseline verification against real assets
{
  const res = spawnSync('node', [SYNC_SCRIPT, '--check'], { encoding: 'utf-8' });
  const passed = res.status === 0 && res.stdout.includes('Summary: Total found: 57');
  report('S1: Baseline check on real assets passes', passed, `status=${res.status}`);
}

// Test S2: Invalid GLB header handling
{
  const dummyDir = join(ROOT_DIR, 'assets', 'biology', 'dummy-corrupted-test-asset', 'out');
  mkdirSync(dummyDir, { recursive: true });
  const badGlb = join(dummyDir, 'dummy-corrupted-test-asset.glb');
  writeFileSync(badGlb, Buffer.from('NOT_A_VALID_GLB_FILE_HEADER'));

  try {
    const res = spawnSync('node', [SYNC_SCRIPT, '--check'], { encoding: 'utf-8' });
    const warned = res.stdout.includes('[WARN] Invalid GLB binary header') || res.stderr.includes('[WARN] Invalid GLB binary header');
    const exitCode1 = res.status === 1;
    report('S2: Corrupted GLB header flagged and causes non-zero exit', warned && exitCode1,
           `warned=${warned}, exit=${res.status}`);
  } finally {
    rmSync(join(ROOT_DIR, 'assets', 'biology', 'dummy-corrupted-test-asset'), { recursive: true, force: true });
  }
}

// Test S3: Truncated GLB (<12 bytes) handling
{
  const dummyDir = join(ROOT_DIR, 'assets', 'physics', 'dummy-truncated-test-asset', 'out');
  mkdirSync(dummyDir, { recursive: true });
  const badGlb = join(dummyDir, 'dummy-truncated-test-asset.glb');
  writeFileSync(badGlb, Buffer.from([0x67, 0x6c])); // only 2 bytes

  try {
    const res = spawnSync('node', [SYNC_SCRIPT, '--check'], { encoding: 'utf-8' });
    const exitCode1 = res.status === 1;
    report('S3: Truncated <12 bytes GLB file flagged and causes non-zero exit', exitCode1,
           `exit=${res.status}`);
  } finally {
    rmSync(join(ROOT_DIR, 'assets', 'physics', 'dummy-truncated-test-asset'), { recursive: true, force: true });
  }
}

// Test S4: Read-only destination file error handling
{
  // Pick one target asset to test permission failure
  const testDest = join(REAL_TARGET, 'battery.glb');
  if (existsSync(testDest)) {
    // Make target file read-only and touch source to force copy
    const srcPath = join(ROOT_DIR, 'assets', 'physics', 'battery', 'out', 'battery.glb');
    const origStat = readFileSync(srcPath);

    // Make target unwritable
    chmodSync(testDest, 0o444);
    try {
      // Append byte to src to force size mismatch and copy attempt
      writeFileSync(srcPath, Buffer.concat([origStat, Buffer.from([0x00])]));
      const res = spawnSync('node', [SYNC_SCRIPT], { encoding: 'utf-8' });
      const caughtError = res.stderr.includes('[ERROR] Failed to copy battery.glb') || res.stdout.includes('[ERROR] Failed to copy battery.glb');
      const exit1 = res.status === 1;
      report('S4: Read-only target file caught and triggers exit code 1', caughtError && exit1,
             `caught=${caughtError}, exit=${res.status}`);
    } finally {
      // Restore src and target permissions
      chmodSync(testDest, 0o644);
      writeFileSync(srcPath, origStat);
      // Resync to ensure clean state
      spawnSync('node', [SYNC_SCRIPT]);
    }
  } else {
    report('S4: Read-only target test', true, 'battery.glb not present in public, skipped');
  }
}

// Test S5: Non-existent destination directory behavior in --check vs normal sync
{
  const testScriptContent = readFileSync(SYNC_SCRIPT, 'utf-8');
  // Temporary test script pointing to a non-existent test target
  const tempTarget = join(ROOT_DIR, 'apps', 'interactive-viewer', 'public', 'assets_temp_stress_dir');
  if (existsSync(tempTarget)) rmSync(tempTarget, { recursive: true, force: true });

  const customScript = testScriptContent.replace(
    "join(ROOT_DIR, 'apps', 'interactive-viewer', 'public', 'assets')",
    `join(ROOT_DIR, 'apps', 'interactive-viewer', 'public', 'assets_temp_stress_dir')`
  );
  const tempScriptPath = join(ROOT_DIR, 'tools', 'sync-temp-test.mjs');
  writeFileSync(tempScriptPath, customScript);

  try {
    // In check mode: should fail with error
    const resCheck = spawnSync('node', [tempScriptPath, '--check'], { encoding: 'utf-8' });
    const checkFailed = resCheck.status === 1 && (resCheck.stderr.includes('Target directory does not exist') || resCheck.stdout.includes('Target directory does not exist'));

    // In normal sync mode: should create directory and copy
    const resSync = spawnSync('node', [tempScriptPath], { encoding: 'utf-8' });
    const dirCreated = existsSync(tempTarget);
    const syncPassed = resSync.status === 0;

    report('S5: Non-existent target directory (check fails, sync creates)', checkFailed && dirCreated && syncPassed,
           `checkFailed=${checkFailed}, dirCreated=${dirCreated}, syncPassed=${syncPassed}`);
  } finally {
    if (existsSync(tempTarget)) rmSync(tempTarget, { recursive: true, force: true });
    if (existsSync(tempScriptPath)) rmSync(tempScriptPath, { force: true });
  }
}

console.log('='.repeat(70));
const total = results.length;
const passed = results.filter(r => r.passed).length;
console.log(`SUMMARY: ${passed}/${total} passed (${total - passed} failed)`);
console.log('='.repeat(70));

if (total !== passed) {
  process.exit(1);
}
