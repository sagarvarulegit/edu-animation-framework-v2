/**
 * AUTO-GENERATED FILE by tools/okf/compile-okf.mjs
 * DO NOT EDIT MANUALLY.
 * Generated on: 2026-08-31T10:09:03.788Z
 */

export type OkfConceptType =
  | 'concept'
  | 'experiment'
  | 'apparatus'
  | 'reaction'
  | 'phenomenon'
  | 'anatomy'
  | 'law'
  | 'curriculum';

export type OkfTrustTier = 'human-reviewed' | 'machine-confirmed' | 'unverified';
export type OkfLifecycleStatus = 'active' | 'draft' | 'reviewed' | 'deprecated';

export interface OkfSourceCitation {
  name: string;
  chapter?: string;
  activity?: string;
  section?: string;
  url?: string;
}

export interface OkfCbseMapping {
  class?: number;
  subject?: 'chemistry' | 'physics' | 'biology' | 'mathematics';
  chapter?: string;
  ncert_activity?: string;
  key_takeaways?: string[];
}

export interface OkfEquation {
  latex: string;
  meaning: string;
  type?: 'chemical' | 'physical' | 'mathematical';
}

export interface OkfMisconception {
  claim: string;
  correction: string;
}

export interface OkfConcept {
  id: string;
  filePath: string;
  category: string;
  type: OkfConceptType;
  title: string;
  description: string;
  status: OkfLifecycleStatus;
  verified: OkfTrustTier;
  timestamp: string;
  stale_after?: string;
  resource?: string;
  tags: string[];
  sources: OkfSourceCitation[];
  cbse_mapping?: OkfCbseMapping;
  equations: OkfEquation[];
  misconceptions: OkfMisconception[];
  safety: string[];
  related_assets: string[];
  related_lessons: string[];
  related_concepts: string[];
  body: string;
}

export interface OkfEdge {
  source: string;
  target: string;
  kind: 'concept-to-concept' | 'concept-to-asset' | 'concept-to-lesson';
}

export interface OkfManifest {
  schemaVersion: string;
  spec: string;
  generatedAt: string;
  totalConcepts: number;
  totalEdges: number;
  byType: Record<string, string[]>;
  byCategory: Record<string, string[]>;
  concepts: Record<string, OkfConcept>;
  edges: OkfEdge[];
}

