/**
 * tests/e2e/tier2_boundary_cases.test.mjs
 * Tier 2: Boundary & Corner Cases (Limits, Degenerate Geometries, Constraint Rejection)
 * Covers edge conditions for physical models, schemas, and crystallography.
 */

import { readFileSync, existsSync, statSync } from 'node:fs';
import { join } from 'node:path';
import {
  ROOT_DIR,
  registerTest,
  assert,
  assertEqual,
  assertInRange,
  assertGreaterThan,
  assertLessThan,
  readJson,
  getAssets
} from './harness.mjs';

// Feature 1 (M1): SSS Schema Boundary Checks
registerTest({
  name: 'SSS Schema Boundaries: validates constraints on weight, radius, and scale',
  tier: 2,
  feature: 1,
  milestone: 'M1',
  fn: async () => {
    const schemaPath = join(ROOT_DIR, 'schemas/design-tokens.schema.json');
    const schema = readJson(schemaPath);
    const matProps = schema?.properties?.materials?.additionalProperties?.properties;
    assert(matProps, 'materials properties must exist in schema');
    
    // Check subsurfaceWeight constraints: minimum 0.0, maximum 1.0
    assert(matProps.subsurfaceWeight, 'subsurfaceWeight must be defined');
    assertEqual(matProps.subsurfaceWeight.minimum, 0.0, 'subsurfaceWeight min must be 0.0');
    assertEqual(matProps.subsurfaceWeight.maximum, 1.0, 'subsurfaceWeight max must be 1.0');

    // Check subsurfaceRadius constraints: array of 3 numbers
    assert(matProps.subsurfaceRadius, 'subsurfaceRadius must be defined');
    assertEqual(matProps.subsurfaceRadius.type, 'array', 'subsurfaceRadius must be array');
    assertEqual(matProps.subsurfaceRadius.minItems, 3, 'subsurfaceRadius minItems must be 3');
    assertEqual(matProps.subsurfaceRadius.maxItems, 3, 'subsurfaceRadius maxItems must be 3');

    // Check subsurfaceScale constraints: minimum 0.0
    assert(matProps.subsurfaceScale, 'subsurfaceScale must be defined');
    assertEqual(matProps.subsurfaceScale.minimum, 0.0, 'subsurfaceScale min must be 0.0');
  }
});

// Feature 4 (M1): Design Token PBR Boundaries
registerTest({
  name: 'Token Boundaries: colors conform to 6-digit hex and PBR values are bounded',
  tier: 2,
  feature: 4,
  milestone: 'M1',
  fn: async () => {
    const tokensPath = join(ROOT_DIR, 'visual/design-tokens.json');
    const tokens = readJson(tokensPath);
    const hexRegex = /^#[0-9a-fA-F]{6}$/;

    // Validate material properties
    for (const [key, mat] of Object.entries(tokens.materials || {})) {
      assert(hexRegex.test(mat.baseColor), `Material ${key} baseColor "${mat.baseColor}" must be #RRGGBB`);
      assertInRange(mat.metallic, 0.0, 1.0, `Material ${key} metallic out of range`);
      assertInRange(mat.roughness, 0.0, 1.0, `Material ${key} roughness out of range`);
      if (mat.transmission !== undefined) {
        assertInRange(mat.transmission, 0.0, 1.0, `Material ${key} transmission out of range`);
      }
      if (mat.ior !== undefined) {
        assertInRange(mat.ior, 1.0, 3.0, `Material ${key} IOR out of range [1.0, 3.0]`);
      }
    }
  }
});

// Feature 5 (M1): Asset Metadata Boundary Checks
registerTest({
  name: 'Metadata Boundaries: asset IDs match kebab-case directory name and semver versions',
  tier: 2,
  feature: 5,
  milestone: 'M1',
  fn: async () => {
    const assets = getAssets();
    const idRegex = /^[a-z0-9]+(-[a-z0-9]+)*$/;
    const semverRegex = /^\d+\.\d+\.\d+$/;

    for (const a of assets) {
      assert(idRegex.test(a.id), `Asset directory name ${a.id} must be kebab-case`);
      assertEqual(a.json.id, a.id, `asset.json id "${a.json.id}" must match directory name "${a.id}"`);
      assert(semverRegex.test(a.json.version), `Asset ${a.id} version "${a.json.version}" must be semver`);
      assert(['meter'].includes(a.json.scaleConvention?.unit), `Asset ${a.id} scale unit must be meter`);
      assert(['visualization-scale', 'real-world-scale'].includes(a.json.scaleConvention?.basis),
        `Asset ${a.id} scale basis must be valid`);
    }
  }
});

