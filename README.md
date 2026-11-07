# Educational Animation Framework Blueprint

## System Overview

An AI-agent-friendly framework for building **2D/3D educational animations, interactive science experiments, and explanatory videos**.

The initial target is school-level STEM education, with the canonical foundation example being:

> **CBSE Class 10 Chemistry — Burning of Magnesium Ribbon (Activity 1.1)**

The architecture strictly decouples educational intent from rendering implementation:

```text
EDUCATIONAL INTENT (knowledge/*.md via OKF v0.2)
        ↓
LESSON SPECIFICATION (lessons/*/*.json)
        ↓
SEMANTIC SCENE GRAPH (scenes/*.json)
        ↓
REUSABLE ASSETS + ANIMATION PRIMITIVES (assets/ + visual/ + renderers/)
        ↓
RENDERERS / RUNTIMES
   ↙         ↓         ↘
Blender   Three.js   Remotion
(Mode B)  (Mode A)   (Mode C)
```

---

## Subdirectories & System Boundaries

- [Lessons](./lessons/README.md): Declarative curriculum lesson specifications, scene graphs, and pedagogical objectives for Biology, Chemistry, and Physics.
- [Renderers](./renderers/README.md): 3D rendering engines and semantic animation primitives (Blender automation pipeline).
- [Schemas](./schemas/README.md): JSON Schema Draft specifications for assets, design tokens, lessons, scenes, and OKF concepts.
- [Tools & Utilities](./tools/README.md): Validation suite (`validate.mjs`), asset synchronization, visual QA capture scripts, and OKF compilation tools.
- [Visual Design System](./visual/README.md): Cross-renderer design tokens defining standardized colors, typography, PBR materials, cameras, lighting, and KaTeX styles.

---

## Global Invariants

1. **Renderer Independence**: Lesson definitions in `lessons/` must never contain engine-specific rendering code (e.g. no Blender bpy or Three.js code inside `lesson.json`).
2. **Visual Consistency (Rule 7)**: Reagent colors, element CPK colors, typography, and PBR materials must resolve strictly through `visual/design-tokens.json` across all renderers.
3. **Scientific Accuracy**: All curriculum content, balanced chemical equations, and ray tracing angles must cite authoritative sources (NCERT/CBSE) via Open Knowledge Format (`knowledge/*.md`).
4. **Schema Compliance**: All assets, lessons, scenes, and tokens must validate with 0 errors via `npm test` before rendering.
5. **Non-destructive Object Scale**: Procedural animations must use minimum scale `0.0001` instead of `0.0` during appearance/disappearance to avoid matrix singularities.

---

## Global Side Effects

- Compiling OKF (`npm run build:okf`) writes `knowledge/manifest.json` and generates TypeScript bindings in web and video applications.
- Asset synchronization (`tools/sync-web-assets.mjs`) copies binary 3D assets (`.glb`) into public web assets directories.
- Blender rendering (`npm run render:all-magnesium-ribbon`) generates image frames (`.png`) and videos on the local filesystem.

---

## System Verification

- Run: `npm test` (executes `node tools/validate.mjs`)
- OKF Compilation: `npm run build:okf`
- Visual Capture: `npm run test:visual`

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

---

# Design principles

## 1. Education first
The framework exists to explain concepts. Visual effects are secondary.

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

# Core Intention & Mission

The core mission of the **Educational Animation Framework** is to provide an AI-agent-friendly, deterministic, and modular architecture for creating accurate, visually consistent educational STEM animations, interactive simulations, and videos for CBSE/NCERT Class 9–12 education.

### Key Intentions:
1. **Scientific Correctness & Provenance**: Ground every apparatus, reaction, formula, and anatomical model in authoritative curricula via the Open Knowledge Format (`knowledge/*.md`).
2. **Pedagogical Clarity**: Every camera movement, glow, label, and timeline action must serve an explicit educational purpose, eliminating visual clutter.
3. **Write Once, Render Three Ways**: Author declarative lessons that can be experienced interactively in the browser (Three.js), rendered as cinematic 3D animations (Blender), or composed into narrated video lessons (Remotion).
4. **Agent-Ready AI Continuity**: Modular JSON schemas and deterministic Python/TypeScript generators allow multiple AI coding agents to collaborate without architectural drift.

---

# How to Use This Project

### 1. Prerequisites & Environment
- **Node.js**: `v18.19.1` or higher
- **Blender**: `v4.2 LTS` (Linux: `blender` on PATH; Windows: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`)
- **Package Manager**: `npm`

---

### 2. Quickstart Commands

```bash
# 1. Validate all schemas, assets, lessons, and OKF knowledge
npm test

# 2. Compile OKF Knowledge Base to runtime TypeScript bindings
npm run build:okf

# 3. Launch the Interactive 3D Viewer & Virtual Lab (Mode A)
npm run interactive:viewer

# 4. Launch the Remotion Video Composer Studio (Mode C)
npm run video:composer

# 5. Render Cinematic 3D Scenes in Blender (Mode B)
npm run render:all-magnesium-ribbon
```

---

### 3. Exploring the Three Delivery Modes

#### Mode A — Interactive 3D Simulation (Three.js / React Three Fiber)
Run `npm run interactive:viewer` (served via Vite at `http://localhost:5173`).
Features:
- **3D Asset Studio Inspector**: Browse 36 standardized science apparatus with PBR properties, dimension rulers, snap socket visualizers, CBSE syllabus tags, OKF trust badges, and JSON metadata export.
- **Interactive Experiment Simulations**:
  - *Chemistry*: Step-by-step burning of magnesium ribbon + Bohr atom electron transfer ($2\text{Mg} + \text{O}_2 \rightarrow 2\text{Mg}^{2+} + 2\text{O}^{2-}$).
  - *Physics*: Glass prism refraction with ray tracing, angle of deviation, and spectrum dispersion.
  - *Biology*: Human heart double circulation with 4 chambers, valves, and systemic/pulmonary circuits.
- **Virtual Lab Game World**: First-person (FPS) exploration navigating between chemistry, physics, and biology experiment benches.

#### Mode B — Cinematic 3D Pipeline (Blender 4.2 LTS)
Execute deterministic Python automation scripts:
```bash
# Generate core procedural apparatus (.blend + .glb + preview.png)
npm run build:lab-core-kit

# Render individual scene timeline plans
npm run render:scene01-introduction
npm run render:scene02-heating
npm run render:scene03-burning
```

#### Mode C — Video Composition Studio (Remotion 4)
Run `npm run video:composer` to open the interactive Remotion studio, or build the video bundle:
```bash
npm run video:render
```
Assembles the 88-second 1080p master video for CBSE Class 10 Chemistry Activity 1.1 with 3D tracks, KaTeX balanced equations, misconception callouts, and synchronized karaoke-style subtitles.

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

# Animation primitives

The framework provides reusable semantic operations:

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

These are semantic operations. A renderer decides how to implement them.
