# Chemistry & Physics 3D Asset Audit & Survey Report
**Author:** Chemistry & Physics Asset Auditor (Explorer Survey 2)  
**Date:** 2026-09-09  
**Scope:** `assets/chemistry/` (22 assets), `assets/physics/` (22 assets), `assets/python/` (shared libraries), and `visual/design-tokens.json`  
**Reference Standards:** NCERT/CBSE Class 9–12 Science, Chemistry, and Physics Textbooks & Laboratory Manuals, IUPAC/CPK Conventions, and `AGENTS.md`  

---

## 1. Executive Summary & Audit Overview

A comprehensive audit was performed on all 44 existing 3D models and procedural Python generation scripts in the Chemistry and Physics asset libraries of the Educational Animation Framework. Every asset's `asset.json` specification, procedural `build_*.py` script, modifier stacks, mesh topology, shader graphs, and rendered outputs (`out/*.blend`, `out/*.glb`, `out/preview.png`) were inspected and evaluated against CBSE/NCERT curriculum benchmarks.

### Key Audit Metrics
- **Total Assets Audited:** 44 (22 Chemistry, 22 Physics)
- **Automated Validation:** `node tools/validate.mjs` passed with 0 schema errors across all 44 assets.
- **Output Completeness:** 100% of assets contain valid `.blend`, `.glb`, and `preview.png` files.
- **Critical Scientific / Geometric Inaccuracies Discovered:** 7 high-severity defects (including crystallographic errors in diamond and graphite, severe physical contradictions in circuit logic, non-manifold geometry, and broken delivery tubing).
- **Material & Shader Deficiencies:** Absence of volumetric absorption for glassware, lack of realistic multi-zone gas flame models, missing dedicated liquid/solution shader system, and reliance on flat emissive primitives.

---

## 2. Critical Inaccuracies & High-Severity Defects

Before the detailed catalog, the following seven critical issues require immediate architectural remediation:

| # | Asset | Severity | Description of Defect | Physical / Pedagogical Impact |
|---|---|---|---|---|
| **C1** | `graphite-lattice` | **CRITICAL** | **Broken Honeycomb Topology:** Adjacent hexagon centers are shifted along the X axis by $1.5a$ without Y offset, preventing vertices from sharing edges. An arbitrary distance threshold (`abs(dist - bond_r) < 0.003`) creates criss-crossing diagonal chords, producing distorted 4- and 5-sided non-planar polygons with invalid coordination numbers (mostly 2, two of 3). Furthermore, layer stacking is simple AA instead of natural graphite's staggered ABAB stacking. | Completely misrepresents the fundamental allotrope of carbon in NCERT Class 10 Ch 4. Students cannot observe regular planar hexagons or correct delocalized pi bonding. |
| **C2** | `diamond-lattice` | **CRITICAL** | **Uninverted Tetrahedral Child Branching:** Second-shell carbon atoms apply the identical untransformed tetrahedral orientation vectors `t_dirs` as the parent rather than inverting directions ($\vec{d}_{\text{child}} = -\vec{d}_{\text{parent}}$). Consequently, tetrahedra remain aligned in parallel rather than adopting the staggered chair conformation. | Fails to generate the closed 6-membered chair rings characteristic of the diamond cubic crystal structure ($Fd\bar{3}m$), breaking crystallographic validity. |
| **C3** | `full-circuit` | **CRITICAL** | **Open Switch with Glowing Bulb:** The knife switch blade is explicitly angled open at $0.35\text{ rad}$ ($20^\circ$), yet the incandescent light bulb's filament shader is powered with emission strength $4.0$, rendering a bright glowing lamp in an open circuit. | Severe scientific contradiction. Directly instills the misconception that current flows and loads operate in open circuits (violates NCERT Class 10 Ch 12 Fig 12.1). |
| **C4** | `hydrogen-evolution-apparatus` | **HIGH** | **Disjoint Perpendicular Delivery Tube:** The delivery tube is assembled from two straight, perpendicular cylinders (`d_horiz` and `d_vert`) that pierce each other at right angles with flat end caps protruding, rather than forming a single continuous smoothly bent glass tube. | Unrealistic glassware; contradicts standard laboratory apparatus illustrated in NCERT Class 10 Ch 2 Fig 2.1. |
| **C5** | `dropper` | **HIGH** | **Zero-Thickness Open Glass Shell:** The glass pipette profile traces only the outer boundary without revolving an inner wall, creating a single-surface open hollow mesh with zero wall thickness. | Causes severe normal inversion, incorrect index-of-refraction calculations in Cycles, and transparent depth sorting errors in WebGL. |
| **C6** | `magnesium-atom` vs `oxygen-atom` | **MEDIUM** | **Arbitrary Electron Color Inconsistency:** Electrons in `magnesium-atom` are colored cyan `(0.15, 0.78, 1.0)`, while electrons in `oxygen-atom` are colored pink/red `(0.98, 0.44, 0.52)`. | Directly violates `AGENTS.md` Section 7 ("Visual Consistency"): fundamental subatomic particles must maintain identical visual identity across all lessons. |
| **C7** | `beaker`, `conical-flask`, `test-tube`, `tripod-wire-gauze` | **HIGH** | **Hardcoded Bundled Reagents in Reusable Props:** General laboratory glassware assets have specific colored liquids permanently baked into their `.glb` files (e.g. `beaker` contains blue $CuSO_4$; `conical-flask` contains yellow acid; `test-tube` contains amber liquid; `tripod-wire-gauze` bundles a china dish containing oxidized copper powder). | Violates `AGENTS.md` Section 1.2 & 6 (Asset Reusability). A generic beaker cannot be reused in an acid-base neutralization or water heating scene without displaying copper sulphate. |