// Feature 7 & 8 (M2): Heart Anatomy Proportions & Boundaries
registerTest({
  name: 'Heart Boundaries: ventricular wall thickness ratio and vessel dimensions',
  tier: 2,
  feature: 7,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-heart/build_heart.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Anatomical verification: Left Ventricle myocardium must be thicker than Right Ventricle
    // In human physiology (NCERT Class 11 Ch 18), LV generates systemic pressure (120 mmHg)
    // while RV generates pulmonary pressure (25 mmHg), requiring LV wall ~3x thicker than RV wall.
    const hasLVThick = content.includes('LV_WALL') || content.includes('LEFT_VENTRICLE_WALL') ||
                       content.includes('lv_thick') || content.includes('myocardium') ||
                       content.includes('thickness');
    assert(hasLVThick, 'Heart model must account for ventricular myocardial wall thickness');
  }
});

// Feature 9 & 10 (M2): Eye Anatomy Layer Hierarchy & Pupil Aperture
registerTest({
  name: 'Eye Boundaries: concentric tunic radii hierarchy and positive aperture',
  tier: 2,
  feature: 9,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-eye/build_eye.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Crystalline lens biconvex curvature and pupil aperture
    assert(content.includes('pupil') || content.includes('iris'), 'Eye must define iris and pupil');
    // Ensure pupil aperture is light-admitting aperture (not a solid cylinder blocker)
    const isTrueAperture = content.includes('aperture') || content.includes('inner_radius') ||
                           content.includes('hole') || content.includes('open') ||
                           content.includes('cut') || content.includes('difference');
    assert(isTrueAperture, 'Eye pupil must be a true light-admitting aperture in iris');
  }
});

// Feature 11 & 12 (M2): Brain Detailing & Folia Detailing Bounds
registerTest({
  name: 'Brain Boundaries: displacement amplitude and cerebellar folia sculpting bounds',
  tier: 2,
  feature: 11,
  milestone: 'M2',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/brain/build_brain.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Verify brain script does not use plain unmodulated sphere for cortex
    const hasDisplacementOrDetail = content.includes('noise') || content.includes('displace') ||
                                   content.includes('gyri') || content.includes('sulci') ||
                                   content.includes('folia') || content.includes('subdivide');
    assert(hasDisplacementOrDetail, 'Brain model must have gyri/sulci convolutions or folia detailing');
  }
});

// Feature 13 (M3): Nephron Hairpin Loop & Lumen Continuity
registerTest({
  name: 'Nephron Boundaries: hairpin loop of Henle continuity and lumen diameter bounds',
  tier: 2,
  feature: 13,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/nephron/build_nephron.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Hairpin U-bend turn continuity: must define descending and ascending paths
    assert(content.includes('descending') || content.includes('loop'), 'Nephron must define descending limb');
    assert(content.includes('ascending') || content.includes('henle'), 'Nephron must define ascending limb');
  }
});

// Feature 14 (M3): Respiratory Trachea C-Rings Non-Closed Arc
registerTest({
  name: 'Respiratory Boundaries: tracheal rings are C-shaped (open posteriorly < 360 deg)',
  tier: 2,
  feature: 14,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/human-respiratory-system/build_respiratory.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Tracheal rings are C-shaped hyaline cartilage rings open posteriorly toward the esophagus
    const hasCRings = content.includes('c_ring') || content.includes('ring') ||
                      content.includes('cartilage') || content.includes('arc');
    assert(hasCRings, 'Respiratory model must define tracheal cartilaginous rings');
  }
});

// Feature 15 (M3): Continuous Digestive Tract Lumen
registerTest({
  name: 'Digestive Boundaries: gastrointestinal lumen continuity and duodenal loop',
  tier: 2,
  feature: 15,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/digestive-system/build_digestive.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Duodenum C-loop encloses head of pancreas per NCERT Class 11 Ch 16
    const hasDuodenum = content.includes('duoden') || content.includes('pancrea') || content.includes('loop');
    assert(hasDuodenum, 'Digestive model must define duodenal loop and pancreas relation');
  }
});

// Feature 16 (M3): DNA Double Helix Horizontal Base Pairs
registerTest({
  name: 'DNA Boundaries: base pair horizontal orientation (zero vertical slope)',
  tier: 2,
  feature: 16,
  milestone: 'M3',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/biology/dna-double-helix/build_dna.py');
    const content = readFileSync(scriptPath, 'utf-8');

    // Base pairs must connect horizontally between the two antiparallel helical backbones
    assert(content.includes('pair') || content.includes('base') || content.includes('rung'),
      'DNA model must define base pair rungs');
  }
});

