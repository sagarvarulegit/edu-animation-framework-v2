#!/usr/bin/env node
/**
 * tests/e2e/run_all_tests.mjs
 * Unified Requirement-Driven E2E Test Runner for Educational Animation Framework
 *
 * Usage:
 *   node tests/e2e/run_all_tests.mjs
 *   node tests/e2e/run_all_tests.mjs --tier 1
 *   node tests/e2e/run_all_tests.mjs --tier 1,2
 *   node tests/e2e/run_all_tests.mjs --milestone M1
 *   node tests/e2e/run_all_tests.mjs --feature 5
 *   node tests/e2e/run_all_tests.mjs --verbose
 *   node tests/e2e/run_all_tests.mjs --json
 */

import { runTests } from './harness.mjs';

// Import all test suites to register tests in the central registry
import './tier1_feature_coverage.test.mjs';
import './tier2_boundary_cases.test.mjs';
import './tier3_cross_feature.test.mjs';
import './tier4_real_world.test.mjs';

function parseArgs(args) {
  const options = {
    tierFilter: null,
    milestoneFilter: null,
    featureFilter: null,
    verbose: false,
    reporter: 'console',
    allowFailing: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--help' || arg === '-h') {
      printHelp();
      process.exit(0);
    } else if (arg === '--tier' || arg === '-t') {
      const val = args[++i];
      if (!val) throw new Error('Missing value for --tier');
      options.tierFilter = new Set(val.split(',').map(n => parseInt(n.trim(), 10)));
    } else if (arg === '--milestone' || arg === '-m') {
      const val = args[++i];
      if (!val) throw new Error('Missing value for --milestone');
      options.milestoneFilter = new Set(val.split(',').map(s => s.trim().toUpperCase()));
    } else if (arg === '--feature' || arg === '-f') {
      const val = args[++i];
      if (!val) throw new Error('Missing value for --feature');
      options.featureFilter = new Set(val.split(',').map(n => parseInt(n.trim(), 10)));
    } else if (arg === '--verbose' || arg === '-v') {
      options.verbose = true;
    } else if (arg === '--json') {
      options.reporter = 'json';
    } else if (arg === '--allow-failing' || arg === '--soft') {
      options.allowFailing = true;
    }
  }

  return options;
}

function printHelp() {
  console.log(`
Educational Animation Framework — E2E Test Runner

Usage:
  node tests/e2e/run_all_tests.mjs [options]

Options:
  --tier, -t <1..4>      Comma-separated list of test tiers to run (e.g. 1, 2, 3, 4)
  --milestone, -m <M1..6> Comma-separated list of milestones to filter (e.g. M1, M2)
  --feature, -f <1..32>   Comma-separated list of feature numbers to run (e.g. 1, 5, 28)
  --verbose, -v           Print verbose assertion details and stacks
  --json                  Output test results in JSON format
  --allow-failing, --soft Exit with code 0 even if tests fail (for diagnostics)
  --help, -h              Show this help message
`);
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const report = await runTests(options);

  if (options.reporter === 'json') {
    console.log(JSON.stringify(report, null, 2));
  }

  if (report.failed > 0 && !options.allowFailing) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

main().catch(err => {
  console.error('Fatal Test Runner Error:', err);
  process.exit(2);
});
