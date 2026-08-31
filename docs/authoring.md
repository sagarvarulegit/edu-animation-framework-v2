# Lesson & Content Authoring Guide

This guide explains how educators, developers, and AI agents author new scientific lessons, scene plans, and assets within the **Educational Animation Framework**.

---

## 1. Authoring Philosophy: Declarative & Semantic

A lesson must describe **WHAT happens conceptually**, not **HOW a renderer moves pixels or vertices**.

### ✅ Good Semantic Authoring:
```json
{
  "primitive": "heat",
  "target": "magnesium-ribbon",
  "duration": 4.0,
  "start": 2.0
}
```

### ❌ Bad Coupled Authoring:
```json
{
  "blender": {
    "object": "Cube.004",
    "location": [1.2, 4.8, 0.2],
    "keyframe": 72
  }
}
```

The latter couples the lesson to Blender and prevents rendering in Three.js or Remotion.

---

## 2. Step-by-Step Authoring Workflow

### Step 1: Define the Verified Concept in OKF (`knowledge/`)
Create a markdown document under `knowledge/<subject>/<id>.md` with YAML frontmatter:
```markdown
---
id: combination-reaction
type: concept
title: Combination Reaction
description: A reaction where two or more substances combine to form a single substance.
status: active
verified: human-reviewed
sources:
  - name: NCERT Class 10 Science
    chapter: Chapter 1 Chemical Reactions and Equations
    activity: Activity 1.1
cbse_mapping:
  class: 10
  subject: chemistry
  chapter: Chemical Reactions and Equations
equations:
  - latex: "A + B \\rightarrow AB"
    meaning: General combination reaction form
misconceptions:
  - claim: "All combination reactions are exothermic."
    correction: "While most combination reactions release heat, some require continuous energy input."
related_assets: [magnesium-ribbon, bunsen-burner, magnesium-oxide]
related_lessons: [chemistry.magnesium-ribbon]
---
```

### Step 2: Compile the OKF Knowledge Base
Run the compiler to update TypeScript runtime modules:
```bash
node tools/okf/compile-okf.mjs
```

### Step 3: Register Assets (`assets/`)
Every asset requires an `asset.json` matching `schemas/asset.schema.json`:
```json
{
  "id": "bunsen-burner",
  "name": "Bunsen Burner",
  "category": "chemistry",
  "version": "1.0.0",
  "semanticDescription": "Standard laboratory gas burner with adjustable air collar.",
  "scaleConvention": {
    "unit": "meters",
    "basis": "real-world-scale"
  },
  "provenance": {
    "generator": "procedural-blender-python",
    "method": "procedural-blender-python"
  },
  "rendererCompatibility": {
    "blender": true,
    "three": true
  }
}
```

### Step 4: Author the Lesson Specification (`lessons/`)
Create `lessons/<subject>/<lesson-id>/lesson.json`:
```json
{
  "id": "chemistry.magnesium-ribbon",
  "title": "Burning of Magnesium Ribbon",
  "subject": "chemistry",
  "grade": 10,
  "curriculum": "CBSE",
  "status": "final",
  "learningObjectives": [
    "Observe the combustion of magnesium in atmospheric oxygen.",
    "Identify the formation of white magnesium oxide powder.",
    "Understand the balanced chemical equation: 2Mg + O2 -> 2MgO."
  ],
  "scenes": [
    { "id": "01-introduction", "purpose": "Establish laboratory setup and apparatus." },
    { "id": "02-heating", "purpose": "Heat magnesium ribbon to ignition temperature." },
    { "id": "03-burning", "purpose": "Demonstrate dazzling white combustion and product formation." }
  ]
}
```

### Step 5: Author Scene Plans (`scenes/NN-<name>.json`)
Each scene plan defines apparatus instances, named camera shots, and timeline actions:
```json
{
  "id": "02-heating",
  "lessonId": "chemistry.magnesium-ribbon",
  "fps": 24,
  "duration": 6.0,
  "camera": {
    "shots": {
      "closeUp": { "position": [0.0, -0.25, 0.15], "target": [0.0, 0.0, 0.12], "lens": 50 }
    }
  },
  "instances": [
    { "asset": "bunsen-burner", "position": [0, 0, 0] },
    { "asset": "magnesium-ribbon", "position": [0, 0, 0.12] }
  ],
  "timeline": [
    { "primitive": "cameraMove", "start": 0.0, "duration": 1.0, "shot": "closeUp" },
    { "primitive": "showFlame", "start": 0.5, "target": "bunsen-burner" },
    { "primitive": "heat", "start": 1.0, "duration": 4.0, "target": "magnesium-ribbon" }
  ]
}
```

### Step 6: Define Narration & Subtitle Cues (`narration.json`)
```json
{
  "lessonId": "chemistry.magnesium-ribbon",
  "fps": 30,
  "totalDurationSeconds": 88.0,
  "scenes": [
    {
      "id": "01-introduction",
      "startFrame": 240,
      "endFrame": 600,
      "cues": [
        {
          "start": 8.0,
          "end": 14.0,
          "speaker": "Instructor",
          "text": "Clean a piece of magnesium ribbon about three to four centimetres long by rubbing it with sandpaper."
        }
      ]
    }
  ]
}
```

### Step 7: Validate & Test
```bash
npm test
```
The validator guarantees zero broken links, invalid IDs, or unrecognized primitives.

---

## 3. Supported Semantic Primitives

| Primitive | Purpose | Key Parameters |
|---|---|---|
| `appear` | Reveal an asset in the scene | `target`, `start`, `duration` |
| `disappear` | Fade or hide an asset | `target`, `start`, `duration` |
| `cameraMove` | Smoothly interpolate camera to a named shot | `shot`, `start`, `duration` |
| `showLabel` | Display a 3D or 2D annotation label | `target`, `text`, `start`, `end` |
| `move` | Translate an asset in 3D space | `target`, `offset: [x,y,z]`, `start`, `duration` |
| `heat` | Elevate temperature & thermal glow | `target`, `start`, `duration`, `strength` |
| `showFlame` | Ignite burner flame / particle plume | `target`, `start`, `color` |
| `burn` | Combustion reaction with dazzling emission | `target`, `start`, `duration` |
| `transform` | Morph or transition material/state | `target`, `look`, `start`, `duration` |
| `collectAsh` | Product powder deposition | `target`, `source`, `start`, `duration` |
| `showMolecule` | Spawn Bohr atom or ionic lattice | `id`, `model`, `position`, `start` |
| `showEquation` | Reveal LaTeX KaTeX equation card | `id`, `text`, `position`, `start`, `end` |

---

## 4. Educational Pacing Guidelines

Students need adequate cognitive time to:
1. **Notice** the apparatus and initial setup.
2. **Observe** the physical/chemical transformation.
3. **Interpret** the underlying scientific mechanism.
4. **Consolidate** the verified law or equation.

Keep pacing intentional and avoid rushing animations solely for speed.

