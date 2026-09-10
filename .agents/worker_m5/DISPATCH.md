# Dispatch Log — Worker M5 (Physics Specialist Worker)

## Mission: Milestone 5 — Physics Apparatus & Demonstration Models
- Workspace root: `/home/sagarv/Projects/edu-animation-framework-v2`
- Your working directory: `/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m5`

## Mandatory Reference Documents
Before taking any action, read and comply with:
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md` (authoritative user requirements)
- `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md` (non-negotiable rules: scientific correctness, procedural architecture, headless determinism)
- `/home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md` (global architecture, milestones, interface contracts)
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/rules/workspace-conventions.md` (Node 18 compatibility, Blender path, validation rules)
- `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/survey_chem_phys.md` (survey notes on physics assets)

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A Forensic Auditor will independently verify your work using automated static analysis, geometric inspection, and runtime testing. Integrity violations WILL be detected and your work WILL be rejected immediately.

---

## Detailed Task Breakdown

### 1. Full Circuit Physics Consistency (Feature 24)
- **Target File**: `assets/physics/full-circuit/build_circuit.py`
- **Pedagogical Requirement**: Closed electric circuit demonstration board (NCERT Class 10 Ch 12, Fig 12.1).
- **Physical Law**: $I = V/R$. In a closed circuit, current flows and the incandescent bulb filament glows. In an open circuit (switch open), $I = 0$ and the bulb filament does NOT glow.
- **Implementation**:
  - Ensure the knife switch blade is closed into the receiving copper U-jaw (`rotation_euler = (0, 0, 0)` or matching engagement angle), completing the circuit.
  - Wire bulb emission to circuit continuity: when the circuit is closed, the bulb filament has warm incandescent emission (strength 4.0, color `#ffaa44`); if switch is open, emission must be 0.0.
  - Ensure the circuit forms a complete closed-loop topological chain: `battery -> switch -> bulb -> resistor -> battery` with smooth interconnecting wire tubes.
  - Geometry must be fully manifold: 0 non-manifold edges across all components.

### 2. DC Electric Motor Split-Ring Commutator (Feature 25)
- **Target File**: `assets/physics/electric-motor/build_electric_motor.py`
- **Pedagogical Requirement**: DC Motor working demonstration model (NCERT Class 10 Ch 13, Section 13.4, Fig 13.15).
- **Implementation**:
  - Replace any overlapping solid cylinders with an authentic semicircular split-ring commutator (two half-cylindrical copper shells P and Q separated by an insulating gap of $15^\circ - 30^\circ$).
  - Add two stationary carbon contact brushes (X and Y) pressed tangentially against the split-rings.
  - Rectangular armature coil (ABCD) must be cleanly routed: end segments must clear the central rotating axle without unnatural mesh intersections (e.g. arched or stepped offsets).
  - Curved permanent magnet poles: North pole (red) and South pole (blue) with concave cylindrical faces facing the armature.
  - Geometry must be fully manifold: strictly 0 non-manifold edges across all objects.

### 3. Glass Slab Emergent Rays & Refraction Pins (Feature 26)
- **Target File**: `assets/physics/glass-slab/build_glass_slab.py`
- **Pedagogical Requirement**: Rectangular glass slab refraction demonstration (NCERT Class 10 Ch 10, Fig 10.10).
- **Implementation**:
  - Borosilicate/crown optical glass slab ($100 \times 65 \times 20\text{ mm}$) with dielectric transmission ($IOR = 1.52$, roughness 0.015).
  - Model the complete optical ray path with exact Snell's law refraction:
    - Incident ray in air at angle $i \approx 30^\circ - 45^\circ$.
    - Surface normal at first interface (air to glass).
    - Refracted ray inside glass at angle $r = \arcsin(\sin(i) / n)$, where $n = 1.52$.
    - Surface normal at second interface (glass to air).
    - Emergent ray in air at angle $e = i$, parallel to the incident ray direction.
    - Lateral displacement: $d = \frac{t \cdot \sin(i - r)}{\cos(r)} > 0$.
  - Refraction pins (CBSE Class 10 laboratory practical):
    - Pins P1 and P2 fixed vertically along the incident ray.
    - Pins P3 and P4 fixed vertically along the emergent ray (collinear with the apparent emergent path).
  - Ray representations: smooth 3D tubes or luminescent ray lines showing the complete path.
  - Geometry must be fully manifold: strictly 0 non-manifold edges.

