# Glass Prism Refraction (`physics.glass-prism-refraction`)

## Overview
CBSE Class 10 Physics lesson specification exploring the refraction of light through an equilateral glass prism, demonstrating double refraction, calculation of the Angle of Deviation ($A + D = i + e$), and white light dispersion into the VIBGYOR spectrum.

## Interface
- `lesson.json`: Primary lesson descriptor defining curriculum metadata and 4 sequential optical scenes.
- `script.md`: Screenplay and optical ray tracing experiment protocol.
- `scenes/01-bench-setup.json`: Drawing board, white paper sheet, and triangular glass prism outline.
- `scenes/02-ray-tracing.json`: Incident ray, first refraction, and passage through glass medium.
- `scenes/03-angle-of-deviation.json`: Emergent ray, normal lines, and calculation of angle of deviation ($D$).
- `scenes/04-dispersion-spectrum.json`: White light beam splitting into seven constituent spectral colours.

## Invariants
- `lesson.json` must conform strictly to `schemas/lesson.schema.json`.
- Prism angles must preserve the optical identity: $\text{Angle of Prism } (A) + \text{Angle of Deviation } (D) = \text{Angle of Incidence } (i) + \text{Angle of Emergence } (e)$.
- Spectrum dispersion order must adhere strictly to wavelength sequence (VIBGYOR).

## Side Effects
- None. Read-only declarative lesson data.

## Verification
- Run: `node tools/validate.mjs`
