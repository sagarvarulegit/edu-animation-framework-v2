export interface AssetRegistryItem {
  id: string;
  name: string;
  category: 'physics' | 'chemistry' | 'biology' | 'electricity';
  subCategory: string;
  semanticDescription: string;
  dimensions: {
    width_mm: number;
    height_mm: number;
    depth_mm: number;
    weight_g?: number;
  };
  materials: {
    transmission: number;
    ior: number;
    roughness: number;
    metalness: number;
    clearcoat: number;
    clearcoatRoughness: number;
    subsurfaceWeight: number;
    subsurfaceRadius: [number, number, number];
    subsurfaceScale: number;
    color: string;
    description: string;
  };
  anchorPoints: Record<string, [number, number, number]>;
  interactiveStates?: Array<{
    state: string;
    label: string;
    description: string;
  }>;
  cbse: {
    class: number;
    chapter: string;
    ncertActivity: string;
    formulas: string[];
    examTakeaway: string;
  };
  tags: string[];
}

export const ASSET_REGISTRY: AssetRegistryItem[] = [
  // 1. PHYSICS & OPTICS
  {
    id: 'glass-prism-refraction',
    name: 'Glass Prism Refraction & Dispersion Setup',
    category: 'physics',
    subCategory: 'Optics & Waveforms',
    semanticDescription: 'Complete laboratory apparatus for studying light refraction and 7-color rainbow dispersion (VIBGYOR) through an equilateral triangular crown glass prism.',
    dimensions: { width_mm: 320, height_mm: 65, depth_mm: 240, weight_g: 380 },
    materials: {
      transmission: 0.98,
      ior: 1.52,
      roughness: 0.01,
      metalness: 0.0,
      clearcoat: 0.2,
      clearcoatRoughness: 0.02,
      color: '#e0f2fe',
      description: 'Schott N-BK7 Crown Glass with optical clarity'
    },
    anchorPoints: {
      'torch_emitter': [-0.14, -0.045, 0.035],
      'ray_entry_face_AB': [-0.02, 0.015, 0.035],
      'ray_exit_face_AC': [0.025, -0.01, 0.035],
      'screen_center': [0.145, -0.045, 0.038],
      'apex_A': [0.0, 0.032, 0.065]
    },
    interactiveStates: [
      { state: 'unlit', label: '1. Apparatus Setup', description: 'Equilateral prism mounted on white drawing sheet pinned to beechwood board.' },
      { state: 'incident_beam', label: '2. White Light Torch On', description: 'Collimated composite white light incident at face AB at i = 48°.' },
      { state: 'refraction', label: '3. Internal Refraction', description: 'Light slows down in crown glass (n=1.517) and bends towards normal.' },
      { state: 'dispersed_vibgyor', label: '4. VIBGYOR Rainbow Spectrum', description: '7 spectral rays fan out onto observation screen due to wavelength dispersion.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 11: Human Eye and the Colourful World',
      ncertActivity: 'Activity 11.2 - Refraction through a Prism',
      formulas: [
        'Snell\'s Law: n = sin(i) / sin(r1)',
        'Prism Angle Relation: A + D = i + e',
        'Dispersion: D = (n - 1) × A'
      ],
      examTakeaway: 'Violet light (400nm) travels slowest in glass and deviates most (42.6°). Red light (700nm) travels fastest and deviates least (37.8°).'
    },
    tags: ['prism', 'refraction', 'dispersion', 'rainbow', 'snell', 'optics']
  },
  {
    id: 'glass-prism',
    name: 'Triangular Glass Prism (Crown Glass)',
    category: 'physics',
    subCategory: 'Optics & Lenses',
    semanticDescription: 'Standalone equilateral optical triangular glass prism with polished lateral refracting facets.',
    dimensions: { width_mm: 50, height_mm: 60, depth_mm: 50, weight_g: 120 },
    materials: {
      transmission: 0.96,
      ior: 1.517,
      roughness: 0.02,
      metalness: 0.0,
      color: '#f0f9ff',
      description: 'Schott N-BK7 Crown Glass'
    },
    anchorPoints: {
      'apex_top': [0, 0.03, 0.06],
      'base_left': [-0.025, -0.015, 0],
      'base_right': [0.025, -0.015, 0]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 11: Colourful World',
      ncertActivity: 'Activity 11.2',
      formulas: ['Angle of Prism A = 60°', 'r1 + r2 = A'],
      examTakeaway: 'Triangular geometry produces angular deviation rather than parallel lateral displacement.'
    },
    tags: ['prism', 'optics', 'glass', 'refraction']
  },
  {
    id: 'convex-lens',
    name: 'Double Convex Lens & Stand',
    category: 'physics',
    subCategory: 'Optics & Lenses',
    semanticDescription: 'Converging double convex lens mounted on adjustable optical laboratory bench stand.',
    dimensions: { width_mm: 60, height_mm: 140, depth_mm: 60, weight_g: 160 },
    materials: {
      transmission: 0.95,
      ior: 1.52,
      roughness: 0.03,
      metalness: 0.05,
      color: '#e0f2fe',
      description: 'Optical glass lens with blackened brass frame'
    },
    anchorPoints: {
      'optical_centre_O': [0, 0, 0.08],
      'principal_focus_F1': [-0.10, 0, 0.08],
      'principal_focus_F2': [0.10, 0, 0.08]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 10: Light - Reflection and Refraction',
      ncertActivity: 'Activity 10.11 - Image Formation by Convex Lenses',
      formulas: ['Lens Formula: 1/f = 1/v - 1/u', 'Power of Lens: P = 1/f(m)', 'Magnification: m = v/u'],
      examTakeaway: 'Convex lenses converge parallel rays to a real focus; forms virtual & magnified image when object is within focal length f.'
    },
    tags: ['lens', 'convex', 'converging', 'focal-point', 'optics']
  },
  {
    id: 'glass-slab',
    name: 'Rectangular Glass Slab',
    category: 'physics',
    subCategory: 'Optics & Refraction',
    semanticDescription: 'Standard rectangular optical glass block demonstrating parallel boundary refraction and lateral displacement.',
    dimensions: { width_mm: 100, height_mm: 25, depth_mm: 65, weight_g: 220 },
    materials: {
      transmission: 0.94,
      ior: 1.517,
      roughness: 0.02,
      metalness: 0.0,
      color: '#f8fafc',
      description: 'Crown Glass rectangular slab'
    },
    anchorPoints: {
      'incident_point': [-0.03, 0.032, 0.012],
      'emergent_point': [0.03, -0.032, 0.012]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 10: Light',
      ncertActivity: 'Activity 10.10 - Refraction through Rectangular Glass Slab',
      formulas: ['Lateral Shift: d = t × sin(i - r) / cos(r)', 'Emergent angle e = Incident angle i'],
      examTakeaway: 'Emergent ray is parallel to incident ray because opposite refracting faces are parallel; it undergoes lateral displacement.'
    },
    tags: ['slab', 'refraction', 'lateral-shift', 'optics']
  },

  // 2. CHEMISTRY & LABORATORY
  {
    id: 'magnesium-burning-setup',
    name: 'Magnesium Ribbon Combustion Setup',
    category: 'chemistry',
    subCategory: 'Chemical Reactions',
    semanticDescription: 'Complete setup with Bunsen burner, crucible tongs holding magnesium ribbon, and watch glass collecting white magnesium oxide powder.',
    dimensions: { width_mm: 280, height_mm: 220, depth_mm: 200, weight_g: 450 },
    materials: {
      roughness: 0.4,
      metalness: 0.85,
      color: '#94a3b8',
      description: 'Chrome laboratory steel tongs and cast iron Bunsen base'
    },
    anchorPoints: {
      'burner_flame_tip': [0, 0, 0.09],
      'tongs_grip': [0, 0, 0.11],
      'watch_glass_center': [0.08, 0, 0.01]
    },
    interactiveStates: [
      { state: 'unheated', label: '1. Cleaned Ribbon', description: 'Magnesium ribbon cleaned with sandpaper to remove protective oxide layer.' },
      { state: 'heating', label: '2. Heating in Flame', description: 'Ribbon brought into hottest non-luminous flame zone (ignition temperature).' },
      { state: 'burning', label: '3. Dazzling White Flame', description: 'Vigorous exothermic reaction producing intense white light.' },
      { state: 'collected', label: '4. MgO Ash in Watch Glass', description: 'White magnesium oxide (MgO) basic powder collected on watch glass.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 1: Chemical Reactions and Equations',
      ncertActivity: 'Activity 1.1 - Burning of Magnesium Ribbon',
      formulas: [
        '2Mg(s) + O₂(g) → 2MgO(s) + Heat + Light',
        'MgO(s) + H₂O(l) → Mg(OH)₂(aq) [Basic: turns red litmus blue]'
      ],
      examTakeaway: 'Combination reaction & Exothermic reaction. Ribbon is rubbed with sandpaper before burning to remove basic magnesium carbonate coating.'
    },
    tags: ['magnesium', 'combustion', 'reaction', 'chemistry', 'mgo']
  },
  {
    id: 'magnesium-atom',
    name: 'Magnesium Bohr Atom (Mg, Z=12)',
    category: 'chemistry',
    subCategory: 'Atomic Structure & Valence',
    semanticDescription: '3D Bohr atomic model of Magnesium (Z=12) showing a central 12p 12n nucleus and 3 concentric electron shells with electronic configuration 2, 8, 2.',
    dimensions: { width_mm: 280, height_mm: 280, depth_mm: 60, weight_g: 1 },
    materials: {
      roughness: 0.25,
      metalness: 0.2,
      color: '#38bdf8',
      description: 'Luminous cyan electron orbitals with glowing nucleons'
    },
    anchorPoints: {
      'nucleus': [0, 0, 0],
      'k_shell': [0, 0.055, 0],
      'l_shell': [0, 0.095, 0],
      'm_valence_shell': [0, 0.138, 0]
    },
    interactiveStates: [
      { state: 'neutral', label: '1. Neutral Mg Atom [2, 8, 2]', description: 'Ground state with 2 valence electrons in outermost M-shell.' },
      { state: 'excited', label: '2. Thermal Activation', description: 'Excited valence electrons ready for transfer.' },
      { state: 'ionized', label: '3. Mg²⁺ Cation [2, 8]', description: 'Loses 2 valence electrons to achieve stable neon octet.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 1 & Chapter 3: Metals and Non-Metals',
      ncertActivity: 'Activity 1.1 / Ionic Formation',
      formulas: ['Mg [2, 8, 2] → Mg²⁺ [2, 8] + 2e⁻'],
      examTakeaway: 'Electropositive metal that readily loses 2 valence electrons to form divalent cation Mg²⁺.'
    },
    tags: ['magnesium', 'atom', 'bohr', 'chemistry', 'valence']
  },
  {
    id: 'oxygen-atom',
    name: 'Oxygen Bohr Atom (O, Z=8)',
    category: 'chemistry',
    subCategory: 'Atomic Structure & Valence',
    semanticDescription: '3D Bohr atomic model of Oxygen (Z=8) showing an 8p 8n nucleus and 2 concentric electron shells with electronic configuration 2, 6.',
    dimensions: { width_mm: 200, height_mm: 200, depth_mm: 50, weight_g: 1 },
    materials: {
      roughness: 0.25,
      metalness: 0.2,
      color: '#f87171',
      description: 'Luminous rose/red atomic core and electron orbits'
    },
    anchorPoints: {
      'nucleus': [0, 0, 0],
      'k_shell': [0, 0.055, 0],
      'l_valence_shell': [0, 0.095, 0]
    },
    interactiveStates: [
      { state: 'neutral', label: '1. Neutral O Atom [2, 6]', description: 'Ground state with 6 valence electrons (needs 2e⁻ to complete octet).' },
      { state: 'accepting', label: '2. Electron Acceptance', description: 'Incoming electrons occupy the 2 vacancies in L-shell.' },
      { state: 'ionized', label: '3. O²⁻ Oxide Anion [2, 8]', description: 'Completes outer L-shell, achieving stable neon octet.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 1 & Chapter 3: Metals and Non-Metals',
      ncertActivity: 'Activity 1.1 / Chemical Combination',
      formulas: ['O [2, 6] + 2e⁻ → O²⁻ [2, 8]'],
      examTakeaway: 'Electronegative non-metal that gains 2 electrons to form oxide anion O²⁻.'
    },
    tags: ['oxygen', 'atom', 'bohr', 'chemistry', 'valence']
  },
  {
    id: 'magnesium-oxide-lattice',
    name: 'Magnesium Oxide Crystal Lattice & Ionic Bond',
    category: 'chemistry',
    subCategory: 'Ionic Compounds & Bonding',
    semanticDescription: '3D animated sub-microscopic simulation of electron transfer from Mg to O and resulting MgO ionic crystal lattice.',
    dimensions: { width_mm: 240, height_mm: 240, depth_mm: 240, weight_g: 5 },
    materials: {
      roughness: 0.2,
      metalness: 0.3,
      color: '#facc15',
      description: 'Electrostatic force fields and alternating ionic lattice'
    },
    anchorPoints: {
      'origin': [0, 0, 0],
      'corner_mg': [-0.08, -0.08, -0.08],
      'corner_o': [0.08, 0.08, 0.08]
    },
    interactiveStates: [
      { state: 'reactants', label: '1. Reactant Atoms (Mg + O)', description: 'Neutral magnesium and oxygen atoms before excitation.' },
      { state: 'transfer', label: '2. 2e⁻ Electron Transfer Arc', description: 'Valence electrons glide along 3D Bézier trajectories into oxygen vacancies.' },
      { state: 'ions', label: '3. Ionization (Mg²⁺ + O²⁻)', description: 'Energy release flash as both ions achieve stable noble gas octets.' },
      { state: 'bonded', label: '4. Coulomb Attraction & Lattice', description: 'Opposite charges attract forming strong ionic bond in MgO lattice.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 3: Metals and Non-Metals',
      ncertActivity: 'Activity 3.13 - Properties of Ionic Compounds',
      formulas: ['2Mg + O₂ → 2MgO', 'Mg²⁺ + O²⁻ → MgO (Ionic Bond)'],
      examTakeaway: 'High melting and boiling points due to strong inter-ionic electrostatic forces of attraction in crystalline solids.'
    },
    tags: ['lattice', 'mgo', 'crystal', 'ionic', 'chemistry']
  },
  {
    id: 'bunsen-burner',
    name: 'Laboratory Bunsen Burner',
    category: 'chemistry',
    subCategory: 'Laboratory Heating',
    semanticDescription: 'Cast iron laboratory Bunsen burner with adjustable air collar, brass barrel, and gas nozzle.',
    dimensions: { width_mm: 90, height_mm: 150, depth_mm: 90, weight_g: 280 },
    materials: {
      roughness: 0.35,
      metalness: 0.9,
      color: '#475569',
      description: 'Heavy cast-iron base with machined brass collar'
    },
    anchorPoints: {
      'gas_inlet': [-0.04, 0, 0.015],
      'air_collar': [0, 0, 0.04],
      'flame_base': [0, 0, 0.15],
      'flame_apex': [0, 0, 0.22]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 4: Carbon and its Compounds',
      ncertActivity: 'Heating apparatus in chemical activities',
      formulas: ['CH₄ + 2O₂ → CO₂ + 2H₂O + Heat (Clean blue flame when air hole open)'],
      examTakeaway: 'Open air holes supply sufficient oxygen producing a non-luminous, soot-free blue flame (complete combustion).'
    },
    tags: ['burner', 'bunsen', 'heat', 'chemistry', 'flame']
  },
  {
    id: 'beaker',
    name: 'Graduated Glass Beaker (250ml)',
    category: 'chemistry',
    subCategory: 'Laboratory Glassware',
    semanticDescription: 'Low-form Pyrex borosilicate glass beaker with volume graduations and pouring spout.',
    dimensions: { width_mm: 70, height_mm: 95, depth_mm: 70, weight_g: 110 },
    materials: {
      transmission: 0.92,
      ior: 1.47,
      roughness: 0.05,
      metalness: 0.0,
      color: '#e0f2fe',
      description: 'Borosilicate 3.3 laboratory glass'
    },
    anchorPoints: {
      'rim_top': [0, 0, 0.095],
      'spout': [0.035, 0, 0.095],
      'liquid_fill_100ml': [0, 0, 0.045]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 2: Acids, Bases and Salts',
      ncertActivity: 'Activity 2.3 - Reaction of acids with metals',
      formulas: ['Zn + H₂SO₄ → ZnSO₄ + H₂↑'],
      examTakeaway: 'Used for holding solutions, dilution of strong acids (always add acid slowly to water with stirring).'
    },
    tags: ['beaker', 'glassware', 'chemistry', 'solution']
  },

  // 3. BIOLOGY & LIFE PROCESSES
  {
    id: 'human-heart',
    name: 'Human Heart (Double Circulation)',
    category: 'biology',
    subCategory: 'Anatomy & Life Processes',
    semanticDescription: 'Anatomical model of the four-chambered human heart illustrating pulmonary and systemic blood circulation circuits.',
    dimensions: { width_mm: 120, height_mm: 140, depth_mm: 100, weight_g: 300 },
    materials: {
      roughness: 0.6,
      metalness: 0.1,
      color: '#dc2626',
      description: 'Myocardial muscular tissue shader with vascular branches'
    },
    anchorPoints: {
      'superior_vena_cava': [-0.02, 0.02, 0.09],
      'aorta_arch': [0.01, 0.01, 0.11],
      'pulmonary_artery': [0.02, -0.01, 0.08],
      'left_ventricle': [0.03, -0.02, 0.02],
      'right_ventricle': [-0.03, -0.02, 0.02]
    },
    interactiveStates: [
      { state: 'deoxygenated', label: '1. Deoxygenated Return', description: 'Blood enters Right Atrium from body via Vena Cava → Right Ventricle.' },
      { state: 'pulmonary', label: '2. Pulmonary Loop', description: 'Right Ventricle pumps blood to lungs via Pulmonary Artery for oxygenation.' },
      { state: 'oxygenated', label: '3. Oxygenated Return', description: 'Oxygenated blood returns to Left Atrium via Pulmonary Veins → Left Ventricle.' },
      { state: 'systemic', label: '4. Systemic Pumping', description: 'Thick muscular Left Ventricle contracts forcefully to pump blood via Aorta to entire body.' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 6: Life Processes',
      ncertActivity: 'Section 6.4.1 - Transportation in Human Beings',
      formulas: ['Cardiac Output = Stroke Volume × Heart Rate (≈ 70ml × 72 bpm ≈ 5 L/min)'],
      examTakeaway: 'Double Circulation: Blood flows twice through the heart during one complete cycle. Left ventricle has thickest walls to pump blood throughout body.'
    },
    tags: ['heart', 'circulation', 'biology', 'aorta', 'ventricle']
  },
  {
    id: 'human-eye',
    name: 'Human Eye Anatomy & Defects',
    category: 'biology',
    subCategory: 'Anatomy & Vision',
    semanticDescription: 'Detailed sagittal cross-section of the human eyeball showing Cornea, Iris, Pupil, Crystalline Lens, Ciliary Muscles, and Retina.',
    dimensions: { width_mm: 80, height_mm: 80, depth_mm: 80, weight_g: 90 },
    materials: {
      roughness: 0.3,
      metalness: 0.1,
      color: '#f8fafc',
      description: 'Sclera, cornea, and retinal layers'
    },
    anchorPoints: {
      'cornea_front': [0, 0, 0.04],
      'pupil_center': [0, 0, 0.032],
      'lens_center': [0, 0, 0.024],
      'retina_fovea': [0, 0, -0.038],
      'optic_nerve': [0.01, -0.005, -0.045]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 11: Human Eye and Colourful World',
      ncertActivity: 'Section 11.1 - The Human Eye',
      formulas: ['Least Distance of Distinct Vision (D) = 25 cm', 'Far Point = Infinity'],
      examTakeaway: 'Ciliary muscles adjust focal length of eye lens (Power of Accommodation). Myopia is corrected by concave lens; Hypermetropia by convex lens.'
    },
    tags: ['eye', 'retina', 'lens', 'vision', 'biology']
  },

  // 4. ELECTRICITY & CIRCUITS
  {
    id: 'full-circuit',
    name: 'Ohm\'s Law Circuit Board Setup',
    category: 'electricity',
    subCategory: 'Electric Circuits',
    semanticDescription: 'Complete laboratory circuit setup for verifying Ohm\'s Law: battery eliminator, plug key switch, rheostat, resistor wire, ammeter (series), and voltmeter (parallel).',
    dimensions: { width_mm: 360, height_mm: 80, depth_mm: 260, weight_g: 650 },
    materials: {
      roughness: 0.35,
      metalness: 0.7,
      color: '#334155',
      description: 'Bakelite circuit base with copper binding posts'
    },
    anchorPoints: {
      'battery_pos': [-0.12, -0.08, 0.03],
      'ammeter_pos': [-0.04, 0.06, 0.03],
      'resistor_terminal_A': [0.04, 0.06, 0.03],
      'voltmeter_pos': [0.04, 0.11, 0.04],
      'rheostat_slider': [0.12, -0.04, 0.03]
    },
    interactiveStates: [
      { state: 'key_open', label: '1. Open Circuit', description: 'Plug key open: zero current flowing (I = 0A, V = 0V).' },
      { state: 'key_closed', label: '2. Closed Circuit', description: 'Key plugged in: current flows from positive to negative terminal.' },
      { state: 'rheostat_adjusted', label: '3. Rheostat Varied', description: 'Sliding contact adjusted: V and I change proportionally (V/I = Constant R).' }
    ],
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Electricity',
      ncertActivity: 'Activity 12.1 - Verification of Ohm\'s Law',
      formulas: ['Ohm\'s Law: V = I × R', 'Resistance: R = ρ × L / A', 'Joule\'s Heating: H = I² × R × t'],
      examTakeaway: 'Ammeter is always connected in series (low resistance); Voltmeter is always connected in parallel across the resistor (high resistance).'
    },
    tags: ['circuit', 'ohms-law', 'resistor', 'ammeter', 'voltmeter', 'electricity']
  },
  {
    id: 'voltmeter',
    name: 'Analog DC Laboratory Voltmeter',
    category: 'electricity',
    subCategory: 'Electrical Meters',
    semanticDescription: 'Moving-coil analog DC voltmeter with red (positive) and black (negative) binding terminals, mirrored dial (0-3V), and zero-adjustment screw.',
    dimensions: { width_mm: 85, height_mm: 100, depth_mm: 85, weight_g: 210 },
    materials: {
      roughness: 0.3,
      metalness: 0.6,
      color: '#1e293b',
      description: 'High-impact bakelite casing with glass window'
    },
    anchorPoints: {
      'pos_terminal_red': [-0.025, -0.035, 0.02],
      'neg_terminal_black': [0.025, -0.035, 0.02],
      'needle_pivot': [0, 0.015, 0.05]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Electricity',
      ncertActivity: 'Activity 12.1',
      formulas: ['Least Count (LC) = Range / Total Divisions (e.g. 3V / 30 div = 0.1V/div)'],
      examTakeaway: 'Has very high internal resistance to avoid drawing significant current from the circuit; must be connected in parallel.'
    },
    tags: ['voltmeter', 'meter', 'voltage', 'electricity']
  },
  {
    id: 'ammeter',
    name: 'Analog DC Laboratory Ammeter',
    category: 'electricity',
    subCategory: 'Electrical Meters',
    semanticDescription: 'Moving-coil analog DC ammeter (0-3A) for measuring electric current flowing through circuit branches.',
    dimensions: { width_mm: 85, height_mm: 100, depth_mm: 85, weight_g: 210 },
    materials: {
      roughness: 0.3,
      metalness: 0.6,
      color: '#1e293b',
      description: 'Bakelite casing with glass dial'
    },
    anchorPoints: {
      'pos_terminal_red': [-0.025, -0.035, 0.02],
      'neg_terminal_black': [0.025, -0.035, 0.02]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Electricity',
      ncertActivity: 'Activity 12.1',
      formulas: ['Current: I = Q / t (Amperes)'],
      examTakeaway: 'Has near-zero internal resistance so it does not alter total circuit current; must be connected in series.'
    },
    tags: ['ammeter', 'meter', 'current', 'electricity']
  },
  // --- BATCH 1: PHYSICS & ELECTROMAGNETISM ---
  {
    id: 'convex-mirror',
    name: 'Spherical Convex Mirror (Diverging)',
    category: 'physics',
    subCategory: 'Optics & Mirrors',
    semanticDescription: 'Spherical diverging convex mirror on optical bench stand with wide field of view.',
    dimensions: { width_mm: 100, height_mm: 180, depth_mm: 90, weight_g: 220 },
    materials: {
      roughness: 0.015,
      metalness: 1.0,
      color: '#f8fafc',
      description: 'Silver coated front surface on glass substrate'
    },
    anchorPoints: {
      'pole_P': [0, 0, 0.12],
      'focus_F_virtual': [0, -0.075, 0.12],
      'center_C_virtual': [0, -0.15, 0.12]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 9: Light – Reflection and Refraction',
      ncertActivity: 'Activity 9.5 & 9.6 - Reflection by Convex Mirrors',
      formulas: ['1/v + 1/u = 1/f', 'm = -v/u = h\'/h', 'R = 2f'],
      examTakeaway: 'Always forms virtual, erect, and diminished images behind the mirror regardless of object position. Ideal for vehicle rear-view mirrors.'
    },
    tags: ['mirror', 'convex', 'diverging', 'optics', 'reflection', 'virtual-image']
  },
  {
    id: 'optical-bench',
    name: 'Dual-Rail Laboratory Optical Bench',
    category: 'physics',
    subCategory: 'Optics & Benches',
    semanticDescription: '1-meter laboratory optical bench with millimeter scale, leveling screws, and sliding riders for candle, lens, and screen.',
    dimensions: { width_mm: 1050, height_mm: 280, depth_mm: 160, weight_g: 3400 },
    materials: {
      roughness: 0.2,
      metalness: 0.95,
      color: '#e2e8f0',
      description: 'Machined stainless steel dual rails with cast iron base'
    },
    anchorPoints: {
      'candle_flame': [-0.35, 0, 0.23],
      'lens_center': [0, 0, 0.22],
      'screen_center': [0.35, 0, 0.22]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 9: Light – Reflection and Refraction',
      ncertActivity: 'Activity 9.10 - Image Formation by Convex Lens',
      formulas: ['Lens Formula: 1/f = 1/v - 1/u', 'Power: P = 1/f(m)', 'Magnification: m = v/u'],
      examTakeaway: 'When candle is at 2F1 (u = 2f), the real inverted equal image forms on screen at 2F2 (v = 2f).'
    },
    tags: ['optical-bench', 'lens-formula', 'focal-length', 'optics', 'candle', 'screen']
  },
  {
    id: 'bar-magnet',
    name: 'Permanent AlNiCo Bar Magnet',
    category: 'physics',
    subCategory: 'Magnetism & Electromagnetism',
    semanticDescription: 'Rectangular AlNiCo permanent bar magnet with red North and blue South poles and 3D magnetic field flux lines.',
    dimensions: { width_mm: 120, height_mm: 24, depth_mm: 16, weight_g: 180 },
    materials: {
      roughness: 0.3,
      metalness: 0.2,
      color: '#dc2626',
      description: 'Painted cast AlNiCo alloy magnet'
    },
    anchorPoints: {
      'north_pole': [0.05, 0, 0.008],
      'south_pole': [-0.05, 0, 0.008],
      'neutral_center': [0, 0, 0.008]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Magnetic Effects of Electric Current',
      ncertActivity: 'Activity 12.1 & 12.2 - Field Lines around a Bar Magnet',
      formulas: ['B = (mu_0 / 4pi) * (2M / r^3)'],
      examTakeaway: 'Field lines emerge from North pole and merge at South pole outside the magnet; no two field lines ever cross.'
    },
    tags: ['bar-magnet', 'magnetism', 'magnetic-field', 'north-pole', 'south-pole', 'compass']
  },
  {
    id: 'solenoid',
    name: 'Helical Current Solenoid',
    category: 'physics',
    subCategory: 'Magnetism & Electromagnetism',
    semanticDescription: 'Long helical coil of insulated copper wire producing uniform parallel axial magnetic field inside.',
    dimensions: { width_mm: 200, height_mm: 100, depth_mm: 120, weight_g: 450 },
    materials: {
      roughness: 0.25,
      metalness: 0.95,
      color: '#ea580c',
      description: 'Enameled copper magnet wire on insulating cylinder'
    },
    anchorPoints: {
      'core_center': [0, 0, 0.05],
      'north_face': [0.08, 0, 0.05],
      'south_face': [-0.08, 0, 0.05],
      'pos_terminal': [-0.06, -0.03, 0.018],
      'neg_terminal': [0.06, -0.03, 0.018]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Magnetic Effects of Electric Current',
      ncertActivity: 'Activity 12.6 - Magnetic Field due to Solenoid',
      formulas: ['B = mu_0 * n * I', 'n = N / L'],
      examTakeaway: 'Internal field is uniform and parallel; behaves identically to a bar magnet and creates an electromagnet with soft iron core.'
    },
    tags: ['solenoid', 'electromagnet', 'magnetic-field', 'uniform-field', 'copper-coil']
  },
  {
    id: 'electric-motor',
    name: 'DC Electric Motor Working Model',
    category: 'physics',
    subCategory: 'Electromechanical Devices',
    semanticDescription: 'Working direct-current electric motor featuring rectangular armature coil ABCD, split-ring commutator, carbon brushes, and curved field magnets.',
    dimensions: { width_mm: 180, height_mm: 140, depth_mm: 160, weight_g: 650 },
    materials: {
      roughness: 0.3,
      metalness: 0.8,
      color: '#334155',
      description: 'Copper armature winding with brass commutator and steel axle'
    },
    anchorPoints: {
      'armature_center': [0, 0, 0.07],
      'split_ring_commutator': [0, -0.045, 0.07],
      'brush_X': [0.01, -0.045, 0.07],
      'brush_Y': [-0.01, -0.045, 0.07],
      'output_pulley': [0, 0.072, 0.07]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Magnetic Effects of Electric Current',
      ncertActivity: 'Section 12.3 - Working of Electric Motor',
      formulas: ['Force: F = I * L * B * sin(theta)', 'Torque: tau = N * I * A * B'],
      examTakeaway: 'Converts electrical energy to mechanical energy via Fleming\'s Left-Hand Rule; split-ring commutator reverses current every half rotation.'
    },
    tags: ['motor', 'dc-motor', 'armature', 'commutator', 'split-ring', 'flemings-left-hand-rule']
  },
  {
    id: 'galvanometer',
    name: 'Center-Zero Moving Coil Galvanometer',
    category: 'electricity',
    subCategory: 'Electrical Meters',
    semanticDescription: 'Sensitive center-zero instrument with needle pointer indicating current magnitude and direction.',
    dimensions: { width_mm: 90, height_mm: 80, depth_mm: 70, weight_g: 220 },
    materials: {
      roughness: 0.4,
      metalness: 0.3,
      color: '#0f172a',
      description: 'Black Bakelite casing with acrylic viewing window'
    },
    anchorPoints: {
      'pos_terminal_red': [0.028, 0.025, 0.078],
      'neg_terminal_black': [-0.028, 0.025, 0.078],
      'center_zero_pointer': [0, -0.04, 0.042]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 12: Magnetic Effects of Electric Current',
      ncertActivity: 'Activity 12.8 - Electromagnetic Induction',
      formulas: ['Deflection: theta proportional to I', 'Induced EMF: e = -dPhi/dt'],
      examTakeaway: 'Stays at center 0 when idle; momentary left/right deflection proves direction of induced current when magnet moves relative to coil.'
    },
    tags: ['galvanometer', 'meter', 'center-zero', 'faradays-law', 'induced-current']
  },
  // --- BATCH 2: CHEMISTRY REACTIONS & APPARATUS ---
  {
    id: 'water-electrolysis-apparatus',
    name: 'Electrolysis of Water Voltameter Apparatus',
    category: 'chemistry',
    subCategory: 'Decomposition Reactions',
    semanticDescription: 'Electrolytic decomposition apparatus with two inverted graduated tubes over carbon electrodes demonstrating 2:1 H2:O2 volume ratio.',
    dimensions: { width_mm: 150, height_mm: 220, depth_mm: 130, weight_g: 480 },
    materials: {
      transmission: 0.95,
      ior: 1.52,
      roughness: 0.02,
      metalness: 0.0,
      color: '#e0f2fe',
      description: 'Borosilicate glass tubes with graphite electrodes'
    },
    anchorPoints: {
      'anode_o2_headspace': [-0.022, 0, 0.15],
      'cathode_h2_headspace': [0.022, 0, 0.14],
      'anode_terminal_pos': [-0.045, -0.045, 0.018],
      'cathode_terminal_neg': [0.045, -0.045, 0.018]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 1: Chemical Reactions and Equations',
      ncertActivity: 'Activity 1.7 - Electrolysis of Water',
      formulas: ['2H2O(l) -> 2H2(g) + O2(g)'],
      examTakeaway: 'Water decomposes into hydrogen and oxygen in 2:1 volume ratio; tested with pop sound for H2 and rekindling splinter for O2.'
    },
    tags: ['electrolysis', 'water', 'hydrogen', 'oxygen', 'decomposition', 'stoichiometry']
  },
  {
    id: 'displacement-reaction-setup',
    name: 'Iron in Copper Sulphate Displacement Setup',
    category: 'chemistry',
    subCategory: 'Displacement Reactions',
    semanticDescription: 'Wooden test tube stand holding reference CuSO4 tube and reaction tube with iron nail developing reddish-brown copper deposit.',
    dimensions: { width_mm: 140, height_mm: 200, depth_mm: 70, weight_g: 310 },
    materials: {
      roughness: 0.5,
      metalness: 0.1,
      color: '#78350f',
      description: 'Beechwood rack with borosilicate test tubes'
    },
    anchorPoints: {
      'tube_a_reference': [-0.025, 0, 0.07],
      'tube_b_reaction': [0.025, 0, 0.07],
      'suspended_nail': [0.025, 0, 0.06]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 1: Chemical Reactions and Equations',
      ncertActivity: 'Activity 1.9 - Displacement Reaction',
      formulas: ['Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s)'],
      examTakeaway: 'Iron displaces copper from CuSO4 because iron is higher in reactivity series; blue solution turns pale green and nail gets reddish-brown coating.'
    },
    tags: ['displacement-reaction', 'iron-nail', 'copper-sulphate', 'reactivity-series', 'redox']
  },
  {
    id: 'tripod-wire-gauze',
    name: 'Tripod Stand with Wire Gauze & China Dish',
    category: 'chemistry',
    subCategory: 'Laboratory Hardware',
    semanticDescription: 'Heavy cast-iron tripod supporting nichrome wire gauze with ceramic pad and porcelain evaporating dish for heating reactions.',
    dimensions: { width_mm: 160, height_mm: 220, depth_mm: 160, weight_g: 520 },
    materials: {
      roughness: 0.6,
      metalness: 0.7,
      color: '#1e293b',
      description: 'Cast iron legs with glazed porcelain evaporating dish'
    },
    anchorPoints: {
      'gauze_surface': [0, 0, 0.168],
      'dish_cavity': [0, 0, 0.176]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 1: Chemical Reactions and Equations',
      ncertActivity: 'Activity 1.11 - Oxidation and Reduction of Copper',
      formulas: ['2Cu + O2 -> 2CuO (Black)', 'CuO + H2 -> Cu + H2O (Brown)'],
      examTakeaway: 'Wire gauze spreads burner flame evenly; heating brown copper powder turns surface black due to copper oxide formation.'
    },
    tags: ['tripod-stand', 'wire-gauze', 'china-dish', 'oxidation', 'copper-oxide', 'heating']
  },
  {
    id: 'hydrogen-evolution-apparatus',
    name: 'Zinc & Acid Hydrogen Gas Evolution Apparatus',
    category: 'chemistry',
    subCategory: 'Gas Evolution Reactions',
    semanticDescription: 'Conical flask with zinc granules and dil. H2SO4, thistle funnel, delivery tube, soap trough, and pop-sound candle.',
    dimensions: { width_mm: 260, height_mm: 220, depth_mm: 140, weight_g: 540 },
    materials: {
      transmission: 0.94,
      ior: 1.52,
      roughness: 0.02,
      metalness: 0.0,
      color: '#e0f2fe',
      description: 'Borosilicate glassware with soap solution trough'
    },
    anchorPoints: {
      'flask_reaction_zone': [-0.06, 0, 0.02],
      'soap_bubble_rise': [0.07, 0, 0.12],
      'testing_candle': [0.125, 0, 0.14]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 2: Acids, Bases and Salts',
      ncertActivity: 'Activity 2.1 - Reaction of Zinc with Acid',
      formulas: ['Zn(s) + H2SO4(aq) -> ZnSO4(aq) + H2(g)', '2H2 + O2 -> 2H2O (Pop sound)'],
      examTakeaway: 'Active metals react with dilute acids to evolve hydrogen gas; trapped in soap bubbles and confirmed via characteristic pop sound.'
    },
    tags: ['hydrogen-gas', 'zinc-granules', 'acids-bases-salts', 'pop-sound', 'soap-bubbles']
  },
  // --- BATCH 3: CARBON & MOLECULAR CHEMISTRY ---
  {
    id: 'methane-molecule',
    name: 'Methane (CH4) Tetrahedral Molecule',
    category: 'chemistry',
    subCategory: 'Carbon Compounds',
    semanticDescription: 'Ball-and-stick covalent molecular model of methane featuring sp3 tetrahedral geometry with 109.5 degree bond angles.',
    dimensions: { width_mm: 110, height_mm: 110, depth_mm: 110, weight_g: 65 },
    materials: {
      roughness: 0.3,
      metalness: 0.15,
      color: '#334155',
      description: 'CPK color-coded carbon (gray) and hydrogen (white) spheres'
    },
    anchorPoints: {
      'carbon_center': [0, 0, 0],
      'hydrogen_vertex_1': [0.032, 0.032, 0.032],
      'hydrogen_vertex_2': [0.032, -0.032, -0.032],
      'hydrogen_vertex_3': [-0.032, 0.032, -0.032],
      'hydrogen_vertex_4': [-0.032, -0.032, 0.032]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 4: Carbon and its Compounds',
      ncertActivity: 'Section 4.1 - Covalent Bonding in Methane',
      formulas: ['CH4', 'H-C-H Bond Angle = 109.5°', 'Covalent single bonds = 4'],
      examTakeaway: 'Carbon shares 4 valence electrons with 4 hydrogen atoms to complete its octet, producing non-polar tetrahedral methane.'
    },
    tags: ['methane', 'ch4', 'carbon-compounds', 'tetrahedral', 'covalent-bond', 'hydrocarbon']
  },
  {
    id: 'diamond-lattice',
    name: 'Diamond 3D Tetrahedral Crystal Lattice',
    category: 'chemistry',
    subCategory: 'Carbon Allotropes',
    semanticDescription: 'Rigid three-dimensional tetrahedral covalent network lattice of diamond allotrope.',
    dimensions: { width_mm: 130, height_mm: 130, depth_mm: 130, weight_g: 140 },
    materials: {
      transmission: 0.5,
      ior: 2.42,
      roughness: 0.08,
      metalness: 0.1,
      color: '#f8fafc',
      description: 'High-refraction diamond crystal nodes with covalent rods'
    },
    anchorPoints: {
      'unit_center': [0, 0, 0]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 4: Carbon and its Compounds',
      ncertActivity: 'Section 4.1.2 - Allotropes of Carbon',
      formulas: ['Coordination number = 4', 'Refractive Index n = 2.42'],
      examTakeaway: 'Each carbon atom is covalently bonded to 4 others in rigid 3D framework; no free electrons make it an insulator and the hardest substance.'
    },
    tags: ['diamond', 'allotrope', 'carbon', 'crystal-lattice', 'tetrahedral-network']
  },
  {
    id: 'graphite-lattice',
    name: 'Graphite Layered Hexagonal Lattice',
    category: 'chemistry',
    subCategory: 'Carbon Allotropes',
    semanticDescription: 'Layered hexagonal planar carbon network of graphite showing in-plane covalent rings and weak interlayer van der Waals bonding.',
    dimensions: { width_mm: 140, height_mm: 70, depth_mm: 100, weight_g: 110 },
    materials: {
      roughness: 0.4,
      metalness: 0.5,
      color: '#1e293b',
      description: 'Graphite carbon atoms with delocalized pi-bonding'
    },
    anchorPoints: {
      'layer_top': [0, 0, 0.021],
      'layer_bottom': [0, 0, -0.021]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 4: Carbon and its Compounds',
      ncertActivity: 'Section 4.1.2 - Allotropes of Carbon',
      formulas: ['In-plane sp2 hybridized hexagonal rings', 'Interlayer distance = 0.34nm'],
      examTakeaway: 'Each carbon forms 3 bonds in a plane; the fourth delocalized electron gives electrical conductivity; layers slide easily making it soft and slippery.'
    },
    tags: ['graphite', 'allotrope', 'carbon', 'hexagonal-layers', 'van-der-waals', 'conductor']
  },
  {
    id: 'soap-micelle',
    name: 'Soap Micelle with Central Oil Droplet',
    category: 'chemistry',
    subCategory: 'Soaps and Detergents',
    semanticDescription: 'Spherical colloidal micelle aggregate with inward hydrophobic hydrocarbon tails trapping grease and outward hydrophilic ionic heads.',
    dimensions: { width_mm: 120, height_mm: 120, depth_mm: 120, weight_g: 75 },
    materials: {
      roughness: 0.3,
      metalness: 0.1,
      color: '#0284c7',
      description: 'Polar ionic carboxylate heads with golden hydrocarbon tails'
    },
    anchorPoints: {
      'oil_droplet_center': [0, 0, 0]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 4: Carbon and its Compounds',
      ncertActivity: 'Section 4.3.4 - Cleansing Action of Soap',
      formulas: ['C17H35COO- Na+ (Sodium Stearate)', 'Hydrophobic tail in oil; Hydrophilic head in water'],
      examTakeaway: 'Micelles keep grease trapped in a colloidal emulsion; electrostatic repulsion between like-charged heads prevents aggregation so dirt washes away.'
    },
    tags: ['soap', 'micelle', 'cleansing-action', 'hydrophilic', 'hydrophobic', 'colloid', 'emulsion']
  },
  // --- BATCH 4: BIOLOGY & ECOLOGY ---
  {
    id: 'human-respiratory-system',
    name: 'Human Respiratory System & Alveoli Cluster',
    category: 'biology',
    subCategory: 'Human Physiology',
    semanticDescription: 'Anatomical model showing larynx, trachea with cartilage C-rings, bronchi, bilateral lungs, diaphragm, and terminal alveoli cluster.',
    dimensions: { width_mm: 220, height_mm: 320, depth_mm: 160, weight_g: 750 },
    materials: {
      roughness: 0.5,
      metalness: 0.05,
      color: '#f43f5e',
      description: 'Vascular lung parenchyma with cartilage rings and capillary loops'
    },
    anchorPoints: {
      'trachea_carina': [0, 0, 0.11],
      'left_lung_center': [-0.048, 0, 0.06],
      'right_lung_center': [0.052, 0, 0.06],
      'diaphragm_center': [0, 0, -0.01],
      'alveolus_micro_sac': [0.08, -0.04, 0.02]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 5: Life Processes',
      ncertActivity: 'Section 5.2.2 - Respiration in Humans',
      formulas: ['C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy (38 ATP)', 'Alveolar Area approx 80 m^2'],
      examTakeaway: 'Tracheal cartilage rings prevent airway collapse; thin-walled vascular alveoli maximize surface area for oxygen/carbon dioxide diffusion.'
    },
    tags: ['respiratory-system', 'lungs', 'trachea', 'bronchi', 'alveoli', 'diaphragm', 'gas-exchange']
  },
  {
    id: 'human-excretory-system',
    name: 'Human Excretory System (Kidneys & Bladder)',
    category: 'biology',
    subCategory: 'Human Physiology',
    semanticDescription: 'Complete urinary tract model showing paired bean-shaped kidneys, renal artery/vein, ureters, urinary bladder, and urethra.',
    dimensions: { width_mm: 200, height_mm: 300, depth_mm: 110, weight_g: 680 },
    materials: {
      roughness: 0.5,
      metalness: 0.08,
      color: '#831843',
      description: 'Renal cortex with vascular supply and muscular bladder'
    },
    anchorPoints: {
      'right_kidney_hilum': [-0.052, 0, 0.128],
      'left_kidney_hilum': [0.052, 0, 0.138],
      'urinary_bladder': [0, 0, 0.016],
      'urethra_exit': [0, 0, -0.01]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 5: Life Processes',
      ncertActivity: 'Section 5.4.1 - Excretion in Human Beings',
      formulas: ['Renal Blood Flow: 180 L/day filtered -> 1.5 L/day urine excreted'],
      examTakeaway: 'Removes toxic nitrogenous wastes (urea); urine passes from kidney pelvis through ureters to bladder and is discharged through urethra.'
    },
    tags: ['excretory-system', 'kidneys', 'ureter', 'urinary-bladder', 'urethra', 'osmoregulation']
  },
  {
    id: 'nephron',
    name: 'Nephron Microscopic Renal Filtration Unit',
    category: 'biology',
    subCategory: 'Cellular & Tissue Anatomy',
    semanticDescription: 'Kidney filtration unit featuring Bowman\'s capsule with glomerulus capillary tuft, PCT, Loop of Henle, DCT, and collecting duct.',
    dimensions: { width_mm: 140, height_mm: 220, depth_mm: 60, weight_g: 85 },
    materials: {
      roughness: 0.45,
      metalness: 0.05,
      color: '#fbbf24',
      description: 'Epithelial reabsorptive nephron tubules with vascular glomerulus'
    },
    anchorPoints: {
      'bowmans_capsule': [-0.05, 0, 0.11],
      'glomerulus_tuft': [-0.05, 0, 0.112],
      'loop_of_henle_bend': [-0.012, 0, -0.06],
      'collecting_duct_top': [0.05, 0, 0.12]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 5: Life Processes',
      ncertActivity: 'Section 5.4.1 - Structure of Nephron',
      formulas: ['Filtration = Glomerular Hydrostatic Pressure - Osmotic Pressure', 'Selective Reabsorption: Glucose, Amino acids, Salts, Water'],
      examTakeaway: 'Ultrafiltration occurs at the glomerulus; selective reabsorption of essential nutrients and water occurs along the tubule and Loop of Henle.'
    },
    tags: ['nephron', 'kidney', 'filtration', 'bowmans-capsule', 'glomerulus', 'loop-of-henle']
  },
  {
    id: 'stoma',
    name: 'Leaf Stomatal Apparatus & Guard Cells',
    category: 'biology',
    subCategory: 'Plant Anatomy',
    semanticDescription: 'Paired bean-shaped guard cells with differential inner/outer wall thickness, chloroplast granules, and open stomatal pore.',
    dimensions: { width_mm: 140, height_mm: 140, depth_mm: 40, weight_g: 60 },
    materials: {
      roughness: 0.35,
      metalness: 0.05,
      color: '#22c55e',
      description: 'Living guard cells with thick inner cellulosic walls and chloroplasts'
    },
    anchorPoints: {
      'stomatal_pore_center': [0, 0, 0],
      'left_guard_cell': [-0.024, 0, 0],
      'right_guard_cell': [0.024, 0, 0]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 5: Life Processes',
      ncertActivity: 'Activity 5.1 - Observation of Stomata in Leaf Peel',
      formulas: ['CO2 + H2O -> Photosynthesis (Stoma open)', 'Transpiration pull = evaporation through stomata'],
      examTakeaway: 'Water inflow causes guard cells to swell and curve outward due to thick inelastic inner walls, opening the pore; water loss closes it.'
    },
    tags: ['stoma', 'stomata', 'guard-cells', 'chloroplasts', 'turgidity', 'transpiration']
  },
  {
    id: 'reflex-arc',
    name: 'Somatic Reflex Arc Neural Pathway',
    category: 'biology',
    subCategory: 'Neuroanatomy',
    semanticDescription: 'Neural emergency pathway linking skin thermal receptor, sensory neuron, spinal cord gray matter with interneuron, motor neuron, and effector muscle.',
    dimensions: { width_mm: 240, height_mm: 160, depth_mm: 80, weight_g: 130 },
    materials: {
      roughness: 0.4,
      metalness: 0.1,
      color: '#3b82f6',
      description: 'Color-coded sensory (blue) and motor (red) nerve tracts'
    },
    anchorPoints: {
      'skin_receptor': [-0.10, 0, -0.03],
      'spinal_interneuron': [0.065, 0, 0.04],
      'effector_muscle': [-0.065, 0, 0.005]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 6: Control and Coordination',
      ncertActivity: 'Section 6.1.1 - Reflex Arc',
      formulas: ['Receptor -> Sensory Neuron -> Spinal Interneuron -> Motor Neuron -> Effector'],
      examTakeaway: 'Spinal cord executes instantaneous motor withdrawal before message reaches brain cortex, preventing tissue burn damage.'
    },
    tags: ['reflex-arc', 'nervous-system', 'sensory-neuron', 'motor-neuron', 'spinal-cord', 'effector']
  },
  {
    id: 'flower-anatomy',
    name: 'Longitudinal Section of a Bisexual Flower',
    category: 'biology',
    subCategory: 'Plant Reproduction',
    semanticDescription: 'Longitudinal floral cross-section showing calyx, corolla, stamen (filament + anther with pollen), and carpel (stigma, style, ovary with ovule).',
    dimensions: { width_mm: 120, height_mm: 160, depth_mm: 100, weight_g: 95 },
    materials: {
      roughness: 0.4,
      metalness: 0.05,
      color: '#e11d48',
      description: 'Velvety magenta petals with pistil and golden pollen anthers'
    },
    anchorPoints: {
      'stigma_surface': [0, 0, 0.122],
      'ovary_ovule': [0, 0, 0.058],
      'anther_tip': [0.03, -0.005, 0.09]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 7: How do Organisms Reproduce?',
      ncertActivity: 'Section 7.2.3 - Reproduction in Flowering Plants',
      formulas: ['Pollen + Ovule -> Zygote -> Seed (Ovule becomes seed, Ovary becomes fruit)'],
      examTakeaway: 'Stamen is male organ producing pollen; Carpel is female organ containing ovary and ovule; cross-pollination leads to syngamy.'
    },
    tags: ['flower', 'angiosperm', 'reproduction', 'stamen', 'anther', 'carpel', 'ovary', 'ovule']
  },
  {
    id: 'trophic-level-pyramid',
    name: 'Ecological Pyramid of Trophic Levels',
    category: 'biology',
    subCategory: 'Ecosystem Ecology',
    semanticDescription: '4-tier 3D stepped pyramid of Producers (10,000 J), Herbivores (1,000 J), Carnivores (100 J), and Apex Predators (10 J) demonstrating 10% energy law.',
    dimensions: { width_mm: 180, height_mm: 160, depth_mm: 180, weight_g: 260 },
    materials: {
      roughness: 0.35,
      metalness: 0.1,
      color: '#10b981',
      description: 'Stepped tiers graded from producer emerald green to apex crimson'
    },
    anchorPoints: {
      'tier_1_producers': [0, 0, 0.016],
      'tier_2_herbivores': [0, 0, 0.048],
      'tier_3_carnivores': [0, 0, 0.080],
      'tier_4_apex': [0, 0, 0.112]
    },
    cbse: {
      class: 10,
      chapter: 'Chapter 13: Our Environment',
      ncertActivity: 'Section 13.1.1 - Food Chains and Trophic Levels',
      formulas: ['Lindeman\'s 10% Law: E(n+1) = 0.10 * E(n)', '10,000 J -> 1,000 J -> 100 J -> 10 J'],
      examTakeaway: 'Only 10% of energy transfers to next level; food chains are limited to 3-4 steps; persistent chemicals biomagnify to maximum levels in apex consumers.'
    },
    tags: ['ecological-pyramid', 'trophic-levels', '10-percent-law', 'energy-flow', 'biomagnification']
  },
  {
    id: 'battery',
    name: 'Dry Cell Battery (1.5V AA)',
    category: 'physics',
    subCategory: 'Current Electricity & Circuits',
    semanticDescription: 'Direct-current electrochemical dry cell source with positive brass contact button, insulating jacket, and zinc bottom terminal.',
    dimensions: {"width_mm": 14, "height_mm": 50, "depth_mm": 14, "weight_g": 24},
    materials: {"roughness": 0.35, "metalness": 0.85, "color": "#2563eb", "description": "Glossy blue battery jacket with golden positive pip and silver negative plate"},
    anchorPoints: {"positive_terminal": [0, 0, 0.026], "negative_terminal": [0, 0, -0.025]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.1 - Closed Electric Circuit", "formulas": ["V = W / Q", "Electromotive Force (EMF) = 1.5 V"], "examTakeaway": "Maintains a constant potential difference across conductor ends, causing electrons to drift from negative to positive terminal."},
    tags: ["battery", "cell", "dc-source", "voltage", "circuit", "potential-difference"]
  },
  {
    id: 'bulb',
    name: 'Incandescent Light Bulb',
    category: 'physics',
    subCategory: 'Current Electricity & Heating Effects',
    semanticDescription: 'Electric lamp with coiled tungsten filament, copper support leads, clear glass envelope, and metallic screw base.',
    dimensions: {"width_mm": 60, "height_mm": 105, "depth_mm": 60, "weight_g": 35},
    materials: {"transmission": 0.95, "ior": 1.52, "roughness": 0.05, "metalness": 0.05, "color": "#f8fafc", "description": "Transparent blown glass bulb with incandescent tungsten filament"},
    anchorPoints: {"filament_center": [0, 0, 0.045], "base_contact": [0, 0, -0.045]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.2 - Heating Effect of Current", "formulas": ["P = V * I = I^2 * R = V^2 / R", "Joule Heating: H = I^2 * R * t"], "examTakeaway": "Tungsten has high melting point (3380 deg C) and emits white light without melting; inert argon/nitrogen gas prevents filament oxidation."},
    tags: ["bulb", "lamp", "tungsten", "joule-heating", "electric-power", "filament"]
  },
  {
    id: 'switch',
    name: 'Plug Key / Knife Switch',
    category: 'physics',
    subCategory: 'Current Electricity & Circuit Elements',
    semanticDescription: 'Laboratory circuit breaker key with solid brass contact blocks, insulated handle, and removable bridging plug.',
    dimensions: {"width_mm": 80, "height_mm": 35, "depth_mm": 45, "weight_g": 110},
    materials: {"roughness": 0.3, "metalness": 0.85, "color": "#d97706", "description": "Machined brass contact blocks mounted on insulating ebonite base"},
    anchorPoints: {"terminal_in": [-0.032, 0, 0.015], "terminal_out": [0.032, 0, 0.015], "plug_handle": [0, 0, 0.032]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.1 - Circuit Switching", "formulas": ["Open Switch: I = 0 A (Air gap)", "Closed Switch: I = V / R (Conducting link)"], "examTakeaway": "Provides a conducting link between cell and load; removing the plug opens the circuit and instantly drops current to zero."},
    tags: ["switch", "plug-key", "circuit", "contact", "open-circuit", "closed-circuit"]
  },
  {
    id: 'resistor',
    name: 'Standard Wire-Wound Resistor',
    category: 'physics',
    subCategory: 'Current Electricity & Ohmic Resistance',
    semanticDescription: 'Axial-leaded through-hole resistor with color-coded resistance bands, ceramic substrate core, and tinned copper wire leads.',
    dimensions: {"width_mm": 25, "height_mm": 8, "depth_mm": 8, "weight_g": 5},
    materials: {"roughness": 0.5, "metalness": 0.1, "color": "#d97706", "description": "Ceramic tubular body with color-coded resistance value rings"},
    anchorPoints: {"lead_left": [-0.015, 0, 0], "lead_right": [0.015, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.2 - Verification of Ohm's Law", "formulas": ["V = I * R (Ohm's Law)", "R = rho * (l / A)"], "examTakeaway": "Resistance opposes charge flow; it is directly proportional to length l, inversely to cross-sectional area A, and depends on material resistivity rho."},
    tags: ["resistor", "resistance", "ohms-law", "resistivity", "circuit"]
  },
  {
    id: 'rheostat',
    name: 'Laboratory Slide-Wire Rheostat',
    category: 'physics',
    subCategory: 'Current Electricity & Variable Resistance',
    semanticDescription: 'Adjustable wire-wound laboratory variable resistor with porcelain tube, oxidized constantan winding, slider guide rod, and phosphor-bronze wiper.',
    dimensions: {"width_mm": 180, "height_mm": 90, "depth_mm": 65, "weight_g": 420},
    materials: {"roughness": 0.3, "metalness": 0.75, "color": "#475569", "description": "Porcelain core with closely wound oxidized constantan resistance wire"},
    anchorPoints: {"fixed_terminal_A": [-0.08, -0.025, 0.015], "fixed_terminal_B": [0.08, -0.025, 0.015], "slider_terminal": [0, 0.025, 0.075]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.3 - Regulating Current with Rheostat", "formulas": ["I = V / R_variable", "Current inversely proportional to inserted resistance wire length"], "examTakeaway": "Enables continuous variation of current in a circuit without altering the source voltage by changing effective resistance wire length."},
    tags: ["rheostat", "variable-resistor", "slider", "current-regulation", "constantan"]
  },
  {
    id: 'connecting-wire',
    name: 'Flexible Insulated Connecting Wire',
    category: 'physics',
    subCategory: 'Current Electricity & Circuit Elements',
    semanticDescription: 'Multi-strand high-conductivity copper connecting lead with thick PVC insulation jacket and bare conductive end pins.',
    dimensions: {"width_mm": 250, "height_mm": 3, "depth_mm": 3, "weight_g": 15},
    materials: {"roughness": 0.4, "metalness": 0.1, "color": "#ef4444", "description": "Bright red flexible PVC insulation with high-conductivity copper core"},
    anchorPoints: {"start_pin": [-0.12, 0, 0], "end_pin": [0.12, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 11: Electricity", "ncertActivity": "Activity 11.1 - Circuit Assembly", "formulas": ["R_wire approx 0 Ohm (negligible voltage loss)"], "examTakeaway": "Copper is chosen for connecting leads due to extremely low resistivity (1.62 * 10^-8 Ohm*m), minimizing internal power dissipation."},
    tags: ["wire", "connecting-wire", "conductor", "copper", "insulation", "lead"]
  },
  {
    id: 'plane-mirror',
    name: 'Plane Optical Mirror with Stand',
    category: 'physics',
    subCategory: 'Optics & Reflection',
    semanticDescription: 'Flat highly-reflective glass front mirror with back-silvered reflecting plane, protective backing, and supporting base stand.',
    dimensions: {"width_mm": 120, "height_mm": 150, "depth_mm": 40, "weight_g": 180},
    materials: {"roughness": 0.02, "metalness": 0.98, "color": "#e2e8f0", "description": "Float glass front with vacuum-aluminized specular rear reflecting film"},
    anchorPoints: {"mirror_center": [0, 0, 0.065], "base_stand": [0, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 9: Light - Reflection and Refraction", "ncertActivity": "Activity 9.1 - Laws of Reflection", "formulas": ["angle i = angle r", "Magnification m = +1", "v = -u (Image distance = Object distance)"], "examTakeaway": "Produces a virtual, erect, and laterally inverted image of identical size located at equal distance behind the reflecting surface."},
    tags: ["plane-mirror", "reflection", "specular", "lateral-inversion", "virtual-image"]
  },
  {
    id: 'concave-mirror',
    name: 'Concave Spherical Mirror',
    category: 'physics',
    subCategory: 'Optics & Spherical Mirrors',
    semanticDescription: 'Inward-curving spherical reflective optical mirror with circular aperture, focal center, and optical axis alignment mount.',
    dimensions: {"width_mm": 85, "height_mm": 85, "depth_mm": 30, "weight_g": 140},
    materials: {"roughness": 0.02, "metalness": 0.98, "color": "#cbd5e1", "description": "Inwardly curved silvered spherical glass dish"},
    anchorPoints: {"pole_P": [0, 0, 0.035], "principal_focus_F": [0, -0.05, 0.035], "center_of_curvature_C": [0, -0.1, 0.035]},
    cbse: {"class": 10, "chapter": "Chapter 9: Light - Reflection and Refraction", "ncertActivity": "Activity 9.2 - Focusing Sunlight with Concave Mirror", "formulas": ["1/f = 1/v + 1/u (Mirror Formula)", "f = R / 2", "m = -v / u = h_i / h_o"], "examTakeaway": "Converges parallel incident rays to principal focus F; forms real inverted images for u > f, and magnified virtual erect image when object is placed between P and F."},
    tags: ["concave-mirror", "converging-mirror", "focus", "real-image", "virtual-image", "spherical-mirror"]
  },
  {
    id: 'concave-lens',
    name: 'Biconcave Diverging Lens',
    category: 'physics',
    subCategory: 'Optics & Refraction',
    semanticDescription: 'Double concave optical glass lens with thin center and thicker periphery, ground edges, and high optical transmission.',
    dimensions: {"width_mm": 60, "height_mm": 60, "depth_mm": 12, "weight_g": 65},
    materials: {"transmission": 0.96, "ior": 1.52, "roughness": 0.02, "metalness": 0.0, "color": "#f0f9ff", "description": "Crown glass biconcave lens with polished spherical surfaces"},
    anchorPoints: {"optical_center_O": [0, 0, 0.03], "focus_F1": [-0.06, 0, 0.03], "focus_F2": [0.06, 0, 0.03]},
    cbse: {"class": 10, "chapter": "Chapter 9: Light - Reflection and Refraction", "ncertActivity": "Activity 9.12 - Image Formation by Concave Lens", "formulas": ["1/f = 1/v - 1/u (Lens Formula)", "Power P = 1 / f (Negative Power)", "m = v / u < 1"], "examTakeaway": "Diverging lens always has a negative focal length f < 0; it always produces a virtual, erect, and diminished image located between optical center O and focus F."},
    tags: ["concave-lens", "diverging-lens", "myopia-correction", "refraction", "focal-length"]
  },
  {
    id: 'conical-flask',
    name: 'Conical Flask (Erlenmeyer 250mL)',
    category: 'chemistry',
    subCategory: 'Laboratory Glassware',
    semanticDescription: 'Wide flat-bottom borosilicate Erlenmeyer flask with tapered conical neck, volume graduations, and fire-polished rim.',
    dimensions: {"width_mm": 110, "height_mm": 165, "depth_mm": 110, "weight_g": 185},
    materials: {"transmission": 0.95, "ior": 1.52, "roughness": 0.03, "metalness": 0.02, "color": "#e0f2fe", "description": "Heat-resistant borosilicate 3.3 laboratory glass"},
    anchorPoints: {"flask_mouth": [0, 0, 0.165], "liquid_center": [0, 0, 0.045], "flask_base": [0, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.3 - Reaction of Zinc with Dilute Sulphuric Acid", "formulas": ["Zn(s) + H2SO4(aq) -> ZnSO4(aq) + H2(g) ^"], "examTakeaway": "Conical geometry facilitates vigorous swirling without liquid spilling; narrow neck accommodates rubber stoppers for gas delivery tubes."},
    tags: ["flask", "erlenmeyer", "glassware", "chemistry", "titration", "gas-evolution"]
  },
  {
    id: 'test-tube',
    name: 'Borosilicate Test Tube (15mL)',
    category: 'chemistry',
    subCategory: 'Laboratory Glassware',
    semanticDescription: 'Cylindrical thin-walled borosilicate reaction tube with hemispherical sealed bottom, fire-polished flared lip, and volume capacity.',
    dimensions: {"width_mm": 20, "height_mm": 150, "depth_mm": 20, "weight_g": 22},
    materials: {"transmission": 0.96, "ior": 1.52, "roughness": 0.02, "metalness": 0.0, "color": "#f0f9ff", "description": "Clear borosilicate test tube with liquid meniscus"},
    anchorPoints: {"tube_mouth": [0, 0, 0.15], "liquid_meniscus": [0, 0, 0.065], "hemisphere_bottom": [0, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.2 - Precipitation of Lead Iodide", "formulas": ["Pb(NO3)2(aq) + 2KI(aq) -> PbI2(s) v (Yellow ppt) + 2KNO3(aq)"], "examTakeaway": "Allows rapid visual inspection of precipitate formation, gas bubbling, thermal decomposition, and color changes in micro-scale reactions."},
    tags: ["test-tube", "glassware", "precipitation", "lead-iodide", "reaction-vessel"]
  },
  {
    id: 'watch-glass',
    name: 'Borosilicate Watch Glass (80mm)',
    category: 'chemistry',
    subCategory: 'Laboratory Glassware',
    semanticDescription: 'Circular shallow-concave glass dish used as an evaporation surface, beaker lid, or collection plate for reaction ash and crystals.',
    dimensions: {"width_mm": 80, "height_mm": 12, "depth_mm": 80, "weight_g": 45},
    materials: {"transmission": 0.95, "ior": 1.52, "roughness": 0.02, "metalness": 0.0, "color": "#f8fafc", "description": "Pressed concave clear borosilicate glass dish"},
    anchorPoints: {"concave_center": [0, 0, 0.003], "rim_lip": [0.04, 0, 0.012]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.1 - Collection of Magnesium Oxide Ash", "formulas": ["2Mg(s) + O2(g) -> 2MgO(s) (White powder collected on watch glass)"], "examTakeaway": "Used to collect burning reaction products safely; water added to the ash forms Mg(OH)2, turning moist red litmus paper blue."},
    tags: ["watch-glass", "evaporation", "ash-collection", "glassware", "precipitate"]
  },
  {
    id: 'dropper',
    name: 'Pasteur Pipette Dropper',
    category: 'chemistry',
    subCategory: 'Fluid Dispensing Tools',
    semanticDescription: 'Precision fluid dispenser with flexible vulcanized rubber squeeze bulb, transparent glass stem, and narrow capillary delivery tip.',
    dimensions: {"width_mm": 18, "height_mm": 135, "depth_mm": 18, "weight_g": 16},
    materials: {"roughness": 0.4, "metalness": 0.1, "color": "#2563eb", "description": "Blue elastic rubber bulb atop clear glass capillary tube"},
    anchorPoints: {"rubber_bulb_top": [0, 0, 0.135], "capillary_nozzle": [0, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 2: Acids, Bases and Salts", "ncertActivity": "Activity 2.1 - Dropwise Indicator Testing", "formulas": ["Acid + Phenolphthalein -> Colorless", "Base + Phenolphthalein -> Pink"], "examTakeaway": "Dispenses precise drop volumes (approx 0.05mL per drop) to detect sharp color transition endpoints without overshooting titration."},
    tags: ["dropper", "pipette", "indicator", "titration", "acid-base", "fluid-dispensing"]
  },
  {
    id: 'retort-stand',
    name: 'Heavy Cast-Iron Retort Stand & Clamp',
    category: 'chemistry',
    subCategory: 'Laboratory Support Apparatus',
    semanticDescription: 'Laboratory support stand with heavy rectangular cast-iron base plate, zinc-plated vertical steel upright rod, and bosshead clamp.',
    dimensions: {"width_mm": 150, "height_mm": 450, "depth_mm": 100, "weight_g": 1200},
    materials: {"roughness": 0.5, "metalness": 0.85, "color": "#1e293b", "description": "Dark hammered cast-iron base with polished chrome-plated steel rod"},
    anchorPoints: {"base_center": [0, 0, 0.015], "clamp_grip": [0.045, 0, 0.25], "rod_top": [0, 0, 0.45]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.5 - Thermal Decomposition of Ferrous Sulphate", "formulas": ["2FeSO4(s) --Delta--> Fe2O3(s) + SO2(g) + SO3(g)"], "examTakeaway": "Provides stable, hands-free elevation of glassware above Bunsen burners during prolonged high-temperature thermal decompositions."},
    tags: ["retort-stand", "clamp", "support", "iron-base", "thermal-decomposition", "apparatus"]
  },
  {
    id: 'laboratory-tongs',
    name: 'Scissor Crucible Tongs',
    category: 'chemistry',
    subCategory: 'Safety & Handling Tools',
    semanticDescription: 'Stainless-steel scissor tongs with serrated bowed jaws, rivet fulcrum pivot, and looped finger handles for holding hot lab materials.',
    dimensions: {"width_mm": 65, "height_mm": 210, "depth_mm": 25, "weight_g": 140},
    materials: {"roughness": 0.35, "metalness": 0.95, "color": "#94a3b8", "description": "Polished stainless steel 304 with knurled gripping jaw tips"},
    anchorPoints: {"jaw_grip": [0, 0.095, 0], "fulcrum_pivot": [0, 0.02, 0], "finger_loops": [0, -0.095, 0]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.1 - Holding Magnesium Ribbon in Flame", "formulas": ["2Mg + O2 -> 2MgO (Exothermic flame T > 3000 K)"], "examTakeaway": "Prevents direct manual contact with burning metals and incandescent crucibles, insulating the experimenter from extreme heat."},
    tags: ["tongs", "crucible-tongs", "safety", "combustion", "magnesium-burning", "laboratory"]
  },
  {
    id: 'magnesium-ribbon',
    name: 'Pure Magnesium Metal Ribbon Strip',
    category: 'chemistry',
    subCategory: 'Metals & Chemical Reagents',
    semanticDescription: 'Silvery-white flexible elemental magnesium ribbon with natural surface passivation texture and ductile strip geometry.',
    dimensions: {"width_mm": 12, "height_mm": 75, "depth_mm": 1, "weight_g": 2},
    materials: {"roughness": 0.3, "metalness": 0.95, "color": "#cbd5e1", "description": "Silvery-white alkaline earth metal with subtle ductile curvature"},
    anchorPoints: {"ribbon_tip": [0, 0.035, 0], "ribbon_base": [0, -0.035, 0]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.1 - Burning of Magnesium Ribbon in Air", "formulas": ["2Mg(s) + O2(g) -> 2MgO(s) + Heat + Blinding White Light"], "examTakeaway": "Must be scrubbed with sandpaper prior to ignition to strip the passivating layer of basic magnesium carbonate [MgCO3.Mg(OH)2]."},
    tags: ["magnesium", "ribbon", "metal", "combustion", "passivation", "combination-reaction"]
  },
  {
    id: 'magnesium-oxide',
    name: 'Magnesium Oxide Ash Powder Mound',
    category: 'chemistry',
    subCategory: 'Reaction Products & Oxides',
    semanticDescription: 'Fine white porous powder mound representing anhydrous magnesium oxide formed by the high-temperature oxidation of magnesium.',
    dimensions: {"width_mm": 40, "height_mm": 15, "depth_mm": 40, "weight_g": 8},
    materials: {"roughness": 0.95, "metalness": 0.0, "color": "#f8fafc", "description": "Porous micro-crystalline chalky white powder mound"},
    anchorPoints: {"apex_peak": [0, 0, 0.015], "base_perimeter": [0, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 1: Chemical Reactions and Equations", "ncertActivity": "Activity 1.1 - Nature of Metallic Oxides", "formulas": ["MgO(s) + H2O(l) -> Mg(OH)2(aq) (Magnesium Hydroxide, basic)"], "examTakeaway": "Metallic oxides are basic in nature; when dissolved in water, MgO forms magnesium hydroxide which turns red litmus paper blue."},
    tags: ["magnesium-oxide", "mgo", "basic-oxide", "white-ash", "litmus-test", "reaction-product"]
  },
  {
    id: 'neuron',
    name: 'Multipolar Motor Neuron (Nerve Cell)',
    category: 'biology',
    subCategory: 'Neurobiology & Nervous System',
    semanticDescription: 'Complete multipolar nerve cell showing cyton/soma, dendritic tree, central nucleus, myelinated axon with Nodes of Ranvier, and synaptic terminal buttons.',
    dimensions: {"width_mm": 140, "height_mm": 45, "depth_mm": 25, "weight_g": 1},
    materials: {"roughness": 0.4, "metalness": 0.1, "color": "#f59e0b", "description": "Golden soma body, pearlescent white myelin sheaths, and glowing cyan synaptic boutons"},
    anchorPoints: {"soma_nucleus": [-0.045, 0, 0], "dendrite_tip": [-0.07, 0.02, 0], "axon_terminal": [0.065, 0, 0]},
    cbse: {"class": 10, "chapter": "Chapter 6: Control and Coordination", "ncertActivity": "Figure 6.1 - Structure of Neuron", "formulas": ["Dendrite (Input) -> Cyton -> Axon -> Synapse (Neurotransmitter diffusion)"], "examTakeaway": "Information is acquired at dendrite tips, generates an electrical impulse across soma and axon, and triggers neurotransmitter chemical release at the synapse."},
    tags: ["neuron", "nerve-cell", "axon", "dendrite", "myelin-sheath", "synapse", "action-potential"]
  },
  {
    id: 'brain',
    name: 'Human Brain (Sagittal Cross-Section)',
    category: 'biology',
    subCategory: 'Central Nervous System',
    semanticDescription: 'Anatomical model of human brain displaying folded cerebrum cortex, corpus callosum, thalamus, cerebellum with folia arborization, and brainstem (pons + medulla).',
    dimensions: {"width_mm": 160, "height_mm": 130, "depth_mm": 140, "weight_g": 1350},
    materials: {"roughness": 0.45, "metalness": 0.05, "color": "#f43f5e", "description": "Convoluted cerebral cortex pink-tan with ivory internal white matter tracts"},
    anchorPoints: {"cerebrum_cortex": [0, 0.03, 0.05], "cerebellum_folia": [-0.045, -0.04, -0.02], "medulla_brainstem": [0, -0.025, -0.06]},
    cbse: {"class": 10, "chapter": "Chapter 6: Control and Coordination", "ncertActivity": "Figure 6.3 - Human Brain Anatomy", "formulas": ["Forebrain (Thinking/Sensation) + Midbrain (Visual/Auditory reflex) + Hindbrain (Vital involuntary functions)"], "examTakeaway": "Cerebrum governs conscious thought, sensory integration, and memory; Cerebellum coordinates precision motor posture/balance; Medulla controls involuntary breathing and blood pressure."},
    tags: ["brain", "cerebrum", "cerebellum", "medulla", "brainstem", "central-nervous-system", "cortex"]
  },
  {
    id: 'digestive-system',
    name: 'Human Digestive System (Gastrointestinal Tract)',
    category: 'biology',
    subCategory: 'Life Processes & Nutrition',
    semanticDescription: 'Complete human alimentary tract showing esophagus, J-shaped stomach, liver with gallbladder, pancreas, duodenum, convoluted small intestine, colon, and appendix.',
    dimensions: {"width_mm": 180, "height_mm": 480, "depth_mm": 120, "weight_g": 2800},
    materials: {"roughness": 0.4, "metalness": 0.05, "color": "#f97316", "description": "Multi-organ GI tract with liver (hepatic brown), gallbladder (bile emerald), and intestines"},
    anchorPoints: {"esophagus_inlet": [0, 0, 0.22], "stomach_body": [-0.025, 0, 0.12], "duodenum_pancreas": [0.015, 0, 0.07], "small_intestine_loops": [0, 0, -0.03]},
    cbse: {"class": 10, "chapter": "Chapter 5: Life Processes", "ncertActivity": "Figure 5.6 - Human Alimentary Canal", "formulas": ["Starch + Amylase -> Maltose", "Proteins + Pepsin/Trypsin -> Amino Acids", "Fats + Bile + Lipase -> Fatty Acids + Glycerol"], "examTakeaway": "Complete digestion occurs in small intestine; liver bile emulsifies large fat globules into micro-droplets, while intestinal villi maximize surface area for rapid nutrient absorption."},
    tags: ["digestive-system", "stomach", "liver", "pancreas", "small-intestine", "villi", "bile", "nutrition"]
  },
  {
    id: 'dna-double-helix',
    name: 'DNA Double Helix Molecule',
    category: 'biology',
    subCategory: 'Genetics & Molecular Biology',
    semanticDescription: 'B-form double-helical nucleic acid model showing intertwined antiparallel sugar-phosphate backbones and complementary purine-pyrimidine base pairs (A-T and G-C).',
    dimensions: {"width_mm": 45, "height_mm": 180, "depth_mm": 45, "weight_g": 25},
    materials: {"roughness": 0.35, "metalness": 0.1, "color": "#8b5cf6", "description": "Purple sugar-phosphate spiral ribbons linked by color-coded nucleotide base pairs"},
    anchorPoints: {"helix_top": [0, 0, 0.09], "helix_mid": [0, 0, 0], "helix_bottom": [0, 0, -0.09]},
    cbse: {"class": 10, "chapter": "Chapter 7 & 8: How do Organisms Reproduce? & Heredity", "ncertActivity": "Section 7.1 - The Importance of Variation in DNA Copying", "formulas": ["Complementary Base Pairing: Adenine (A) = Thymine (T)", "Guanine (G) == Cytosine (C)"], "examTakeaway": "DNA in cell nucleus is the information source for protein synthesis; copying mechanism introduces subtle biochemical errors creating population variations essential for species survival."},
    tags: ["dna", "double-helix", "nucleotides", "adenine-thymine", "guanine-cytosine", "heredity", "replication"]
  },
];