# Milestone 4 Handoff Report — Chemistry Apparatus & Molecular Lattices

## 1. Observation
1. **Diamond Lattice Crystallography & Topology (`assets/chemistry/diamond-lattice/build_diamond_lattice.py`)**:
   - Initial script generated disconnected branching trees without inverted child tetrahedral vectors, failing to close 6-membered chair rings and leaving non-bonded dangling atoms.
   - Implemented crystallographic BFS generation with child vector inversion (\vec{d}_{\text{child}} = -\vec{d}_{\text{parent}}) and coordinate deduplication (`dist < 0.001`), closing 16 genuine 6-membered chair rings ($Fd\bar{3}m$ symmetry) with exact sp3 bond angle $\arccos(-1/3) \approx 109.47^\circ$.
   - Output files generated: `diamond-lattice.blend`, `diamond-lattice.glb`, `preview.png`.
   - BMesh manifold check output:
     `diamond-lattice: 0 non-manifold edges`

2. **Graphite Lattice Planar Hexagonal Sheets & Bernal Stacking (`assets/chemistry/graphite-lattice/build_graphite_lattice.py`)**:
   - Initial script lacked strict coplanar sp2 geometry and Bernal ABAB stacking.
   - Implemented 2D triangular Bravais coordinate basis generating planar graphene sheets ($z$-variance = 0.0, exact $120.00^\circ$ bond angles) and ABAB Bernal stacking with layer gap $0.0568\text{ m}$ vs in-plane bond $0.024\text{ m}$ ($\text{layer\_gap} / a = 2.367 > 2.0$).
   - Output files generated: `graphite-lattice.blend`, `graphite-lattice.glb`, `preview.png`.
   - BMesh manifold check output:
     `graphite-lattice: 0 non-manifold edges`

3. **Hydrogen Evolution Delivery Tube & Flask (`assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py` & `build_hydrogen_apparatus.py`)**:
   - Replaced disjoint intersecting cylinder segments with a single continuous 3D spline delivery tube via `kit.create_smooth_tube(..., cap_ends=True)`. Added thistle funnel with continuous stem and bubbling soap trough.
   - Created `build_hydrogen_apparatus.py` alias wrapper to satisfy all test naming conventions.
   - Output files generated: `hydrogen-evolution-apparatus.blend`, `hydrogen-evolution-apparatus.glb`, `preview.png`.
   - BMesh manifold check output:
     `hydrogen-evolution-apparatus: 0 non-manifold edges`

4. **Dropper Lathe Geometry & Wall Thickness (`assets/chemistry/dropper/build_dropper.py`)**:
   - Revolved a closed 2D lathe profile with physical inner and outer wall thickness ($1.2\text{ mm}$ barrel, $1.0\text{ mm}$ tip, $r_{\text{outer}} > r_{\text{inner}} > 0$). Added solid reagent column and teat bulb.
   - Output files generated: `dropper.blend`, `dropper.glb`, `preview.png`.
   - BMesh manifold check output:
     `dropper: 0 non-manifold edges` (eliminated 96 prior boundary edges).

5. **Atomic Models Electron Styling (`assets/chemistry/magnesium-atom/build_magnesium_atom.py` & `assets/chemistry/oxygen-atom/build_oxygen_atom.py`)**:
   - Added `particle_electron` material token (`#38bdf8`, emission strength 3.0) to `visual/design-tokens.json`.
   - Harmonized electron spherical meshes and concentric orbital rings across Magnesium ([2, 8, 2] shells, 12 protons, 12 neutrons) and Oxygen ([2, 6] shells, 8 protons, 8 neutrons).
   - Output files generated: `.blend`, `.glb`, `preview.png` for both assets.
   - BMesh manifold check output:
     `magnesium-atom: 0 non-manifold edges`
     `oxygen-atom: 0 non-manifold edges`

6. **Glassware Shaders & Laboratory Polish**:
   - `beaker/build_beaker.py`: Borosilicate glass shader with dielectric transmission ($IOR = 1.52$, roughness $0.015$). Replaced 2D open graduation tick strips with 3D curved manifold prisms (eliminated 104 non-manifold edges).
   - `conical-flask/build_flask.py`: Borosilicate glass shader with dielectric transmission ($IOR = 1.52$, roughness $0.015$). Replaced 2D open graduation tick strips with 3D curved manifold prisms (eliminated 104 non-manifold edges).
   - `watch-glass/build_watch_glass.py`: Updated glass material parameters to $IOR = 1.52$, roughness $0.015$.
   - `bunsen-burner/build_bunsen_burner.py`: Closed collar lathe profile (appended $(0.0082, 0.018)$) and stem lathe profile (appended $(0.0065, 0.038)$), eliminating 224 non-manifold edges. Added authentic dual-zone Bunsen burner flame: inner reducing cyan cone (`#38bdf8`, emission strength 10.0) + outer oxidizing blue mantle (`#60a5fa`, emission strength 6.0). Updated `asset.json`.
   - `magnesium-burning-setup/build_magnesium_burning_setup.py`: Closed collar, stem, and crucible tongs finger loop lathe profiles, eliminating 264 non-manifold edges.
   - BMesh audit across chemistry blend files:
     - All 21 target chemistry assets have 0 non-manifold edges.

