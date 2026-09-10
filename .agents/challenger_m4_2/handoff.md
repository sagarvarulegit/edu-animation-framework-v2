# Milestone 4 Empirical Challenge Report — Challenger M4-2

## 1. Observation

1. **Exact Byte / SHA-256 Parity Verification**:
   - Executed SHA-256 verification between `assets/chemistry/*/out/<id>.glb` and `apps/interactive-viewer/public/assets/<id>.glb`:
     - `diamond-lattice`: `d8b6d36d2b4310b2d0c9f5c136f6394d87f81f6ca0a39450d8ce30ced79dcafc` (1,716,860 bytes, match: `True`)
     - `graphite-lattice`: `04c5b738882863c38761f9b700053bd50b5d14b1375dccdb0d58da9eddfd02b3` (2,826,256 bytes, match: `True`)
     - `hydrogen-evolution-apparatus`: `3f67fb4bd60d034bd332e0a9bb05e8e212846570f6bb41c8ed57d5e080d04a89` (389,688 bytes, match: `True`)
     - `dropper`: `7472c888ae617e2fe8869a1910636a2ac8bfa80ba0495e5a956f0a32163b2579` (88,492 bytes, match: `True`)
     - `magnesium-atom`: `da1d3a6f290e40a6335463d4c497a6cceb063c648bdb106631b935d8e9b9af41` (2,043,972 bytes, match: `True`)
     - `oxygen-atom`: `5018409d09177d171c592596a397f6892cb1cfbe6c803f18bd68cd32cb447da3` (1,363,072 bytes, match: `True`)
     - `bunsen-burner`: `79c4478096571c19fdaa2be616ed2970088b59f594d4645ef20fb255d3b69a7b` (65,508 bytes, match: `True`)
     - `beaker`: `c3281aa4260572bbf236c90bfc42badd654fdab50d5b2e88b18477eef383a5e9` (55,036 bytes, match: `True`)
     - `conical-flask`: `e70c3913c08bbb7e69718a449d7e2dc1ae91b0c5a08ac0bb19fce1a8584885c8` (59,752 bytes, match: `True`)
     - `watch-glass`: `5a5cc8e89032479b2e38cfd0afa16dce8f1e7a2cc96f6dc0f21d707a036e2a16` (17,488 bytes, match: `True`)
     - `magnesium-burning-setup`: `6661aaf2352cbe9fbd231f0fbb060f04b00cbb57180faa9f037151c09f9e7fdf` (155,360 bytes, match: `True`)
   - Extended check across all 22 chemistry assets with `.glb` in `assets/chemistry/` showed 100% SHA-256 match in `apps/interactive-viewer/public/assets/`.