### 4. Optics & Physics Materials Polish (Feature 27)
- Review and refine physical shaders and geometry across other physics assets as needed:
  - `assets/physics/glass-prism/build_prism.py` and `assets/physics/glass-prism-refraction/build_glass_prism_refraction.py`: Ensure crown glass transmission ($IOR = 1.52$).
  - `assets/physics/convex-lens/build_convex_lens.py` and `assets/physics/concave-lens/build_concave_lens.py`: Accurate dielectric optical glass ($IOR = 1.52$).
  - `assets/physics/bar-magnet/build_bar_magnet.py`: Ensure directional indicators/arrows on external magnetic field lines pointing North to South (NCERT Fig 13.3 & 13.4).
  - `assets/physics/solenoid/build_solenoid.py`: Uniform axial internal field lines and curved return loops with directional indicators pointing from North to South.
  - `assets/physics/ammeter/build_ammeter.py`, `assets/physics/voltmeter/build_voltmeter.py`, `assets/physics/galvanometer/build_galvanometer.py`: Verify realistic dials, scale arcs, and needles.
- Maintain strictly 0 non-manifold edges across all modified physics assets!

---

## Execution & Verification Workflow

1. **Procedural Updates**:
   - Update the procedural python build scripts under `assets/physics/`.
   - Ensure all object creation creates closed, clean, manifold geometry without loose edges or open boundaries.
2. **Headless Blender Execution**:
   - For every modified asset, run:
     ```bash
     blender -b -P assets/physics/<asset-id>/build_<name>.py
     ```
   - Must complete with exit code 0 and generate `out/<asset-id>.blend`, `out/<asset-id>.glb`, and `out/preview.png`.
3. **Synchronize Web Assets**:
   - Run:
     ```bash
     node tools/sync-web-assets.mjs --force
     ```
   - Verify that production GLBs in `assets/physics/*/out/*.glb` match byte-for-byte with `apps/interactive-viewer/public/assets/*.glb`.
4. **Validation**:
   - Run:
     ```bash
     node tools/validate.mjs
     ```
   - Must pass with 0 errors across all 57 assets and 44 OKF concepts.
5. **E2E Test Suite**:
   - Run:
     ```bash
     node tests/e2e/run_all_tests.mjs --milestone M5
     ```
   - Must pass 100% of Milestone 5 tests (Tier 1, Tier 2, Tier 3).
   - Run:
     ```bash
     node tests/e2e/run_all_tests.mjs
     ```
   - Must pass 100% of tests.
6. **Web Apps Build**:
   - Verify `npm run build --prefix apps/interactive-viewer` succeeds with 0 errors.
7. **Handoff Documentation**:
   - Update your `progress.md` with every action taken.
   - Write your final `handoff.md` in `.agents/worker_m5/handoff.md` detailing:
     - Changes made per asset.
     - Verification command outputs (Blender builds, validate.mjs, e2e tests, sync status).
     - Topology audit (non-manifold edge count = 0 across all modified assets).
     - Exact SHA-256 hashes of generated GLBs.
8. Send a message to the orchestrator upon completion.

## 2026-09-09T13:37:19Z
You are Worker M5 (Physics Specialist Worker).
Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m5/DISPATCH.md.
Also read /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md, /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md, /home/sagarv/Projects/edu-animation-framework-v2/PROJECT.md, and /home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/survey_chem_phys.md.

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your objective:
Implement Milestone 5:
1. Full Circuit (build_circuit.py): Wire knife switch blade into receiving jaw completing the circuit, bulb emission is wired to circuit state (I = V/R, glowing filament when closed, 0.0 when open), complete closed loop topological chain (battery -> switch -> bulb -> resistor -> battery), 0 non-manifold edges.
2. Electric Motor (build_electric_motor.py): Authentic semicircular split-ring commutator (two half-rings with 15-30 deg insulating gap), stationary carbon contact brushes X and Y, rectangular armature coil ABCD clearing rotating axle, curved concave magnet poles (N red, S blue), 0 non-manifold edges.
3. Glass Slab (build_glass_slab.py): Borosilicate/crown glass block (IOR = 1.52), complete optical ray paths with exact Snell's law refraction (i = e, lateral shift d > 0, surface normals, refracted ray inside block), refraction pins P1, P2 (incident) and P3, P4 (emergent), 0 non-manifold edges.
4. Optics & Physics Materials: Crown glass IOR 1.52 across lenses and prisms, realistic meter dials and needles, directional arrows on magnetic field lines (bar-magnet, solenoid) North to South, 0 non-manifold edges.
5. Run headless Blender builds for all modified assets generating .blend, .glb, preview.png.
6. Run `node tools/sync-web-assets.mjs --force`.
7. Verify: `node tools/validate.mjs` (0 errors) and `node tests/e2e/run_all_tests.mjs --milestone M5` (all pass) and `node tests/e2e/run_all_tests.mjs` (all pass).
8. Write progress.md and handoff.md in your directory (/home/sagarv/Projects/edu-animation-framework-v2/.agents/worker_m5).
9. Send a message to the caller when complete.