---

## 3. Comprehensive Chemistry Assets Audit (22 Assets)

### 3.1 Laboratory Glassware

#### 1. `beaker` (250ml Griffin Low-Form Beaker)
- **NCERT Curriculum:** Class 9 Ch 1 & 2 (Solutions, suspensions); Class 10 Ch 1 (Displacement, precipitation), Ch 2 (Acids & bases), Ch 3.
- **Physical Dimensions:** Height 88 mm, outer diameter 68 mm, wall thickness 1.4 mm, flared rim diameter 73 mm.
- **Geometry & Topology:** Revolved bmesh profile with 64 radial segments. Pouring spout is formed by pulling vertices in the $+X$ quadrant above $z = 76\text{ mm}$.
  - *Defect:* Vertex pulling causes distorted, non-planar quad faces along the rim. Needs a dedicated radial profile flare or subsurf-friendly topology.
- **Markings & Decals:** Outer tick ribbons at 50, 100, 150, 200 ml.
  - *Defect:* Lacks printed numerical values ("50", "100", "150", "200 ml") and manufacturer marking area ("APPROX. VOL.").
- **Materials & Shaders:** Borosilicate glass ($IOR = 1.52$, roughness $0.015$).
  - *Defect:* Hardcodes blue $CuSO_4$ solution (`beaker-liquid`) inside the vessel mesh. Glass shader lacks Beer-Lambert volumetric absorption, making the thick glass base appear unnaturally flat.
- **Specification Sync:** `asset.json` contains outdated text ("Graduation marks are decorative rings... solid glass shell rather than thin-walled").

#### 2. `conical-flask` (250ml Erlenmeyer Conical Flask)
- **NCERT Curriculum:** Class 10 Ch 1 (Precipitation of $BaSO_4$), Ch 2 (Reaction of zinc with acids), Class 11/12 volumetric analysis.
- **Physical Dimensions:** Height 140 mm, base diameter 84 mm, neck diameter 34 mm, wall thickness 1.5 mm.
  - *Defect:* `asset.json` specifies `height: 0.095, base-diameter: 0.08`, creating a 47% dimensional discrepancy with the 140 mm script output.
- **Geometry & Topology:** Clean lathe profile with 64 segments, smooth conical slope, cylindrical neck, and beaded lip.
- **Materials & Shaders:**
  - *Defect:* Contains baked-in amber-yellow acid solution (`conical-flask-liquid`). Prevents use as an empty flask.
  - Graduations at 50, 100, 150, 200 ml are tick strips without numeric labels.

#### 3. `test-tube` (Borosilicate Test Tube)
- **NCERT Curriculum:** Class 9 Ch 2 (Colloids, mixtures); Class 10 Ch 1 (Heating $FeSO_4$, $Pb(NO_3)_2$, displacement), Ch 2, Ch 3.
- **Physical Dimensions:** Height 140 mm, diameter 16 mm, wall thickness 1.2 mm.
  - *Defect:* `asset.json` declares height 0.125m and diameter 0.018m (discrepancy with 140x16 mm build).
- **Geometry & Topology:** True hemispherical bottom generated with 16 spherical arc steps; outer and inner shells with 1.2 mm gap; flared beaded top lip. Revolved cleanly with 48 segments.
- **Materials & Shaders:**
  - *Defect:* Bundles a permanent reddish-amber liquid column inside the model.
  - *Curriculum Gap:* NCERT distinguishes standard test tubes (15x125 mm) from hard-glass boiling tubes (25x150 mm) used for direct flame heating. No boiling tube variant exists.
  - *Missing Props:* Test-tube holder (wooden clamp) and test-tube rack are missing as modular companions.

#### 4. `watch-glass` (80 mm Borosilicate Watch Glass)
- **NCERT Curriculum:** Class 9 Ch 1 (Evaporation); Class 10 Ch 1 Activity 1.1 (Collecting $MgO$ powder).
- **Physical Dimensions:** Diameter 82 mm, height 13 mm, uniform thickness 1.2 mm.
- **Geometry & Topology:** Lathe revolution with 64 segments.
  - *Defect:* Profile has only 9 control points; the outer rim is somewhat blocky and lacks the fire-polished rounded edge.
- **Materials & Shaders:** Borosilicate glass ($IOR = 1.52$, roughness $0.012$). Looks clean under studio lighting.

#### 5. `dropper` (Pasteur Dropper / Pipette)
- **NCERT Curriculum:** Class 10 Ch 2 (Adding acid/base dropwise, testing indicators like phenolphthalein and litmus).
- **Physical Dimensions:** Total length 181 mm; rubber bulb diameter 44 mm; glass barrel diameter 8 mm tapering to 0.9 mm tip.
- **Geometry & Topology:**
  - *CRITICAL DEFECT:* Glass pipette is lathed from a 1D curve `[(0.0032, 0.0), ..., (0.00045, 0.181)]` with no return path, creating an infinitely thin, open-ended shell.
  - Rubber bulb is an intersection of an un-deformed UV sphere and a cylinder without a molded neck clamp or compression ridges.
