# Educational Animation Framework

An AI-agent-friendly framework for building **2D/3D educational animations, interactive science experiments, and explanatory videos**.

The initial target is school-level STEM education, with the first canonical example being:

> **CBSE Class 10 Chemistry — Burning of Magnesium Ribbon**

The project is deliberately designed so that different AI coding agents can take over the repository without losing architectural context.

---

# Why this framework exists

Generating a complete educational animation directly from:

```text
Prompt → AI → Blender script
```

often produces inconsistent results.

Typical problems:

- objects are rebuilt from scratch every time;
- visual style changes between scenes;
- Blender scripts become enormous;
- animation timing is difficult to maintain;
- scientific content becomes mixed with rendering code;
- another AI agent cannot easily understand the scene;
- interactive and video versions require separate implementations.

This framework separates:

```text
EDUCATIONAL INTENT
        ↓
LESSON SPECIFICATION
        ↓
SEMANTIC SCENE GRAPH
        ↓
REUSABLE ASSETS + ANIMATION PRIMITIVES
        ↓
RENDERER
   ↙    ↓     ↘
Blender Three.js Remotion
```

---

# Design principles

## 1. Education first

The framework exists to explain concepts.

Visual effects are secondary.

## 2. Reuse before reinvention

Build reusable assets and animation primitives.

## 3. Semantic over technical

Lessons should say:

```text
heat magnesium
```

not:

```text
set Blender object Cube.004 rotation to ...
```

## 4. Renderer independence

A lesson should not be tightly coupled to Blender.

## 5. AI-agent continuity

Every major architectural decision must be documented so a different coding agent can continue the project.

## 6. Visual consistency

A magnesium atom should not look different in every lesson.

---

# Recommended technology stack

| Purpose | Technology |
|---|---|
| 3D modeling | Blender |
| Blender automation | Python |
| Interactive 3D | Three.js |
| React integration | React Three Fiber |
| Video composition | Remotion |
| Main application language | TypeScript |
| Scientific/offline utilities | Python |
| Source control | Git |
| AI development | Codex / Claude Code / Gemini CLI / other coding agents |

The framework does NOT require all tools to be used for every lesson.

---

# When to use each tool

## Blender

Use Blender when you need:

- high-quality 3D rendering;
- complex geometry;
- realistic laboratory equipment;
- procedural geometry;
- particles;
- camera choreography;
- offline rendering.

Blender is the primary **3D production tool**.

## Three.js / React Three Fiber

Use this when students need to interact with the scene.

Examples:

- rotate a molecule;
- click an atom;
- change resistance;
- adjust voltage;
- move a light ray;
- start/stop an experiment;
- inspect components.

Three.js is the primary **interactive 3D tool**.

## Remotion

Use this when producing:

- YouTube videos;
- classroom videos;
- short educational reels;
- narrated lessons;
- captioned lessons;
- diagram-heavy explanations.

Remotion is the primary **video composition layer**.

---

# Project architecture

Recommended target structure:

```text
edu-animation-framework/
│
├── AGENTS.md
├── README.md
├── package.json
├── tsconfig.json
│
├── docs/
│   ├── architecture.md
│   ├── authoring.md
│   ├── visual-system.md
│   ├── scientific-accuracy.md
│   └── agent-handoff.md
│
├── packages/
│   ├── core/
│   │   ├── lesson/
│   │   ├── scene/
│   │   ├── animation/
│   │   ├── assets/
│   │   └── validation/
│   │
│   ├── blender/
│   │   ├── python/
│   │   ├── assets/
│   │   └── renderer/
│   │
│   ├── three/
│   │   ├── components/
│   │   ├── scenes/
│   │   └── renderer/
│   │
│   └── remotion/
│       ├── compositions/
│       ├── components/
│       └── renderer/
│
├── assets/
│   ├── chemistry/
│   ├── physics/
│   ├── biology/
│   └── shared/
│
├── lessons/
│   └── chemistry/
│       └── magnesium-ribbon/
│           ├── lesson.json
│           ├── script.md
│           └── scenes/
│
├── examples/
│
└── tests/
```

