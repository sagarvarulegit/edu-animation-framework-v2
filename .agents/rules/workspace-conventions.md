---
trigger: always_on
description: Workspace execution rules, working directories, Blender paths, and architecture invariants
---

# Educational Animation Framework Workspace Conventions

## 1. Working Directory
- The active codebase and Git repository reside in `edu-animation-framework-v2/`.
- Always set `Cwd` to `c:\Sagar\Projects\edu-animation-framework-agent-ready\edu-animation-framework-v2` (or the relative `edu-animation-framework-v2` folder) for shell commands (`git`, `npm`, `node`, `blender`).

## 2. Blender CLI on Windows
- Blender is installed at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`.
- When invoking Blender from PowerShell, use:
  `& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" <args>`
  or ensure path resolution if running npm scripts.

## 3. Adding New Semantic Primitives
Whenever adding a new animation primitive or timeline action, update all 4 layers in lockstep:
1. `schemas/scene.schema.json` (schema constraints)
2. `tools/validate.mjs` (validation rules)
3. `renderers/blender/render_scene.py` (scene timeline dispatcher)
4. `renderers/blender/semantic_primitives.py` (blender visual implementation)

## 4. Asset & Scene Validation
- Always run `node tools/validate.mjs` (or `npm test`) before and after changes to verify all scene plans and assets match schemas.
- Do not track `.blend1` or temporary cache files in git commits.
