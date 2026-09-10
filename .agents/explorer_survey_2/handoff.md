# Handoff Report — Chemistry & Physics 3D Asset Audit

**Sender:** Chemistry & Physics Asset Auditor (`explorer_survey_2`)  
**Recipient:** Orchestrator / Lead Parent Agent (`40c9ff71-e711-4e13-b090-171086460054`)  
**Date:** 2026-09-09  
**Handoff Type:** Hard Handoff (Investigation & Audit Task Complete)  
**Primary Artifact:** `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/survey_chem_phys.md`  

---

## 1. Observation

Direct code observations from the inspected codebase:

1. **Graphite Lattice Honeycomb Failure:**
   - File: `assets/chemistry/graphite-lattice/build_graphite_lattice.py:33-49`
   - Lines 33: `centers = [(-bond_r * 1.5, 0.0), (0.0, 0.0), (bond_r * 1.5, 0.0)]`
   - Lines 48-49: `if abs(dist - bond_r) < 0.003: bonds.append((i, j))`
   - Observed output of python test:
     `v3: (-0.025, -0.0217), degree=2`
     `v6: (-0.0125, -0.0217), degree=2`
     `Bond (4, 6): (-0.025, 0.0) -> (-0.0125, -0.0217) (dist=0.0250)`
     `Bond (7, 10): (-0.0125, 0.0) -> (0.0125, 0.0) (dist=0.0250)`
   - Hexagons do not share vertices; bonds criss-cross across disjoint rings, creating non-planar polygons with invalid coordination numbers (mostly 2, two of 3).

2. **Diamond Lattice Second-Shell Branching:**
   - File: `assets/chemistry/diamond-lattice/build_diamond_lattice.py:44-54`
   - Lines 48-54:
     ```python
     for t in t_dirs:
         if (t + dir1).length > 0.01:
             p2 = parent_pos + t
             idx2 = len(nodes)
             nodes.append(p2)
             edges.append((idx1, idx2))
     ```
   - Observed: Tetrahedral vectors are identical for parent and child rather than inverted ($\vec{d}_{\text{child}} = -\vec{d}_{\text{parent}}$), preventing the formation of closed 6-membered chair rings.

3. **Full Circuit Open Switch with Glowing Light Bulb:**
   - File: `assets/physics/full-circuit/build_circuit.py:63-66` and `20-22, 95-97`
   - Knife switch blade:
     `sw_blade = kit.primitive_object(..., rotation_euler=(0.0, -0.35, 0.0))` (open at $20^\circ$)
   - Light bulb filament:
     `glow_mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 4.0`
     `bulb_fil = kit.primitive_object(..., glow_mat)`
   - Observed: Bulb filament actively emits bright light while switch is physically open.

4. **Hydrogen Evolution Delivery Tube:**
   - File: `assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py:82-90`
   - Lines 82-90:
     ```python
     d_horiz = kit.primitive_object(f'{ASSET_ID}-deliv-horiz', 'cylinder', glass_mat, size=(0.004, 0.004, 0.12), location=(0.002, 0.0, 0.12), rotation_euler=(0.0, math.pi / 2, 0.0))
     d_vert  = kit.primitive_object(f'{ASSET_ID}-deliv-vert',  'cylinder', glass_mat, size=(0.004, 0.004, 0.10), location=(0.06,  0.0, 0.07))
     ```
   - Observed: Two disjoint cylinders intersecting at $90^\circ$ with protruding flat ends, rather than a single smoothly bent glass tube.

5. **Dropper Zero-Thickness Profile:**
   - File: `assets/chemistry/dropper/build_dropper.py:17`
   - Line 17: `pipette = kit.lathe_object(f"{ASSET_ID}-glass-pipette", [(0.0032, 0.0), (0.0040, 0.008), (0.0040, 0.125), (0.0010, 0.165), (0.00045, 0.181)], segments=48, material=glass, ...)`
   - Observed: Profile contains 5 points along outer wall only; no return path, generating an open surface with zero wall thickness.

6. **Electron Color Inconsistency:**
   - `assets/chemistry/magnesium-atom/build_magnesium_atom.py:36`: `(0.15, 0.78, 1.0)` (Cyan)
   - `assets/chemistry/oxygen-atom/build_oxygen_atom.py:36`: `(0.98, 0.44, 0.52)` (Pink/Red)
   - Both represent the fundamental electron in atomic models of the same lesson series.

7. **DC Motor Split-Ring Commutator:**
   - File: `assets/physics/electric-motor/build_electric_motor.py:94-99`
   - Commutator halves P and Q are created as two full solid cylinders shifted by $0.001\text{ m}$ (`size=(0.013, 0.013, 0.010)`), rather than semicircular split rings.

8. **Glass Slab Missing Emergent Pins & Rays:**
   - File: `assets/physics/glass-slab/build_glass_slab.py:37`
   - Only pins P1 and P2 exist in the loop (`[('p1', ...), ('p2', ...)]`); P3, P4, and ray lines are omitted.

9. **Framework Validation:**
   - Executed `node tools/validate.mjs`:
     - 44 OKF concepts validated
     - 57 assets checked (13 biology, 22 chemistry, 22 physics)
     - 0 schema errors; all declared files exist.

---

## 2. Logic Chain

