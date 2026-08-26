# AGENTS.md — Educational Animation Framework

## Mission

Build a reusable, AI-agent-friendly framework for creating accurate, visually clear 2D/3D educational animations and interactive science demonstrations.

The framework is intended for school-level STEM education first, especially CBSE/Class 9–12 topics, but architecture should remain general enough for mathematics, biology, chemistry, and physics.

The primary goal is NOT photorealism. The primary goals are:

1. Scientific correctness.
2. Pedagogical clarity.
3. Visual consistency.
4. Deterministic/reproducible scenes.
5. Reusable assets and animation primitives.
6. Easy continuation by a different AI coding agent.
7. Separation between lesson content and rendering technology.

---

# 1. Non-negotiable agent rules

## 1.1 Read before changing anything

Before modifying the repository:

- Read this file completely.
- Read `README.md`.
- Inspect the repository tree.
- Inspect existing lesson specifications.
- Inspect existing reusable components before creating new ones.
- Never assume a component does not exist.

If a task references an existing lesson, asset, animation, or renderer, locate it first.

## 1.2 Preserve the architecture

Do NOT collapse the system into a single script.

Do NOT create a giant Blender Python script containing:

- lesson content
- asset definitions
- animation logic
- camera logic
- narration
- captions
- rendering configuration

Instead keep these concerns separate.

Preferred flow:

Lesson specification
    ↓
Scene / semantic model
    ↓
Reusable educational primitives
    ↓
Renderer adapter
    ↓
Blender / Three.js / Remotion output

## 1.3 Do not over-engineer prematurely

Prefer a small working abstraction over a generalized framework nobody can use.

Create an abstraction only when:

- it is used by at least two scenes, OR
- it clearly represents a stable educational primitive.

Avoid speculative plugin systems, complex ECS architectures, or unnecessary microservices.

## 1.4 Never sacrifice scientific correctness for visual effects

Effects must never change the scientific meaning.

If a visual is scientifically simplified, document that simplification.

For example:

- molecular models are representations, not literal photographs;
- atom sizes are not to scale unless explicitly stated;
- reaction animations may compress time;
- particle counts may be illustrative.

## 1.5 Do not hallucinate scientific facts

For educational content:

- distinguish facts from visual metaphors;
- verify equations and reaction products;
- use authoritative educational/scientific sources when needed;
- do not invent numerical values;
- do not silently change a textbook concept.

If the requested content is scientifically ambiguous, stop and flag the ambiguity in the lesson specification rather than inventing an answer.

---

# 2. Technology strategy

Use the following architecture unless there is a strong documented reason not to.

## Blender

Use Blender for:

- 3D asset creation
- complex 3D scenes
- scientific 3D visualizations
- lighting
- materials
- camera animation
- final 3D rendering
- procedural geometry
- reusable `.blend` assets when appropriate

Use Blender Python for deterministic scene construction and automation.

Do NOT use Blender as the lesson-authoring language.

## Three.js / React Three Fiber

Use Three.js / React Three Fiber for:

- browser-based interactive 3D
- student-controlled camera
- clickable objects
- sliders
- toggles
- interactive experiments
- exploratory molecular models
- simulations that benefit from real-time interaction

## Remotion

Use Remotion for:

- final educational video composition
- titles
- captions
- narration synchronization
- diagrams
- 2D overlays
- transitions
- reusable video templates

## TypeScript

Prefer TypeScript for:

- lesson definitions
- scene metadata
- semantic animation descriptions
- interactive applications
- renderer orchestration

## Python

Prefer Python for:

- Blender automation
- asset processing
- procedural geometry
- scientific data preparation
- offline rendering helpers

---

# 3. Rendering philosophy

The framework should support three output modes.

### Mode A — Interactive

Three.js / React Three Fiber

Example:

Student can rotate a magnesium ribbon experiment and press "Heat".

### Mode B — Cinematic 3D

Blender

Example:

A controlled 90-second educational animation of magnesium burning.

### Mode C — Educational video

Remotion + rendered assets

