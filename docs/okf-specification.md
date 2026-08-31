# Open Knowledge Format (OKF v0.2) Specification & Architecture

## Overview

The **Open Knowledge Format (OKF)** is a vendor-neutral, Markdown-first open specification (formalized by Google Cloud and the Knowledge Catalog community) designed to represent structured knowledge for both humans and AI coding agents.

Within the **Educational Animation Framework**, OKF acts as the foundational knowledge layer that decouples scientific concepts, pedagogical rules, chemical equations, apparatus profiles, and curriculum standards from rendering technology (Blender, Three.js, Remotion).

```text
       ┌────────────────────────────────────────────────────────┐
       │             OKF Knowledge Base (knowledge/)            │
       │   • Concepts • Apparatus • Reactions • Curriculum      │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             Lesson Specifications (lessons/)           │
       │   • Pedagogical Flow • Scene Definitions • Narration   │
       └───────────────────────────┬────────────────────────────┘
                                   │
                                   ▼
       ┌────────────────────────────────────────────────────────┐
       │             Semantic Primitives & 3D Assets            │
       │   • appear, heat, burn • 3D Assets (assets/)           │
       └───────────────────────────┬────────────────────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 ▼                 ▼                 ▼
             Blender            Three.js          Remotion
           Cinematic 3D       Interactive 3D    Composed Video
```

---

## 1. Directory Layout

OKF concept files reside under `knowledge/` categorized by scientific domain:

```text
knowledge/
├── manifest.json                  # Compiled knowledge graph & concept index
├── chemistry/                     # Chemistry concepts, reactions, and reagents
│   ├── magnesium-ribbon-combustion.md
│   ├── magnesium-metal.md
│   ├── magnesium-oxide.md
│   ├── bunsen-burner.md
│   ├── crucible-tongs.md
│   └── combination-reaction.md
├── physics/                       # Optics, electricity, and mechanics
│   ├── glass-prism-refraction.md
│   ├── optical-prism.md
│   ├── angle-of-deviation.md
│   ├── optical-dispersion.md
│   ├── snells-law.md
│   ├── convex-lens.md
│   └── electric-circuit.md
├── biology/                       # Anatomy, physiology, and life processes
│   ├── human-heart-circulation.md
│   ├── cardiac-chambers.md
│   ├── aorta-systemic-trunk.md
│   ├── human-eye-optics.md
│   └── digestive-system.md
└── curriculum/                    # Curriculum standards & chapter specifications
    ├── cbse-class-10-science.md
    ├── ncert-chemistry-ch01.md
    ├── ncert-physics-ch11.md
    └── ncert-biology-ch06.md
```

---

## 2. File Format & Frontmatter Specification

Every OKF document is a standard Markdown file (`.md`) beginning with a YAML frontmatter block.

### Required Fields (OKF v0.2)

- `id`: Stable kebab-case identifier matching the file basename (e.g. `magnesium-ribbon-combustion`).
- `type`: Concept archetype enum (`concept`, `experiment`, `apparatus`, `reaction`, `phenomenon`, `anatomy`, `law`, `curriculum`).
- `title`: Human-readable title.
- `description`: Single-sentence summary for agent and UI previews.
- `status`: Lifecycle status (`active`, `draft`, `reviewed`, `deprecated`).
- `sources`: Provenance citations array with name, chapter, activity, section, or URL.
- `verified`: Trust tier enum (`human-reviewed`, `machine-confirmed`, `unverified`).

### Educational Domain Fields

- `cbse_mapping`: Mapping to Class (1–12), Subject, Chapter, and NCERT Activity.
- `equations`: LaTeX representations with physical/chemical meaning.
- `misconceptions`: Common student errors and explicit scientific corrections.
- `safety`: Experimental safety precautions (e.g. eye protection, heat handling).
- `related_assets`: Associated 3D asset IDs in `assets/`.
- `related_lessons`: Associated lesson IDs in `lessons/`.
- `related_concepts`: Associated OKF concept IDs forming the knowledge graph.

### Example OKF Document

```markdown
---
id: magnesium-ribbon-combustion
type: experiment
title: Combustion of Magnesium Ribbon in Air
description: Exothermic combination reaction between magnesium metal and atmospheric oxygen yielding magnesium oxide.
status: active
verified: human-reviewed
timestamp: "2026-08-28T00:00:00Z"
resource: assets/chemistry/magnesium-burning-setup
tags: [chemistry, cbse-class-10, combination-reaction, combustion, oxidation]
sources:
  - name: NCERT Class 10 Science
    chapter: "Chapter 1: Chemical Reactions and Equations"
    activity: "Activity 1.1"
cbse_mapping:
  class: 10
  subject: chemistry
  chapter: "Chemical Reactions and Equations"
  ncert_activity: "Activity 1.1"
  key_takeaways:
    - Magnesium burns with a dazzling white flame.
    - Forms a white ash of basic magnesium oxide (MgO).
    - Requires sandpaper cleaning beforehand to remove basic magnesium carbonate protective layer.
equations:
  - latex: "2\\text{Mg}(s) + \\text{O}_2(g) \\xrightarrow{\\Delta} 2\\text{MgO}(s) + \\text{Heat} + \\text{Light}"
    meaning: "2 moles of solid magnesium react with 1 mole of oxygen gas under heat to form 2 moles of solid magnesium oxide."
    type: chemical
misconceptions:
  - claim: "The white powder produced is magnesium ash."
    correction: "The product is a distinct chemical compound, magnesium oxide (MgO), not residual ash."
safety:
  - "Wear UV-protective safety goggles to avoid retinal dazzle from intense white light."
  - "Hold the ribbon with crucible tongs, never with bare fingers."
related_assets:
  - magnesium-ribbon
  - bunsen-burner
  - laboratory-tongs
  - watch-glass
  - magnesium-oxide
  - magnesium-burning-setup
related_lessons:
  - chemistry.magnesium-ribbon
related_concepts:
  - magnesium-metal
  - magnesium-oxide
  - combination-reaction
---

# Combustion of Magnesium Ribbon in Air

## Scientific Principle
When magnesium metal is heated in the presence of air...
```

---

## 3. Tooling & Pipeline

1. **Compilation (`npm run build:okf`)**:
   - Parses all `knowledge/**/*.md` files.
   - Generates `knowledge/manifest.json` (graph vertices + edges).
   - Generates `apps/interactive-viewer/src/data/generated/okfKnowledge.ts`.
2. **Validation (`npm test` / `npm run validate`)**:
   - Enforces frontmatter adherence to `schemas/okf.schema.json`.
   - Validates referential integrity: every `related_assets` ID must exist in `assets/`, every `related_lessons` ID in `lessons/`, and every `related_concepts` ID in `knowledge/`.

---

## 4. Trust Tiers & Provenance

OKF v0.2 establishes 3 trust tiers:
- 🛡️ **`human-reviewed`**: Verified by subject matter expert against authoritative textbooks (e.g. NCERT).
- ⚙️ **`machine-confirmed`**: Verified by automated theorem provers, balanced equation solvers, or optical trace checkers.
- ⚠️ **`unverified`**: Draft or AI-proposed concept awaiting pedagogical validation.