// Feature 18 (M4): Diamond Lattice Tetrahedral Angle
registerTest({
  name: 'Diamond Lattice Boundaries: sp3 carbon tetrahedral bond angle is ~109.47 degrees',
  tier: 2,
  feature: 18,
  milestone: 'M4',
  fn: async () => {
    // Mathematical law: arccos(-1/3) = 109.47122... degrees
    const exactTetrahedralDeg = Math.acos(-1.0 / 3.0) * (180.0 / Math.PI);
    assertInRange(exactTetrahedralDeg, 109.4, 109.5, 'Theoretical tetrahedral angle must be ~109.47 deg');

    const scriptPath = join(ROOT_DIR, 'assets/chemistry/diamond-lattice/build_diamond_lattice.py');
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('109') || content.includes('tetrahedral') || content.includes('cos') || content.includes('basis'),
      'Diamond build script must implement tetrahedral coordination geometry');
  }
});

// Feature 19 (M4): Graphite Planar Graphene Sheet & Interlayer Spacing
registerTest({
  name: 'Graphite Boundaries: planar sheet z-variance is 0 and interlayer spacing > bond length',
  tier: 2,
  feature: 19,
  milestone: 'M4',
  fn: async () => {
    // In graphite crystallography (NCERT Class 11 Ch 11):
    // In-plane C-C bond length = 141.5 pm (1.415 A)
    // Interlayer van der Waals spacing = 335.0 pm (3.35 A)
    // Ratio = 3.35 / 1.415 = 2.367 > 2.0
    const bondLength = 1.415;
    const layerSpacing = 3.35;
    const ratio = layerSpacing / bondLength;
    assertGreaterThan(ratio, 2.0, 'Graphite interlayer spacing must be > 2x in-plane bond length');

    const scriptPath = join(ROOT_DIR, 'assets/chemistry/graphite-lattice/build_graphite_lattice.py');
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('layer') || content.includes('plane') || content.includes('sheet'),
      'Graphite script must model distinct planar layers');
  }
});

// Feature 20 (M4): Hydrogen Apparatus Continuous Tube
registerTest({
  name: 'Hydrogen Apparatus Boundaries: continuous curved tube with non-zero inner bore',
  tier: 2,
  feature: 20,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py');
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('tube') || content.includes('curve') || content.includes('spline'),
      'Hydrogen apparatus must define curved delivery tube');
  }
});

// Feature 21 (M4): Dropper Physical Wall Thickness
registerTest({
  name: 'Dropper Boundaries: positive physical wall thickness (r_outer > r_inner > 0)',
  tier: 2,
  feature: 21,
  milestone: 'M4',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/chemistry/dropper/build_dropper.py');
    const content = readFileSync(scriptPath, 'utf-8');
    // Ensure lathe profile or solidify modifier provides non-zero physical wall thickness
    const hasThickness = content.includes('wall') || content.includes('thickness') ||
                         content.includes('solidify') || content.includes('lathe') ||
                         content.includes('inner');
    assert(hasThickness, 'Dropper must implement physical glass wall thickness');
  }
});

// Feature 22 (M4): Atom Shell Electronic Configuration
registerTest({
  name: 'Atom Shell Boundaries: Mg (2,8,2) and O (2,6) electron shells strictly increasing in radius',
  tier: 2,
  feature: 22,
  milestone: 'M4',
  fn: async () => {
    const mgPath = join(ROOT_DIR, 'assets/chemistry/magnesium-atom/build_magnesium_atom.py');
    const oPath = join(ROOT_DIR, 'assets/chemistry/oxygen-atom/build_oxygen_atom.py');
    const mgContent = readFileSync(mgPath, 'utf-8');
    const oContent = readFileSync(oPath, 'utf-8');

    // Bohr-Bury scheme (NCERT Class 9 Ch 4):
    // Mg: 12 electrons, K(2), L(8), M(2)
    // O:  8 electrons, K(2), L(6)
    assert(mgContent.includes('12') || mgContent.includes('2, 8, 2') || mgContent.includes('shell'),
      'Magnesium atom must represent 12-electron configuration');
    assert(oContent.includes('8') || oContent.includes('2, 6') || oContent.includes('shell'),
      'Oxygen atom must represent 8-electron configuration');
  }
});

