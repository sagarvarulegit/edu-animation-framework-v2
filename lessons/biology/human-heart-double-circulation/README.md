# Double Circulation in the Human Heart (`biology.human-heart-double-circulation`)

## Overview
Declarative CBSE Class 10 Biology lesson specification demonstrating the 4 chambers of the human heart, systemic and pulmonary circulatory loops, and valvular action preventing backflow during the cardiac cycle.

## Interface
- `lesson.json`: Primary lesson descriptor defining curriculum metadata, learning objectives, and 5 sequential scenes.
- `scenes/01-cardiac-anatomy.json`: Scene graph establishing 3D heart anatomy, chambers, and great vessels.
- `scenes/02-pulmonary-circulation.json`: Scene graph tracing deoxygenated blood pathway from vena cava to lungs.
- `scenes/03-systemic-circulation.json`: Scene graph tracing oxygenated blood from pulmonary veins to the aorta.
- `scenes/04-valvular-action-and-cycle.json`: Dynamic valvular action (tricuspid, bicuspid, semilunar) during systole and diastole.
- `scenes/05-double-circulation-summary.json`: Schematic consolidation of pulmonary and systemic double circulation.

## Invariants
- `lesson.json` must conform strictly to `schemas/lesson.schema.json`.
- All referenced scene identifiers must match existing scene graph JSON files under `scenes/`.
- Referenced asset `human-heart` must exist in `assets/biology/human-heart/asset.json`.

## Side Effects
- None. Declarative data consumed by 3D renderers and interactive viewers.

## Verification
- Run: `node tools/validate.mjs`