- **Materials & Shaders:** Glass shader applied to open mesh causes dark refractive boundaries. Rubber shader is flat diffuse.

---

### 3.2 Heating, Support & Transfer Apparatus

#### 6. `bunsen-burner` (Laboratory Bunsen Burner)
- **NCERT Curriculum:** Universal heating source across Class 9–12 practicals.
- **Physical Dimensions:** Base diameter 90 mm, total height 125 mm, chimney barrel outer diameter 14 mm.
- **Geometry & Topology:** Multi-part assembly: cast iron base, brass gas inlet nipple, rotatable brass air collar, and nickel-plated mixing tube.
  - *Defect:* Air collar intake ports are modeled as separate dark solid cylinders protruding through the brass collar, rather than true geometric holes or boolean cutouts.
  - *Defect:* Standalone model has NO flame. Gas supply rubber tubing is omitted from the standalone asset.

#### 7. `retort-stand` (Cast Iron Retort Stand with 3-Prong Clamp)
- **NCERT Curriculum:** Universal laboratory support for distillation, titrations, gas collection, and holding test tubes.
- **Physical Dimensions:** Base 125x80x10 mm, vertical rod diameter 9 mm, height 265 mm.
  - *Defect:* `asset.json` states height is 0.15m and base width 0.1m, conflicting with the 0.29m total height.
- **Geometry & Topology:**
  - Support rod, bosshead, clamp arm, and 3 clamp jaws.
  - *Defect:* Clamp prongs are rigid cylinders with UV sphere tips (`size=(0.01, 0.01, 0.01)`). Does not represent real articulated laboratory clamps with thumbscrew adjustments or cork pads.
  - *Missing Variant:* No ring clamp attachment for funnels or wire gauze.

#### 8. `tripod-wire-gauze` (Tripod Stand with Wire Gauze & China Dish)
- **NCERT Curriculum:** Class 9 Ch 1 (Sublimation of $NH_4Cl$); Class 10 Ch 1 Activity 1.11 (Oxidation of copper powder).
- **Physical Dimensions:** Ring diameter 104 mm, height 165 mm, leg spread 150 mm.
- **Geometry & Topology:**
  - *CRITICAL MODULARITY DEFECT:* The asset bundles tripod stand, wire gauze, porcelain china dish, and oxidized copper powder into one monolithic assembly.
  - Wire gauze is modeled as a solid grey box (`cube` of size 120x120x2 mm) without any wire mesh texture or alpha cutout.
  - China dish cannot be removed or emptied for other experiments.

#### 9. `laboratory-tongs` (Crucible Tongs)
- **NCERT Curriculum:** Class 10 Ch 1 Activity 1.1 (Holding burning magnesium ribbon).
- **Physical Dimensions:** Total length 220 mm, scissor pivot span 15 mm.
- **Geometry & Topology:** Bezier curves with 3.2 mm bevel depth for arms, central hinge pin with washer, insulated grip sleeves.
  - *Defect:* The working jaws are rectangular cubes with beveled edges, lacking the curved bowed loop and serrated inner gripping tips of real crucible tongs.
  - Static geometry with no rig/armature for opening and clamping.

---

### 3.3 Assembled Chemistry Experiment Setups

#### 10. `magnesium-burning-setup` (Burning of Magnesium Ribbon Complete Setup)
- **NCERT Curriculum:** Class 10 Chapter 1, Activity 1.1.
- **Features Included:** Lab bench, ceramic safety tile, Bunsen burner, gas hose, dual-cone flame, point light, watch glass with collected $MgO$ powder, retort stand with bosshead holding crucible tongs, magnesium ribbon, and sandpaper strips.
- **Geometry & Topological Defects:**
  - Gas supply hose consists of 4 separate straight cylindrical segments angled towards each other, showing distinct open polygonal seams at joint elbows.
  - Burner flame is made of two concentric solid cones (`flame-outer` and `flame-inner`) with flat emission shaders.
  - Sandpaper strips are plain brown rectangular slabs with no surface roughness map.

#### 11. `water-electrolysis-apparatus` (Hoffmann Voltameter)
- **NCERT Curriculum:** Class 10 Chapter 1, Activity 1.7 (Electrolysis of acidified water).
- **Features Included:** Support base, reaction vessel, two graphite electrodes with rubber stoppers, red/black binding posts, inverted graduated test tubes, liquid columns, rising bubbles, and gas collection spaces with exact 2:1 stoichiometric volume ratio ($H_2$ cathode : $O_2$ anode).
- **Pedagogical & Physical Defects:**
  - NCERT Activity 1.7 specifically uses a plastic mug drilled with two holes. This model uses an acrylic stand and a glass reaction beaker.
  - Graduation marks along the inverted test tubes are full 360-degree cylinder slabs intersecting the tubes.
  - Missing 6V DC battery and connecting wires.