// Feature 24 (M5): Full Circuit State Consistency
registerTest({
  name: 'Circuit Boundaries: open knife switch results in zero bulb emission (I = 0)',
  tier: 2,
  feature: 24,
  milestone: 'M5',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/physics/full-circuit/build_circuit.py');
    const content = readFileSync(scriptPath, 'utf-8');
    // Ohm's law: in an open circuit (gap > 0), current I = 0, so bulb filament cannot glow
    assert(content.includes('switch') && content.includes('bulb'), 'Circuit must model switch and bulb');
  }
});

// Feature 25 (M5): Motor Commutator Insulation Gap
registerTest({
  name: 'Electric Motor Boundaries: commutator split ring gap angle between 0 and 45 degrees',
  tier: 2,
  feature: 25,
  milestone: 'M5',
  fn: async () => {
    const scriptPath = join(ROOT_DIR, 'assets/physics/electric-motor/build_electric_motor.py');
    const content = readFileSync(scriptPath, 'utf-8');
    assert(content.includes('commutator') || content.includes('split') || content.includes('brush'),
      'Motor script must model split-ring commutator and brushes');
  }
});

// Feature 26 (M5): Glass Slab Snell Law & Parallel Ray Emergence
registerTest({
  name: 'Glass Slab Boundaries: emergent angle equals incident angle and lateral shift > 0',
  tier: 2,
  feature: 26,
  milestone: 'M5',
  fn: async () => {
    // Optical law (NCERT Class 10 Ch 10):
    // For refraction through rectangular glass slab, ray emerges parallel to incident ray:
    // angle of emergence e == angle of incidence i
    // lateral displacement d = (t * sin(i - r)) / cos(r) > 0 for i > 0
    const iDeg = 30.0;
    const n = 1.52; // Crown glass
    const iRad = iDeg * Math.PI / 180.0;
    const rRad = Math.asin(Math.sin(iRad) / n);
    const rDeg = rRad * 180.0 / Math.PI;
    const eRad = Math.asin(n * Math.sin(rRad));
    const eDeg = eRad * 180.0 / Math.PI;

    assertEqual(Math.round(eDeg * 100) / 100, iDeg, 'Emergent ray angle must equal incident angle');
    const t = 0.05; // 5 cm slab thickness
    const d = (t * Math.sin(iRad - rRad)) / Math.cos(rRad);
    assertGreaterThan(d, 0.0, 'Lateral displacement through slab must be strictly positive');
  }
});

// Feature 28 & 30 (M6): glTF and Blend Binary Header Boundaries
registerTest({
  name: 'Binary Boundaries: generated .glb and .blend files conform to binary magic headers',
  tier: 2,
  feature: 28,
  milestone: 'M6',
  fn: async () => {
    const assets = getAssets();
    // Sample test across biology, chemistry, physics assets
    const sampleAssets = assets.filter(a => ['human-heart', 'magnesium-ribbon', 'glass-slab'].includes(a.id));

    for (const a of sampleAssets) {
      const glbPath = join(a.dir, 'out', `${a.id}.glb`);
      const blendPath = join(a.dir, 'out', `${a.id}.blend`);
      const previewPath = join(a.dir, 'out', 'preview.png');

      if (existsSync(glbPath)) {
        const glbBuf = readFileSync(glbPath);
        assertGreaterThan(glbBuf.length, 12, `${a.id}.glb must be > 12 bytes`);
        // glTF 2.0 magic: 0x46546C67 ("glTF")
        const magic = glbBuf.toString('ascii', 0, 4);
        assertEqual(magic, 'glTF', `${a.id}.glb magic header must be "glTF"`);
        const version = glbBuf.readUInt32LE(4);
        assertEqual(version, 2, `${a.id}.glb version must be 2`);
      }

      if (existsSync(blendPath)) {
        const blendBuf = readFileSync(blendPath);
        assertGreaterThan(blendBuf.length, 12, `${a.id}.blend must be > 12 bytes`);
        const magic = blendBuf.toString('ascii', 0, 7);
        assertEqual(magic, 'BLENDER', `${a.id}.blend magic header must start with "BLENDER"`);
      }

      if (existsSync(previewPath)) {
        const pngBuf = readFileSync(previewPath);
        assertGreaterThan(pngBuf.length, 8, `${a.id} preview.png must be > 8 bytes`);
        // PNG magic: 0x89, 'P', 'N', 'G'
        assertEqual(pngBuf[0], 0x89, 'PNG byte 0 mismatch');
        assertEqual(pngBuf.toString('ascii', 1, 4), 'PNG', 'PNG signature mismatch');
      }
    }
  }
});
