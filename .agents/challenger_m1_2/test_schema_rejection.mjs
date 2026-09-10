import Ajv2020 from 'ajv/dist/2020.js';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = '/home/sagarv/Projects/edu-animation-framework-v2';
const schemaPath = join(ROOT, 'schemas/design-tokens.schema.json');
const tokensPath = join(ROOT, 'visual/design-tokens.json');

const schema = JSON.parse(readFileSync(schemaPath, 'utf8'));
const baseTokens = JSON.parse(readFileSync(tokensPath, 'utf8'));

const ajv = new Ajv2020({ allErrors: true, strict: false });
const validate = ajv.compile(schema);

function testCase(desc, mutator, expectedValid, expectedErrorKeyword) {
  const clone = JSON.parse(JSON.stringify(baseTokens));
  mutator(clone);
  const valid = validate(clone);
  
  if (expectedValid) {
    if (!valid) {
      console.error(`FAIL: ${desc} was expected to be VALID, but failed with:`, validate.errors);
      return false;
    } else {
      console.log(`PASS: ${desc} accepted as valid as expected.`);
      return true;
    }
  } else {
    if (valid) {
      console.error(`FAIL: ${desc} was expected to be REJECTED, but PASSED!`);
      return false;
    } else {
      const match = expectedErrorKeyword 
        ? validate.errors.some(e => e.keyword === expectedErrorKeyword || e.message?.includes(expectedErrorKeyword))
        : true;
      if (!match) {
        console.warn(`WARN: ${desc} rejected, but keyword '${expectedErrorKeyword}' not in errors:`, validate.errors);
      }
      console.log(`PASS: ${desc} rejected as expected. Error: ${validate.errors[0]?.message} (${validate.errors[0]?.keyword})`);
      return true;
    }
  }
}

console.log('=== TESTING SCHEMA BOUNDARY REJECTION ===\n');

let allPassed = true;

// 1. subsurfaceWeight
allPassed &&= testCase(
  'Negative subsurfaceWeight (-0.1)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = -0.1; },
  false,
  'minimum'
);

allPassed &&= testCase(
  'Negative subsurfaceWeight (-1.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = -1.0; },
  false,
  'minimum'
);

allPassed &&= testCase(
  'Boundary subsurfaceWeight (0.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = 0.0; },
  true
);

allPassed &&= testCase(
  'Boundary subsurfaceWeight (1.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = 1.0; },
  true
);

allPassed &&= testCase(
  'Excessive subsurfaceWeight (1.01)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = 1.01; },
  false,
  'maximum'
);

allPassed &&= testCase(
  'Excessive subsurfaceWeight (2.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceWeight = 2.0; },
  false,
  'maximum'
);

// 2. subsurfaceRadius array lengths
allPassed &&= testCase(
  'subsurfaceRadius with 0 items',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = []; },
  false,
  'minItems'
);

allPassed &&= testCase(
  'subsurfaceRadius with 1 item',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = [1.0]; },
  false,
  'minItems'
);

allPassed &&= testCase(
  'subsurfaceRadius with 2 items',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = [1.0, 0.2]; },
  false,
  'minItems'
);

allPassed &&= testCase(
  'subsurfaceRadius with 3 items (valid)',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = [1.0, 0.2, 0.1]; },
  true
);

allPassed &&= testCase(
  'subsurfaceRadius with 4 items',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = [1.0, 0.2, 0.1, 0.05]; },
  false,
  'maxItems'
);

allPassed &&= testCase(
  'subsurfaceRadius with non-number items',
  (t) => { t.materials.tissueMuscle.subsurfaceRadius = [1.0, "0.2", 0.1]; },
  false,
  'type'
);

// 3. subsurfaceScale
allPassed &&= testCase(
  'Negative subsurfaceScale (-0.01)',
  (t) => { t.materials.tissueMuscle.subsurfaceScale = -0.01; },
  false,
  'minimum'
);

allPassed &&= testCase(
  'Negative subsurfaceScale (-1.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceScale = -1.0; },
  false,
  'minimum'
);

allPassed &&= testCase(
  'Boundary subsurfaceScale (0.0)',
  (t) => { t.materials.tissueMuscle.subsurfaceScale = 0.0; },
  true
);

allPassed &&= testCase(
  'Valid subsurfaceScale (0.02)',
  (t) => { t.materials.tissueMuscle.subsurfaceScale = 0.02; },
  true
);

// 4. subsurfaceColor
allPassed &&= testCase(
  'Invalid subsurfaceColor (3-digit hex #fff)',
  (t) => { t.materials.tissueMuscle.subsurfaceColor = '#fff'; },
  false,
  'pattern'
);

allPassed &&= testCase(
  'Invalid subsurfaceColor (named color "red")',
  (t) => { t.materials.tissueMuscle.subsurfaceColor = 'red'; },
  false,
  'pattern'
);

allPassed &&= testCase(
  'Valid subsurfaceColor (#991b1b)',
  (t) => { t.materials.tissueMuscle.subsurfaceColor = '#991b1b'; },
  true
);

console.log(`\nOverall Schema Rejection Result: ${allPassed ? 'ALL TESTS PASSED' : 'SOME TESTS FAILED'}`);
process.exit(allPassed ? 0 : 1);
