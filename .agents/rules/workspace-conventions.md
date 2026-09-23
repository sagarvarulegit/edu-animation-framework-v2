---
trigger: always_on
description: Workspace execution rules, working directories, Blender paths, and architecture invariants
---

# Educational Animation Framework Workspace Conventions

## 1. Working Directory
- The active codebase and Git repository reside in `edu-animation-framework-v2/`.
- Always set `Cwd` to `c:\Sagar\Projects\edu-animation-framework-agent-ready\edu-animation-framework-v2` (or the relative `edu-animation-framework-v2` folder) for shell commands (`git`, `npm`, `node`, `blender`).

## 2. Blender CLI
- On Linux, Blender is available on PATH at `/home/sagarv/.local/bin/blender` (v5.2 LTS). Invoke directly as `blender <args>`.
- On Windows, Blender is installed at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`. When invoking from PowerShell:
  `& "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" <args>`

## 3. Node.js & Vite Compatibility
- System Node.js is `v18.19.1`.
- Do NOT use `vite@^8.x` (which pulls `rolldown` and fails on Node 18 due to `styleText`). Always pin `vite` to `^6.2.0` and `@vitejs/plugin-react` to `^4.3.4` in `apps/interactive-viewer` and `apps/video-composer`.
- Build commands:
  - Interactive Viewer: `npm run build --prefix apps/interactive-viewer`
  - Video Composer: `npm run build --prefix apps/video-composer`

## 4. Open Knowledge Format (OKF v0.2) Workflow
- Knowledge documents reside in `knowledge/*.md`.
- Whenever adding or editing OKF concepts, always run `node tools/okf/compile-okf.mjs` (or `npm run build:okf`) to regenerate runtime TypeScript bindings in both web applications.

## 5. Adding New Semantic Primitives
Whenever adding a new animation primitive or timeline action, update all 4 layers in lockstep:
1. `schemas/scene.schema.json` (schema constraints)
2. `tools/validate.mjs` (validation rules)
3. `renderers/blender/render_scene.py` (scene timeline dispatcher)
4. `renderers/blender/semantic_primitives.py` (blender visual implementation)

## 6. Asset & Scene Validation
- Always run `node tools/validate.mjs` (or `npm test`) before and after changes to verify all scene plans, assets, lessons, OKF concepts, and design tokens match schemas.
- Do not track `.blend1` or temporary cache files in git commits.

## 7. Git Commit & Push Discipline
- **Frequent Commits & Pushes**: Whenever solid progress or a meaningful subtask/milestone is completed, validate and immediately `git commit` and `git push` to `origin`.
- **Prevent Multi-Machine Desync**: The developer works across multiple locations (office machine and home machine). Never leave completed or validated work uncommitted or unpushed at the end of a session or task milestone.
- **Standard Protocol**:
  1. Validate: `node tools/validate.mjs` (or relevant test/build commands).
  2. Commit: `git add .` and `git commit -m "..."` with clear, descriptive commit messages.
  3. Push: `git push origin <branch>` immediately so remote is always the source of truth.