The exact implementation may evolve. Do not create every directory just for the sake of having directories.

---

# Lesson model

A lesson represents educational intent.

Example:

```json
{
  "id": "chemistry.magnesium-ribbon",
  "title": "Burning of Magnesium Ribbon",
  "subject": "chemistry",
  "grade": 10,
  "curriculum": "CBSE",
  "scenes": [
    "introduction",
    "heating",
    "burning",
    "molecular-explanation",
    "chemical-equation"
  ]
}
```

The lesson definition should not contain Blender-specific implementation details.

---

# Canonical lesson

## Burning of Magnesium Ribbon

The first lesson should explain:

```text
Magnesium ribbon
       ↓
Heating
       ↓
Burning with bright white flame
       ↓
Magnesium reacts with oxygen
       ↓
Magnesium oxide forms
       ↓
2Mg + O₂ → 2MgO
```

The exact educational explanation must be validated against appropriate curriculum/scientific sources.

---

# Proposed scene sequence

## Scene 01 — Introduction

Show:

- laboratory environment;
- magnesium ribbon;
- tongs;
- burner.

Goal:

Establish the experiment.

---

## Scene 02 — Heating

Show:

- ribbon being held;
- flame;
- increasing heat.

Optional visual:

- temperature indicator;
- subtle material glow.

---

## Scene 03 — Burning

Show:

- bright white combustion;
- reaction;
- resulting white solid.

Avoid making the flame visually overwhelming.

The student must understand what happened.

---

## Scene 04 — Molecular explanation

Transition from the macroscopic experiment to a conceptual molecular representation.

Show:

```text
Mg atoms + O₂
       ↓
MgO
```

Important:

This is a conceptual visualization, not a claim that atoms can literally be observed this way.

---

## Scene 05 — Chemical equation

End with:

```text
2Mg + O₂ → 2MgO
```

Then optionally reveal:

```text
Magnesium + Oxygen → Magnesium Oxide
```

---

# Animation primitives

The framework should eventually provide reusable primitives such as:

```text
appear()
disappear()

move()
rotate()
scale()

highlight()
glow()

heat()
cool()
ignite()
burn()

combine()
separate()
transform()

flow()
orbit()

zoomCamera()
panCamera()

showLabel()
showEquation()
showMeasurement()

showAtom()
showMolecule()

showVector()
showGraph()
```

These are semantic operations.

A renderer decides how to implement them.

---

# Asset philosophy

Assets should represent concepts.

Examples:

```text
magnesium-ribbon
magnesium-atom
oxygen-molecule
magnesium-oxide
laboratory-tongs
bunsen-burner
```

Avoid exposing implementation-specific names such as:

```text
Cube.001
Sphere.004
Cylinder.008
```

---

# Visual system

Create a consistent visual language for:

- atoms;
- molecules;
- labels;
- arrows;
- equations;
- measurement indicators;
- highlights;
- particles;
- camera transitions.

A lesson should look like part of the same educational product even when another AI agent creates it.

---

# Scientific visualization conventions

Scientific diagrams often require deliberate exaggeration.

For example:

- atoms may be enlarged;
- molecules may be spaced apart;
- reaction time may be accelerated;
- energy may be represented by glow;
- invisible processes may be visualized using particles.

Whenever this happens, the visualization should be pedagogically clear and should not imply false physical scale.

---

# Interactive mode

An interactive lesson may expose controls such as:

```text
[ Heat ]

[ Start Reaction ]

[ Show Atoms ]

[ Show Molecules ]

[ Show Equation ]

[ Reset ]
```

Controls should be designed around learning objectives.

Avoid adding controls merely because the framework can support them.

---

# Video mode

A final educational video can combine:

```text
Blender render
     +
Remotion overlays
     +
Narration
     +
Captions
     +
Equations
     +
2D diagrams
```

