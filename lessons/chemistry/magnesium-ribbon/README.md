# Burning of Magnesium Ribbon (`chemistry.magnesium-ribbon`)

## Overview
Canonical foundation lesson for CBSE Class 10 Chemistry Activity 1.1. Guides students from macro laboratory observations (heating ribbon, dazzling white flame, white magnesium oxide powder) to micro molecular explanations and balanced chemical equations.

## Interface
- `lesson.json`: Primary lesson descriptor with learning objectives, curriculum alignment, and 5 sequential scenes.
- `narration.json`: Subtitle timestamps, karaoke cues, and voiceover synchronization data.
- `script.md`: Director's screenplay, voice script, and pedagogical staging notes.
- `scenes/01-introduction.json`: Laboratory apparatus setup (ribbon, tongs, burner, watch glass).
- `scenes/02-heating.json`: Application of thermal energy to the magnesium ribbon.
- `scenes/03-burning.json`: Combustion reaction with brilliant white luminescence and ash formation.
- `scenes/04-molecular-explanation.json`: Conceptual Bohr atom and electron transfer visualization.
- `scenes/05-chemical-equation.json`: Transition from word equation to balanced formula ($2\text{Mg} + \text{O}_2 \rightarrow 2\text{MgO}$).

## Invariants
- `lesson.json` must conform strictly to `schemas/lesson.schema.json`.
- All 5 scenes must pass schema validation in `schemas/scene.schema.json`.
- Balanced chemical equation must match NCERT Class 10 Chapter 1 canonical notation.

## Side Effects
- None. Read-only declarative lesson data.

## Verification
- Run: `node tools/validate.mjs`