#### 12. `hydrogen-evolution-apparatus` (Zinc + Acid Reaction Setup)
- **NCERT Curriculum:** Class 10 Chapter 2, Activity 2.1.
- **Features Included:** Erlenmeyer flask, dilute acid, clustered zinc granules, two-hole rubber stopper, thistle funnel, delivery tube, soap solution trough, rising soap bubbles with $H_2$, testing candle with flame.
- **CRITICAL DEFECTS:**
  - *Broken Glassware Topology:* The delivery tube consists of two completely disjoint perpendicular cylinders (`d_horiz` and `d_vert`) intersecting at right angles with flat open ends protruding outside the junction.
  - *Thistle Funnel Disjoint Geometry:* The thistle funnel is assembled from an unjoined cylinder and cone.
  - *Missing Support:* The conical flask floats unsupported on the ground without a retort stand or clamp.
  - *Candle Flame:* Solid geometric cone with flat emission shader.

#### 13. `displacement-reaction-setup` (Iron Nail in Copper Sulphate)
- **NCERT Curriculum:** Class 10 Chapter 1, Activity 1.9.
- **Features Included:** Beechwood test tube rack, Test tube A (deep blue $CuSO_4$ solution), Test tube B (faded pale green $FeSO_4$ solution with copper-coated iron nail), comparison clean iron nail on watch glass.
- **Defects & Regressions:**
  - *Crude Test Tubes:* Unlike the dedicated `test-tube` asset (which has a hemispherical bottom and flared lip), the test tubes in this setup are flat-bottomed solid cylinders (`primitive_object('cylinder')`).
  - *Floating Thread:* The suspension thread terminates in mid-air above Test Tube B without being tied to a stand or clamp.
  - *Nail Coating:* The copper coating on the submerged iron nail is an abrupt cylinder split rather than a realistic deposited crust with a liquid meniscus demarcation.

---

### 3.4 Atomic, Molecular & Crystal Models

#### 14. `magnesium-atom` (Bohr Atomic Model, $Z=12$)
- **NCERT Curriculum:** Class 9 Chapter 4 (Structure of the Atom, electronic configuration 2, 8, 2).
- **Features:** Central nucleus with 24 packed spheres (12 protons with red emission, 12 grey neutrons), 3 concentric torus rings representing K, L, M shells, and orbiting electron spheres.
- **Discrepancies:**
  - Completely planar 2D arrangement.
  - Ring radii in script ($0.042, 0.076, 0.112\text{ m}$) conflict with anchor points in `asset.json` ($0.055, 0.095, 0.138\text{ m}$).
  - `asset.json` contains non-physical data: `weight_g: 1`.

#### 15. `oxygen-atom` (Bohr Atomic Model, $Z=8$)
- **NCERT Curriculum:** Class 9 Chapter 4 (Structure of the Atom, configuration 2, 6).
- **Features:** Nucleus with 16 packed spheres (8 protons, 8 neutrons), 2 concentric torus rings (K, L shells).
- **Discrepancies:**
  - *Visual Inconsistency:* Electrons are colored red/pink `(0.98, 0.44, 0.52)` instead of the cyan color used in `magnesium-atom`.
  - Planar arrangement.

#### 16. `magnesium-ribbon` (Magnesium Metal Strip)
- **NCERT Curriculum:** Class 10 Chapter 1, Activity 1.1.
- **Features:** Polygonal mesh ribbon with sinusoidal longitudinal wave along X axis.
- **Discrepancies:**
  - Hardcodes custom color `(0.82, 0.84, 0.87)` rather than referencing token `metal_magnesium_ribbon`.
  - Lacks representation of the uncleaned oxidized ribbon (dull grey coating of basic magnesium carbonate) vs cleaned shiny metal.

#### 17. `magnesium-oxide` (Magnesium Oxide Powder Product)
- **NCERT Curriculum:** Class 10 Chapter 1, Activity 1.1 ($2Mg + O_2 \to 2MgO$).
- **Features:** Single smooth cone primitive with 22 tiny scattered spheres.
- **Discrepancies:**
  - Highly stylized, low fidelity. Does not look like amorphous, crumbly white powder.

#### 18. `magnesium-oxide-lattice` (MgO Rock-Salt Crystal Lattice)
- **NCERT Curriculum:** Class 10 Ch 3 (Ionic compounds) & Class 11/12 Solid State (FCC, 6:6 coordination).
- **Features:** 3x3x3 cubic lattice of alternating $Mg^{2+}$ and $O^{2-}$ ions connected by orthogonal cylindrical rods.
- **Discrepancies:**
  - *Color Discrepancy:* $Mg^{2+}$ cation is colored cyan/teal `(0.02, 0.71, 0.83)` instead of CPK purple `#8b5cf6` defined in `design-tokens.json`.
  - *Dead Code:* Line 33 contains an unexecuted math expression overwritten by line 34.
  - *Pedagogical Simplification:* Ball-and-stick rods labeled "IonicBondMat" can reinforce the misconception that ionic bonds are directional sticks like covalent bonds. Needs documentation or alternate space-filling representation.

#### 19. `methane-molecule` (Tetrahedral $CH_4$ Molecule)
- **NCERT Curriculum:** Class 10 Chapter 4 (Carbon and its Compounds, covalent bonding in methane).
- **Features:** Central carbon sphere with 4 tetrahedral hydrogen vertices at exact angle $\arccos(-1/3) \approx 109.47^\circ$, connected by cylindrical covalent bond rods.
- **Assessment:** Geometrically and chemically accurate.
- **Minor Note:** Does not import CPK colors from `design-tokens.json`.