This is preferable to forcing Blender to perform every piece of the production.

---

# AI coding workflow

The framework is specifically designed for AI coding agents.

When starting a task, an agent should:

1. Read `AGENTS.md`.
2. Read `README.md`.
3. Inspect the repository.
4. Find related lesson/asset/component.
5. Understand existing abstractions.
6. Plan the smallest change.
7. Implement.
8. Run validation.
9. Render/preview where relevant.
10. Inspect visual output.
11. Update documentation.
12. Report remaining limitations.

---

# Important instruction for AI agents

Do not interpret this repository as a blank canvas.

Before writing code, ask:

> "Can I reuse an existing primitive, asset, renderer, or lesson abstraction?"

If yes, reuse it.

If not, add the smallest reusable abstraction that solves the problem.

---

# Visual QA

A successful build is not enough.

For 3D scenes:

```text
Code works
    ≠
Animation looks correct
```

Agents should generate previews when possible.

Check:

- camera;
- framing;
- object visibility;
- scale;
- lighting;
- materials;
- animation timing;
- labels;
- scientific meaning;
- visual clutter.

---

# Performance

Interactive 3D must remain performant.

Prefer:

- low/moderate polygon assets;
- instancing;
- reusable geometries;
- compressed textures;
- lazy loading;
- reasonable particle counts.

Do not optimize prematurely, but do not import a 500 MB asset for a simple school experiment.

---

# Versioning

Use Git.

Prefer small commits.

Example:

```text
feat(chemistry): add magnesium ribbon asset
feat(animation): add heat primitive
feat(lesson): add magnesium burning scene
fix(blender): correct camera framing
docs: document molecular visualization scale
```

---

# Handoff protocol

Every AI agent should leave the repository in a state that another agent can continue.

At the end of work report:

```text
## Completed

- ...

## Files changed

- ...

## Validation

- ...

## Visual QA

- ...

## Known limitations

- ...

## Recommended next step

- ...
```

Do not leave important decisions only in chat.

Put durable knowledge in repository documentation.

---

# Development roadmap

## Phase 0 — Foundation

- repository structure;
- schemas;
- validation;
- design system;
- agent documentation.

## Phase 1 — Blender foundation

- deterministic scene creation;
- reusable asset conventions;
- camera system;
- material system;
- basic animation primitives.

## Phase 2 — First complete lesson

Build:

**Magnesium Ribbon Burning**

End-to-end.

## Phase 3 — Interactive renderer

Implement the same lesson in Three.js / React Three Fiber.

## Phase 4 — Video renderer

Implement Remotion composition.

## Phase 5 — Asset library

Add reusable:

- chemistry;
- physics;
- biology;
- mathematics assets.

## Phase 6 — Lesson authoring

Make it possible to define lessons mostly through declarative data.

## Phase 7 — AI authoring

Give an AI agent the ability to transform a lesson description into:

```text
lesson spec
→ scene plan
→ asset requests
→ animation plan
→ renderer implementation
→ validation
```

---

# What NOT to build yet

Do not start with:

- a full lesson CMS;
- cloud rendering;
- multiplayer;
- authentication;
- complex physics engine;
- AI video generation pipeline;
- massive asset marketplace;
- automatic curriculum generation.

First prove that one lesson can be created beautifully and repeatably.

---

# Definition of success

The framework is successful when an AI agent can receive:

> "Create an interactive Class 10 CBSE animation explaining why magnesium burns with a white flame."

and produce a lesson using existing:

- assets;
- scene primitives;
- animation primitives;
- visual system;
- validation;
- renderer infrastructure.

The agent should extend the framework rather than rebuild it.

---

# Long-term vision

The eventual system should allow an educator or developer to describe:

```text
Explain Ohm's Law to a Class 10 student.
```

and produce:

```text
Interactive 3D experiment
        +
2D explanatory diagrams
        +
Narrated video
        +
Captions
        +
Student controls
        +
Concept checks
```

from a common lesson specification.

That is the actual goal of this repository.
