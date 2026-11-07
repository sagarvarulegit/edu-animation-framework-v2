# Blender 3D Renderer & Semantic Primitives

## Overview
Blender automation engine and procedural animation primitives that translate declarative educational scene graph JSON files into cinematic 3D renders using Blender 4.2 LTS and Python.

## Interface
- `appear(target, start, duration, fps)`: Animates object scale entry from zero with ease-out interpolation.
- `disappear(target, start, duration, fps)`: Animates object exit with ease-in scale reduction.
- `camera_move(cam_obj, cam_data, from_shot, to_shot, start, duration, fps)`: Interpolates camera position, tracking orientation, and focal length.
- `show_label(text, location, end, cam, name)`: Generates camera-tracking 3D billboard text with emissive ink.
- `show_equation(text, location, cam, name, size)`: Renders extruded 3D mathematical and chemical equations.
- `show_molecule(model, name, position)`: Builds conceptual ball-and-stick representations of atoms and molecules.
- `move(target, start, duration, offset, fps)`: Performs keyframed 3D translational movement.
- `heat(parent, start, duration, color, strength, fps)`: Modulates material emission shaders for thermal heating effects.
- `burn(parent, start, duration, strength, fps)`: Animates combustion flash, dynamic point lighting, and reaction transformation.
- `render_scene.py`: Command-line script to parse scene graph JSON, assemble the 3D studio, and render designated QA frames or full animations.

## Invariants
- Minimum object scale is constrained to `0.0001` during disappear/appear to prevent singular transformation matrices.
- Camera targets must maintain non-zero directional displacement vectors for valid quaternion tracking.
- Molecular visualizations are explicitly flagged as pedagogical conceptual models, not empirical physical scale claims.

## Side Effects
- Allocates and links mesh, curve, and light objects in the active Blender scene (`bpy.data`).
- Inserts animation f-curves and keyframe points into object animation data.
- Writes rendered image frames (`.png`) and videos to specified filesystem paths.

## Verification
- Run: `blender --background --python renderers/blender/render_scene.py -- --scene lessons/chemistry/magnesium-ribbon/scenes/01-introduction.json --qa-frames 12 --width 480 --height 270 --samples 16`