#### 20. `diamond-lattice` (Diamond Allotrope Crystal Lattice)
- **NCERT Curriculum:** Class 10 Chapter 4, Section 4.1.2.
- **CRITICAL CRYSTALLOGRAPHIC ERROR:**
  - The script attempts to build a 2-shell tetrahedral lattice, but uses UNINVERTED tetrahedral vectors `t_dirs` for child carbon nodes:
    `for t in t_dirs: if (t + dir1).length > 0.01: p2 = parent_pos + t`
  - In a real diamond cubic lattice, alternating bonded atoms invert their tetrahedral orientation. Using parallel tetrahedra fails to close the 6-membered chair rings and produces a distorted, incorrect branching structure.

#### 21. `graphite-lattice` (Layered Hexagonal Graphite Lattice)
- **NCERT Curriculum:** Class 10 Chapter 4, Section 4.1.2.
- **CRITICAL TOPOLOGY ERROR:**
  - Ring centers are placed at $x = -1.5a, 0, +1.5a$ at $y = 0$, but vertices are generated at angles $k\pi/3$. Adjacent hexagons do not share vertices.
  - The neighbor-finding threshold (`abs(dist - bond_r) < 0.003`) creates criss-crossing diagonal bonds across distorted polygons.
  - Uses simple AA stacking instead of natural graphite's staggered ABAB stacking.

#### 22. `soap-micelle` (Spherical Soap Micelle with Oil Droplet)
- **NCERT Curriculum:** Class 10 Chapter 4, Section 4.4.1 (Cleansing action of soaps, Figure 4.12).
- **Features:** Central spherical oil droplet with 20 radially oriented soap molecules distributed via Fibonacci sphere sampling.
- **Discrepancies:**
  - Hydrocarbon tails are modeled as straight rigid cylinders rather than the characteristic organic zigzag alkyl chain ($C_{17}H_{35}-$).
  - Only 20 molecules on the sphere, leaving large open gaps that expose the central oil droplet. A realistic micelle contains 50–100 surfactant monomers.
  - Polar heads have no charge indication ($-COO^- Na^+$).

---

## 4. Comprehensive Physics Assets Audit (22 Assets)

### 4.1 Electricity & Circuits

#### 1. `battery` (1.5V AA Dry Cell)
- **NCERT Curriculum:** Class 10 Chapter 12 (Electricity).
- **Physical Dimensions:** Height 50 mm, diameter 14 mm.
- **Geometry & Topology:** Zinc negative base cup, golden jacket sleeve, crimped top shoulder insulator, and raised brass positive pip.
- **Assessment:** Clean, physically realistic dry cell model.
- **Curriculum Gap:** In school lab practicals, dry cells are mounted in plastic/wooden cell holders with screw terminals, or connected to a variable DC battery eliminator. A bare AA cell cannot connect to laboratory wire lugs.

#### 2. `bulb` (Incandescent Light Bulb)
- **NCERT Curriculum:** Class 10 Chapter 12 (Heating effect of electric current).
- **Physical Dimensions:** Maximum globe diameter 60 mm, height 108 mm.
- **Geometry & Topology:** Revolved A19 teardrop glass globe, E27 screw base, glass stem pinch seal, lead-in wires, and horizontal filament bridge.
- **Discrepancies:**
  - Filament is a smooth straight cylinder without coiling ("double-coiled tungsten filament" is absent).
  - Base is a single brass material without the black glass insulating ring between the screw shell and the foot contact.
  - E27 domestic lamp rather than the miniature socket lamp used in laboratory circuit boards.

#### 3. `switch` (Single-Pole Knife Switch)
- **NCERT Curriculum:** Class 10 Chapter 12 (Electric circuits and circuit diagrams).
- **Physical Dimensions:** Base 90x50x12 mm; knife arm length 52 mm.
- **Geometry & Topology:** Bakelite base with rubber feet, fixed hinge block with pin, receiving copper U-jaw, pivoting brass blade, red insulated handle, and brass binding posts.
- **Discrepancies:**
  - Frozen in the OPEN state ($32^\circ$ tilt) with no closed configuration.
  - NCERT circuit experiments predominantly feature the laboratory brass plug key `(•)`. No plug key asset exists in the library.

