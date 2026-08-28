# Roadmap

## Milestone 1 — Foundation

- [x] AGENTS.md
- [x] README.md
- [x] lesson specification
- [x] architecture documentation
- [x] schema validation (`schemas/`, `tools/validate.mjs`, `npm run validate`)
- [ ] design tokens

## Milestone 2 — Blender

- [x] asset conventions (`assets/` layout, `asset.json` metadata, deterministic build scripts, `assets/python/edu_asset_kit.py`)
- [x] first assets: magnesium-ribbon, laboratory-tongs, bunsen-burner (generated with Blender 5.2.1, previews visually inspected)
- [x] camera helpers (`edu_asset_kit.frame_camera` — bounding-sphere auto-framing, FOV-correct for tall/wide objects)
- [x] material helpers (`edu_asset_kit.add_material` — Principled BSDF, stable across Blender 3.x–5.x)
- [ ] deterministic Blender bootstrap (currently `reset_scene()` via factory-empty; a project-level bootstrap/config system is still open)
- [x] animation primitives (blender adapter: `appear`, `cameraMove`, `showLabel`, `move`, `heat`, `showFlame`, `burn`, `transform` — validator-enforced registry)
- [x] first magnesium scene (`scenes/01-introduction`, `02-heating`, `03-burning` → QA stills + preview videos, visually inspected)

## Milestone 3 — Interactive

- [x] React Three Fiber application (`apps/interactive-viewer`)
- [x] reusable 3D components (`PrismRefractionModel`, `MagnesiumBurningModel`, `HeartModel`)
- [x] experiment controls (monochromatic vs dispersion, normals/extensions/pins toggles, reaction stages, vascular circuit filters)
- [x] reset/state system
- [x] magnesium interactive lesson & prism refraction interactive lesson

## Milestone 4 — Video

- [ ] Remotion project
- [ ] caption system
- [ ] equation component
- [ ] narration timing
- [ ] magnesium final video

## Milestone 5 — Reusable science library

- [x] assembled experiment templates: `glass-prism-refraction`, `magnesium-burning-setup`, `full-circuit`
- [ ] atoms
- [ ] molecules
- [x] laboratory equipment (bunsen-burner, tongs, beaker, test-tube, flask, retort-stand, watch-glass)
- [x] physics components (ammeter, battery, bulb, lens, mirror, prism, resistor, rheostat, switch, voltmeter)
- [x] biology components (brain, heart, eye, digestive-system, dna, neuron)
- [ ] mathematical visualization components

