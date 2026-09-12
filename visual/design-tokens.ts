/**
 * Educational Animation Framework — Design Tokens Adapter
 * Strongly-typed access to visual/design-tokens.json for React, Three.js, and Remotion.
 */

import tokensJson from './design-tokens.json';

export interface DesignTokens {
  version: string;
  name: string;
  description: string;
  colors: {
    ui: {
      background: string;
      surface: string;
      surfaceElevated: string;
      border: string;
      borderMuted: string;
      textPrimary: string;
      textMuted: string;
      accent: string;
      accentGlow: string;
      [key: string]: string;
    };
    reagents: {
      magnesiumRibbon: string;
      magnesiumOxide: string;
      bunsenFlameInner: string;
      bunsenFlameOuter: string;
      combustionFlash: string;
      heatGlow: string;
      cpkOxygen: string;
      cpkMagnesium: string;
      cpkHydrogen: string;
      cpkCarbon: string;
      cpkNitrogen: string;
      [key: string]: string;
    };
    optics: {
      incidentRay: string;
      normalLine: string;
      refractedRay: string;
      emergentRay: string;
      spectrumRed: string;
      spectrumOrange: string;
      spectrumYellow: string;
      spectrumGreen: string;
      spectrumBlue: string;
      spectrumIndigo: string;
      spectrumViolet: string;
      copperConductor: string;
      wirePositive: string;
      wireNegative: string;
      [key: string]: string;
    };
    biology: {
      oxygenatedBlood: string;
      deoxygenatedBlood: string;
      myocardium: string;
      endocardium: string;
      neuralImpulse: string;
      dnaPhosphate: string;
      dnaBaseAdenine: string;
      dnaBaseThymine: string;
      dnaBaseGuanine: string;
      dnaBaseCytosine: string;
      [key: string]: string;
    };
    pedagogy: {
      trustBadge: string;
      misconceptionAlert: string;
      safetyWarning: string;
      observationInfo: string;
      formulaAccent: string;
      [key: string]: string;
    };
  };
  typography: {
    fontFamilies: {
      sans: string;
      mono: string;
      math: string;
    };
    fontSizes: Record<string, string>;
    fontWeights: Record<string, number>;
    lineHeights: Record<string, number>;
  };
  materials: Record<
    string,
    {
      baseColor: string;
      metallic: number;
      roughness: number;
      transmission: number;
      ior: number;
      clearcoat: number;
      clearcoatRoughness: number;
      subsurfaceWeight: number;
      subsurfaceRadius: [number, number, number];
      subsurfaceScale: number;
      emissionColor?: string;
      emissionStrength?: number;
      subsurfaceColor?: string;
    }
  >;
  camera: {
    lenses: Record<string, number>;
    shots: Record<
      string,
      {
        lens: number;
        fovDegrees: number;
        description: string;
      }
    >;
    clipping: {
      near: number;
      far: number;
    };
  };
  lighting: {
    threePointStudio: {
      key: { energyWatts: number; color: string; radius: number };
      fill: { energyWatts: number; color: string; radius: number };
      rim: { energyWatts: number; color: string; radius: number };
      ambient: { color: string; strength: number };
    };
    combustionFlash: {
      peakWatts: number;
      baseWatts: number;
      color: string;
    };
  };
  labels: {
    threeD: {
      fontSize: number;
      inkColor: string;
      emissionStrength: number;
      billboardTrackAxis: string;
    };
    twoDOverlay: {
      borderRadius: string;
      backdropBlur: string;
      borderWidth: string;
      padding: string;
    };
  };
  arrows: {
    shaftRadius: number;
    headRatio: number;
    glowStrength: number;
    styles: Record<string, { color: string; dashed: boolean }>;
  };
  equations: {
    katexColors: {
      reactant: string;
      product: string;
      catalystOrHeat: string;
      stateSymbol: string;
      coefficient: string;
    };
    stateSymbols: Record<string, string>;
    transitionTimings: {
      wordToSkeletalFrames: number;
      skeletalToBalancedFrames: number;
    };
  };
  particles: {
    combustionSmoke: {
      ratePerSecond: number;
      lifetimeSeconds: number;
      baseColor: string;
      turbulence: number;
    };
    magnesiumSparks: {
      ratePerSecond: number;
      lifetimeSeconds: number;
      baseColor: string;
      speed: number;
    };
    electronTransfer: {
      durationSeconds: number;
      trailGlowColor: string;
      orbitSpeed: number;
    };
  };
}

export const TOKENS: DesignTokens = tokensJson as unknown as DesignTokens;

/**
 * Converts a hex color string to an RGB tuple in the range [0, 255].
 */
export function hexToRgb(hex: string): [number, number, number] {
  const clean = hex.replace('#', '');
  const r = parseInt(clean.substring(0, 2), 16);
  const g = parseInt(clean.substring(2, 4), 16);
  const b = parseInt(clean.substring(4, 6), 16);
  return [r, g, b];
}

/**
 * Converts a hex color string to normalized RGB components in the range [0.0, 1.0] for Three.js / WebGL shaders.
 */
export function hexToNormalizedRgb(hex: string): [number, number, number] {
  const [r, g, b] = hexToRgb(hex);
  return [r / 255, g / 255, b / 255];
}

/**
 * Converts a hex color string and alpha value into a standard CSS rgba(...) string.
 */
export function hexToRgba(hex: string, alpha: number): string {
  const [r, g, b] = hexToRgb(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Returns the standardized KaTeX color string for a chemical equation element.
 */
export function getKaTeXColor(
  role: 'reactant' | 'product' | 'catalystOrHeat' | 'stateSymbol' | 'coefficient'
): string {
  return TOKENS.equations.katexColors[role] || '#ffffff';
}

/**
 * Returns the hex color for a given visible light wavelength (nm).
 */
export function getWavelengthColor(wavelengthNm: number): string {
  if (wavelengthNm >= 620) return TOKENS.colors.optics.spectrumRed;
  if (wavelengthNm >= 590) return TOKENS.colors.optics.spectrumOrange;
  if (wavelengthNm >= 570) return TOKENS.colors.optics.spectrumYellow;
  if (wavelengthNm >= 500) return TOKENS.colors.optics.spectrumGreen;
  if (wavelengthNm >= 450) return TOKENS.colors.optics.spectrumBlue;
  if (wavelengthNm >= 420) return TOKENS.colors.optics.spectrumIndigo;
  return TOKENS.colors.optics.spectrumViolet;
}