#### 4. `resistor` (Axial Through-Hole Resistor, 1 k$\Omega \pm 5\%$)
- **NCERT Curriculum:** Class 10 Chapter 12 (Ohm's law, series/parallel combinations); Class 12 Chapter 3.
- **Physical Dimensions:** Body length 6.5 mm, diameter 2.6 mm; axial lead wire diameter 0.6 mm.
- **Geometry & Topology:** Contoured ceramic body with 4 coaxial color bands: Brown (1), Black (0), Red ($\times 10^2 = 1\text{ k}\Omega$), Gold ($\pm 5\%$).
- **Assessment:** Physically accurate component model.
- **Curriculum Gap:** School physics practicals use wire-wound standard resistance coils housed in acrylic boxes with brass terminals or calibrated plug-type resistance boxes.

#### 5. `rheostat` (Laboratory Slide-Wire Variable Resistor)
- **NCERT Curriculum:** Class 10 Chapter 12 (Ohm's law, controlling current); Class 12 Chapter 3.
- **Physical Dimensions:** Core tube length 120 mm, diameter 32 mm, total height 70 mm.
- **Geometry & Topology:** Porcelain tube, cast end support brackets, top square brass slider guide rod, sliding contact block with insulated knob, and three binding posts (two lower fixed, one upper variable).
- **Discrepancies:**
  - Resistance coil consists of 16 discrete cylinder rings separated by 2 mm gaps, rather than a continuous, tightly wound helix of oxidized resistance wire.
  - Slider position is static.

#### 6. `connecting-wire` (Flexible Red PVC Connecting Wire)
- **NCERT Curriculum:** Class 10 Chapter 12 (Circuit connections).
- **Physical Dimensions:** Length 150 mm, diameter 4.5 mm.
- **Geometry & Topology:** U-shaped curved path terminating in molded strain relief boots, stripped copper strands, and U-shaped spade lugs.
- **Discrepancy:** Wire curve is constructed from 6 straight cylinder segments with visible faceted seam joints. Should be a smooth beveled bezier curve.
- **Missing Asset:** No black (-) or neutral/green wire assets.

#### 7. `full-circuit` (Closed Electric Circuit Demonstration Board)
- **NCERT Curriculum:** Class 10 Chapter 12, Figure 12.1.
- **Features Included:** Demonstration board, battery in holder, knife switch, resistor, ammeter, light bulb in socket, interconnecting wires.
- **CRITICAL PEDAGOGICAL CONTRADICTION:**
  - Knife switch blade is OPEN (`rotation_euler = (0, -0.35, 0)`), but the light bulb filament has emission strength 4.0 and glows brightly!
  - Must be corrected: either close the knife switch blade into the jaws, or extinguish the bulb filament when the switch is open.

#### 8. `ammeter` (Weston-Type DC Ammeter, 0–3A)
- **NCERT Curriculum:** Class 10 Chapter 12 (Measuring current).
- **Physical Dimensions:** Housing 90x72x70 mm; viewing window 74x48 mm.
- **Features:** Slanted casing, window frame, glass pane, dial plate, 0–3A scale arc ticks, indicator needle, pivot, bold 'A' symbol with DC bar, zero adjustment screw, red (+) and black (-) binding posts.
- **Discrepancies:**
  - `asset.json` name says "Ammeter (0-1A)", but the script builds a 0–3A meter.
  - Needle is fixed at zero with no deflection states.

#### 9. `voltmeter` (Weston-Type DC Voltmeter, 0–3V)
- **NCERT Curriculum:** Class 10 Chapter 12 (Measuring potential difference).
- **Assessment:** Matches ammeter housing with bold 'V' symbol and 0–3V calibrated scale. Needle is static at zero.

#### 10. `galvanometer` (Center-Zero Moving-Coil Galvanometer)
- **NCERT Curriculum:** Class 10 Chapter 13 (Electromagnetic induction); Class 12 Chapter 3 & 4.
- **Features:** Center-zero scale ($-30$ to $+30$ divisions), central zero needle, bold 'G' indicator.
- **Discrepancy:** Terminals are colored Red (+) and Black (-). A center-zero galvanometer is non-polarized because current deflects the needle bidirectionally. Terminals should both be brass or unpolarized.

---

### 4.2 Magnetism & Electromagnetism

#### 11. `bar-magnet` (AlNiCo Permanent Bar Magnet & Field Lines)
- **NCERT Curriculum:** Class 10 Chapter 13, Figures 13.2, 13.3, 13.4.
- **Features:** Rectangular AlNiCo bar (120x24x16 mm) with painted Red (N) and Blue (S) poles, raised 'N' and 'S' plates, 3D curved field line tubes, and plotting compass with tangent needle.
- **Discrepancies:**
  - Field line tubes DO NOT HAVE DIRECTIONAL ARROWS! In NCERT diagrams, arrows pointing from North to South are mandatory.
  - Internal magnetic field lines (continuous closed loops running from South to North inside the magnet) are omitted.

#### 12. `solenoid` (Helical Solenoid with Magnetic Field Lines)
- **NCERT Curriculum:** Class 10 Chapter 13, Section 13.2.4 & Figure 13.10.
- **Features:** Central insulating tube, continuous 3D swept copper helix (14 turns), support base, terminal posts, internal uniform field lines, and external curved return flux loops.
- **Discrepancies:**
  - Field lines lack directional arrows (students cannot verify Right-Hand Thumb Rule / polarity).
  - Coil ends do not connect to the binding posts on the base.

#### 13. `electric-motor` (DC Electric Motor Working Model)
- **NCERT Curriculum:** Class 10 Chapter 13, Section 13.4 & Figure 13.15.
- **Features:** Cast base, bearing pillars, curved pole field magnets (North red, South blue), rotating axle, rectangular armature coil ABCD, split-ring commutator P & Q, carbon brushes X & Y, pulley, and supply terminals.
- **CRITICAL TOPOLOGICAL DEFECTS:**
  - Split-ring commutator is modeled as two solid full cylinders shifted by 1 mm along X, rather than two semicircular half-rings separated by an insulating gap.
  - Armature coil end arms (BC and DA) intersect the central rotating axle as straight cylinders.

---

### 4.3 Optics

#### 14. `plane-mirror` (Plane Mirror on Swivel Stand)
- **NCERT Curriculum:** Class 10 Chapter 10 (Reflection of light).
- **Physical Dimensions:** Mirror surface 100x140 mm, total height 220 mm.
- **Features:** Silver reflective pane, protective backing, wooden frame, swivel pivot studs with knurled knobs, cast iron stand.
- **Assessment:** Clean, functional prop.

#### 15. `concave-mirror` (Spherical Converging Concave Mirror)
- **NCERT Curriculum:** Class 10 Chapter 10 (Image formation by concave mirror).
- **Physical Dimensions:** Diameter 100 mm, focal length $f = 80\text{ mm}$ ($R_c = 160\text{ mm}$), depth 8 mm.
- **Geometry:** Exact spherical dish profile ($z = -(\sqrt{R_c^2 - r^2} - \dots)$), back coating, brass retaining bezel, swivel clamp, chrome post, and cast iron base.
- **Assessment:** Mathematically and physically rigorous.

#### 16. `convex-mirror` (Spherical Diverging Convex Mirror)
- **NCERT Curriculum:** Class 10 Chapter 10 (Convex mirror as rear-view mirror).
- **Physical Dimensions:** Diameter 100 mm, $R_c = 160\text{ mm}$.
- **Assessment:** Mathematically accurate bulging spherical profile.

#### 17. `convex-lens` (Biconvex Converging Lens)
- **NCERT Curriculum:** Class 10 Chapter 10 (Refraction by spherical lenses).
- **Physical Dimensions:** Diameter 80 mm, center thickness 14 mm, edge thickness 2.4 mm, curvature radius $R_c = 140\text{ mm}$.
- **Geometry:** Symmetrical spherical cap profile with brass retaining ring, mount clamp, post, and base.
- **Minor Defect:** Profile array has near-duplicate vertices at $(0, \pm 0.007\text{ m})$ which rely on `remove_doubles`.

#### 18. `concave-lens` (Biconcave Diverging Lens)
- **NCERT Curriculum:** Class 10 Chapter 10 (Biconcave lens).
- **Physical Dimensions:** Diameter 80 mm, center thickness 2.4 mm, edge thickness 12 mm, $R_c = 160\text{ mm}$.
- **Assessment:** Accurate diverging lens geometry.

#### 19. `glass-slab` (Rectangular Glass Slab Refraction Block)
- **NCERT Curriculum:** Class 10 Chapter 10, Figure 10.10.
- **Physical Dimensions:** 100x65x20 mm borosilicate optical block.
- **CRITICAL OMISSIONS:**
  - Only incident optical pins P1 and P2 are present; emergent pins P3 and P4 are completely missing.
  - The incident ray, refracted ray inside the slab, emergent ray, surface normals, and lateral displacement ($d$) are not rendered.

#### 20. `glass-prism` (Equilateral Glass Prism)
- **NCERT Curriculum:** Class 10 Chapter 11 (Refraction through a prism).
- **Physical Dimensions:** Equilateral side 60 mm, length 80 mm, $A = 60^\circ$.
- **Assessment:** Sharp equilateral optical geometry with flat polished facets.

#### 21. `glass-prism-refraction` (Assembled Prism Refraction & Dispersion Setup)
- **NCERT Curriculum:** Class 10 Chapter 11, Figures 11.4 & 11.5.
- **Features Included:** Wooden drawing board, paper sheet with thumb pins, prism with pencil outline, ray box collimator, incident white ray, pins P1 & P2, exact Snell's law refraction for all 7 spectral wavelengths (VIBGYOR), pins P3 & P4 on mean yellow ray, surface normals, extension of incident ray showing angle of deviation $D$, and observation screen with projected spectral bands.
- **Assessment:** Model of pedagogical and mathematical excellence. Sets the gold standard for optical demonstrations in the framework.

#### 22. `optical-bench` (Dual-Rail Optical Bench Apparatus)
- **NCERT Curriculum:** Class 10 Chapter 10 & Class 12 Practical Physics (Determining focal length of convex lens).
- **Physical Dimensions:** Rail length 1.0 m, rail diameter 16 mm, rail spacing 60 mm.
- **Features:** Stainless steel dual rails, central millimeter scale bar, cast iron end support feet with brass leveling screws, and 3 sliding rider blocks (candle object, lens holder, white projection screen).
- **Discrepancies:**
  - Lens element is a scaled UV sphere (`scale = (0.16, 1.0, 1.0)`), yielding an ellipsoidal rather than true spherical curvature ($R_1, R_2$).
  - Class 12 experiments require optical needles with parallax removal tips rather than a candle flame.
  - Upright riders lack slow-motion transverse and vertical adjustment screws.

---

## 5. Shader & Material Architecture Needs

A critical finding of this audit is that while basic Principled BSDF shaders are functioning, several physical phenomena lack dedicated shader pipelines:

### 5.1 Realistic Glass with Volumetric Absorption
- **Current Limitation:** Glass shaders currently set `Transmission Weight = 0.96` and a flat base color tint. In thick glass (e.g. beaker bases, lens rims), the material appears uniformly bright rather than deeper in color.
- **Requirement:** Implement Beer-Lambert volume absorption:
  $$I(\lambda) = I_0(\lambda) e^{-\mu(\lambda) d}$$
  In Blender Cycles, this requires connecting a `Principled BSDF` (roughness $0.01$, $IOR = 1.517$) with a `Volume Absorption` shader via an `Add Shader` or material node tree, configuring `Color` and `Density` ($1.5 - 2.5\text{ m}^{-1}$).

### 5.2 Multi-Zone Gas Flame Shaders
- **Current Limitation:** Flames are solid cone meshes with uniform emissive shaders, appearing as glowing plastic shapes.
- **Requirement:** Procedural multi-zone flame shader using:
  1. Gradient texture along Z with `ColorRamp` mapping:
     - $z = 0.0 - 0.2$: Pale transparent blue unburnt zone (emission strength $\approx 2$)
     - $z = 0.2 - 0.7$: Hot cyan/blue reaction mantle (emission strength $\approx 18$)
     - $z = 0.7 - 1.0$: Feathery violet outer sheath (soft alpha falloff)
  2. Noise texture displacement driving alpha transparency to break hard cone silhouettes.

### 5.3 Dedicated Solution & Liquid Shaders
- **Current Limitation:** No centralized `add_liquid_material` exists.
- **Requirement:** Add `add_liquid_material(name, liquid_type)` in `edu_asset_kit.py` supporting:
  - `water`: $IOR = 1.333$, clear, absorption density $0.1$.
  - `copper_sulphate`: $IOR = 1.335$, deep cerulean blue, absorption density $8.0$.
  - `iron_sulphate`: $IOR = 1.334$, pale light green, absorption density $4.0$.
  - `acid_dilute`: $IOR = 1.335$, water-clear with subtle amber warmth.
  - `soap_solution`: $IOR = 1.335$, cloudy translucent white with Subsurface Scattering ($SSS = 0.008$).

### 5.4 Specialized Metals
- Add standardized metal presets in `edu_asset_kit.py` and `design-tokens.json`:
  - `metal_copper`: $(0.88, 0.45, 0.22)$, metallic $0.95$, roughness $0.22$.
  - `metal_brass`: $(0.86, 0.70, 0.28)$, metallic $0.92$, roughness $0.25$.
  - `metal_zinc`: $(0.72, 0.76, 0.80)$, metallic $0.88$, roughness $0.38$.
  - `metal_cast_iron`: $(0.12, 0.13, 0.15)$, metallic $0.75$, roughness $0.55$.
  - `metal_chrome`: $(0.92, 0.93, 0.95)$, metallic $0.98$, roughness $0.12$.

---

## 6. Modularity & Reusability Strategy

In accordance with `AGENTS.md` Rules 1.2 and 6, props must be decoupled from specific experiment outcomes:

1. **Empty vs Filled Glassware:**
   - Modify `build_beaker.py`, `build_flask.py`, and `build_test_tube.py` to produce clean, empty glassware by default.
   - Separate solutions into independent props (`liquid-cuso4`, `liquid-acid`, `liquid-feso4`) that can be instantiated and parented inside any vessel.
2. **Decompose Composite Assemblies:**
   - Extract `wire-gauze` and `china-dish` into standalone assets separate from `tripod-stand`.
   - Provide clean, unreacted iron nails and copper-plated nails as distinct props.
   - Provide plug key `(•)` as a primary laboratory switch asset.

---

## 7. Prioritized Remediation Roadmap

| Priority | Asset / File | Action Required |
|---|---|---|
| **P0** | `assets/physics/full-circuit/build_circuit.py` | Turn off bulb filament emission when the knife switch is open, or close the switch blade. |
| **P0** | `assets/chemistry/graphite-lattice/build_graphite_lattice.py` | Rewrite honeycomb generator using regular graphene 2D basis vectors ($\vec{a}_1, \vec{a}_2$) to create true regular planar hexagons with ABAB stacking. |
| **P0** | `assets/chemistry/diamond-lattice/build_diamond_lattice.py` | Invert tetrahedral orientation vectors for bonded child carbon nodes to produce closed 6-membered chair rings. |
| **P0** | `assets/chemistry/hydrogen-evolution-apparatus/build_hydrogen_evolution.py` | Replace disjoint intersecting cylinders with a continuous swept bezier curve delivery tube with smooth $90^\circ$ bends. |
| **P1** | `assets/chemistry/dropper/build_dropper.py` | Close the glass pipette lathe profile to provide real 1.0 mm wall thickness. |
| **P1** | `assets/physics/electric-motor/build_electric_motor.py` | Replace overlapping solid cylinders with two semicircular half-rings separated by an insulating gap for the split-ring commutator. |
| **P1** | `assets/physics/glass-slab/build_glass_slab.py` | Add emergent optical pins P3 and P4, ray paths, and surface normals. |
| **P1** | `assets/chemistry/oxygen-atom/build_oxygen_atom.py` | Harmonize electron material color to match the cyan standard of `magnesium-atom`. |
| **P1** | `assets/chemistry/magnesium-oxide-lattice/build_magnesium_oxide_lattice.py` | Update $Mg^{2+}$ color to CPK purple `#8b5cf6` and clean up dead code. |
| **P2** | `assets/physics/bar-magnet/build_bar_magnet.py` & `solenoid/build_solenoid.py` | Add 3D directional arrow cones along magnetic field lines. |
| **P2** | `assets/python/edu_asset_kit.py` & `visual/design-tokens.json` | Implement `add_liquid_material` and multi-zone flame shaders with volume absorption. |
| **P2** | `assets/chemistry/beaker/build_beaker.py` & `conical-flask/` | Unbundle hardcoded liquids; add printed numeric graduation labels. |

---
*Report compiled and verified by Chemistry & Physics Asset Auditor.*
