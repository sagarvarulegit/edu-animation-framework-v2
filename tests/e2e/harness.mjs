/**
 * tests/e2e/harness.mjs
 * End-to-End Test Suite Harness & Assertion Engine
 * Designed for Node.js v18.19.1+ ESM without external dependencies.
 */

import { readFileSync, existsSync, statSync, readdirSync } from 'node:fs';
import { resolve, join, dirname, relative } from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
export const ROOT_DIR = resolve(__dirname, '../..');

export const testRegistry = [];

/**
 * Register a test case.
 * @param {Object} options
 * @param {string} options.name - Descriptive test name
 * @param {number} options.tier - 1, 2, 3, or 4
 * @param {number} options.feature - 1 to 32
 * @param {string} options.milestone - 'M1', 'M2', 'M3', 'M4', 'M5', 'M6'
 * @param {Function} options.fn - Async test function
 */
export function registerTest({ name, tier, feature, milestone, fn }) {
  if (!name || !tier || !feature || !milestone || typeof fn !== 'function') {
    throw new Error(`Invalid test registration: ${JSON.stringify({ name, tier, feature, milestone })}`);
  }
  testRegistry.push({ name, tier, feature, milestone, fn });
}

// ---------------------------------------------------------------------------
// Assertion Utilities
// ---------------------------------------------------------------------------

export class AssertionError extends Error {
  constructor(message, actual, expected) {
    super(message);
    this.name = 'AssertionError';
    this.actual = actual;
    this.expected = expected;
  }
}

export function assert(condition, message = 'Assertion failed') {
  if (!condition) {
    throw new AssertionError(message, condition, true);
  }
}

export function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    const msg = message || `Expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`;
    throw new AssertionError(msg, actual, expected);
  }
}

export function assertDeepEqual(actual, expected, message) {
  const actualStr = JSON.stringify(actual);
  const expectedStr = JSON.stringify(expected);
  if (actualStr !== expectedStr) {
    const msg = message || `Deep equality mismatch:\nActual:   ${actualStr}\nExpected: ${expectedStr}`;
    throw new AssertionError(msg, actual, expected);
  }
}

export function assertMatch(actual, regex, message) {
  if (typeof actual !== 'string' || !regex.test(actual)) {
    const msg = message || `String "${actual}" does not match regex ${regex}`;
    throw new AssertionError(msg, actual, regex.toString());
  }
}

export function assertGreaterThan(actual, threshold, message) {
  if (!(actual > threshold)) {
    const msg = message || `Expected ${actual} > ${threshold}`;
    throw new AssertionError(msg, actual, `> ${threshold}`);
  }
}

export function assertLessThan(actual, threshold, message) {
  if (!(actual < threshold)) {
    const msg = message || `Expected ${actual} < ${threshold}`;
    throw new AssertionError(msg, actual, `< ${threshold}`);
  }
}

export function assertInRange(actual, min, max, message) {
  if (actual < min || actual > max) {
    const msg = message || `Expected ${actual} to be in range [${min}, ${max}]`;
    throw new AssertionError(msg, actual, `[${min}, ${max}]`);
  }
}

export function assertFileExists(filePath, message) {
  const exists = existsSync(filePath);
  if (!exists) {
    const msg = message || `File does not exist: ${filePath}`;
    throw new AssertionError(msg, false, true);
  }
}

export function assertNonEmptyFile(filePath, minBytes = 1, message) {
  assertFileExists(filePath, message);
  const st = statSync(filePath);
  if (st.size < minBytes) {
    const msg = message || `File ${filePath} is too small (${st.size} bytes < ${minBytes} bytes)`;
    throw new AssertionError(msg, st.size, `>= ${minBytes}`);
  }
}

export function assertBinaryHeader(filePath, expectedBytes, message) {
  assertFileExists(filePath, message);
  const fd = readFileSync(filePath);
  if (fd.length < expectedBytes.length) {
    throw new AssertionError(`File ${filePath} shorter than expected header length`, fd.length, expectedBytes.length);
  }
  for (let i = 0; i < expectedBytes.length; i++) {
    if (fd[i] !== expectedBytes[i]) {
      const msg = message || `Header byte mismatch at offset ${i} in ${filePath}: expected 0x${expectedBytes[i].toString(16)}, got 0x${fd[i].toString(16)}`;
      throw new AssertionError(msg, fd[i], expectedBytes[i]);
    }
  }
}

// ---------------------------------------------------------------------------
// Filesystem & Asset Query Helpers
// ---------------------------------------------------------------------------

export function readJson(filePath) {
  const content = readFileSync(filePath, 'utf-8');
  return JSON.parse(content);
}

export function getAssets() {
  const assetsDir = join(ROOT_DIR, 'assets');
  const categories = ['biology', 'chemistry', 'physics'];
  const results = [];

  for (const cat of categories) {
    const catDir = join(assetsDir, cat);
    if (!existsSync(catDir)) continue;
    const entries = readdirSync(catDir, { withFileTypes: true });
    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      const assetDir = join(catDir, entry.name);
      const jsonPath = join(assetDir, 'asset.json');
      if (existsSync(jsonPath)) {
        try {
          const json = readJson(jsonPath);
          results.push({
            id: entry.name,
            category: cat,
            dir: assetDir,
            jsonPath,
            json
          });
        } catch (err) {
          results.push({
            id: entry.name,
            category: cat,
            dir: assetDir,
            jsonPath,
            json: null,
            error: err.message
          });
        }
      }
    }
  }
  return results;
}