Example:

3D experiment + narration + captions + equation + diagrams.

The same lesson should ideally be able to share semantic content between these modes.

---

# 4. Lesson architecture

Every lesson should have a semantic specification.

Example conceptual structure:

```text
lesson/
  lesson.json
  script.md
  scenes/
    01-introduction.json
    02-heating.json
    03-burning.json
    04-molecular-view.json
    05-equation.json
```

A lesson specification should describe WHAT happens, not HOW Blender implements it.

Good:

```json
{
  "action": "heat",
  "target": "magnesium-ribbon",
  "duration": 3
}
```

Bad:

```json
{
  "blender": {
    "object": "Cube.004",
    "location": [1.2, 4.8, 0.2],
    "keyframe": 72
  }
}
```

The second format couples the lesson to Blender implementation and is prohibited in lesson specifications.

---

# 5. Semantic animation primitives

Prefer reusable primitives such as:

- `appear`
- `disappear`
- `move`
- `rotate`
- `scale`
- `highlight`
- `heat`
- `cool`
- `glow`
- `burn`
- `ignite`
- `explode`
- `combine`
- `separate`
- `transform`
- `dissolve`
- `flow`
- `orbit`
- `zoomCamera`
- `panCamera`
- `showLabel`
- `showEquation`
- `showMeasurement`
- `showMolecule`
- `showAtom`
- `showVector`
- `showGraph`

A primitive must have a documented semantic meaning and renderer implementations where applicable.

---

# 6. Asset rules

Assets should be reusable.

Preferred structure:

```text
assets/
  chemistry/
    magnesium/
    oxygen/
    magnesium-oxide/
  physics/
    battery/
    resistor/
    bulb/
  biology/
    cell/
```

Every reusable asset should have:

- stable ID
- human-readable name
- category
- source/license information where applicable
- scale convention
- semantic description
- renderer compatibility
- optional preview

Never encode meaning solely through arbitrary Blender object names.

Bad:

`Cube.001`

Better:

`magnesium-ribbon`

---

# 7. Visual consistency

The same concept must look the same across lessons unless a lesson intentionally overrides it.

Examples:

- magnesium ribbon has a consistent material;
- oxygen molecule has a consistent representation;
- arrows use the same visual language;
- labels use the same typography;
- chemical equations use the same formatting;
- camera conventions are predictable.

Create a design system.

Suggested categories:

```text
visual/
  colors
  typography
  materials
  camera
  lighting
  labels
  arrows
  equations
  particles
```

Do not scatter arbitrary colors and font sizes throughout scene code.

---

# 8. Coordinate and scale conventions

Choose one world-unit convention and document it.

Do not mix arbitrary scales between assets.

For scientific visualizations:

- physical laboratory objects may use approximate real-world scale;
- molecular scenes may intentionally use a different visualization scale;
- transitions between scales must be explicit.

Never claim molecular visualization is physically to scale unless it actually is.

---

# 9. Camera rules

Camera movement should communicate information.

Avoid:

- unnecessary camera spins;
- constant motion;
- dramatic zooms with no pedagogical purpose;
- motion that makes labels difficult to read.

Prefer:

- establish;
- focus;
- explain;
- reveal;
- return.

Camera animation should be named semantically where possible:

```text
establishExperiment
focusOnRibbon
zoomIntoMolecularScale
returnToExperiment
```

---

# 10. Animation quality rules

Animations should have:

- clear start state;
- clear action;
- clear end state;
- readable timing;
- intentional easing;
- enough pause time for students to understand.

Avoid mechanically linear movement everywhere.

Use appropriate easing.

Important educational events should have a short anticipation or pause when helpful.

---

# 11. AI-generated assets

AI-generated assets may be used, but:

- inspect geometry;
- inspect topology when relevant;
- inspect scale;
- inspect materials;
- remove unnecessary complexity;
- normalize naming;
- optimize before committing;
- document provenance if required.

Do not blindly import an AI-generated asset into the core library.

---

# 12. Blender-specific rules

