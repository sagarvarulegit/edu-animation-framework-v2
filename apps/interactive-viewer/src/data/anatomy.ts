export interface PartInfo {
  name: string;
  circuit: 'pulmonary' | 'systemic' | 'coronary' | 'valvular';
  bloodType: 'Deoxygenated (CO2-rich)' | 'Oxygenated (O2-rich)' | 'Structural / Flow Control';
  function: string;
  cbseKeyPoint: string;
}

export const ANATOMY_KNOWLEDGE: Record<string, PartInfo> = {
  'human-heart-right-atrium': {
    name: 'Right Atrium (Upper Right Chamber)',
    circuit: 'pulmonary',
    bloodType: 'Deoxygenated (CO2-rich)',
    function: 'Receives oxygen-depleted blood returning from upper and lower body via the Superior and Inferior Vena Cava.',
    cbseKeyPoint: 'Thin-walled receiving chamber. Relaxes (atrial diastole) to fill with blood from vena cava, then contracts to pump blood past tricuspid valve into right ventricle.'
  },
  'human-heart-right-ventricle': {
    name: 'Right Ventricle (Lower Right Chamber)',
    circuit: 'pulmonary',
    bloodType: 'Deoxygenated (CO2-rich)',
    function: 'Pumps deoxygenated blood through the pulmonary semilunar valve into the pulmonary artery heading to the lungs.',
    cbseKeyPoint: 'Has thinner muscular walls than the left ventricle because it only needs to pump blood to the adjacent lungs against low pulmonary resistance.'
  },
  'human-heart-left-atrium': {
    name: 'Left Atrium (Upper Left Chamber)',
    circuit: 'systemic',
    bloodType: 'Oxygenated (O2-rich)',
    function: 'Receives freshly oxygenated blood returning from both lungs through the 4 pulmonary veins.',
    cbseKeyPoint: 'Receives blood with no muscular resistance during diastole, then contracts to pass blood through bicuspid (mitral) valve into the left ventricle.'
  },
  'human-heart-left-ventricle': {
    name: 'Left Ventricle (Lower Left Chamber)',
    circuit: 'systemic',
    bloodType: 'Oxygenated (O2-rich)',
    function: 'Powerhouse of systemic circulation; pumps oxygenated blood under high pressure through the aorta to the entire body.',
    cbseKeyPoint: 'Possesses the thickest muscular myocardium (~3x thicker than right ventricle) to generate necessary hydrostatic force to circulate blood throughout systemic organs.'
  },
  'human-heart-aortic-arch': {
    name: 'Aorta & Aortic Arch',
    circuit: 'systemic',
    bloodType: 'Oxygenated (O2-rich)',
    function: 'Main and largest artery of the human body, branching into brachiocephalic, carotid, subclavian, and descending systemic arteries.',
    cbseKeyPoint: 'Elastic arterial walls absorb systolic surge pressure and recoil during diastole to maintain steady blood pressure throughout the vascular tree.'
  },
  'human-heart-pulmonary-trunk': {
    name: 'Pulmonary Trunk & Arteries',
    circuit: 'pulmonary',
    bloodType: 'Deoxygenated (CO2-rich)',
    function: 'Conveys deoxygenated blood from right ventricle into the left and right lungs for gaseous exchange (alveolar oxygen uptake).',
    cbseKeyPoint: 'Crucial CBSE Exam Fact: The ONLY arteries in the human body that carry deoxygenated blood.'
  },
  'human-heart-superior-vena-cava': {
    name: 'Superior & Inferior Vena Cava',
    circuit: 'pulmonary',
    bloodType: 'Deoxygenated (CO2-rich)',
    function: 'Great systemic veins that collect venous deoxygenated blood from the head, neck, limbs, and abdomen into the right atrium.',
    cbseKeyPoint: 'Low pressure conduits with wide lumen facilitating steady venous return to the heart.'
  },
  'human-heart-left-superior-pulmonary-vein': {
    name: 'Pulmonary Veins',
    circuit: 'systemic',
    bloodType: 'Oxygenated (O2-rich)',
    function: 'Four vascular conduits transporting oxygen-saturated blood from pulmonary capillary beds directly into the left atrium.',
    cbseKeyPoint: 'Crucial CBSE Exam Fact: The ONLY veins in the human body that carry oxygenated blood.'
  }
};