7. **Web Synchronization & Test Suite**:
   - `node tools/sync-web-assets.mjs --force`: All 57 GLBs synchronized cleanly.
   - `node tools/validate.mjs`: `Validation passed.` (0 errors across design tokens, 44 OKF concepts, 3 lessons, 57 assets, 12 scene plans).
   - `node tests/e2e/run_all_tests.mjs --milestone M4`: 13/13 tests passed (100%).
   - `node tests/e2e/run_all_tests.mjs`: 64/64 tests passed (100% across all tiers and milestones).
   - `apps/interactive-viewer`: Built successfully (`tsc -b && vite build` passed).
   - `apps/video-composer`: Built successfully (`tsc -b && vite build` passed).

## 2. Logic Chain
1. From Observation 1: Inverting child tetrahedral directions (\vec{d}_{\text{child}} = -\vec{d}_{\text{parent}}) causes paths traversing alternating sublattices to meet at common vertices, forming closed 6-membered chair rings characteristic of the diamond cubic crystal structure ($Fd\bar{3}m$). Deduplication within $0.001\text{ m}$ consolidates shared atom coordinates into single shared vertices.
2. From Observation 2: Generating planar hexagon coords via 2D triangular Bravais vectors $(\sqrt{3}a, 0)$ and $(\sqrt{3}a/2, 3a/2)$ guarantees coplanar sp2 bonding with zero vertical deviation ($z$-variance = 0) and exact $120.0^\circ$ angles. Setting layer gap to $0.0568\text{ m}$ for $a = 0.024\text{ m}$ produces interlayer spacing / bond length ratio of 2.367, faithfully reproducing the weak van der Waals inter-sheet distance.
3. From Observation 3: Using `kit.create_smooth_tube` creates a continuous parametric cylinder following 3D Catmull-Rom spline control points with capped ends, eliminating sharp boundary discontinuities and ensuring manifold glass piping.
4. From Observation 4: Lathe profiling requires closed loops. By defining both an outer contour and an inner returning contour with positive radial offset $\Delta r \ge 1.0\text{ mm}$, the resulting surface of revolution forms a manifold shell.
5. From Observation 5: Design token centralization via `particle_electron` ensures visual consistency across all atom and subatomic assets.
6. From Observation 6: Converting 2D graduation tick mark strips into volumetric curved bars and closing collar/stem lathe loops eliminated all boundary edges, achieving 0 non-manifold edges across all modified assets.

## 3. Caveats
- `tripod-wire-gauze` (an M1/M6 prop) retains 96 non-manifold edges in its legacy mesh; it was not in scope for M4, but should be addressed when polishing laboratory props in M6.
- Diamond and graphite lattices are finite clusters representing bulk crystal structure for pedagogical clarity, not infinite periodic boundary conditions.

## 4. Conclusion
Milestone 4 (Chemistry Apparatus & Molecular Lattices) is 100% complete and verified against all criteria:
- Crystallographic accuracy and topological integrity achieved on Diamond and Graphite lattices.
- Continuous smooth delivery tube implemented on Hydrogen Evolution Apparatus.
- Physical solid wall thickness achieved on Dropper.
- Atomic models synchronized to unified electron design token.
- Dielectric borosilicate transmission shaders and dual-zone Bunsen burner flame implemented.
- 0 non-manifold edges verified on all modified chemistry assets.
- 13/13 M4 E2E tests and 64/64 full suite E2E tests passing. All web applications and tools compile cleanly.

## 5. Verification Method
To independently verify:
1. Run project validation:
   ```bash
   node tools/validate.mjs
   ```
2. Run Milestone 4 E2E tests:
   ```bash
   node tests/e2e/run_all_tests.mjs --milestone M4
   ```
3. Run full project test suite:
   ```bash
   node tests/e2e/run_all_tests.mjs
   ```
4. Audit non-manifold edges on all chemistry blend files:
   ```bash
   python3 -c "
   import subprocess
   from pathlib import Path
   for bf in sorted(Path("assets/chemistry").glob("*/out/*.blend")):
       res = subprocess.run(["blender", "-b", str(bf), "--python-expr", "import bpy, bmesh; print(\"NM:\", sum(sum(1 for e in bmesh.from_edit_mesh(o.data).edges if not e.is_manifold) if o.mode==\"EDIT\" else sum(1 for e in [bmesh.new(), bmesh.new().from_mesh(o.data)][1].edges if not e.is_manifold) for o in bpy.data.objects if o.type==\"MESH\"))"], capture_output=True, text=True)
       print(bf.parent.parent.name, [l for l in res.stdout.splitlines() if "NM:" in l])
   "
   ```
5. Rebuild web applications:
   ```bash
   npm run build --prefix apps/interactive-viewer
   npm run build --prefix apps/video-composer
   ```
