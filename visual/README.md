# Educational Design System (`visual/`)

## Purpose

As defined in **Rule 7 of `AGENTS.md` ("Visual Consistency")**, educational STEM animations require consistent visual representations across lessons, disciplines, and rendering engines.

A magnesium ribbon, oxygen molecule, KaTeX chemical equation, or optical ray must share the exact same palette, typography, PBR shader parameters, camera framing conventions, and callout styles whether rendered in **Blender**, **Three.js / React Three Fiber**, or **Remotion**.

---

## Token Categories

The design system is partitioned into 9 core categories:

1. **`colors`**:
   - `ui`: Canvas background (`#020617`), surfaces (`#0f172a`), borders, and text hierarchy.
   - `reagents`: Scientific metals (`magnesiumRibbon`), reaction products (`magnesiumOxide`), flame zones (non-luminous blue vs. luminous yellow), and standard CPK element colors.
   - `optics`: Visible light wavelengths (400nm violet to 700nm red), normals, incident/refracted/emergent rays, and electrical conductors.
   - `biology`: Oxygenated vs. deoxygenated blood, myocardium cardiac tissue, DNA nucleotide bases, and neural action potentials.
   - `pedagogy`: OKF trust badges (`#10b981`), misconception warnings (`#f97316`), laboratory safety alerts (`#ef4444`), and observation callouts (`#38bdf8`).

2. **`typography`**:
   - Font families (`sans`, `mono`, `math`), font sizes (`badge` through `hero`), line heights, and weights.

3. **`materials`**:
   - Standard PBR material presets (`glass_borosilicate`, `metal_machined_steel`, `metal_magnesium_ribbon`, `powder_magnesium_oxide`, `flame_luminescent`, `prism_optical_glass`, etc.).

4. **`camera`**:
   - Standard educational focal lengths (35mm wide establishing, 50mm focus, 85mm molecular, 105mm macro product inspection) and shot specifications.

5. **`lighting`**:
   - Deterministic 3-point laboratory studio lighting rigs (Key, Fill, Rim, and Ambient) plus combustion flash profiles.

6. **`labels`**:
   - 3D Billboard font sizes and emissive ink styles; 2D overlay card padding, border radii, and backdrop blur constants.

7. **`arrows`**:
   - Vector arrows for chemical reactions, ray tracing, normal guides, electron flow, and hemodynamics.

8. **`equations`**:
   - KaTeX color semantics for reactants, products, catalysts, state symbols, and transition durations.

9. **`particles`**:
   - Rate, lifetime, color, and speed constants for combustion smoke, bright sparks, and electron transfers.

---

## Usage Across Renderers

### TypeScript / React / Remotion
```ts
import { TOKENS, hexToRgb, getKaTeXColor } from '../visual/design-tokens';

// Accessing colors
const flameColor = TOKENS.colors.reagents.bunsenFlameInner;

// Formatting KaTeX equations with unified token colors
const reactantLatex = `\\textcolor{${getKaTeXColor('reactant')}}{\\text{2Mg}}`;
```

### Blender Python
```python
import edu_design_tokens as tokens
import edu_asset_kit as kit

# Get linear sRGB color for Blender Principled BSDF
ribbon_color = tokens.color_linear("reagents.magnesiumRibbon")
kit.add_material("MagnesiumRibbonMat", color=ribbon_color[:3], metallic=0.85, roughness=0.35)
```
