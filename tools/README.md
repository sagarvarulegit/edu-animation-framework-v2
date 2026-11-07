# Framework Tools & Utilities

## Overview
Operational CLI tools, build utilities, schema validators, asset synchronizers, and automated visual QA capture harnesses for the educational animation framework.

## Interface
- `tools/validate.mjs`: Validates all JSON schemas, asset descriptors, lessons, scenes, design tokens, and OKF concept citations.
- `tools/sync-web-assets.mjs`: Synchronizes built GLTF/GLB models to interactive viewer and video composer public directories.
- `tools/capture.py`: Headless visual regression testing and screenshot capture utility using Blender and Puppeteer.
- `tools/audit_all_57_topology.py`: Mesh and topology compliance auditor for scientific 3D models.
- [OKF Tooling](./okf/README.md): Lightweight YAML parser and TypeScript binding compiler for Open Knowledge Format specifications.

## Invariants
- `validate.mjs` must pass with 0 errors before assets, lessons, or scenes can be deployed or rendered.
- Asset and lesson IDs must follow kebab-case identifiers (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- Synced assets must maintain valid file paths and relative references without broken symlinks.

## Side Effects
- `validate.mjs` reads repository metadata, lessons, scenes, schemas, and asset definitions from disk.
- `sync-web-assets.mjs` copies binary asset files (`.glb`, `.png`) to web public directories.
- Visual capture scripts write rendered PNG and MP4 artifacts to disk.

## Verification
- Run: `node tools/validate.mjs`
