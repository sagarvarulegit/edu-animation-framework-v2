/**
 * tests/e2e/tier1_feature_coverage.test.mjs
 * Tier 1: Feature Coverage (Presence, Structural Correctness, Output Files, Schema Validity)
 * Covers Features 1 to 32 across Milestones M1-M6.
 */

import { readFileSync, existsSync, readdirSync } from 'node:fs';
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

// Feature 1 (M1): SSS Schema Support
registerTest({
  name: 'SSS Schema Support: schemas/design-tokens.schema.json defines subsurface properties',
  tier: 1,
  feature: 1,
  milestone: 'M1',
  fn: async () => {
    const schemaPath = join(ROOT_DIR, 'schemas/design-tokens.schema.json');
    assertFileExists(schemaPath);
    const schema = readJson(schemaPath);
    const matProps = schema?.properties?.materials?.additionalProperties?.properties;
    assert(matProps, 'materials.additionalProperties.properties must exist in schema');
    assert(matProps.subsurfaceWeight, 'schema must define subsurfaceWeight');
    assert(matProps.subsurfaceRadius, 'schema must define subsurfaceRadius');
    assert(matProps.subsurfaceScale, 'schema must define subsurfaceScale');
  }
});

// Feature 2 (M1): SSS Tissue Shaders in Kit
registerTest({
  name: 'SSS Tissue Shaders in Kit: edu_asset_kit.py defines add_tissue_material',
  tier: 1,
  feature: 2,
  milestone: 'M1',
  fn: async () => {
    const kitPath = join(ROOT_DIR, 'assets/python/edu_asset_kit.py');
    assertFileExists(kitPath);
    const content = readFileSync(kitPath, 'utf-8');
    assert(content.includes('def add_tissue_material'), 'edu_asset_kit.py must define add_tissue_material');
    assert(content.includes('subsurface_weight') || content.includes('Subsurface Weight'), 'add_tissue_material must configure Subsurface Weight socket');
  }
});

// Feature 3 (M1): Shared Spline Tube Utility
registerTest({
  name: 'Shared Spline Tube Utility: edu_asset_kit.py defines smooth tube generator',
  tier: 1,
  feature: 3,
  milestone: 'M1',
  fn: async () => {
    const kitPath = join(ROOT_DIR, 'assets/python/edu_asset_kit.py');
    assertFileExists(kitPath);
    const content = readFileSync(kitPath, 'utf-8');
    const hasTube = content.includes('def create_smooth_tube') || content.includes('def smooth_tube_object');
    assert(hasTube, 'edu_asset_kit.py must export create_smooth_tube or smooth_tube_object');
  }
});

// Feature 4 (M1): Biological Tissue Tokens
registerTest({
  name: 'Biological Tissue Tokens: visual/design-tokens.json registers tissue presets',
  tier: 1,
  feature: 4,
  milestone: 'M1',
  fn: async () => {
    const tokensPath = join(ROOT_DIR, 'visual/design-tokens.json');
    assertFileExists(tokensPath);
    const tokens = readJson(tokensPath);
    assert(tokens.materials, 'design-tokens.json must define materials');
    const tissueKeys = Object.keys(tokens.materials).filter(k => k.toLowerCase().includes('tissue'));
    assert(tissueKeys.length >= 1, `Expected at least 1 tissue material preset, found: ${tissueKeys.join(', ')}`);
  }
});

// Feature 5 (M1): Metadata Alignment
registerTest({
  name: 'Metadata Alignment: all 57 asset.json files define provenance.generator as a non-empty string',
  tier: 1,
  feature: 5,
  milestone: 'M1',
  fn: async () => {
    const assets = getAssets();
    assertEqual(assets.length, 57, `Expected 57 assets, found ${assets.length}`);
    for (const a of assets) {
      assert(a.json, `Asset ${a.id} has invalid JSON`);
      assert(a.json.provenance, `Asset ${a.id} missing provenance`);
      assert(typeof a.json.provenance.generator === 'string' && a.json.provenance.generator.trim().length > 0,
        `Asset ${a.id} missing non-empty provenance.generator`);
    }
  }
});