Blender automation must be deterministic.

Scripts should:

- start from a known scene state;
- avoid dependence on current selection;
- avoid dependence on current active object;
- explicitly create or retrieve objects;
- use stable names/IDs;
- explicitly configure camera;
- explicitly configure render settings;
- save outputs to known paths.

Do not write scripts that depend on:

```python
bpy.context.selected_objects
```

unless selection is intentionally part of the operation.

Prefer explicit object references.

Avoid hard-coded object indices.

---

# 13. Three.js-specific rules

Prefer React Three Fiber for larger interactive lessons.

Keep:

- lesson state;
- scene state;
- UI state;
- rendering;
- educational narration

separate.

Do not put all logic into a single React component.

Use reusable components:

```text
<MagnesiumRibbon />
<LabStand />
<Burner />
<Atom />
<Molecule />
<ReactionArrow />
<Equation />
<CameraController />
```

Interactive controls must have an educational purpose.

---

# 14. Remotion rules

Remotion compositions should separate:

- content
- timing
- visual components
- audio
- narration
- captions

Do not hard-code every frame number throughout a composition.

Prefer semantic timing constants:

```ts
const INTRO_DURATION = ...
const HEATING_DURATION = ...
const REACTION_DURATION = ...
```

---

# 15. Testing

At minimum, test:

### Lesson validation

- required metadata exists;
- referenced assets exist;
- referenced primitives exist;
- no duplicate IDs;
- schema is valid.

### Rendering validation

- scene can initialize from a clean environment;
- camera exists;
- render settings exist;
- expected output is generated.

### Interactive validation

- application starts;
- scene loads;
- controls work;
- no console errors;
- reset returns to initial state.

### Visual validation

When possible generate preview renders and inspect them.

AI agents must not claim a scene "looks correct" merely because code executed successfully.

Code correctness != visual correctness.

---

# 16. Agent workflow

For every task:

### Step 1 — Understand

Read:

- AGENTS.md
- README.md
- relevant lesson
- relevant component
- relevant renderer

### Step 2 — Plan

Before implementation, identify:

- affected files;
- reusable components;
- new assets;
- new primitives;
- tests;
- outputs.

### Step 3 — Implement the smallest useful change

Do not rewrite unrelated code.

### Step 4 — Validate

Run:

- type checks;
- lint;
- tests;
- lesson validation;
- renderer checks;
- render/preview where applicable.

### Step 5 — Inspect

If visual output exists, inspect it.

### Step 6 — Document

Update documentation when architecture or public behavior changes.

### Step 7 — Handoff

At the end of the task, report:

```text
Changed:
- ...

Added:
- ...

Validated:
- ...

Known limitations:
- ...

Next recommended step:
- ...
```

---

# 17. Do not leave hidden assumptions

If you make a decision that another AI agent would need to know, document it.

Especially document:

- coordinate conventions;
- asset scale;
- renderer limitations;
- temporary hacks;
- external dependencies;
- known visual defects;
- scientific assumptions.

---

# 18. Never destroy working work

Before large refactors:

- inspect git status;
- preserve working behavior;
- make incremental changes.

Do not delete an existing implementation merely because you prefer a different architecture.

If replacement is necessary, explain why and preserve migration compatibility where practical.

---

# 19. Definition of Done

A feature is not done because the code compiles.

A lesson feature is done when:

- semantic lesson data exists;
- assets are reusable;
- renderer implementation works;
- visual result has been inspected;
- educational meaning is clear;
- documentation is updated;
- validation passes;
- another AI agent can understand the implementation without asking the original author.

---

# 20. Current project priority

The first canonical lesson is:

**CBSE Class 10 Chemistry — Burning of Magnesium Ribbon**

Use it to prove the architecture.

Target sequence:

1. Physical experiment.
2. Heating.
3. Bright white combustion.
4. White magnesium oxide product.
5. Molecular explanation.
6. Balanced chemical equation.
7. Optional interactive exploration.

Do not build dozens of lessons before this pipeline works end-to-end.
