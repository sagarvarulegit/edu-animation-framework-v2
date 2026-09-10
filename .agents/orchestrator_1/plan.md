# Orchestrator Master Plan

## Project Overview
Refine, audit, and procedurally enhance 3D educational models in `edu-animation-framework-v2` for CBSE/NCERT Class 9–12 scientific and anatomical accuracy, procedural mesh quality, realistic pedagogical shaders, and automated headless multi-format pipeline generation (.blend, .glb, preview.png), verified against `tools/validate.mjs` with 0 errors.

## Execution Phases

### Phase 0: Survey & Full Scope Mapping (Current)
- Spawn 3 Explorers in parallel:
  - Explorer 1: Biology anatomical models (Heart, Brain, Eye, Nephron, Respiratory, Digestive, etc.)
  - Explorer 2: Chemistry & Physics models and apparatus
  - Explorer 3: Validation, build pipelines, headless Blender scripts, and export infrastructure
- Synthesize findings into `PROJECT.md` (Architecture, Feature Inventory, Milestones, Interface Contracts, Code Layout).

### Phase 1: Test Infrastructure & Dual Track Setup
- Spawn E2E Testing Orchestrator to establish test harness, headless blender validation runner, and test matrix across Tiers 1-4.
- Create `TEST_INFRA.md`.

### Phase 2: Milestone Decomposition & Implementation
- Milestone 1: Biology Core Anatomical Systems Part A (Heart, Eye, Brain)
- Milestone 2: Biology Core Anatomical Systems Part B (Nephron, Respiratory, Digestive, Cell/others)
- Milestone 3: Chemistry Apparatus & Molecular Assets
- Milestone 4: Physics Apparatus & Demonstration Models
- Milestone 5: Pipeline & Asset Catalog Integration, Schema Validation, Multi-format Verification

### Phase 3: E2E Verification & Adversarial Coverage Hardening (Tier 5)
- Verify 100% pass on all E2E tests and `node tools/validate.mjs`.
- Adversarial review via Challengers & Forensic Auditor.
- Final victory audit preparation and handoff to Sentinel.
