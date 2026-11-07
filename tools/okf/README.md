# OKF Compiler & Parser Tooling

## Overview
Lightweight tooling for the Open Knowledge Format (OKF v0.2). Parses YAML frontmatter and Markdown lesson/concept specifications in `knowledge/` and compiles them into a unified knowledge manifest and type-safe TypeScript bindings for the interactive viewer and video composer applications.

## Interface
- `parseYaml(yamlStr: string): object`: Parses lightweight YAML key-value pairs, nested dictionaries, and lists.
- `parseOkfDocument(content: string): { frontmatter: object, body: string }`: Extracts YAML frontmatter and Markdown body from OKF documents.
- `compileOkf(): object`: Compiles all OKF documents into `knowledge/manifest.json` and generates `okfKnowledge.ts` for web and video applications.

## Invariants
- Frontmatter must be delimited by `---` fences.
- OKF concepts must declare an `id` or fallback to file basename.
- Compiled manifest must adhere to the OKF v0.2 specification.

## Side Effects
- Reads all `.md` files under `knowledge/`.
- Overwrites `knowledge/manifest.json`.
- Writes generated TypeScript files to `apps/interactive-viewer/src/data/generated/okfKnowledge.ts` and `apps/video-composer/src/data/generated/okfKnowledge.ts`.

## Verification
- Run: `node tools/okf/compile-okf.mjs`