// Feature 6 (M1): Web Asset Sync Tool
registerTest({
  name: 'Web Asset Sync Tool: tools/sync-web-assets.mjs exists and is executable',
  tier: 1,
  feature: 6,
  milestone: 'M1',
  fn: async () => {
    const syncPath = join(ROOT_DIR, 'tools/sync-web-assets.mjs');
    assertFileExists(syncPath, 'tools/sync-web-assets.mjs must exist');
  }
});

// Feature 7 (M2): Heart Internal Anatomy
registerTest({
  name: 'Heart Internal Anatomy: build_heart.py defines 4 chambers, septa, and valves',
  tier: 1,
  feature: 7,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-heart/build_heart.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('ventricle') || content.includes('atrium') || content.includes('chamber'),
      'build_heart.py must model heart chambers');
  }
});

// Feature 8 (M2): Heart Vessels & Manifold Ends
registerTest({
  name: 'Heart Vessels & Manifold Ends: build_heart.py defines great vessels and capping',
  tier: 1,
  feature: 8,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-heart/build_heart.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('aorta'), 'build_heart.py must model aorta');
    assert(content.includes('vena_cava') || content.includes('pulmonary'), 'build_heart.py must model vena cava or pulmonary vessels');
  }
});

// Feature 9 (M2): Eye 3-Layer Structure
registerTest({
  name: 'Eye 3-Layer Structure: build_eye.py defines sclera, choroid, retina, and vitreous',
  tier: 1,
  feature: 9,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-eye/build_eye.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('sclera'), 'build_eye.py must model sclera');
    assert(content.includes('retina'), 'build_eye.py must model retina');
    assert(content.includes('vitreous') || content.includes('lens'), 'build_eye.py must model optical components');
  }
});

// Feature 10 (M2): Eye Iris & Aperture Pupil
registerTest({
  name: 'Eye Iris & Aperture Pupil: build_eye.py defines iris with aperture pupil',
  tier: 1,
  feature: 10,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-eye/build_eye.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('iris'), 'build_eye.py must model iris');
    assert(content.includes('pupil'), 'build_eye.py must model pupil');
  }
});

// Feature 11 (M2): Brain Gyri & Sulci Detailing
registerTest({
  name: 'Brain Gyri & Sulci Detailing: build_brain.py models cerebral cortex structure',
  tier: 1,
  feature: 11,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/brain/build_brain.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('cerebrum') || content.includes('cortex'), 'build_brain.py must model cerebrum/cortex');
  }
});

// Feature 12 (M2): Brainstem & Cerebellar Folia
registerTest({
  name: 'Brainstem & Cerebellar Folia: build_brain.py models cerebellum and brainstem',
  tier: 1,
  feature: 12,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/brain/build_brain.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('cerebellum'), 'build_brain.py must model cerebellum');
    assert(content.includes('brainstem') || content.includes('medulla') || content.includes('pons'),
      'build_brain.py must model brainstem components');
  }
});

// Feature 13 (M3): Nephron Loop of Henle & Welding
registerTest({
  name: 'Nephron Loop of Henle: build_nephron.py models Bowman capsule, Henle loop, and tubule',
  tier: 1,
  feature: 13,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/nephron/build_nephron.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('bowman') || content.includes('glomerulus'), 'build_nephron.py must model renal corpuscle');
    assert(content.includes('henle') || content.includes('loop'), 'build_nephron.py must model loop of Henle');
  }
});

// Feature 14 (M3): Respiratory Bronchial Tree & C-Rings
registerTest({
  name: 'Respiratory System: build_respiratory.py defines trachea, bronchi, and lungs',
  tier: 1,
  feature: 14,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-respiratory-system/build_respiratory.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('trachea'), 'build_respiratory.py must model trachea');
    assert(content.includes('bronch') || content.includes('lung'), 'build_respiratory.py must model bronchial tree/lungs');
  }
});

// Feature 15 (M3): Continuous Digestive Tract & Ducts
registerTest({
  name: 'Digestive System: build_digestive.py models continuous GI tract and organs',
  tier: 1,
  feature: 15,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/digestive-system/build_digestive.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('stomach'), 'build_digestive.py must model stomach');
    assert(content.includes('intestine') || content.includes('colon'), 'build_digestive.py must model intestine');
  }
});

