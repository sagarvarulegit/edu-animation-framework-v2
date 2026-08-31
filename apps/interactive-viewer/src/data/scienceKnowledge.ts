import {
  OKF_CONCEPTS,
  OKF_MANIFEST,
  getOkfConcept,
  getOkfConceptsByCategory,
  getOkfConceptsForAsset,
  getOkfConceptsForLesson,
  type OkfConcept,
  type OkfTrustTier,
  type OkfSourceCitation,
  type OkfEquation,
  type OkfMisconception
} from './generated/okfKnowledge';

export type {
  OkfConcept,
  OkfTrustTier,
  OkfSourceCitation,
  OkfEquation,
  OkfMisconception
};

export {
  OKF_CONCEPTS,
  OKF_MANIFEST,
  getOkfConcept,
  getOkfConceptsByCategory,
  getOkfConceptsForAsset,
  getOkfConceptsForLesson
};

export interface ScienceTopicInfo {
  name: string;
  category: 'physics' | 'chemistry' | 'biology';
  subType: string;
  description: string;
  cbseKeyPoint: string;
  formulaOrEquation?: string;
  okfId?: string;
}

export const SCIENCE_KNOWLEDGE: Record<string, ScienceTopicInfo> = {
  // PHYSICS: Prism Refraction
  'prism-glass-body': {
    name: 'Equilateral Triangular Glass Prism',
    category: 'physics',
    subType: 'Optical Dispersive Medium (Crown Glass n=1.517)',
    description: 'A transparent optical element with two triangular bases and three rectangular lateral refracting surfaces inclined at an angle of 60° (Angle of Prism A).',
    cbseKeyPoint: 'Because refracting faces are not parallel (unlike a rectangular glass slab), light rays undergo angular deviation rather than mere lateral shift.',
    formulaOrEquation: 'Angle of Prism A = 60°',
    okfId: 'optical-prism'
  },
  'prism-incident-ray': {
    name: 'Incident Light Ray (PE)',
    category: 'physics',
    subType: 'Monochromatic / White Collimated Beam',
    description: 'Light ray approaching refracting face AB at Angle of Incidence i = 48° with respect to the normal N1N1\'. Optical pins P1 and P2 mark its trajectory.',
    cbseKeyPoint: 'Snell\'s Law at first boundary: sin(i) / sin(r1) = n_glass. Since glass is denser than air, the ray refracts towards the normal (r1 < i).',
    formulaOrEquation: 'sin(48°) = 1.517 × sin(29.3°)',
    okfId: 'snells-law'
  },
  'prism-refracted-ray': {
    name: 'Refracted Light Ray inside Glass (EF)',
    category: 'physics',
    subType: 'Propagating Optical Wavefront',
    description: 'Ray propagating through the denser glass medium along path EF. Connects point of incidence E on face AB to point of emergence F on face AC.',
    cbseKeyPoint: 'Internal incident angle at face AC is r2 = A - r1 = 60° - 29.3° = 30.7°. In a symmetrical minimum-deviation setup, EF runs parallel to the base BC.',
    formulaOrEquation: 'r1 + r2 = A = 60°',
    okfId: 'glass-prism-refraction'
  },
  'prism-emergent-ray': {
    name: 'Emergent Light Ray (FS)',
    category: 'physics',
    subType: 'Deviated Exit Beam',
    description: 'Ray exiting face AC into rarer air at Emergent Angle e = 50.7° with respect to normal N2N2\'. Optical pins P3 and P4 align with images of P1 and P2.',
    cbseKeyPoint: 'Snell\'s Law at second boundary: n_glass × sin(r2) = sin(e). Passing into rarer air causes the ray to bend away from the normal.',
    formulaOrEquation: '1.517 × sin(30.7°) = sin(50.7°)',
    okfId: 'glass-prism-refraction'
  },
  'prism-deviation-angle': {
    name: 'Angle of Deviation (D or δ)',
    category: 'physics',
    subType: 'Fundamental Prism Metric',
    description: 'The angle subtended between the forward extension of the incident ray (EH) and the backward extension of the emergent ray (FG) at vertex G (D = 38.7°).',
    cbseKeyPoint: 'Universal Prism Law: Angle of Prism (A) + Angle of Deviation (D) = Angle of Incidence (i) + Angle of Emergence (e).',
    formulaOrEquation: 'A + D = i + e (60° + 38.7° = 48° + 50.7° = 98.7°)',
    okfId: 'angle-of-deviation'
  },
  'prism-dispersion-spectrum': {
    name: 'Dispersion & Rainbow Spectrum (VIBGYOR)',
    category: 'physics',
    subType: 'Wavelength-Dependent Refraction',
    description: 'Splitting of composite white light into 7 colors (Violet, Indigo, Blue, Green, Yellow, Orange, Red) on the observation screen due to varying refractive indices.',
    cbseKeyPoint: 'Violet light has the shortest wavelength and highest refractive index, so it bends the most. Red light has the longest wavelength and lowest refractive index, so it bends the least.',
    formulaOrEquation: 'n_violet (1.532) > n_red (1.513) ⇒ D_violet > D_red',
    okfId: 'optical-dispersion'
  },
  'prism-optical-pins': {
    name: 'Optical Alignment Pins (P1, P2, P3, P4)',
    category: 'physics',
    subType: 'Experimental Parallax Alignment',
    description: 'Vertical steel pins with crimson spherical heads fixed along incident ray (P1, P2) and aligned visually with their virtual images on emergent face (P3, P4).',
    cbseKeyPoint: 'Pins P1 and P2 should be spaced at least 5 cm apart to minimize parallax error when sighting through face AC.',
    formulaOrEquation: 'P1, P2 collinear with E; P3, P4 collinear with F',
    okfId: 'glass-prism-refraction'
  },

  // CHEMISTRY: Magnesium Ribbon Burning
  'chem-bunsen-burner': {
    name: 'Laboratory Bunsen Burner',
    category: 'chemistry',
    subType: 'Gas Flame Heat Source',
    description: 'Cast-iron base burner with adjustable brass air-collar providing a non-luminous blue oxidizing flame with temperatures exceeding 1000°C.',
    cbseKeyPoint: 'Provides the activation energy required to initiate the highly exothermic combination reaction between magnesium metal and atmospheric oxygen.',
    formulaOrEquation: 'CH4 + 2O2 → CO2 + 2H2O + Heat',
    okfId: 'bunsen-burner'
  },
  'chem-magnesium-ribbon': {
    name: 'Magnesium Ribbon Strip (Mg)',
    category: 'chemistry',
    subType: 'Alkaline Earth Metal Reactant',
    description: 'Silvery elemental magnesium metal strip held with tongs. Must be rubbed with sandpaper prior to burning to remove the protective layer of basic magnesium carbonate/oxide.',
    cbseKeyPoint: 'CBSE Exam Favourite: Magnesium ribbon is cleaned with sandpaper before burning to remove the protective oxide layer that hinders combustion.',
    formulaOrEquation: '2Mg(s) + O2(g) → 2MgO(s) + Heat + Light',
    okfId: 'magnesium-ribbon-combustion'
  },
  'chem-tongs': {
    name: 'Crucible / Laboratory Tongs',
    category: 'chemistry',
    subType: 'Safety Handling Apparatus',
    description: 'Stainless steel scissor tongs used to securely hold the magnesium strip at distance while burning, preventing thermal burns.',
    cbseKeyPoint: 'Safety guideline: Always hold burning magnesium with tongs and wear UV-protective safety glasses to protect retinas from intense ultraviolet/white glare.',
    formulaOrEquation: 'Safety Equipment',
    okfId: 'crucible-tongs'
  },
  'chem-watch-glass': {
    name: 'Watch Glass Collector & MgO Powder',
    category: 'chemistry',
    subType: 'Product Collector & Oxide Ash',
    description: 'Borosilicate concave watch glass holding the fluffy brilliant-white magnesium oxide (MgO) ash powder produced during combustion.',
    cbseKeyPoint: 'Magnesium Oxide is a basic oxide. When dissolved in water, it forms Magnesium Hydroxide [Mg(OH)2], which turns red litmus paper blue.',
    formulaOrEquation: 'MgO(s) + H2O(l) → Mg(OH)2(aq) (Basic)',
    okfId: 'magnesium-oxide'
  },
  'chem-sandpaper': {
    name: 'Abrasive Sandpaper Sheet',
    category: 'chemistry',
    subType: 'Surface Preparation Tool',
    description: 'Silicon carbide abrasive paper used to scour the ribbon surface and expose fresh, reactive magnesium metal before ignition.',
    cbseKeyPoint: 'Exposure to humid air forms a dull passivation layer of MgCO3.Mg(OH)2 on magnesium; sandpaper mechanically removes this layer.',
    formulaOrEquation: 'Mechanical Surface Cleaning',
    okfId: 'magnesium-metal'
  },

  // BIOLOGY: Human Heart & Double Circulation
  'human-heart-right-atrium': {
    name: 'Right Atrium (Upper Right Chamber)',
    category: 'biology',
    subType: 'Deoxygenated (CO2-rich) Blood Receiver',
    description: 'Receives oxygen-depleted blood returning from upper and lower body via the Superior and Inferior Vena Cava.',
    cbseKeyPoint: 'Thin-walled receiving chamber. Relaxes (atrial diastole) to fill with blood from vena cava, then contracts to pump blood past tricuspid valve into right ventricle.',
    formulaOrEquation: 'Deoxygenated Blood → Right Atrium',
    okfId: 'cardiac-chambers'
  },
  'human-heart-right-ventricle': {
    name: 'Right Ventricle (Lower Right Chamber)',
    category: 'biology',
    subType: 'Pulmonary Circuit Pump',
    description: 'Pumps deoxygenated blood through the pulmonary semilunar valve into the pulmonary artery heading to the lungs.',
    cbseKeyPoint: 'Has thinner muscular walls than the left ventricle because it only needs to pump blood to the adjacent lungs against low pulmonary resistance.',
    formulaOrEquation: 'Right Ventricle → Pulmonary Artery → Lungs',
    okfId: 'cardiac-chambers'
  },
  'human-heart-left-atrium': {
    name: 'Left Atrium (Upper Left Chamber)',
    category: 'biology',
    subType: 'Oxygenated (O2-rich) Blood Receiver',
    description: 'Receives freshly oxygenated blood returning from both lungs through the 4 pulmonary veins.',
    cbseKeyPoint: 'Receives blood with no muscular resistance during diastole, then contracts to pass blood through bicuspid (mitral) valve into the left ventricle.',
    formulaOrEquation: 'Lungs → Pulmonary Veins → Left Atrium',
    okfId: 'cardiac-chambers'
  },
  'human-heart-left-ventricle': {
    name: 'Left Ventricle (Lower Left Chamber)',
    category: 'biology',
    subType: 'Systemic Circuit High-Pressure Pump',
    description: 'Powerhouse of systemic circulation; pumps oxygenated blood under high pressure through the aorta to the entire body.',
    cbseKeyPoint: 'Possesses the thickest muscular myocardium (~3x thicker than right ventricle) to generate necessary hydrostatic force to circulate blood throughout systemic organs.',
    formulaOrEquation: 'Left Ventricle → Aorta → Systemic Organs',
    okfId: 'cardiac-chambers'
  },
  'human-heart-aortic-arch': {
    name: 'Aorta & Aortic Arch',
    category: 'biology',
    subType: 'Great Systemic Elastic Artery',
    description: 'Main and largest artery of the human body, branching into brachiocephalic, carotid, subclavian, and descending systemic arteries.',
    cbseKeyPoint: 'Elastic arterial walls absorb systolic surge pressure and recoil during diastole to maintain steady blood pressure throughout the vascular tree.',
    formulaOrEquation: 'Aorta: Main Systemic Trunk',
    okfId: 'aorta-systemic-trunk'
  }
};
