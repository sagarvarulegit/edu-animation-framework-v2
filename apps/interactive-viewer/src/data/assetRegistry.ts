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
    transmission?: number;
    ior?: number;
    roughness: number;
    metalness: number;
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
      ior: 1.517,
      roughness: 0.015,
      metalness: 0.02,
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
  }
];