// ---------------------------------------------------------------------------
// Test Execution Engine
// ---------------------------------------------------------------------------

/**
 * Run tests in the registry matching the provided filter options.
 */
export async function runTests(options = {}) {
  const {
    tierFilter = null,       // Set of numbers, e.g. new Set([1, 2])
    milestoneFilter = null,  // Set of strings, e.g. new Set(['M1', 'M2'])
    featureFilter = null,    // Set of numbers, e.g. new Set([1, 5])
    verbose = false,
    reporter = 'console'     // 'console' or 'json'
  } = options;

  const filteredTests = testRegistry.filter(t => {
    if (tierFilter && !tierFilter.has(t.tier)) return false;
    if (milestoneFilter && !milestoneFilter.has(t.milestone)) return false;
    if (featureFilter && !featureFilter.has(t.feature)) return false;
    return true;
  });

  const results = [];
  const startTime = Date.now();

  for (const t of filteredTests) {
    const testStart = Date.now();
    let passed = false;
    let error = null;

    try {
      await t.fn();
      passed = true;
    } catch (err) {
      passed = false;
      error = {
        message: err.message,
        actual: err.actual,
        expected: err.expected,
        stack: err.stack
      };
    }

    const durationMs = Date.now() - testStart;
    results.push({
      name: t.name,
      tier: t.tier,
      feature: t.feature,
      milestone: t.milestone,
      passed,
      durationMs,
      error
    });
  }

  const totalDurationMs = Date.now() - startTime;
  const total = results.length;
  const passedCount = results.filter(r => r.passed).length;
  const failedCount = total - passedCount;

  if (reporter === 'json') {
    return {
      total,
      passed: passedCount,
      failed: failedCount,
      durationMs: totalDurationMs,
      results
    };
  }

  // Console output
  const ANSI = {
    reset: '\x1b[0m',
    bold: '\x1b[1m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    cyan: '\x1b[36m',
    dim: '\x1b[2m'
  };

  console.log(`\n${ANSI.bold}======================================================================${ANSI.reset}`);
  console.log(`${ANSI.bold}${ANSI.cyan}EDUCATIONAL ANIMATION FRAMEWORK — E2E TEST SUITE REPORT${ANSI.reset}`);
  console.log(`${ANSI.bold}======================================================================${ANSI.reset}`);

  for (let tier = 1; tier <= 4; tier++) {
    const tierTests = results.filter(r => r.tier === tier);
    if (tierTests.length === 0) continue;

    const tierPassed = tierTests.filter(r => r.passed).length;
    const tierFailed = tierTests.length - tierPassed;
    const tierColor = tierFailed === 0 ? ANSI.green : ANSI.yellow;

    console.log(`\n${ANSI.bold}[TIER ${tier}] ${getTierName(tier)} (${tierColor}${tierPassed}/${tierTests.length} Passed${ANSI.reset}${ANSI.bold})${ANSI.reset}`);

    for (const r of tierTests) {
      const mark = r.passed ? `${ANSI.green}✓${ANSI.reset}` : `${ANSI.red}✗${ANSI.reset}`;
      const fNum = String(r.feature).padStart(2, '0');
      const timeStr = `${ANSI.dim}(${r.durationMs}ms)${ANSI.reset}`;
      console.log(`  ${mark} [F${fNum}] [${r.milestone}] ${r.name} ${timeStr}`);
      if (!r.passed && (verbose || tierFailed > 0)) {
        console.log(`    ${ANSI.red}Error: ${r.error.message}${ANSI.reset}`);
        if (r.error.expected !== undefined) {
          console.log(`    ${ANSI.dim}Expected: ${JSON.stringify(r.error.expected)}${ANSI.reset}`);
          console.log(`    ${ANSI.dim}Actual:   ${JSON.stringify(r.error.actual)}${ANSI.reset}`);
        }
      }
    }
  }

  console.log(`\n${ANSI.bold}======================================================================${ANSI.reset}`);
  const summaryColor = failedCount === 0 ? ANSI.green : ANSI.red;
  console.log(`${ANSI.bold}Summary: ${ANSI.cyan}${total}${ANSI.reset}${ANSI.bold} Tests Executed | ${summaryColor}Passed: ${passedCount}${ANSI.reset}${ANSI.bold} | Failed: ${failedCount > 0 ? ANSI.red : ANSI.green}${failedCount}${ANSI.reset}${ANSI.bold} | Total Time: ${(totalDurationMs / 1000).toFixed(2)}s${ANSI.reset}`);
  console.log(`${ANSI.bold}======================================================================${ANSI.reset}\n`);

  return {
    total,
    passed: passedCount,
    failed: failedCount,
    durationMs: totalDurationMs,
    results
  };
}

function getTierName(tier) {
  switch (tier) {
    case 1: return 'Feature Coverage (Presence, Structure & Schemas)';
    case 2: return 'Boundary & Corner Cases (Limits & Rejection)';
    case 3: return 'Cross-Feature Combinations (Parity & Laws)';
    case 4: return 'Real-World Application Scenarios (Pipeline & Delivery)';
    default: return `Tier ${tier}`;
  }
}