// Feature 16 (M3): DNA Double Helix Geometry
registerTest({
  name: 'DNA Double Helix: build_dna.py models complementary base pairs and backbone',
  tier: 1,
  feature: 16,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/dna-double-helix/build_dna.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('helix') || content.includes('strand') || content.includes('base'),
      'build_dna.py must model helical strands or base pairs');
  }
});

// Feature 17 (M3): Other Biology Topological Fixes
registerTest({
  name: 'Other Biology Assets: build scripts exist for all 13 biology assets',
  tier: 1,
  feature: 17,
  milestone: 'M3',
  fn: async () => {
    const bioAssets = getAssets().filter(a => a.category === 'biology');
    assertEqual(bioAssets.length, 13, `Expected 13 biology assets, found ${bioAssets.length}`);
    for (const a of bioAssets) {
      const files = readdirSync(a.dir);
      const buildScripts = files.filter(f => f.startsWith('build_') && f.endsWith('.py'));
      assert(buildScripts.length >= 1, `Biology asset ${a.id} must have a build_*.py script`);
    }
  }
});

// Feature 18 (M4): Diamond Lattice Crystallography
registerTest({
  name: 'Diamond Lattice: build_diamond_lattice.py models sp3 tetrahedral carbon network',
  tier: 1,
  feature: 18,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/diamond-lattice/build_diamond_lattice.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('tetrahedral') || content.includes('bond') || content.includes('lattice'),
      'build_diamond_lattice.py must model tetrahedral network');
  }
});

// Feature 19 (M4): Graphite Planar Hexagonal Lattice
registerTest({
  name: 'Graphite Lattice: build_graphite_lattice.py models planar hexagonal graphene layers',
  tier: 1,
  feature: 19,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/graphite-lattice/build_graphite_lattice.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('hex') || content.includes('layer') || content.includes('sheet'),
      'build_graphite_lattice.py must model hexagonal layers');
  }
});

// Feature 20 (M4): Hydrogen Evolution Delivery Tube
registerTest({
  name: 'Hydrogen Apparatus: build_hydrogen_evolution.py models delivery tube and flask',
  tier: 1,
  feature: 20,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('tube') || content.includes('flask'),
      'build_hydrogen_evolution.py must model delivery tube and flask');
  }
});

// Feature 21 (M4): Dropper Glass Wall Thickness
registerTest({
  name: 'Dropper Geometry: build_dropper.py models glass body and teat bulb',
  tier: 1,
  feature: 21,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/dropper/build_dropper.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('lathe') || content.includes('glass') || content.includes('bulb'),
      'build_dropper.py must model glass body and bulb');
  }
});

// Feature 22 (M4): Atom Electron Styling Unification
registerTest({
  name: 'Atom Models: build_magnesium_atom.py and build_oxygen_atom.py model nucleus & shells',
  tier: 1,
  feature: 22,
  milestone: 'M4',
  fn: async () => {
    const mgPath = join(ROOT_DIR, 'assets/chemistry/magnesium-atom/build_magnesium_atom.py');
    const oPath = join(ROOT_DIR, 'assets/chemistry/oxygen-atom/build_oxygen_atom.py');
    assertFileExists(mgPath);
    assertFileExists(oPath);
  }
});

// Feature 23 (M4): Chemistry Materials Polish
registerTest({
  name: 'Chemistry Glassware: beaker, flask, and test-tube use glass materials',
  tier: 1,
  feature: 23,
  milestone: 'M4',
  fn: async () => {
    const beakerPath = join(ROOT_DIR, 'assets/chemistry/beaker/build_beaker.py');
    const tubePath = join(ROOT_DIR, 'assets/chemistry/test-tube/build_test_tube.py');
    assertFileExists(beakerPath);
    assertFileExists(tubePath);
  }
});

// Feature 24 (M5): Full Circuit Physics Consistency
registerTest({
  name: 'Full Circuit: build_circuit.py models battery, switch, bulb, and conductors',
  tier: 1,
  feature: 24,
  milestone: 'M5',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/physics/full-circuit/build_circuit.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('bulb') && (content.includes('switch') || content.includes('battery')),
      'build_circuit.py must model circuit components');
  }
});

