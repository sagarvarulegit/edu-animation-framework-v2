# Architecture

## Core pipeline

```text
OKF Knowledge Base (knowledge/)
     ↓
Lesson Content & Pedagogical Flow
     ↓
Lesson Specification (lessons/)
     ↓
Semantic Scene Graph
     ↓
Assets + Animation Primitives
     ↓
Renderer Adapter
     ↓
 ┌──────────┬──────────────┬─────────────┐
 ↓          ↓              ↓
Blender   Three.js       Remotion
 3D       Interactive     Video
```

## Separation of concerns

### Knowledge layer (OKF v0.2)

Answers:

> What is the verified scientific fact, chemical equation, apparatus specification, and curriculum standard?

### Lesson layer

Answers:

> What should the student learn?

### Scene layer

Answers:

> What should be visible and what should happen?

### Primitive layer

Answers:

> What does "heat", "burn", "combine", etc. mean?

### Renderer layer

Answers:

> How do we visually implement it?

This separation is one of the most important architectural rules in the repository.

## Example

Lesson:

```text
Heat magnesium ribbon.
```

Semantic scene:

```json
{
  "action": "heat",
  "target": "magnesium-ribbon",
  "duration": 3
}
```

Blender:

```text
material temperature animation
+ flame
+ light intensity
+ camera
```

Three.js:

```text
material transition
+ flame component
+ light component
+ UI control
```

Remotion:

```text
rendered sequence
+ caption
+ narration
```

The lesson remains the same.

## Current repository layout (implemented)

```text
schemas/            JSON Schema contracts for lessons and assets
tools/validate.mjs  zero-dependency validator (npm run validate)
assets/
  python/           shared deterministic Blender helpers (edu_asset_kit.py)
  chemistry/<id>/   one directory per asset:
    asset.json      metadata conforming to schemas/asset.schema.json
    build_*.py      headless Blender generator (deterministic)
    out/            generated .blend / .glb / preview.png
lessons/
  <subject>/<id>/   lesson.json + script.md
```

Asset build command (requires Blender on PATH):

```bash
blender --background --python assets/chemistry/magnesium-ribbon/build_magnesium_ribbon.py -- --out out
```

Environment note (2026-08-26): no system Blender was installed; assets were generated and
visually inspected with a portable **Blender 5.2.1 LTS** extracted to
`C:\Users\sunwa\AppData\Local\Temp\opencode\blender-portable\blender-5.2.1-windows-x64\blender.exe`.
This temp location is ephemeral — a future agent should install Blender permanently or update this note.

Conventions enforced by the validator: kebab-case asset ids matching directory names,
every scene-referenced asset must exist in `assets/`, provenance and scale convention are mandatory.

## Scene rendering pipeline (implemented for Blender)

```text
lessons/<subject>/<lesson>/scenes/NN-<name>.json   semantic scene plan
        ↓  (instances + named camera shots + timeline of primitives)
renderers/blender/render_scene.py                  adapter: appends asset .blend files,
                                                   applies semantic primitives, renders
renderers/blender/semantic_primitives.py           appear / cameraMove / showLabel
        ↓
scenes/out/  qa_frame_*.png + NN-<name>.mp4 (via PNG sequence + ffmpeg)
```

Scene plan conventions: meters at real-world laboratory scale, origin at the bench
surface beneath the burner center, +Y toward viewer, +Z up. Timeline times are seconds.
Supported primitives are enforced by the validator (`SUPPORTED_PRIMITIVES` in
`tools/validate.mjs`); extend that list when a renderer implements a new one.

Blender 5.x notes (bugs already solved here, do not regress):
- appended library objects are NOT auto-linked to the scene collection — link MESH
  objects explicitly and discard appended preview cameras/lights;
- `Action.fcurves` is gone (slotted actions) — use the layer/strip channelbag fallback
  in `semantic_primitives._fcurves_for`;
- image settings no longer support FFMPEG output — render PNG sequences and encode
  with external ffmpeg.

### Render quality notes

- Emission "dazzle" on burning magnesium is conveyed so far by Principled emission
  strength + a white point light. A compositor bloom pass (`CompositorNodeGlare`
  FOG_GLOW) is the planned follow-up to strengthen the "dazzling white flame"
  perception; deferred because it is a visual choice that needs direct inspection.
- Videos are encoded at low preview resolution (320-640 px, 16-24 samples) for QA speed.
  Production renders should raise `--width --height --samples` and add bloom.