2. **Empirical Crystallographic & Physical Parameter Audit (`tests/empirical/test_m4_challenger.py`)**:
   - **Diamond Lattice C-C-C Angles**:
     - Measured directly from 3D atom locations in `diamond-lattice.blend`: 29 atoms, 40 bond rods.
     - 78 distinct C-C-C angles evaluated.
     - Min angle: $109.4712^\circ$, Max angle: $109.4712^\circ$, Mean: $109.4712^\circ$, Std Dev: $0.0000^\circ$.
     - Matches theoretical sp3 tetrahedral angle $\arccos(-1/3) \approx 109.47122^\circ$ with error $< 0.001\%$.
   - **Graphite Lattice Planarity & Interlayer Spacing**:
     - Measured from 47 carbon atoms in `graphite-lattice.blend`.
     - Distinct layer $Z$-coordinates: $[-0.0284, +0.0284]\text{ m}$.
     - Interlayer gap: $0.05680\text{ m}$.
     - In-plane bond length: $0.02400\text{ m}$.
     - Interlayer gap to bond length ratio: $0.05680 / 0.02400 = 2.3667 > 2.0$.
     - Layer planarity: $Z$-variance $= 0.0$ across 23 atoms in Layer A and 24 atoms in Layer B.
     - In-plane C-C-C bond angles: 43 angles evaluated, all strictly $120.00^\circ$.
   - **Dropper Physical Wall Thickness**:
     - Measured directly on `dropper-glass-pipette` bmesh geometry across 6 distinct $Z$-height slices:
       - $z = 0.0\text{ mm}$: $r_{\text{inner}} = 3.20\text{ mm}, r_{\text{outer}} = 4.40\text{ mm}, \Delta r = 1.20\text{ mm}$
       - $z = 8.0\text{ mm}$: $r_{\text{inner}} = 3.20\text{ mm}, r_{\text{outer}} = 4.40\text{ mm}, \Delta r = 1.20\text{ mm}$
       - $z = 16.0\text{ mm}$: $r_{\text{inner}} = 2.80\text{ mm}, r_{\text{outer}} = 4.00\text{ mm}, \Delta r = 1.20\text{ mm}$
       - $z = 125.0\text{ mm}$: $r_{\text{inner}} = 2.80\text{ mm}, r_{\text{outer}} = 4.00\text{ mm}, \Delta r = 1.20\text{ mm}$
       - $z = 165.0\text{ mm}$: $r_{\text{inner}} = 0.80\text{ mm}, r_{\text{outer}} = 1.80\text{ mm}, \Delta r = 1.00\text{ mm}$
       - $z = 181.0\text{ mm}$: $r_{\text{inner}} = 0.50\text{ mm}, r_{\text{outer}} = 1.50\text{ mm}, \Delta r = 1.00\text{ mm}$
     - Minimum physical wall thickness: $1.00\text{ mm} \ge 1.0\text{ mm}$.
   - **Atomic Model Electron Shells**:
     - Magnesium (`magnesium-atom.blend`): 12 electrons distributed across radii $[0.042, 0.076, 0.112]\text{ m}$ in configuration $[2, 8, 2]$ (K, L, M). Radius sequence strictly monotonically increases ($r_0 < r_1 < r_2$). Nucleus contains 12 protons and 12 neutrons.
     - Oxygen (`oxygen-atom.blend`): 8 electrons distributed across radii $[0.042, 0.076]\text{ m}$ in configuration $[2, 6]$ (K, L). Radius sequence strictly monotonically increases ($r_0 < r_1$). Nucleus contains 8 protons and 8 neutrons.
   - **Glassware Shaders & Transmission**:
     - `beaker` (`beaker-glass`): IOR = 1.5200, Transmission Weight = 0.9600, Roughness = 0.015.
     - `conical-flask` (`conical-flask-glass`): IOR = 1.5200, Transmission Weight = 0.9600, Roughness = 0.015.
     - `watch-glass` (`watch-glass-borosilicate`): IOR = 1.5200, Transmission Weight = 0.9600, Roughness = 0.015.
     - `dropper` (`dropper-glass`): IOR = 1.5200, Transmission Weight = 0.9600, Roughness = 0.015.
     - `hydrogen-evolution-apparatus` (`h2-glass`): IOR = 1.5200, Transmission Weight = 0.9600, Roughness = 0.015.
     - Conforms to `glass_borosilicate` in `visual/design-tokens.json`.
   - **BMesh Manifold Mesh Check**:
     - Audited all 11 modified chemistry blend files: exactly 0 non-manifold edges across all meshes.

3. **Validation & Automated Test Suites**:
   - `node tools/validate.mjs`: `Validation passed.` (0 errors across 57 assets, 44 OKF concepts, 3 lessons, 12 scene plans, design tokens).
   - `node tests/e2e/run_all_tests.mjs --milestone M4`: 13/13 tests passed (100%).
   - `node tests/e2e/run_all_tests.mjs`: 64/64 tests passed across all Tiers 1-4 (100%).
   - `blender -b --python tests/empirical/test_m4_challenger.py`: 33/33 assertions passed (0 failures).

## 2. Logic Chain

