/**
 * tests/e2e/tier4_real_world.test.mjs
 * Tier 4: Real-World Application Scenarios (Pipeline Execution & Delivery Readiness)
 * Runs end-to-end integration checks: validator execution, Python compilation, glTF verification.
 */

import { execSync } from 'node:child_process';
import { readFileSync, existsSync, statSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  ROOT_DIR,
  registerTest,
  assert,
  assertEqual,
  assertGreaterThan,
  assertFileExists,
  readJson,
  getAssets
} from './harness.mjs';

// Feature 28 (M6): Python Compilation of All 57 Build Scripts
registerTest({
  name: 'Headless Pipeline Readiness: all 57 build_*.py scripts compile cleanly in Python',
  tier: 4,
  feature: 28,
  milestone: 'M6',
  fn: async () => {
    const assets = getAssets();
    assertEqual(assets.length, 57, `Expected 57 assets, found ${assets.length}`);

    const syntaxErrors = [];

    for (const a of assets) {
      const files = readdirSync(a.dir);
      const buildScripts = files.filter(f => f.startsWith('build_') && f.endsWith('.py'));
      assert(buildScripts.length >= 1, `Asset ${a.id} missing build script`);

      for (const bs of buildScripts) {
        const fullPath = join(a.dir, bs);
        try {
          execSync(`python3 -m py_compile "${fullPath}"`, { stdio: 'pipe' });
        } catch (err) {
          syntaxErrors.push(`${a.id}/${bs}: ${err.message}`);
        }
      }
    }

    assertEqual(
      syntaxErrors.length,
      0,
      `Python syntax compilation errors:\n${syntaxErrors.join('\n')}`
    );
  }
});

// Feature 28 (M6): Shared Edu Asset Kit Compilation
registerTest({
  name: 'Edu Asset Kit Readiness: assets/python/edu_asset_kit.py compiles cleanly in Python',
  tier: 4,
  feature: 28,
  milestone: 'M6',
  fn: async () => {
    const kitPath = join(ROOT_DIR, 'assets/python/edu_asset_kit.py');
    assertFileExists(kitPath);
    try {
      execSync(`python3 -m py_compile "${kitPath}"`, { stdio: 'pipe' });
    } catch (err) {
      assert(false, `edu_asset_kit.py syntax error: ${err.message}`);
    }
  }
});

// Feature 28 (M6): Blender CLI Host Availability
registerTest({
  name: 'Blender Environment: blender CLI is available and reports Blender 4.2 LTS',
  tier: 4,
  feature: 28,
  milestone: 'M6',
  fn: async () => {
    let output = '';
    try {
      output = execSync('blender --version', { stdio: 'pipe', encoding: 'utf-8' });
    } catch (err) {
      assert(false, `Blender CLI invocation failed: ${err.message}`);
    }
    assert(output.includes('Blender 4.2'), `Expected Blender 4.2, got: ${output.split('\n')[0]}`);
  }
});

// Feature 29 (M6): Full Schema & Catalog Validator Execution
registerTest({
  name: 'Framework Validation: node tools/validate.mjs passes with 0 errors across entire workspace',
  tier: 4,
  feature: 29,
  milestone: 'M6',
  fn: async () => {
    let output = '';
    try {
      output = execSync('node tools/validate.mjs', {
        cwd: ROOT_DIR,
        stdio: 'pipe',
        encoding: 'utf-8'
      });
    } catch (err) {
      assert(false, `tools/validate.mjs failed:\n${err.stdout || ''}\n${err.stderr || ''}`);
    }
    assert(output.includes('Validation passed'), `Validation did not pass:\n${output}`);
  }
});

// Feature 30 (M6): Production Binary Output Integrity Audit (All 57 Assets)
registerTest({
  name: 'Production Delivery Audit: all 57 assets possess verified non-empty .blend, .glb, and preview.png',
  tier: 4,
  feature: 30,
  milestone: 'M6',
  fn: async () => {
    const assets = getAssets();
    const failures = [];

    for (const a of assets) {
      const blendPath = join(a.dir, 'out', `${a.id}.blend`);
      const glbPath = join(a.dir, 'out', `${a.id}.glb`);
      const previewPath = join(a.dir, 'out', 'preview.png');

      // Check blend
      if (!existsSync(blendPath) || statSync(blendPath).size < 1000) {
        failures.push(`${a.id}: missing or degenerate .blend (< 1KB)`);
      } else {
        const buf = readFileSync(blendPath);
        if (buf.toString('ascii', 0, 7) !== 'BLENDER') {
          failures.push(`${a.id}: .blend invalid header signature`);
        }
      }

      // Check glb
      if (!existsSync(glbPath) || statSync(glbPath).size < 1000) {
        failures.push(`${a.id}: missing or degenerate .glb (< 1KB)`);
      } else {
        const buf = readFileSync(glbPath);
        if (buf.toString('ascii', 0, 4) !== 'glTF') {
          failures.push(`${a.id}: .glb invalid glTF signature`);
        }
      }

      // Check preview.png
      if (!existsSync(previewPath) || statSync(previewPath).size < 1000) {
        failures.push(`${a.id}: missing or degenerate preview.png (< 1KB)`);
      } else {
        const buf = readFileSync(previewPath);
        if (buf[0] !== 0x89 || buf.toString('ascii', 1, 4) !== 'PNG') {
          failures.push(`${a.id}: preview.png invalid PNG signature`);
        }
      }
    }

    assertEqual(
      failures.length,
      0,
      `Asset output integrity failures found (${failures.length} issues):\n${failures.join('\n')}`
    );
  }
});

// Feature 30 (M6): Interactive Viewer Asset Loading Readiness
registerTest({
  name: 'Interactive Viewer Readiness: all 57 glb models present in public/assets with valid glTF headers',
  tier: 4,
  feature: 30,
  milestone: 'M6',
  fn: async () => {
    const assets = getAssets();
    const webAssetsDir = join(ROOT_DIR, 'apps/interactive-viewer/public/assets');
    const invalidFiles = [];

    for (const a of assets) {
      const webGlb = join(webAssetsDir, `${a.id}.glb`);
      if (!existsSync(webGlb)) {
        invalidFiles.push(`${a.id}: missing in public/assets`);
        continue;
      }
      const buf = readFileSync(webGlb);
      if (buf.length < 12 || buf.toString('ascii', 0, 4) !== 'glTF') {
        invalidFiles.push(`${a.id}: corrupted glTF binary in public/assets`);
      }
    }

    assertEqual(
      invalidFiles.length,
      0,
      `Web public assets corrupted or missing:\n${invalidFiles.join('\n')}`
    );
  }
});
