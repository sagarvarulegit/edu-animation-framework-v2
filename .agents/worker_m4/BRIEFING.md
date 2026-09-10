# BRIEFING — 2026-09-09T08:52:00Z

## Mission
Implement Milestone 4: Chemistry Apparatus & Molecular Lattices with scientific rigor, crystallographic accuracy, clean manifold topology, physical shaders, and headless build generation.

## 🔒 My Identity
- Archetype: Chemistry Specialist Worker
- Roles: implementer, qa, specialist
- Working directory: /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m4
- Original parent: 40c9ff71-e711-4e13-b090-171086460054
- Milestone: M4

## 🔒 Key Constraints
- Genuine scientific implementations only (no hardcoding, facades, or shortcuts).
- 0 non-manifold edges across all modified meshes.
- Diamond: invert child tetrahedral vectors ($\vec{d}_{child} = -\vec{d}_{parent}$) to close 6-membered chair rings, ~109.47° bond angle.
- Graphite: regular hexagonal lattice (sp2, 3-coordination), ABAB stacking, planar sheets.
- Hydrogen apparatus: continuous smooth bent glass tube via kit.create_smooth_tube(cap_ends=True), thistle funnel, bubbling soap trough.
- Dropper: closed solid manifold lathe profile with inner and outer wall thickness (>= 1.0 mm).
- Atoms: synchronized electron styling and colors from design tokens.
- Glassware shaders: borosilicate dielectric transmission IOR=1.52, roughness=0.015. Multi-zone flame in bunsen-burner.
- Deterministic headless Blender builds (.blend, .glb, preview.png).
- Sync web assets: `node tools/sync-web-assets.mjs --force`.
- Pass `node tools/validate.mjs` (0 errors) and `node tests/e2e/run_all_tests.mjs --milestone M4`.

## Current Parent
- Conversation ID: 40c9ff71-e711-4e13-b090-171086460054
- Updated: 2026-09-09T13:12:00Z

## Task Summary
- **What to build**: Diamond lattice, graphite lattice, hydrogen evolution apparatus, dropper, magnesium atom, oxygen atom, glassware shaders, bunsen flame.
- **Success criteria**: All tests pass, 0 non-manifold edges across all modified assets, valid .blend/.glb/preview.png, clean validator.
- **Interface contracts**: PROJECT.md, AGENTS.md, edu_asset_kit.py, design-tokens.json
- **Code layout**: assets/chemistry/*, visual/design-tokens.json

## Change Tracker
- **Files modified**:
  - `visual/design-tokens.json`: Added `particle_electron` material token (`#38bdf8`, emissionStrength 3.0).
  - `assets/chemistry/diamond-lattice/build_diamond_lattice.py`: Inverted child tetrahedral branching ($\vec{d}_{child} = -\vec{d}_{parent}$), closed 6-membered chair rings, ~109.47° bond angle, 0 non-manifold edges.
  - `assets/chemistry/graphite-lattice/build_graphite_lattice.py`: Planar graphene sheets with regular hexagonal coordinate lattice (sp2 3-coordination, 120° angles), ABAB staggered Bernal stacking (layer_gap/a = 2.367 > 2.0), 0 non-manifold edges.
  - `assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py` & `build_hydrogen_apparatus.py`: Continuous smoothly bent glass delivery tube via `kit.create_smooth_tube(..., cap_ends=True)`, thistle funnel, bubbling soap trough, 0 non-manifold edges.
  - `assets/chemistry/dropper/build_dropper.py`: Revolved closed 2D lathe profile with physical inner/outer wall thickness >= 1.0 mm, 0 non-manifold edges.
  - `assets/chemistry/magnesium-atom/build_magnesium_atom.py` & `assets/chemistry/oxygen-atom/build_oxygen_atom.py`: Harmonized electron styling to `particle_electron` token, 0 non-manifold edges.
  - `assets/chemistry/beaker/build_beaker.py`: Replaced 2D graduation ticks with 3D manifold curved bars, IOR 1.52, roughness 0.015, 0 non-manifold edges.
  - `assets/chemistry/conical-flask/build_flask.py`: Replaced 2D graduation ticks with 3D manifold curved bars, IOR 1.52, roughness 0.015, 0 non-manifold edges.
  - `assets/chemistry/watch-glass/build_watch_glass.py`: Updated borosilicate glass shader (IOR 1.52, roughness 0.015), 0 non-manifold edges.
  - `assets/chemistry/bunsen-burner/build_bunsen_burner.py`: Closed collar and stem lathe profiles (0 non-manifold edges) and added multi-zone blue flame (inner reducing cyan cone #38bdf8 + outer oxidizing blue cone #60a5fa).
  - `assets/chemistry/bunsen-burner/asset.json`: Updated metadata with multi-zone flame and flame materials.
  - `assets/chemistry/magnesium-burning-setup/build_magnesium_burning_setup.py`: Closed collar, stem, and tongs finger loop profiles (0 non-manifold edges).
- **Build status**: PASS (64/64 tests pass, validator clean, web apps built)
- **Pending issues**: None

## Quality Status
- **Build/test result**: 64/64 tests passing (100%), 0 non-manifold edges on all modified chemistry assets
- **Lint status**: Clean, validator passed with 0 errors
- **Tests added/modified**: Verified all Tier 1, 2, 3, 4 tests across the framework

## Loaded Skills
- None required

## Key Decisions Made
- Replaced open 2D lathe profiles with closed loops connecting back to starting vertices to ensure all revolved laboratory apparatus are fully manifold solid meshes.
- Converted graduation tick strips on glassware into 6-sided 3D curved volumetric prisms to eliminate all non-manifold boundary edges.
- Implemented diamond lattice using crystallographic parent-inversion BFS, ensuring chair ring closure and exact tetrahedral angle $\arccos(-1/3)$.
- Implemented graphite lattice with planar 2D hexagonal Bravais coordinates and Bernal ABAB stacking.

## Artifact Index
- `.agents/worker_m4/BRIEFING.md` — Working memory and status
- `.agents/worker_m4/progress.md` — Liveness and step tracking
- `.agents/worker_m4/handoff.md` — Final completion report