1. From Observation 1: Comparing SHA-256 hashes of generated GLBs against downstream web assets proves bit-for-bit parity without divergence or missing models.
2. From Observation 2 (Diamond): Computing pairwise dot products of normalized bond vectors from atom positions gives $\cos\theta = -0.333333$, yielding $\theta = 109.4712^\circ$ for all 78 angles. This confirms that the crystallographic BFS generator correctly inverted child basis vectors and deduplicated lattice positions to close genuine 6-membered chair rings.
3. From Observation 2 (Graphite): Evaluating $Z$-coordinates proves $z$-variance is 0.0 for all atoms in each layer, ensuring planarity. Computing $\Delta z / a_{\text{in-plane}} = 0.05680 / 0.02400 = 2.3667$ confirms the interlayer spacing ratio exceeds the $> 2.0$ physical threshold, faithfully representing weak van der Waals forces relative to strong covalent bonding.
4. From Observation 2 (Dropper): Measuring the radial delta between inner returning profile vertices and outer wall profile vertices across all 6 height levels demonstrates $\Delta r \ge 1.00\text{ mm}$ everywhere, ensuring realistic refraction and manifold 3D shell topology.
5. From Observation 2 (Atoms): Bohr-Bury electronic configurations $[2, 8, 2]$ for Mg and $[2, 6]$ for O with strictly monotonic shell radii confirm curriculum alignment with NCERT Class 9/10/11 chemistry.
6. From Observation 2 (Glassware): Checking the Principled BSDF socket values in all glassware assets confirms exact dielectric borosilicate optical parameters ($IOR = 1.52$, Transmission Weight $= 0.96$).
7. From Observation 3: Passing 0-error workspace validation, 13/13 M4 E2E tests, and 64/64 full test suite tests confirms framework stability and zero regressions.

## 3. Caveats

- As noted by the worker, `tripod-wire-gauze` (an M1/M6 prop) contains 96 non-manifold edges in its legacy mesh; it was out of scope for M4, but should be addressed in M6.
- The diamond and graphite lattices are pedagogical finite clusters representing bulk crystal geometry, rather than periodic boundary simulations.
- No other caveats.

## 4. Conclusion

**VERDICT: APPROVE**

Milestone 4 implementation fully satisfies all empirical criteria, boundary parameters, web synchronization requirements, and educational benchmarks:
1. Exact SHA-256 bit parity confirmed across all chemistry assets in `apps/interactive-viewer/public/assets/`.
2. Diamond C-C-C tetrahedral angle confirmed at $109.4712^\circ$.
3. Graphite interlayer / bond ratio confirmed at $2.3667 > 2.0$ with strictly planar graphene sheets.
4. Dropper wall thickness confirmed at $\ge 1.00\text{ mm}$ throughout.
5. Atomic models confirmed with strictly monotonically increasing electron shell radii and authentic Bohr-Bury distributions.
6. Glassware dielectric shaders confirmed with $IOR = 1.52$ and Transmission Weight $= 0.96$.
7. 0 non-manifold edges verified on all 11 modified chemistry assets.
8. 13/13 M4 E2E tests, 64/64 full project E2E tests, and 33/33 empirical test assertions passed with 0 errors.

## 5. Verification Method

To independently verify all findings:
1. Execute the empirical challenge test suite:
   ```bash
   blender -b --python tests/empirical/test_m4_challenger.py
   ```
2. Verify GLB SHA-256 parity:
   ```bash
   python3 -c '
   import hashlib
   from pathlib import Path
   for a in ["diamond-lattice", "graphite-lattice", "hydrogen-evolution-apparatus", "dropper", "magnesium-atom", "oxygen-atom", "bunsen-burner", "beaker", "conical-flask", "watch-glass", "magnesium-burning-setup"]:
       s = hashlib.sha256(Path(f"assets/chemistry/{a}/out/{a}.glb").read_bytes()).hexdigest()
       d = hashlib.sha256(Path(f"apps/interactive-viewer/public/assets/{a}.glb").read_bytes()).hexdigest()
       assert s == d, f"Mismatch on {a}"
   print("All 11 assets match SHA-256 parity.")
   '
   ```
3. Run project validation and E2E test suite:
   ```bash
   node tools/validate.mjs
   node tests/e2e/run_all_tests.mjs --milestone M4
   node tests/e2e/run_all_tests.mjs
   ```
