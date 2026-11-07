# JSON Schema Specifications

## Overview
Declarative JSON Schema contracts defining the structural integrity, data formats, and validation rules for assets, design tokens, lessons, scenes, and Open Knowledge Format (OKF) educational concepts.

## Interface
- `asset.schema.json`: Contract for 3D asset metadata, dimensions, bounding boxes, materials, snap sockets, and provenance.
- `design-tokens.schema.json`: Contract for visual tokens across colors, typography, PBR materials, cameras, lights, and annotations.
- `lesson.schema.json`: Contract for high-level lesson specifications, CBSE/NCERT curriculum mappings, and scene order.
- `okf.schema.json`: Contract for Open Knowledge Format (OKF v0.2) frontmatter, citations, misconceptions, and concept relationships.
- `scene.schema.json`: Contract for declarative 3D scene graphs, object hierarchies, camera shots, and timeline animation primitives.

## Invariants
- All schemas must adhere strictly to valid JSON Schema specifications.
- Properties marked as required must never be omitted by authoring tools or generators.
- Backward compatibility must be preserved across minor schema versions.

## Side Effects
- None. Schemas are pure structural definitions consumed read-only by validators and code generators.

## Verification
- Run: `node tools/validate.mjs`