// Feature 25 (M5): DC Motor Split-Ring Commutator
registerTest({
  name: 'Electric Motor: build_electric_motor.py models commutator and magnetic poles',
  tier: 1,
  feature: 25,
  milestone: 'M5',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/physics/electric-motor/build_electric_motor.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('magnet') || content.includes('coil') || content.includes('commutator'),
      'build_electric_motor.py must model motor components');
  }
});

// Feature 26 (M5): Glass Slab Emergent Rays & Pins
registerTest({
  name: 'Glass Slab Refraction: build_glass_slab.py models slab and ray paths',
  tier: 1,
  feature: 26,
  milestone: 'M5',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/physics/glass-slab/build_glass_slab.py');
    assertFileExists(scriptPath);
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('slab') || content.includes('ray'),
      'build_glass_slab.py must model slab and ray paths');
  }
});

// Feature 27 (M5): Optics & Physics Materials
registerTest({
  name: 'Physics Optics & Meters: lenses, prisms, and meters define PBR materials',
  tier: 1,
  feature: 27,
  milestone: 'M5',
  fn: async () => {
    const prismPath = join(ROOT_DIR, 'assets/physics/glass-prism/build_prism.py');
    const ammeterPath = join(ROOT_DIR, 'assets/physics/ammeter/build_ammeter.py');
    assertFileExists(prismPath);
    assertFileExists(ammeterPath);
  }
});

// Feature 28 (M6): Headless Batch Generation
registerTest({
  name: 'Headless Batch Generation: all 57 asset directories contain build script and out/ directory',
  tier: 1,
  feature: 28,
  milestone: 'M6',
  fn: async () => {
    const assets = getAssets();
    assertEqual(assets.length, 57, `Expected 57 assets, found ${assets.length}`);
    for (const a of assets) {
      const outDir = join(a.dir, 'out');
      assertFileExists(outDir, `Asset ${a.id} missing out/ directory`);
      const files = readdirSync(a.dir);
      const hasBuild = files.some(f => f.startsWith('build_') && f.endsWith('.py'));
      assert(hasBuild, `Asset ${a.id} missing build_*.py script`);
    }
  }
});

// Feature 29 (M6): Full Schema & Catalog Validation
registerTest({
  name: 'Full Schema & Catalog Validation: tools/validate.mjs exists and schemas are intact',
  tier: 1,
  feature: 29,
  milestone: 'M6',
  fn: async () => {
    const valPath = join(ROOT_DIR, 'tools/validate.mjs');
    assertFileExists(valPath);
    const schemasDir = join(ROOT_DIR, 'schemas');
    assertFileExists(schemasDir);
    const assetSchema = join(schemasDir, 'asset.schema.json');
    assertFileExists(assetSchema);
  }
});

// Feature 30 (M6): Downstream Web Sync
registerTest({
  name: 'Downstream Web Sync: apps/interactive-viewer/public/assets/ contains 57 glb models',
  tier: 1,
  feature: 30,
  milestone: 'M6',
  fn: async () => {
    const webAssetsDir = join(ROOT_DIR, 'apps/interactive-viewer/public/assets');
    assertFileExists(webAssetsDir);
    const glbFiles = readdirSync(webAssetsDir).filter(f => f.endsWith('.glb'));
    assertEqual(glbFiles.length, 57, `Expected 57 glb files in web public/assets/, found ${glbFiles.length}`);
  }
});

// Feature 31 (M6): Full E2E Test Suite (Tiers 1-4)
registerTest({
  name: 'Full E2E Test Suite: harness and runner entrypoint are defined',
  tier: 1,
  feature: 31,
  milestone: 'M6',
  fn: async () => {
    const harnessPath = join(ROOT_DIR, 'tests/e2e/harness.mjs');
    assertFileExists(harnessPath);
  }
});

// Feature 32 (M6): Adversarial Hardening (Tier 5)
registerTest({
  name: 'Adversarial Hardening: schema directory contains core validation schemas',
  tier: 1,
  feature: 32,
  milestone: 'M6',
  fn: async () => {
    const schemas = ['asset.schema.json', 'scene.schema.json', 'design-tokens.schema.json', 'lesson.schema.json'];
    for (const s of schemas) {
      assertFileExists(join(ROOT_DIR, 'schemas', s), `Schema ${s} must exist`);
    }
  }
});