export const OKF_MANIFEST: OkfManifest = {
  "schemaVersion": "0.2.0",
  "spec": "https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md",
  "generatedAt": "2026-08-31T10:09:03.788Z",
  "totalConcepts": 23,
  "totalEdges": 114,
  "byType": {
    "anatomy": [
      "aorta-systemic-trunk",
      "cardiac-chambers",
      "digestive-system",
      "human-eye-optics"
    ],
    "concept": [
      "human-heart-circulation",
      "combination-reaction",
      "magnesium-metal",
      "magnesium-oxide",
      "oxygen-element",
      "angle-of-deviation"
    ],
    "apparatus": [
      "bunsen-burner",
      "crucible-tongs",
      "convex-lens",
      "electric-circuit",
      "optical-prism"
    ],
    "experiment": [
      "magnesium-ribbon-combustion",
      "glass-prism-refraction"
    ],
    "curriculum": [
      "cbse-class-10-science",
      "ncert-biology-ch06",
      "ncert-chemistry-ch01",
      "ncert-physics-ch11"
    ],
    "phenomenon": [
      "optical-dispersion"
    ],
    "law": [
      "snells-law"
    ]
  },
  "byCategory": {
    "biology": [
      "aorta-systemic-trunk",
      "cardiac-chambers",
      "digestive-system",
      "human-eye-optics",
      "human-heart-circulation"
    ],
    "chemistry": [
      "bunsen-burner",
      "combination-reaction",
      "crucible-tongs",
      "magnesium-metal",
      "magnesium-oxide",
      "magnesium-ribbon-combustion",
      "oxygen-element"
    ],
    "curriculum": [
      "cbse-class-10-science",
      "ncert-biology-ch06",
      "ncert-chemistry-ch01",
      "ncert-physics-ch11"
    ],
    "physics": [
      "angle-of-deviation",
      "convex-lens",
      "electric-circuit",
      "glass-prism-refraction",
      "optical-dispersion",
      "optical-prism",
      "snells-law"
    ]
  },
  "concepts": {
    "aorta-systemic-trunk": {
      "id": "aorta-systemic-trunk",
      "filePath": "knowledge/biology/aorta-systemic-trunk.md",
      "category": "biology",
      "type": "anatomy",
      "title": "Aorta & Great Systemic Arterial Trunk",
      "description": "The largest systemic artery in the human body, arising from the left ventricle and distributing oxygenated blood under pulsatile systolic pressure.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/biology/human-heart",
      "tags": [
        "anatomy",
        "blood-vessels",
        "aorta",
        "arterial-system",
        "hemodynamics"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 6: Life Processes",
          "section": "6.4.2 Blood Vessels"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [
        "human-heart"
      ],
      "related_lessons": [
        "biology.human-heart-double-circulation"
      ],
      "related_concepts": [
        "human-heart-circulation",
        "cardiac-chambers"
      ],
      "body": "# Aorta & Great Systemic Arterial Trunk\n\nThe aorta is the prime systemic conduit delivering oxygenated blood from the left ventricle. Its high concentration of elastic fibers allows it to expand during systolic ejection and recoil during diastole (Windkessel effect), ensuring continuous peripheral perfusion."
    },
    "cardiac-chambers": {
      "id": "cardiac-chambers",
      "filePath": "knowledge/biology/cardiac-chambers.md",
      "category": "biology",
      "type": "anatomy",
      "title": "The Four Cardiac Chambers & Valvular System",
      "description": "Morphological and functional specialization of the right and left atria and ventricles, partitioned by the interventricular septum and unidirectional atrioventricular/semilunar valves.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/biology/human-heart",
      "tags": [
        "anatomy",
        "cardiology",
        "chambers",
        "valves",
        "myocardium"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 6: Life Processes",
          "section": "6.4.1 Our Pump — The Heart"
        }
      ],
      "equations": [],
      "misconceptions": [
        {
          "claim": "The left and right ventricles pump different volumes of blood per beat.",
          "correction": "Both ventricles pump the exact same stroke volume (~70 mL per beat); only the systolic pressure generated differs (~120 mmHg in Left Ventricle vs ~25 mmHg in Right Ventricle)."
        }
      ],
      "safety": [],
      "related_assets": [
        "human-heart"
      ],
      "related_lessons": [
        "biology.human-heart-double-circulation"
      ],
      "related_concepts": [
        "human-heart-circulation",
        "aorta-systemic-trunk"
      ],
      "body": "# The Four Cardiac Chambers & Valvular System\n\nThe human heart is divided by muscular and fibrous septa into four distinct chambers:\n1. **Right Atrium (RA)**: Receives systemic venous return via Superior Vena Cava (SVC) and Inferior Vena Cava (IVC).\n2. **Right Ventricle (RV)**: Pumps into Pulmonary Trunk through the Pulmonary Semilunar Valve.\n3. **Left Atrium (LA)**: Receives 4 Pulmonary Veins (2 left, 2 right).\n4. **Left Ventricle (LV)**: High-pressure conical chamber pumping into the Aorta through the Aortic Semilunar Valve."
    },
    "digestive-system": {
      "id": "digestive-system",
      "filePath": "knowledge/biology/digestive-system.md",
      "category": "biology",
      "type": "anatomy",
      "title": "Human Alimentary Canal & Digestive System",
      "description": "Gastrointestinal organ system responsible for mechanical mastication, enzymatic hydrolysis, nutrient absorption, and waste excretion.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/biology/digestive-system",
      "tags": [
        "biology",
        "anatomy",
        "digestion",
        "alimentary-canal",
        "enzymes",
        "life-processes"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 6: Life Processes",
          "section": "6.2.3 Nutrition in Human Beings"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [
        "digestive-system"
      ],
      "related_lessons": [],
      "related_concepts": [],
      "body": "# Human Alimentary Canal & Digestive System\n\nThe human alimentary canal is a continuous muscular tube spanning approximately $9\\text{ meters}$ extending from the buccal cavity to the anus, accompanied by specialized accessory digestive glands (salivary glands, liver with gallbladder, and pancreas)."
    },
    "human-eye-optics": {
      "id": "human-eye-optics",
      "filePath": "knowledge/biology/human-eye-optics.md",
      "category": "biology",
      "type": "anatomy",
      "title": "The Human Eye as an Optical Instrument",
      "description": "Biological photoreceptive organ utilizing a curved cornea, iris diaphragm, crystalline lens, and retina to focus light into visual neural impulses.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/biology/human-eye",
      "tags": [
        "biology",
        "optics",
        "eye",
        "vision",
        "accommodation",
        "retina"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 11: The Human Eye and the Colourful World",
          "section": "11.1 The Human Eye and Power of Accommodation"
        }
      ],
      "equations": [],
      "misconceptions": [
        {
          "claim": "The eye lens provides the vast majority of refraction.",
          "correction": "Most refraction occurs at the outer air-cornea interface (~43 dioptres); the crystalline lens fine-tunes focal accommodation (~15–20 dioptres)."
        }
      ],
      "safety": [],
      "related_assets": [
        "human-eye",
        "convex-lens"
      ],
      "related_lessons": [],
      "related_concepts": [
        "convex-lens",
        "snells-law"
      ],
      "body": "# The Human Eye as an Optical Instrument\n\nThe human eyeball is approximately spherical with a diameter of about $2.3\\text{ cm}$. Light entering through the protective transparent cornea passes through the aqueous humor, pupil aperture, crystalline lens, and vitreous body to cast a real, inverted image onto the neuro-retinal membrane."
    },
    "human-heart-circulation": {
      "id": "human-heart-circulation",
      "filePath": "knowledge/biology/human-heart-circulation.md",
      "category": "biology",
      "type": "concept",
      "title": "Double Circulation in the Human Heart",
      "description": "Closed dual-circuit cardiovascular system consisting of a low-pressure pulmonary loop to the lungs and a high-pressure systemic loop to the body organs.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/biology/human-heart",
      "tags": [
        "biology",
        "circulatory-system",
        "double-circulation",
        "heart",
        "life-processes",
        "cbse-class-10"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 6: Life Processes",
          "section": "6.4.1 Transportation in Human Beings — Our Pump: The Heart"
        }
      ],
      "equations": [],
      "misconceptions": [
        {
          "claim": "All arteries always carry oxygen-rich blood, and all veins carry carbon-dioxide-rich blood.",
          "correction": "Exception: The Pulmonary Artery carries deoxygenated blood from the heart to the lungs, while the Pulmonary Veins carry oxygenated blood from the lungs to the heart."
        },
        {
          "claim": "The right and left sides of the heart contract at completely separate times.",
          "correction": "Both atria contract simultaneously (atrial systole) while ventricles relax (ventricular diastole), followed by simultaneous contraction of both ventricles (ventricular systole)."
        }
      ],
      "safety": [],
      "related_assets": [
        "human-heart"
      ],
      "related_lessons": [
        "biology.human-heart-double-circulation"
      ],
      "related_concepts": [
        "cardiac-chambers",
        "aorta-systemic-trunk"
      ],
      "body": "# Double Circulation in the Human Heart\n\n## 1. Physiological Mechanism\nHuman circulation is termed *double circulation* because blood passes through the four-chambered heart twice in one complete cardiovascular transit:\n1. **Pulmonary Circulation**: Transports deoxygenated blood from the right ventricle through the pulmonary arteries to the lung alveoli for gaseous exchange ($\\text{CO}_2$ release, $\\text{O}_2$ uptake), and returns oxygenated blood through the pulmonary veins into the left atrium.\n2. **Systemic Circulation**: Transports oxygenated blood from the muscular left ventricle through the aorta to all capillary beds in systemic tissues and organs, returning oxygen-depleted blood via the superior and inferior vena cava into the right atrium."
    },
    "bunsen-burner": {
      "id": "bunsen-burner",
      "filePath": "knowledge/chemistry/bunsen-burner.md",
      "category": "chemistry",
      "type": "apparatus",
      "title": "Laboratory Bunsen Burner",
      "description": "Standard gas-fueled laboratory apparatus delivering an adjustable oxidizing or reducing flame for heating and combustion reactions.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/chemistry/bunsen-burner",
      "tags": [
        "apparatus",
        "chemistry",
        "heating",
        "laboratory",
        "flame"
      ],
      "sources": [
        {
          "name": "NCERT Laboratory Manual for Class 10 Science",
          "section": "Laboratory Techniques: Heating and Burners"
        }
      ],
      "equations": [
        {
          "latex": "\\\\text{CH}_4 + 2\\\\text{O}_2 \\\\rightarrow \\\\text{CO}_2 + 2\\\\text{H}_2\\\\text{O} + \\\\Delta H",
          "meaning": "Complete combustion of methane fuel with open collar in blue non-luminous flame.",
          "type": "chemical"
        }
      ],
      "misconceptions": [],
      "safety": [
        "Always light match before opening the gas valve.",
        "Use blue non-luminous flame for clean heating without soot deposits."
      ],
      "related_assets": [
        "bunsen-burner",
        "magnesium-burning-setup"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion"
      ],
      "body": "# Laboratory Bunsen Burner\n\n## Anatomy & Operation\nThe Bunsen burner comprises a heavy cast-iron base, a vertical brass barrel, a needle gas jet, and an adjustable rotating air collar. Adjusting the air collar controls air-fuel stoichiometry between a sooty yellow flame ($300^\\circ\\text{C}$) and a clean, high-temperature blue oxidizing flame ($1100^\\circ\\text{C}$)."
    },
    "combination-reaction": {
      "id": "combination-reaction",
      "filePath": "knowledge/chemistry/combination-reaction.md",
      "category": "chemistry",
      "type": "concept",
      "title": "Combination Reaction (Synthesis Reaction)",
      "description": "Chemical reaction type where two or more reactants combine to form a single product.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "chemistry",
        "reaction-types",
        "synthesis",
        "cbse-class-10"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 1: Chemical Reactions and Equations",
          "section": "1.2.1 Combination Reaction"
        }
      ],
      "equations": [
        {
          "latex": "A + B \\\\rightarrow AB",
          "meaning": "Two distinct elemental or compound reactants join to produce a single unified product compound.",
          "type": "chemical"
        }
      ],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion",
        "magnesium-metal",
        "magnesium-oxide"
      ],
      "body": "# Combination Reaction\n\nA reaction in which a single product is formed from two or more reactants is known as a combination reaction.\nIn the burning of magnesium ribbon:\n$$2\\text{Mg}(s) + \\text{O}_2(g) \\rightarrow 2\\text{MgO}(s)$$\nElemental magnesium and molecular oxygen combine into a single substance, solid magnesium oxide."
    },
    "crucible-tongs": {
      "id": "crucible-tongs",
      "filePath": "knowledge/chemistry/crucible-tongs.md",
      "category": "chemistry",
      "type": "apparatus",
      "title": "Crucible & Laboratory Tongs",
      "description": "Scissor-style stainless steel gripping apparatus designed for safely holding hot crucibles, evaporating dishes, and magnesium strips.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/chemistry/laboratory-tongs",
      "tags": [
        "apparatus",
        "safety",
        "chemistry",
        "laboratory-handling"
      ],
      "sources": [
        {
          "name": "NCERT Laboratory Manual for Class 10 Science",
          "section": "Safety Regulations & Apparatus Handling"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [
        "Ensure serrated gripping tips have firm mechanical traction on the object before lifting.",
        "Never touch hot metal ends with bare hands even after removing from flame."
      ],
      "related_assets": [
        "laboratory-tongs",
        "magnesium-burning-setup"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion"
      ],
      "body": "# Crucible & Laboratory Tongs\n\nStainless steel laboratory tongs with bowed serrated jaws and looped handles designed to manipulate hot experimental vessels and combustible metal strips at safe operator distance."
    },
    "magnesium-metal": {
      "id": "magnesium-metal",
      "filePath": "knowledge/chemistry/magnesium-metal.md",
      "category": "chemistry",
      "type": "concept",
      "title": "Magnesium Metal (Mg, Atomic Number 12)",
      "description": "Highly reactive alkaline earth metal in Group 2 of the Periodic Table with electronic configuration 2, 8, 2.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/chemistry/magnesium-ribbon",
      "tags": [
        "chemistry",
        "element",
        "metal",
        "alkaline-earth-metal",
        "valency"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 3: Metals and Non-Metals",
          "section": "3.2 Chemical Properties of Metals"
        }
      ],
      "equations": [
        {
          "latex": "\\\\text{Mg} \\\\rightarrow \\\\text{Mg}^{2+} + 2e^-",
          "meaning": "Electropositive magnesium atom donates two valence electrons during oxidation.",
          "type": "chemical"
        }
      ],
      "misconceptions": [
        {
          "claim": "Magnesium ribbon stored in the laboratory is 100% pure elemental magnesium at the surface.",
          "correction": "Atmospheric moisture and carbon dioxide form a thin protective layer of basic magnesium carbonate that must be abraded off with sandpaper."
        }
      ],
      "safety": [],
      "related_assets": [
        "magnesium-ribbon",
        "magnesium-atom"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion",
        "magnesium-oxide"
      ],
      "body": "# Magnesium Metal (Mg)\n\n## Electronic Structure & Reactivity\nMagnesium ($Z = 12$) has 12 protons and 12 electrons configured as $1s^2 2s^2 2p^6 3s^2$ (or $2, 8, 2$). \nWith a low first and second ionization enthalpy, it acts as a strong reducing agent in combination and displacement reactions."
    },
    "magnesium-oxide": {
      "id": "magnesium-oxide",
      "filePath": "knowledge/chemistry/magnesium-oxide.md",
      "category": "chemistry",
      "type": "concept",
      "title": "Magnesium Oxide (MgO)",
      "description": "White ionic solid compound composed of Mg²⁺ and O²⁻ ions in a face-centered cubic lattice; acts as a basic metallic oxide.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/chemistry/magnesium-oxide",
      "tags": [
        "chemistry",
        "compound",
        "basic-oxide",
        "ionic-solid",
        "cbse-class-10"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 1: Chemical Reactions and Equations",
          "section": "1.1.1 Writing a Chemical Equation"
        },
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 2: Acids, Bases and Salts",
          "section": "2.1.5 Reaction of Metallic Oxides with Acids"
        }
      ],
      "equations": [
        {
          "latex": "\\\\text{MgO}(s) + \\\\text{H}_2\\\\text{O}(l) \\\\rightarrow \\\\text{Mg(OH)}_2(aq)",
          "meaning": "Magnesium oxide hydrolyzes into alkaline magnesium hydroxide solution.",
          "type": "chemical"
        },
        {
          "latex": "\\\\text{MgO}(s) + 2\\\\text{HCl}(aq) \\\\rightarrow \\\\text{MgCl}_2(aq) + \\\\text{H}_2\\\\text{O}(l)",
          "meaning": "Basic oxide neutralizes hydrochloric acid to yield magnesium chloride and water.",
          "type": "chemical"
        }
      ],
      "misconceptions": [
        {
          "claim": "All metal oxides are completely insoluble in water.",
          "correction": "While most are insoluble, oxides of metals like Mg dissolve slightly to produce alkaline solutions."
        }
      ],
      "safety": [],
      "related_assets": [
        "magnesium-oxide",
        "watch-glass",
        "magnesium-oxide-lattice"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion",
        "magnesium-metal",
        "combination-reaction"
      ],
      "body": "# Magnesium Oxide (MgO)\n\n## Nature and Properties\nMagnesium oxide is an odorless, non-toxic white powder possessing a high melting point ($2852^\\circ\\text{C}$), making it valuable as a refractory lining material. In CBSE Class 10 chemistry, it serves as the primary exemplar of basic metallic oxides."
    },
    "magnesium-ribbon-combustion": {
      "id": "magnesium-ribbon-combustion",
      "filePath": "knowledge/chemistry/magnesium-ribbon-combustion.md",
      "category": "chemistry",
      "type": "experiment",
      "title": "Combustion of Magnesium Ribbon in Air",
      "description": "Highly exothermic combination reaction where magnesium ribbon burns in atmospheric oxygen with a dazzling white flame to form magnesium oxide ash.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/chemistry/magnesium-burning-setup",
      "tags": [
        "chemistry",
        "combustion",
        "oxidation",
        "cbse-class-10",
        "combination-reaction"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 1: Chemical Reactions and Equations",
          "activity": "Activity 1.1",
          "section": "1.1 Chemical Equations"
        }
      ],
      "equations": [
        {
          "latex": "2\\\\text{Mg}(s) + \\\\text{O}_2(g) \\\\xrightarrow{\\\\Delta} 2\\\\text{MgO}(s) + \\\\text{Heat} + \\\\text{Light}",
          "meaning": "Two moles of solid magnesium metal react with one mole of atmospheric oxygen gas upon heating to produce two moles of solid magnesium oxide powder along with substantial thermal and luminous energy.",
          "type": "chemical"
        },
        {
          "latex": "\\\\text{MgO}(s) + \\\\text{H}_2\\\\text{O}(l) \\\\rightarrow \\\\text{Mg(OH)}_2(aq)",
          "meaning": "Magnesium oxide reacts with water to form basic magnesium hydroxide, turning red litmus paper blue.",
          "type": "chemical"
        }
      ],
      "misconceptions": [
        {
          "claim": "The white powder left behind is unburnt magnesium or soot.",
          "correction": "The powder is a completely new chemical compound, magnesium oxide (MgO), with distinct physical and chemical properties."
        },
        {
          "claim": "Magnesium catches fire immediately at room temperature.",
          "correction": "Magnesium requires initial activation energy provided by the Bunsen flame before the reaction becomes self-sustaining and exothermic."
        }
      ],
      "safety": [
        "Wear UV-protective safety glasses or darkened goggles to prevent retinal glare and UV radiation damage.",
        "Always hold the ribbon using steel crucible tongs at arm's length; never touch the burning strip.",
        "Collect ash in a watch glass or porcelain crucible placed over a heat-resistant ceramic mat."
      ],
      "related_assets": [
        "magnesium-ribbon",
        "bunsen-burner",
        "laboratory-tongs",
        "watch-glass",
        "magnesium-oxide",
        "magnesium-burning-setup"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-metal",
        "magnesium-oxide",
        "combination-reaction",
        "bunsen-burner",
        "crucible-tongs"
      ],
      "body": "# Combustion of Magnesium Ribbon in Air\n\n## 1. Educational Overview\nThe burning of magnesium ribbon in air is the canonical foundational demonstration in the CBSE Class 10 Chemistry curriculum (NCERT Chapter 1, Activity 1.1). It introduces students to the observable hallmarks of a chemical reaction:\n- Evolution of energy (heat and dazzling white light).\n- Change in state and color (silvery flexible metal strip $\\rightarrow$ brittle white powder).\n- Formation of a new chemical substance with basic oxide properties.\n\n## 2. Experimental Procedure\n1. Take a 3–4 cm long strip of magnesium ribbon.\n2. Clean its surface thoroughly by rubbing with sandpaper until the silvery metal shines.\n3. Hold the cleaned ribbon securely with a pair of crucible tongs.\n4. Heat the tip of the ribbon in the hottest oxidizing zone (blue outer cone) of a Bunsen burner flame.\n5. As soon as the dazzling white ignition starts, hold the burning strip over a clean watch glass to collect the white magnesium oxide powder."
    },
    "oxygen-element": {
      "id": "oxygen-element",
      "filePath": "knowledge/chemistry/oxygen-element.md",
      "category": "chemistry",
      "type": "concept",
      "title": "Oxygen Element & Diatomic Molecule (O, O₂)",
      "description": "Highly electronegative non-metal in Group 16 of the Periodic Table with electronic configuration 2, 6; acts as the primary oxidizing agent in combustion reactions.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-29T00:00:00Z",
      "resource": "assets/chemistry/oxygen-atom",
      "tags": [
        "chemistry",
        "element",
        "non-metal",
        "oxygen",
        "valence",
        "combustion"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 1: Chemical Reactions and Equations",
          "section": "1.1 Chemical Reactions"
        },
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 3: Metals and Non-Metals",
          "section": "3.2.1 What happens when Metals are burnt in Air?"
        }
      ],
      "equations": [
        {
          "latex": "\\\\text{O} [2,6] + 2e^- \\\\rightarrow \\\\text{O}^{2-} [2,8]",
          "meaning": "Oxygen atom gains two electrons to form the divalent oxide anion.",
          "type": "chemical"
        },
        {
          "latex": "\\\\text{O}_2(g) \\\\rightarrow 2\\\\text{O}",
          "meaning": "Thermal dissociation of covalent oxygen molecules in combustion flame.",
          "type": "chemical"
        }
      ],
      "misconceptions": [
        {
          "claim": "Oxygen itself burns during combustion reactions.",
          "correction": "Oxygen is a supporter of combustion and an oxidizing agent; it does not burn on its own."
        }
      ],
      "safety": [],
      "related_assets": [
        "oxygen-atom"
      ],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion",
        "magnesium-metal",
        "magnesium-oxide",
        "combination-reaction"
      ],
      "body": "# Oxygen Element (O, Z=8)\n\n## Electronic Structure & Chemical Behavior\nOxygen ($Z = 8$) has 8 protons and 8 electrons configured as $1s^2 2s^2 2p^4$ (or $[2, 6]$). \nWith high electronegativity (3.44 on the Pauling scale), it readily pulls valence electrons from electropositive metals such as magnesium, forming crystalline basic oxides."
    },
    "cbse-class-10-science": {
      "id": "cbse-class-10-science",
      "filePath": "knowledge/curriculum/cbse-class-10-science.md",
      "category": "curriculum",
      "type": "curriculum",
      "title": "CBSE Class 10 Science (Board Examination Framework)",
      "description": "Official national curriculum standard published by CBSE and NCERT for secondary science education across Chemical Substances, World of Living, and Natural Phenomena.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "curriculum",
        "cbse",
        "ncert",
        "class-10",
        "science",
        "standards"
      ],
      "sources": [
        {
          "name": "Central Board of Secondary Education (CBSE)",
          "section": "Secondary School Curriculum: Science (Subject Code 086)",
          "url": "https://cbseacademic.nic.in"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [],
      "related_concepts": [
        "ncert-chemistry-ch01",
        "ncert-physics-ch11",
        "ncert-biology-ch06"
      ],
      "body": "# CBSE Class 10 Science Curriculum Specification\n\nThe CBSE Class 10 Science course (Code 086) establishes foundational STEM literacy organized into five thematic units:\n1. **Unit I: Chemical Substances — Nature and Behaviour** (Chemical Reactions, Acids/Bases/Salts, Metals and Non-Metals, Carbon Compounds).\n2. **Unit II: World of Living** (Life Processes, Control and Coordination, Reproduction, Heredity).\n3. **Unit III: Natural Phenomena** (Light – Reflection and Refraction, The Human Eye and Colourful World).\n4. **Unit IV: Effects of Current** (Electricity, Magnetic Effects of Electric Current).\n5. **Unit V: Natural Resources** (Our Environment)."
    },
    "ncert-biology-ch06": {
      "id": "ncert-biology-ch06",
      "filePath": "knowledge/curriculum/ncert-biology-ch06.md",
      "category": "curriculum",
      "type": "curriculum",
      "title": "NCERT Class 10 Biology — Chapter 6: Life Processes",
      "description": "Curriculum mapping for nutrition, respiration, transportation in animals and plants, and excretory systems.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "curriculum",
        "biology",
        "cbse-class-10",
        "life-processes",
        "circulation"
      ],
      "sources": [
        {
          "name": "NCERT Textbook for Class 10 Science",
          "chapter": "Chapter 6"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [
        "biology.human-heart-double-circulation"
      ],
      "related_concepts": [
        "human-heart-circulation",
        "cardiac-chambers",
        "cbse-class-10-science"
      ],
      "body": "# NCERT Class 10 Biology Chapter 6: Life Processes\n\nComprehensive study of metabolic life-sustaining processes: Autotrophic & Heterotrophic Nutrition, Aerobic & Anaerobic Respiration, Double Circulation & Lymphatic System, and Human Excretory System (Nephron structure)."
    },
    "ncert-chemistry-ch01": {
      "id": "ncert-chemistry-ch01",
      "filePath": "knowledge/curriculum/ncert-chemistry-ch01.md",
      "category": "curriculum",
      "type": "curriculum",
      "title": "NCERT Class 10 Chemistry — Chapter 1: Chemical Reactions and Equations",
      "description": "Curriculum mapping for chemical equations, balancing by hit-and-trial, combination, decomposition, displacement, double displacement, oxidation, and reduction reactions.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "curriculum",
        "chemistry",
        "cbse-class-10",
        "chemical-equations",
        "reactions"
      ],
      "sources": [
        {
          "name": "NCERT Textbook for Class 10 Science",
          "chapter": "Chapter 1"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [
        "chemistry.magnesium-ribbon"
      ],
      "related_concepts": [
        "magnesium-ribbon-combustion",
        "combination-reaction",
        "cbse-class-10-science"
      ],
      "body": "# NCERT Class 10 Chemistry Chapter 1\n\n## Core Activities & Practical Demonstrations\n- **Activity 1.1**: Burning of Magnesium Ribbon in Air ($2\\text{Mg} + \\text{O}_2 \\rightarrow 2\\text{MgO}$).\n- **Activity 1.2**: Precipitation of Lead Iodide ($\\text{Pb(NO}_3)_2 + 2\\text{KI} \\rightarrow \\text{PbI}_2 \\downarrow + 2\\text{KNO}_3$).\n- **Activity 1.3**: Zinc Granules in Dilute Sulphuric Acid ($\\text{Zn} + \\text{H}_2\\text{SO}_4 \\rightarrow \\text{ZnSO}_4 + \\text{H}_2 \\uparrow$)."
    },
    "ncert-physics-ch11": {
      "id": "ncert-physics-ch11",
      "filePath": "knowledge/curriculum/ncert-physics-ch11.md",
      "category": "curriculum",
      "type": "curriculum",
      "title": "NCERT Class 10 Physics — Chapter 11: The Human Eye and the Colourful World",
      "description": "Curriculum mapping for refraction through prisms, atmospheric refraction, dispersion, spectrum formation, rainbow physics, and Tyndall scattering.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "curriculum",
        "physics",
        "cbse-class-10",
        "optics",
        "prism",
        "dispersion"
      ],
      "sources": [
        {
          "name": "NCERT Textbook for Class 10 Science",
          "chapter": "Chapter 11"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "glass-prism-refraction",
        "optical-prism",
        "optical-dispersion",
        "cbse-class-10-science"
      ],
      "body": "# NCERT Class 10 Physics Chapter 11\n\nCovers the structure and defects of the human eye, refraction of light through a glass prism, dispersion of white light, atmospheric refraction (twinkling of stars, advance sunrise), and scattering of light (blue color of sky, red color at sunset)."
    },
    "angle-of-deviation": {
      "id": "angle-of-deviation",
      "filePath": "knowledge/physics/angle-of-deviation.md",
      "category": "physics",
      "type": "concept",
      "title": "Angle of Deviation (D or δ)",
      "description": "The angular difference between the forward trajectory of the incident light ray and the backward extension of the emergent ray after passing through a prism.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "physics",
        "optics",
        "deviation",
        "prism",
        "geometry",
        "cbse-class-10"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 11: The Human Eye and the Colourful World",
          "section": "11.2 Refraction of Light through a Prism"
        }
      ],
      "equations": [
        {
          "latex": "D = i + e - A",
          "meaning": "Deviation D equals the sum of incidence angle i and emergence angle e minus prism angle A.",
          "type": "physical"
        }
      ],
      "misconceptions": [],
      "safety": [],
      "related_assets": [],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "glass-prism-refraction",
        "optical-prism",
        "snells-law"
      ],
      "body": "# Angle of Deviation (D)\n\nIn a triangular prism, because the two lateral refracting surfaces are not parallel, the emergent ray is bent towards the thicker base of the prism. The angle between the incident direction and the final emergent direction is termed the Angle of Deviation ($D$)."
    },
    "convex-lens": {
      "id": "convex-lens",
      "filePath": "knowledge/physics/convex-lens.md",
      "category": "physics",
      "type": "apparatus",
      "title": "Double Convex Lens (Converging Lens)",
      "description": "Transparent optical element bounded by two outwardly curved spherical surfaces that refracts parallel incident light rays to converge at a focal point.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/physics/convex-lens",
      "tags": [
        "apparatus",
        "physics",
        "optics",
        "lens",
        "converging",
        "focal-length"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 10: Light – Reflection and Refraction",
          "section": "10.3.3 Refraction by Spherical Lenses"
        }
      ],
      "equations": [
        {
          "latex": "\\\\frac{1}{v} - \\\\frac{1}{u} = \\\\frac{1}{f}",
          "meaning": "Lens Formula relating image distance v, object distance u, and focal length f.",
          "type": "physical"
        },
        {
          "latex": "P = \\\\frac{1}{f\\\\text{ (meters)}}",
          "meaning": "Optical power of a lens in dioptres (D).",
          "type": "physical"
        }
      ],
      "misconceptions": [],
      "safety": [],
      "related_assets": [
        "convex-lens",
        "concave-lens"
      ],
      "related_lessons": [],
      "related_concepts": [
        "snells-law"
      ],
      "body": "# Double Convex Lens\n\nDouble convex lenses are the principal optical component in compound microscopes, astronomical telescopes, camera objectives, and corrective spectacles for hypermetropia (farsightedness)."
    },
    "electric-circuit": {
      "id": "electric-circuit",
      "filePath": "knowledge/physics/electric-circuit.md",
      "category": "physics",
      "type": "apparatus",
      "title": "Electric Circuit & Ohm's Law Verification Setup",
      "description": "Closed conducting loop comprising a DC power source, plug key switch, ammeter in series, voltmeter in parallel, rheostat, and nichrome resistor wire.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/physics/full-circuit",
      "tags": [
        "apparatus",
        "physics",
        "electricity",
        "ohms-law",
        "resistance",
        "circuit"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 12: Electricity",
          "activity": "Activity 12.1",
          "section": "12.2 Ohm's Law"
        }
      ],
      "equations": [
        {
          "latex": "V = I \\\\cdot R",
          "meaning": "Ohm's Law: Potential difference V across conductor equals electric current I multiplied by resistance R.",
          "type": "physical"
        },
        {
          "latex": "R = \\\\rho \\\\frac{l}{A}",
          "meaning": "Resistance formula in terms of electrical resistivity rho, length l, and cross-sectional area A.",
          "type": "physical"
        }
      ],
      "misconceptions": [],
      "safety": [
        "Ensure key is inserted only while taking readings to prevent resistor heating and resistance drift."
      ],
      "related_assets": [
        "full-circuit",
        "ammeter",
        "voltmeter",
        "resistor",
        "rheostat",
        "battery",
        "switch"
      ],
      "related_lessons": [],
      "related_concepts": [],
      "body": "# Electric Circuit & Ohm's Law Apparatus\n\nStandard CBSE Class 10 electricity setup for verifying the linear $V-I$ characteristic of metallic conductors. By varying the position of the rheostat sliding contact, students record multiple current-voltage pairs to plot a straight-line graph through the origin, whose slope represents the ohmic resistance $R = \\Delta V / \\Delta I$."
    },
    "glass-prism-refraction": {
      "id": "glass-prism-refraction",
      "filePath": "knowledge/physics/glass-prism-refraction.md",
      "category": "physics",
      "type": "experiment",
      "title": "Refraction of Light Through a Triangular Glass Prism",
      "description": "Experimental demonstration of angular deviation and chromatic dispersion when a collimated light ray traverses non-parallel refracting boundaries of an optical prism.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/physics/glass-prism-refraction",
      "tags": [
        "physics",
        "optics",
        "refraction",
        "prism",
        "dispersion",
        "cbse-class-10"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 11: The Human Eye and the Colourful World",
          "activity": "Activity 11.2",
          "section": "11.2 Refraction of Light through a Prism"
        }
      ],
      "equations": [
        {
          "latex": "\\\\angle A + \\\\angle D = \\\\angle i + \\\\angle e",
          "meaning": "The sum of the angle of the prism (A) and the angle of deviation (D) equals the sum of the angle of incidence (i) and the angle of emergence (e).",
          "type": "physical"
        },
        {
          "latex": "n = \\\\frac{\\\\sin\\\\left(\\\\frac{A + D_m}{2}\\\\right)}{\\\\sin\\\\left(\\\\frac{A}{2}\\\\right)}",
          "meaning": "Prism formula relating refractive index n to apex angle A and minimum angle of deviation Dm.",
          "type": "physical"
        }
      ],
      "misconceptions": [
        {
          "claim": "Light passing through a prism behaves exactly like light passing through a rectangular glass slab.",
          "correction": "In a rectangular slab with parallel faces, light undergoes lateral displacement without angular deviation. In a prism with inclined faces, light undergoes net angular deviation (D)."
        }
      ],
      "safety": [],
      "related_assets": [
        "glass-prism-refraction",
        "glass-prism",
        "glass-slab"
      ],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "optical-prism",
        "angle-of-deviation",
        "optical-dispersion",
        "snells-law"
      ],
      "body": "# Refraction of Light Through a Triangular Glass Prism\n\n## 1. Pedagogical Overview\nWhen a ray of light enters an equilateral triangular glass prism ($A = 60^\\circ$):\n1. **At first face $AB$ (Air $\\rightarrow$ Glass)**: Light enters an optically denser medium ($n \\approx 1.517$) and refracts towards the normal ($r_1 < i$).\n2. **Inside the prism along $EF$**: The ray propagates through the bulk glass.\n3. **At second face $AC$ (Glass $\\rightarrow$ Air)**: Light exits into the optically rarer air and refracts away from the second normal ($e > r_2$).\n4. **Deviation Angle ($D$)**: Extending the forward incident ray and backward emergent ray reveals the net angular deviation subtended at vertex $G$."
    },
    "optical-dispersion": {
      "id": "optical-dispersion",
      "filePath": "knowledge/physics/optical-dispersion.md",
      "category": "physics",
      "type": "phenomenon",
      "title": "Dispersion of White Light into Spectrum (VIBGYOR)",
      "description": "The phenomenon of splitting composite polychromatic white light into its seven constituent spectral colors upon refraction through a dispersive medium.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "physics",
        "optics",
        "dispersion",
        "spectrum",
        "vibgyor",
        "wavelength"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 11: The Human Eye and the Colourful World",
          "section": "11.3 Dispersion of White Light by a Glass Prism"
        }
      ],
      "equations": [
        {
          "latex": "n_{\\\\text{violet}} > n_{\\\\text{red}} \\\\implies D_{\\\\text{violet}} > D_{\\\\text{red}}",
          "meaning": "Higher refractive index for shorter wavelengths leads to greater angular deviation.",
          "type": "physical"
        }
      ],
      "misconceptions": [
        {
          "claim": "The prism creates color out of colorless light.",
          "correction": "White light already contains all spectral frequencies; the prism simply separates them spatially because their phase velocities in glass differ (dispersion)."
        }
      ],
      "safety": [],
      "related_assets": [
        "glass-prism-refraction"
      ],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "glass-prism-refraction",
        "optical-prism",
        "angle-of-deviation"
      ],
      "body": "# Dispersion of White Light by a Glass Prism\n\nSir Isaac Newton was the first to demonstrate that sunlight consists of seven constituent colors by placing two identical prisms in an inverted combination to recombine the separated spectrum back into white light.\nThe dispersion arises because the speed of light $v$ in a material medium varies with wavelength $\\lambda$ (Cauchy's dispersion equation: $n(\\lambda) = A + B/\\lambda^2$)."
    },
    "optical-prism": {
      "id": "optical-prism",
      "filePath": "knowledge/physics/optical-prism.md",
      "category": "physics",
      "type": "apparatus",
      "title": "Equilateral Triangular Glass Prism",
      "description": "Transparent optical element with two parallel triangular bases and three rectangular lateral refracting surfaces inclined at 60°.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "resource": "assets/physics/glass-prism",
      "tags": [
        "apparatus",
        "physics",
        "optics",
        "prism",
        "crown-glass"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 11: The Human Eye and the Colourful World",
          "section": "11.2 Refraction of Light through a Prism"
        }
      ],
      "equations": [],
      "misconceptions": [],
      "safety": [],
      "related_assets": [
        "glass-prism",
        "glass-prism-refraction"
      ],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "glass-prism-refraction",
        "angle-of-deviation",
        "optical-dispersion"
      ],
      "body": "# Equilateral Triangular Glass Prism\n\nA solid homogeneous block of optical glass (such as Schott N-BK7 crown glass) with two equilateral triangular end-faces and three rectangular lateral faces that refract and disperse light rays."
    },
    "snells-law": {
      "id": "snells-law",
      "filePath": "knowledge/physics/snells-law.md",
      "category": "physics",
      "type": "law",
      "title": "Snell's Law of Refraction",
      "description": "Fundamental optical law defining the invariant ratio between the sine of the angle of incidence and the sine of the angle of refraction across two isotropic media.",
      "status": "active",
      "verified": "human-reviewed",
      "timestamp": "2026-08-28T00:00:00Z",
      "tags": [
        "physics",
        "optics",
        "refraction",
        "snells-law",
        "wave-optics"
      ],
      "sources": [
        {
          "name": "NCERT Class 10 Science",
          "chapter": "Chapter 10: Light – Reflection and Refraction",
          "section": "10.3.2 Laws of Refraction of Light"
        }
      ],
      "equations": [
        {
          "latex": "\\\\frac{\\\\sin i}{\\\\sin r} = n_{21} = \\\\frac{n_2}{n_1} = \\\\frac{v_1}{v_2}",
          "meaning": "Snell's Law expressing refractive index n21 in terms of incident angle i, refracted angle r, and phase velocities v1 and v2.",
          "type": "physical"
        }
      ],
      "misconceptions": [],
      "safety": [],
      "related_assets": [
        "glass-prism-refraction",
        "glass-slab",
        "glass-prism"
      ],
      "related_lessons": [
        "physics.glass-prism-refraction"
      ],
      "related_concepts": [
        "glass-prism-refraction",
        "angle-of-deviation"
      ],
      "body": "# Snell's Law of Refraction\n\nThe refractive index $n$ quantifies the factor by which light wavefronts slow down when entering an optically denser medium. \nFor crown glass in air, $n \\approx 1.517$, meaning light travels approximately $1.517\\times$ slower in glass ($v \\approx 1.98 \\times 10^8\\text{ m/s}$) than in air/vacuum."
    }
  },
  "edges": [
    {
      "source": "aorta-systemic-trunk",
      "target": "human-heart-circulation",
      "kind": "concept-to-concept"
    },
    {
      "source": "aorta-systemic-trunk",
      "target": "cardiac-chambers",
      "kind": "concept-to-concept"
    },
    {
      "source": "aorta-systemic-trunk",
      "target": "human-heart",
      "kind": "concept-to-asset"
    },
    {
      "source": "aorta-systemic-trunk",
      "target": "biology.human-heart-double-circulation",
      "kind": "concept-to-lesson"
    },
    {
      "source": "cardiac-chambers",
      "target": "human-heart-circulation",
      "kind": "concept-to-concept"
    },
    {
      "source": "cardiac-chambers",
      "target": "aorta-systemic-trunk",
      "kind": "concept-to-concept"
    },
    {
      "source": "cardiac-chambers",
      "target": "human-heart",
      "kind": "concept-to-asset"
    },
    {
      "source": "cardiac-chambers",
      "target": "biology.human-heart-double-circulation",
      "kind": "concept-to-lesson"
    },
    {
      "source": "digestive-system",
      "target": "digestive-system",
      "kind": "concept-to-asset"
    },
    {
      "source": "human-eye-optics",
      "target": "convex-lens",
      "kind": "concept-to-concept"
    },
    {
      "source": "human-eye-optics",
      "target": "snells-law",
      "kind": "concept-to-concept"
    },
    {
      "source": "human-eye-optics",
      "target": "human-eye",
      "kind": "concept-to-asset"
    },
    {
      "source": "human-eye-optics",
      "target": "convex-lens",
      "kind": "concept-to-asset"
    },
    {
      "source": "human-heart-circulation",
      "target": "cardiac-chambers",
      "kind": "concept-to-concept"
    },
    {
      "source": "human-heart-circulation",
      "target": "aorta-systemic-trunk",
      "kind": "concept-to-concept"
    },
    {
      "source": "human-heart-circulation",
      "target": "human-heart",
      "kind": "concept-to-asset"
    },
    {
      "source": "human-heart-circulation",
      "target": "biology.human-heart-double-circulation",
      "kind": "concept-to-lesson"
    },
    {
      "source": "bunsen-burner",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "bunsen-burner",
      "target": "bunsen-burner",
      "kind": "concept-to-asset"
    },
    {
      "source": "bunsen-burner",
      "target": "magnesium-burning-setup",
      "kind": "concept-to-asset"
    },
    {
      "source": "bunsen-burner",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "combination-reaction",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "combination-reaction",
      "target": "magnesium-metal",
      "kind": "concept-to-concept"
    },
    {
      "source": "combination-reaction",
      "target": "magnesium-oxide",
      "kind": "concept-to-concept"
    },
    {
      "source": "combination-reaction",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "crucible-tongs",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "crucible-tongs",
      "target": "laboratory-tongs",
      "kind": "concept-to-asset"
    },
    {
      "source": "crucible-tongs",
      "target": "magnesium-burning-setup",
      "kind": "concept-to-asset"
    },
    {
      "source": "crucible-tongs",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "magnesium-metal",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-metal",
      "target": "magnesium-oxide",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-metal",
      "target": "magnesium-ribbon",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-metal",
      "target": "magnesium-atom",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-metal",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "magnesium-oxide",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-oxide",
      "target": "magnesium-metal",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-oxide",
      "target": "combination-reaction",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-oxide",
      "target": "magnesium-oxide",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-oxide",
      "target": "watch-glass",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-oxide",
      "target": "magnesium-oxide-lattice",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-oxide",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "magnesium-metal",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "magnesium-oxide",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "combination-reaction",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "bunsen-burner",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "crucible-tongs",
      "kind": "concept-to-concept"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "magnesium-ribbon",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "bunsen-burner",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "laboratory-tongs",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "watch-glass",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "magnesium-oxide",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "magnesium-burning-setup",
      "kind": "concept-to-asset"
    },
    {
      "source": "magnesium-ribbon-combustion",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "oxygen-element",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "oxygen-element",
      "target": "magnesium-metal",
      "kind": "concept-to-concept"
    },
    {
      "source": "oxygen-element",
      "target": "magnesium-oxide",
      "kind": "concept-to-concept"
    },
    {
      "source": "oxygen-element",
      "target": "combination-reaction",
      "kind": "concept-to-concept"
    },
    {
      "source": "oxygen-element",
      "target": "oxygen-atom",
      "kind": "concept-to-asset"
    },
    {
      "source": "oxygen-element",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "cbse-class-10-science",
      "target": "ncert-chemistry-ch01",
      "kind": "concept-to-concept"
    },
    {
      "source": "cbse-class-10-science",
      "target": "ncert-physics-ch11",
      "kind": "concept-to-concept"
    },
    {
      "source": "cbse-class-10-science",
      "target": "ncert-biology-ch06",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-biology-ch06",
      "target": "human-heart-circulation",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-biology-ch06",
      "target": "cardiac-chambers",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-biology-ch06",
      "target": "cbse-class-10-science",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-biology-ch06",
      "target": "biology.human-heart-double-circulation",
      "kind": "concept-to-lesson"
    },
    {
      "source": "ncert-chemistry-ch01",
      "target": "magnesium-ribbon-combustion",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-chemistry-ch01",
      "target": "combination-reaction",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-chemistry-ch01",
      "target": "cbse-class-10-science",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-chemistry-ch01",
      "target": "chemistry.magnesium-ribbon",
      "kind": "concept-to-lesson"
    },
    {
      "source": "ncert-physics-ch11",
      "target": "glass-prism-refraction",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-physics-ch11",
      "target": "optical-prism",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-physics-ch11",
      "target": "optical-dispersion",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-physics-ch11",
      "target": "cbse-class-10-science",
      "kind": "concept-to-concept"
    },
    {
      "source": "ncert-physics-ch11",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    },
    {
      "source": "angle-of-deviation",
      "target": "glass-prism-refraction",
      "kind": "concept-to-concept"
    },
    {
      "source": "angle-of-deviation",
      "target": "optical-prism",
      "kind": "concept-to-concept"
    },
    {
      "source": "angle-of-deviation",
      "target": "snells-law",
      "kind": "concept-to-concept"
    },
    {
      "source": "angle-of-deviation",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    },
    {
      "source": "convex-lens",
      "target": "snells-law",
      "kind": "concept-to-concept"
    },
    {
      "source": "convex-lens",
      "target": "convex-lens",
      "kind": "concept-to-asset"
    },
    {
      "source": "convex-lens",
      "target": "concave-lens",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "full-circuit",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "ammeter",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "voltmeter",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "resistor",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "rheostat",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "battery",
      "kind": "concept-to-asset"
    },
    {
      "source": "electric-circuit",
      "target": "switch",
      "kind": "concept-to-asset"
    },
    {
      "source": "glass-prism-refraction",
      "target": "optical-prism",
      "kind": "concept-to-concept"
    },
    {
      "source": "glass-prism-refraction",
      "target": "angle-of-deviation",
      "kind": "concept-to-concept"
    },
    {
      "source": "glass-prism-refraction",
      "target": "optical-dispersion",
      "kind": "concept-to-concept"
    },
    {
      "source": "glass-prism-refraction",
      "target": "snells-law",
      "kind": "concept-to-concept"
    },
    {
      "source": "glass-prism-refraction",
      "target": "glass-prism-refraction",
      "kind": "concept-to-asset"
    },
    {
      "source": "glass-prism-refraction",
      "target": "glass-prism",
      "kind": "concept-to-asset"
    },
    {
      "source": "glass-prism-refraction",
      "target": "glass-slab",
      "kind": "concept-to-asset"
    },
    {
      "source": "glass-prism-refraction",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    },
    {
      "source": "optical-dispersion",
      "target": "glass-prism-refraction",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-dispersion",
      "target": "optical-prism",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-dispersion",
      "target": "angle-of-deviation",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-dispersion",
      "target": "glass-prism-refraction",
      "kind": "concept-to-asset"
    },
    {
      "source": "optical-dispersion",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    },
    {
      "source": "optical-prism",
      "target": "glass-prism-refraction",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-prism",
      "target": "angle-of-deviation",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-prism",
      "target": "optical-dispersion",
      "kind": "concept-to-concept"
    },
    {
      "source": "optical-prism",
      "target": "glass-prism",
      "kind": "concept-to-asset"
    },
    {
      "source": "optical-prism",
      "target": "glass-prism-refraction",
      "kind": "concept-to-asset"
    },
    {
      "source": "optical-prism",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    },
    {
      "source": "snells-law",
      "target": "glass-prism-refraction",
      "kind": "concept-to-concept"
    },
    {
      "source": "snells-law",
      "target": "angle-of-deviation",
      "kind": "concept-to-concept"
    },
    {
      "source": "snells-law",
      "target": "glass-prism-refraction",
      "kind": "concept-to-asset"
    },
    {
      "source": "snells-law",
      "target": "glass-slab",
      "kind": "concept-to-asset"
    },
    {
      "source": "snells-law",
      "target": "glass-prism",
      "kind": "concept-to-asset"
    },
    {
      "source": "snells-law",
      "target": "physics.glass-prism-refraction",
      "kind": "concept-to-lesson"
    }
  ]
};

export const OKF_CONCEPTS: Record<string, OkfConcept> = OKF_MANIFEST.concepts;

export function getOkfConcept(id: string): OkfConcept | undefined {
  return OKF_CONCEPTS[id];
}

export function getOkfConceptsByCategory(category: string): OkfConcept[] {
  const ids = OKF_MANIFEST.byCategory[category] || [];
  return ids.map((id) => OKF_CONCEPTS[id]).filter(Boolean);
}

export function getOkfConceptsByType(type: OkfConceptType): OkfConcept[] {
  const ids = OKF_MANIFEST.byType[type] || [];
  return ids.map((id) => OKF_CONCEPTS[id]).filter(Boolean);
}

export function getOkfConceptsForAsset(assetId: string): OkfConcept[] {
  return Object.values(OKF_CONCEPTS).filter(
    (c) => c.related_assets && c.related_assets.includes(assetId)
  );
}

export function getOkfConceptsForLesson(lessonId: string): OkfConcept[] {
  return Object.values(OKF_CONCEPTS).filter(
    (c) => c.related_lessons && c.related_lessons.includes(lessonId)
  );
}
