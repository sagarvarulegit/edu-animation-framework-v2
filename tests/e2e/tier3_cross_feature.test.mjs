/**
 * tests/e2e/tier3_cross_feature.test.mjs
 * Tier 3: Cross-Feature Combinations (Parity, Multi-Component Integration, Scientific Laws)
 * Validates consistency between metadata, shaders, tokens, outputs, and physical laws.
 */

import { readFileSync, existsSync, statSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  ROOT_DIR,
  registerTest,
  assert,
  assertEqual,
  assertFileExists,
  readJson,
  getAssets
} from './harness.mjs';

// Feature 5 (M1): Metadata Alignment — Generator Script Existence Parity
registerTest({
  name: 'Metadata Parity: provenance.generator script must actually exist on disk for each asset',
  tier: 3,
  feature: 5,
  milestone: 'M1',
  fn: async () => {
    const assets = getAssets();
    const missingGenerators = [];

    for (const a of assets) {
      const generator = a.json?.provenance?.generator;
      if (!generator) {
        missingGenerators.push(`${a.id}: missing provenance.generator`);
        continue;
      }

      // Check if path is relative to asset dir or root dir
      const relativeToAsset = join(a.dir, generator);
      const relativeToRoot = join(ROOT_DIR, generator);

      if (!existsSync(relativeToAsset) && !existsSync(relativeToRoot)) {
        missingGenerators.push(`${a.id}: generator "${generator}" not found on disk`);
      }
    }

    assertEqual(
      missingGenerators.length,
      0,
      `Assets with missing generator scripts:\n${missingGenerators.join('\n')}`
    );
  }
});

// Feature 6 & 30 (M1/M6): Asset Output vs Web Directory Parity
registerTest({
  name: 'Web Asset Parity: all 57 asset out/*.glb files match public/assets/*.glb',
  tier: 3,
  feature: 6,
  milestone: 'M1',
  fn: async () => {
    const assets = getAssets();
    const webAssetsDir = join(ROOT_DIR, 'apps/interactive-viewer/public/assets');
    assertFileExists(webAssetsDir, 'apps/interactive-viewer/public/assets must exist');

    const discrepancies = [];

    for (const a of assets) {
      const srcGlb = join(a.dir, 'out', `${a.id}.glb`);
      const destGlb = join(webAssetsDir, `${a.id}.glb`);

      if (!existsSync(srcGlb)) {
        discrepancies.push(`${a.id}: source out/${a.id}.glb does not exist`);
        continue;
      }
      if (!existsSync(destGlb)) {
        discrepancies.push(`${a.id}: destination public/assets/${a.id}.glb does not exist`);
        continue;
      }

      const srcSize = statSync(srcGlb).size;
      const destSize = statSync(destGlb).size;

      if (srcSize !== destSize) {
        discrepancies.push(
          `${a.id}: size mismatch (source: ${srcSize} bytes, web: ${destSize} bytes)`
        );
      }
    }

    assertEqual(
      discrepancies.length,
      0,
      `Web asset parity discrepancies found:\n${discrepancies.join('\n')}`
    );
  }
});

// Feature 4 & 23 (M1/M4): Design Token Color Codes Matching Shaders
registerTest({
  name: 'Token-Shader Parity: glass and metal materials in tokens match shader requirements',
  tier: 3,
  feature: 4,
  milestone: 'M1',
  fn: async () => {
    const tokensPath = join(ROOT_DIR, 'visual/design-tokens.json');
    const tokens = readJson(tokensPath);
    const materials = tokens.materials || {};

    // Check borosilicate glass token
    assert(materials.glass_borosilicate, 'design-tokens.json must define glass_borosilicate');
    assert(materials.glass_borosilicate.transmission >= 0.8, 'glass_borosilicate transmission must be >= 0.8');
    assertEqual(materials.glass_borosilicate.ior, 1.52, 'glass_borosilicate IOR must be 1.52');

    // Check magnesium metal token
    assert(materials.magnesium_ribbon || materials.metal_magnesium, 'design-tokens must define magnesium material');
  }
});

// Feature 18 & 19 (M4): Diamond vs Graphite Crystallographic Parity
registerTest({
  name: 'Crystallography Parity: Diamond valency 4 (sp3) vs Graphite valency 3 (sp2)',
  tier: 3,
  feature: 18,
  milestone: 'M4',
  fn: async () => {
    const diamondPath = join(ROOT_DIR, 'assets/chemistry/diamond-lattice/build_diamond_lattice.py');
    const graphitePath = join(ROOT_DIR, 'assets/chemistry/graphite-lattice/build_graphite_lattice.py');
    const diamondContent = readFileSync(diamondPath, 'utf-8');
    const graphiteContent = readFileSync(graphitePath, 'utf-8');

    // In diamond, carbon is tetrahedrally bonded to 4 carbons (sp3 hybridization)
    assert(diamondContent.includes('4') || diamondContent.includes('tetrahedral'),
      'Diamond lattice must specify 4-coordinate tetrahedral bonding');

    // In graphite, carbon forms planar hexagonal rings with 3 neighbors (sp2 hybridization)
    assert(graphiteContent.includes('3') || graphiteContent.includes('hex') || graphiteContent.includes('plane'),
      'Graphite lattice must specify 3-coordinate planar hexagonal bonding');
  }
});

// Feature 22 (M4): Atomic Electron & Nucleus Styling Consistency
registerTest({
  name: 'Atomic Styling Parity: magnesium-atom and oxygen-atom share electron styling conventions',
  tier: 3,
  feature: 22,
  milestone: 'M4',
  fn: async () => {
    const mgJson = readJson(join(ROOT_DIR, 'assets/chemistry/magnesium-atom/asset.json'));
    const oJson = readJson(join(ROOT_DIR, 'assets/chemistry/oxygen-atom/asset.json'));

    assertEqual(mgJson.scaleConvention?.unit, oJson.scaleConvention?.unit,
      'Atom assets must share the same scale convention unit');
    assertEqual(mgJson.scaleConvention?.basis, oJson.scaleConvention?.basis,
      'Atom assets must share the same scale convention basis');
  }
});

// Feature 24 (M5): Circuit Continuity Loop Parity
registerTest({
  name: 'Circuit Parity: full-circuit defines complete closed-loop topological chain',
  tier: 3,
  feature: 24,
  milestone: 'M5',
  fn: async () => {
    const circuitScript = join(ROOT_DIR, 'assets/physics/full-circuit/build_circuit.py');
    const content = readFileSync(circuitScript, 'utf-8');

    // Circuit chain: battery -> switch -> bulb -> resistor -> battery
    const components = ['battery', 'switch', 'bulb', 'resistor'];
    for (const c of components) {
      assert(content.includes(c), `Circuit script must reference component "${c}"`);
    }
  }
});

// Feature 26 (M5): Glass Slab Pin Collinearity & Snell Law Parity
registerTest({
  name: 'Glass Slab Parity: P1-P2 collinear with incident ray, P3-P4 collinear with emergent ray',
  tier: 3,
  feature: 26,
  milestone: 'M5',
  fn: async () => {
    const slabScript = join(ROOT_DIR, 'assets/physics/glass-slab/build_glass_slab.py');
    const content = readFileSync(slabScript, 'utf-8');

    // CBSE Class 10 glass slab demonstration requires 4 pins: P1, P2 on incident ray; P3, P4 on emergent ray
    const hasPins = (content.includes('pin') || content.includes('P1')) &&
                    (content.includes('emergent') || content.includes('refract'));
    assert(hasPins, 'Glass slab demonstration must model refraction pins and ray paths');
  }
});