1. **From Observation 1 to Conclusion on Graphite:**
   - In 2D hexagonal lattices, regular hexagons sharing vertical edges must have centers separated by $\sqrt{3}a \approx 1.732a$ (if rotated) or $1.5a$ horizontally accompanied by $\pm \frac{\sqrt{3}}{2}a$ vertically.
   - Setting centers with $\Delta x = 1.5a$ and $\Delta y = 0$ places vertices at $0.0125\text{ m}$ apart (half the bond length $a = 0.025\text{ m}$).
   - Applying a distance threshold of $0.025 \pm 0.003\text{ m}$ matches across disjoint non-neighboring rings, creating an invalid criss-cross web of chords where carbon atoms have valency 2 instead of 3.
   - Therefore, `build_graphite_lattice.py` fails to represent graphite's planar hexagonal structure.

2. **From Observation 2 to Conclusion on Diamond:**
   - The diamond structure consists of two interpenetrating FCC lattices shifted by $(1/4, 1/4, 1/4)$. Every atom has 4 neighbors forming an adamantane chair unit.
   - Inverting the tetrahedral vectors for child bonds is mathematically necessary for the bonds to stagger into chair hexagons.
   - Retaining the same vector set results in parallel tetrahedra that form an artificial branching tree rather than a diamond crystal.

3. **From Observation 3 to Conclusion on Circuit Logic:**
   - An electric switch serves as a mechanical break in an electrical loop ($I = V/R$).
   - When the knife switch blade is angled open, the resistance of the air gap is infinite and current is zero ($I = 0$).
   - A light bulb emitting light with emission strength 4.0 in this state contradicts basic physics and CBSE Class 10 Chapter 12 principles.

4. **From Observation 5 to Conclusion on Glassware Shaders:**
   - Physically based glass rendering requires refraction across two interfaces (air-to-glass and glass-to-air) governed by Snell's law:
     $$n_1 \sin(\theta_1) = n_2 \sin(\theta_2)$$
   - A zero-thickness mesh has only one surface, causing the ray tracer to assume the entire interior is solid glass, leading to black refraction borders and inverted shading normals.

---

## 3. Caveats

1. **Interactive Three.js Runtime Testing:** While all 44 `.glb` files exist and conform to the glTF 2.0 binary standard, client-side WebGL rendering was evaluated from procedural build scripts and preview renders. Real-time shader performance and multi-layer transparency sorting in Three.js will need visual spot-checking when integrated into interactive lessons.
2. **Animation Rigs:** Knife switches, ammeter needles, rheostat sliders, and laboratory tongs are currently modeled in single static poses without Blender armatures or animation shape keys. Interactive/animated lessons will require adding rotation pivots or shape keys.
3. **No Code Modification:** In strict adherence to the Explorer role (read-only investigation), no source files, assets, or scripts were modified. All proposals are documented in `survey_chem_phys.md`.

---

## 4. Conclusion

1. The Chemistry and Physics asset libraries possess a solid procedural base (44 assets, fully automated headless Blender build pipelines, unified design token architecture).
2. However, **7 critical defects** directly undermine scientific and pedagogical validity:
   - Severe crystallographic errors in `diamond-lattice` and `graphite-lattice`.
   - Scientific contradiction in `full-circuit` (open switch with glowing bulb).
   - Topological flaws in `dropper` (zero-thickness mesh) and `hydrogen-evolution-apparatus` (broken delivery tube).
   - Inconsistencies in subatomic particle styling (`magnesium-atom` vs `oxygen-atom`).
   - Anti-pattern of bundling reactive solutions permanently into reusable laboratory glassware.
3. A prioritized remediation plan (P0, P1, P2) and architectural shader specifications for realistic glass (volume absorption), multi-zone flames, liquids, and specialized metals have been formulated in `survey_chem_phys.md`.

---

## 5. Verification Method

Independent verification can be executed with the following steps:

1. **Schema and Asset Validation:**
   ```bash
   node tools/validate.mjs
   ```
   *Expected Result:* 0 errors across 57 assets.

2. **Verify Graphite Topology Error:**
   ```bash
   python3 -c "
   import math
   bond_r = 0.025
   pts = set()
   for cx in [-bond_r * 1.5, 0.0, bond_r * 1.5]:
       for k in range(6):
           ang = math.pi * k / 3
           pts.add((round(cx + bond_r * math.cos(ang), 4), round(bond_r * math.sin(ang), 4)))
   pt_list = sorted(list(pts))
   bonds = [(i, j) for i in range(len(pt_list)) for j in range(i+1, len(pt_list)) if abs(math.hypot(pt_list[i][0]-pt_list[j][0], pt_list[i][1]-pt_list[j][1]) - bond_r) < 0.003]
   print('Vertices:', len(pt_list), 'Bonds:', len(bonds))
   print('Degrees:', [sum(1 for b in bonds if i in b) for i in range(len(pt_list))])
   "
   ```
   *Expected Result:* Vertex degrees of 2 and 3 with irregular polygons, confirming non-hexagonal topology.

3. **Verify Open Switch Contradiction:**
   Inspect `assets/physics/full-circuit/build_circuit.py` lines 66 (`rotation_euler=(0.0, -0.35, 0.0)`) and line 22 (`Emission Strength = 4.0`).
