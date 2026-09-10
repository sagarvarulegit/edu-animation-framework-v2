# Comprehensive Biology 3D Asset & Procedural Script Audit

**Author:** Biology Asset Auditor (Explorer Survey 1)  
**Date:** 2026-09-09  
**Repository Scope:** `edu-animation-framework-v2/assets/biology/`  
**Reference Standards:** NCERT/CBSE Class 9–12 Biology Textbooks, `AGENTS.md`, `ORIGINAL_REQUEST.md`, `visual/design-tokens.json`  

---

## 1. Executive Summary & Audit Scorecard

A comprehensive anatomical, topological, and pedagogical audit was conducted across all **13 existing 3D biology assets** in `assets/biology/`. Each asset was evaluated against NCERT Class 9–12 textbook benchmarks, procedural Blender generation scripts (`build_*.py`), metadata specifications (`asset.json`), production `.blend` scene hierarchies, web-ready `.glb` exports, and preview renders.

While the codebase demonstrates a functional procedural framework using `edu_asset_kit.py` and passes schema validation (`node tools/validate.mjs`), **critical scientific discrepancies, topological flaws, and provenance contradictions exist across the entire biological catalog**. Several assets claiming museum-grade or Z-Anatomy scanned fidelity are in reality crude assemblies of basic geometric primitives (spheres, cubes, and cylinders) that misrepresent fundamental anatomical relationships.

### Audit Scorecard

| Asset ID | Primary NCERT Reference | Objects | Vertices / Faces | Non-Manifold Elements | Anatomical Fidelity | Topology / Shader Quality | Overall Grade | Priority |
|---|---|---|---|---|---|---|---|---|
| **`human-heart`** | Cl 10 Ch 5 (Fig 5.10); Cl 11 Ch 18 (Fig 18.2) | 23 | 31,172 / 31,192 | **508** open edges | ⚠️ Incomplete (Closed mass) | ⚠️ High (No SSS, 508 open rims) | **C+** | **P0 (Critical)** |
| **`human-eye`** | Cl 10 Ch 11 (Fig 11.1); Cl 11 Ch 21 (Fig 21.6) | 9 | 4,956 / 5,306 | 0 (Boolean seam) | ⚠️ Missing choroid, vitreous | ⚠️ Solid sphere cutouts; plastic pupil | **C** | **P0 (Critical)** |
| **`brain`** | Cl 10 Ch 7 (Fig 7.3); Cl 11 Ch 21 (Fig 21.4) | 10 | 9,338 / 9,798 | 0 | ❌ Severe (No gyri/sulci/folia) | ❌ Primitives only (spheres & cubes) | **D** | **P0 (Critical)** |
| **`nephron`** | Cl 10 Ch 5 (Fig 5.14); Cl 11 Ch 19 (Fig 19.3) | 20 | 46,962 / 46,720 | **576** open edges | ⚠️ Good, but no JGA/boundary | ⚠️ 18 disconnected open tubes | **B-** | **P0 (Critical)** |
| **`human-respiratory-system`** | Cl 10 Ch 5 (Fig 5.9); Cl 11 Ch 17 (Fig 17.1) | 37 | 43,702 / 44,772 | **280** open edges | ⚠️ Closed lungs hide bronchi | ⚠️ O-rings instead of C-rings | **B-** | **P0 (Critical)** |
| **`digestive-system`** | Cl 10 Ch 5 (Fig 5.6); Cl 11 Ch 16 (Fig 16.1-3) | 25 | 18,088 / 19,398 | 0 | ❌ Unrealistic (7 floating spheres) | ❌ Disjointed primitive blocks | **D+** | **P0 (Critical)** |
| **`human-excretory-system`** | Cl 10 Ch 5 (Fig 5.13); Cl 11 Ch 19 (Fig 19.1-2) | 17 | 26,474 / 26,928 | **168** open edges | ⚠️ No internal pyramids/cortex | ⚠️ Open vessel/ureter rims | **B-** | **P1 (High)** |
| **`neuron`** | Cl 10 Ch 7 (Fig 7.1); Cl 11 Ch 21 (Fig 21.1) | 33 | 21,970 / 23,808 | 0 | ⚠️ Spherical myelin beads | ⚠️ Rigid stick dendrites; no Nissl | **C+** | **P1 (High)** |
| **`reflex-arc`** | Cl 10 Ch 7 (Fig 7.2) | 15 | 5,664 / 6,354 | 0 | ⚠️ Cubical gray matter wings | ⚠️ Segmented jagged nerve cylinders | **C** | **P1 (High)** |
| **`dna-double-helix`** | Cl 11 Ch 9 (Fig 9.5); Cl 12 Ch 6 (Fig 6.2-3) | 30 | 1,930 / 1,488 | **80** non-manifold | ❌ Severe orientation bug | ❌ Unapplied skin mod; vertical rungs | **F** | **P1 (High)** |
| **`stoma`** | Cl 10 Ch 5 (Fig 5.3); Cl 11 Ch 6 (Fig 6.4) | 32 | 37,648 / 38,228 | **64** open edges | ⚠️ Only open state modeled | ⚠️ Inner wall floating overlay tube | **B** | **P2 (Medium)** |
| **`flower-anatomy`** | Cl 10 Ch 8 (Fig 8.7); Cl 12 Ch 2 (Fig 2.1, 2.7) | 20 | 15,224 / 15,584 | 0 | ⚠️ Solid ovary; no bilobed anther | ⚠️ Overlapping primitives | **C+** | **P2 (Medium)** |
| **`trophic-level-pyramid`** | Cl 10 Ch 15 (Fig 15.2); Cl 12 Ch 14 (Fig 14.4) | 10 | 260 / 368 | 0 | ⚠️ No numerical labels on 3D mesh | ⚠️ Degenerate cone thickness bug | **C** | **P2 (Medium)** |

---

## 2. Systematic & Architectural Deficiencies Across the Biology Catalog

### 2.1 Provenance Misrepresentation vs. Code Reality
Four core assets (`human-heart`, `human-eye`, `brain`, `digestive-system`) state in their `asset.json`:
- `"method": "scanned-sourced"`
- `"source": "https://github.com/Z-Anatomy/Z-Anatomy"`
- `"generator": "tools/extract_z_anatomy_*.py"`
- `"license": "CC-BY-SA-4.0"`

**Direct Finding:** The corresponding generator scripts (`tools/extract_z_anatomy_*.py`) **do not exist in the repository**, and the models are built entirely from procedural primitives in `build_*.py`. For instance:
- In `brain/build_brain.py`, the cerebrum is a stretched `uv_sphere`, the hypothalamus is a `cube`, the corpus callosum is a rotated `cylinder`, and the cerebellum is an untextured `uv_sphere`.
- In `digestive-system/build_digestive.py`, the small intestine is a set of 7 disconnected spheres, the liver is a rounded cube, and the colon is 5 disconnected cylinders.
- In `human-heart/build_heart.py`, the atria are UV spheres and the ventricular mass is a single solid mesh without internal chambers.

This creates a serious architectural violation of **AGENTS.md Rule 1.4, 1.5, and 17** (false provenance metadata, claiming scanned realism when the geometry is primitive).

### 2.2 Open Non-Manifold Tubular Boundaries (1,676 Open Rims)
The standard helper `create_smooth_tube()` and `create_smooth_curved_tube()` in `edu_asset_kit.py` and local scripts generate tubular geometry by creating 3D Bezier splines with `bevel_depth` and converting them to meshes (`bpy.ops.object.convert(target='MESH')`).
- Because the splines have open start and end points, the resulting cylinder caps are left open.
- When converted to mesh, every open end creates a circular boundary of non-manifold edges.
- In `human-heart`, 16 vessels produce **508 non-manifold edges**.
- In `nephron`, 18 tubule and capillary segments produce **576 non-manifold edges**.
- In `human-respiratory-system`, bronchi and fissures produce **280 non-manifold edges**.
- In `human-excretory-system`, renal vessels and ureters produce **168 non-manifold edges**.
- In `stoma`, inner wall tubes produce **64 non-manifold edges**.
- Total non-manifold edges across biology: **1,596 edges** (+ 80 unapplied skin vertices/edges in DNA = **1,676 non-manifold defects**).
- *Consequence:* While three.js can render single-sided open surfaces, raytracing in Cycles and real-time shadows produce dark artifacts at vessel terminations, and boolean operations or subdivision modifiers fail unpredictably on open meshes.

### 2.3 Interior Anatomy Inaccessibility & Occlusion
In multiple assets designed to teach internal physiological pathways:
1. **Heart:** The model is a solid exterior shell. NCERT Class 10 and 11 explicitly teach double circulation through a **coronal section** revealing the 4 internal chambers, the interatrial and interventricular septa, the tricuspid and bicuspid valves, and papillary muscles with chordae tendineae.
2. **Respiratory System:** The lungs are modeled as solid opaque meshes (`lung-tissue`), completely occluding the internal bronchial tree and lobar branches beneath them.
3. **Excretory System:** The kidneys are solid outer bean shapes. The internal renal pyramids, cortex, medulla, minor/major calyces, and renal pelvis are entirely missing despite being promised in `asset.json` ("Internal renal pyramid structures visible on cutaway profile").
4. **Eye:** The cutaway boolean cuts through solid UV spheres, creating flat slicing planes instead of revealing hollow chambers (anterior/posterior cavities) and natural layered coats.

### 2.4 PBR Shading & Material Gaps
1. **Absence of Subsurface Scattering (SSS):** Biological tissues (cardiac muscle, lung parenchyma, renal cortex, liver, brain gray matter) have significant optical transradiancy. Currently, all materials in `build_*.py` are created using simple `kit.add_material(name, color, metallic=0.04, roughness=0.3-0.6)` without SSS. They appear like polished latex rubber or painted plastic rather than organic living tissue.
2. **Unused Defined Materials:** 
   - In `build_eye.py`, `choroid_mat` and `vitreous_mat` are defined at lines 19 and 24, but are **never attached to any object**.
   - In `human-heart/asset.json`, `heart-valve` is declared, but never instantiated in `build_heart.py`.
3. **Design Token Decoupling & Color Conflicts:**
   - In `visual/design-tokens.json`, `dnaBaseAdenine` is `#22c55e` (Green) and `dnaBaseThymine` is `#ef4444` (Red).
   - In `dna-double-helix/build_dna.py`, Adenine is Red (`0.85, 0.20, 0.20`) and Thymine is Yellow (`0.90, 0.85, 0.20`).
   - In `dna-double-helix/asset.json`, materials are described as `orange backbone`, `red AT pairs`, `blue GC pairs`.
   - In `neuron/asset.json`, material IDs are `yellow soma`, `blue axon`, `white myelin`, whereas in `build_neuron.py` they are `neuron-soma`, `neuron-axon`, `neuron-myelin`.

---

## 3. Granular System-by-System Benchmark Audits

### 3.1 Human Heart (`human-heart`)

- **NCERT Benchmark:** Class 10 Ch 5 Section 5.4.1 (Fig 5.10 "Schematic sectional view of the human heart"); Class 11 Ch 18 Section 18.3.1 (Fig 18.2 "Section of a human heart").
- **Asset Path:** `assets/biology/human-heart/` (`build_heart.py`, `asset.json`, `out/human-heart.blend`, `out/human-heart.glb`).
- **Observed Geometry:** 23 objects, 31,172 vertices, 31,192 faces, 508 non-manifold edges.

#### Discrepancies & Flaws:
1. **No Internal Cavities or Septal Division:** `build_heart.py` line 48 implements `create_ventricular_mass()`, which builds a single solid exterior lofted cone. There are no right and left ventricular chambers, no inter-ventricular septum, and no inter-atrial septum. In NCERT Class 10/11, the separation of the right (deoxygenated) and left (oxygenated) sides by the septum is the primary pedagogical takeaway of double circulation.
2. **Missing Valves & Subvalvular Apparatus:** The Tricuspid valve (right AV), Bicuspid/Mitral valve (left AV), Aortic semilunar valve, and Pulmonary semilunar valve are completely absent. Chordae tendineae and papillary muscles are not modeled.
3. **Great Vessel Connections:**
   - The Pulmonary Trunk correctly emerges anterior to the aorta from the RV base (lines 187–195), which is scientifically sound.
   - However, the vessels end abruptly with open circular holes (508 non-manifold edges total).
   - The right and left pulmonary veins (4 vessels total) terminate as open stumps intersecting the atrium walls with no ostia/openings into the left atrial lumen.
4. **Auricles:** Modeled as crude scaled UV spheres (`ra_auricle`, `la_auricle`, lines 162–182) rather than scalloped, pectinate muscular ear-like flaps.
5. **Myocardial Material:** Uniform dark crimson (`heart-myocardium`) with roughness 0.28, metallic 0.04. Lacks subsurface scattering, fibrous muscle grain, and natural coronary sulcus fat integration.

---

### 3.2 Human Eye (`human-eye`)

- **NCERT Benchmark:** Class 10 Ch 11 Section 11.1 (Fig 11.1 "The human eye"); Class 11 Ch 21 Section 21.6.1 (Fig 21.6 "Diagram showing parts of an eye").
- **Asset Path:** `assets/biology/human-eye/` (`build_eye.py`, `asset.json`).
- **Observed Geometry:** 9 objects, 4,956 vertices, 5,306 faces.

#### Discrepancies & Flaws:
1. **Missing Middle Layer (Choroid):** The eye has 3 fundamental tunics: Sclera (outer), Choroid (middle vascular), and Retina (inner sensory). In `build_eye.py` line 19, `choroid_mat` is created, but **no choroid geometry is instantiated**. The model jumps directly from sclera to retina.
2. **Missing Vitreous Body & Aqueous Humor:** `vitreous_mat` is defined at line 24, but no vitreous body exists. The internal eye is completely hollow air behind the lens. The anterior chamber (aqueous humor between cornea and lens) is also absent.
3. **Pupil is a Solid Plastic Disc:** Line 60 models the pupil as a solid black cylinder (`size=(0.009, 0.009, 0.0025)`). Anatomically and pedagogically, the pupil is a **circular aperture (hole)** in the iris diaphragm through which light passes to reach the lens. Representing it as a physical black token is an anatomical misconception.
4. **Suspensory Ligaments (Zonules of Zinn):** The ciliary body is represented only as a solid flat cylinder ring (`ciliary_ring`, line 82). The radial suspensory ligaments that attach the ciliary processes to the lens equator (crucial for accommodation in Class 10 Physics/Biology) are omitted.
5. **Solid Boolean Cutaway Artifacts:** Lines 109–120 apply an exact boolean difference against solid UV spheres. The resulting cut faces are solid cross-sectional discs that block the natural lumen of the eyeball.
6. **Optical Parameters:** The crystalline lens is modeled as a biconvex lathe with IOR 1.406, and cornea with IOR 1.376. These refractive index values are physically correct, but without aqueous and vitreous humors, ray-tracing through the optical axis fails.

---

### 3.3 Human Brain (`brain`)

- **NCERT Benchmark:** Class 10 Ch 7 Section 7.1.2 (Fig 7.3 "Human brain"); Class 11 Ch 21 Section 21.4 (Fig 21.4 "Diagrammatic presentation of the human brain - Sagittal section").
- **Asset Path:** `assets/biology/brain/` (`build_brain.py`, `asset.json`).
- **Observed Geometry:** 10 objects, 9,338 vertices, 9,798 faces.

#### Discrepancies & Flaws:
1. **Complete Absence of Gyri and Sulci:** The cerebral cortex is modeled as an undeformed UV sphere (`size=(0.076, 0.054, 0.050)`, scaled `1.2, 0.85, 0.80`). It has a completely smooth, mirror-like surface. The cerebral convolutions (gyri ridges, sulci furrows) and the 4 anatomical lobes (Frontal, Parietal, Temporal, Occipital) described in NCERT and `asset.json` do not exist.
2. **Cerebellum Lacks Folia & Arbor Vitae:** The cerebellum is modeled as a smooth UV sphere (`size=(0.036, 0.032, 0.028)`). It completely lacks the characteristic horizontal folia folds and internal white-matter branching pattern (*arbor vitae*) that defines hindbrain anatomy.
3. **Corpus Callosum is a Straight Cylinder:** Line 44 models the corpus callosum as a straight cylinder rotated 0.25 radians. Anatomically, the corpus callosum is a prominent C-shaped commissural arch (genu, body, splenium) bridging the cerebral hemispheres above the lateral ventricles.
4. **Hypothalamus is a Cube:** Line 57 models the hypothalamus as a literal cube (`cube`, `size=(0.012, 0.008, 0.008)`).
5. **Missing Anatomical Structures:**
   - **Midbrain:** Completely absent (no cerebral peduncles, no corpora quadrigemina / optic colliculi).
   - **Ventricular System:** Lateral, third, and fourth ventricles are completely absent.
   - **Cerebral Aqueduct (Aqueduct of Sylvius):** Absent.
   - **Meninges & Cranium:** Dura mater, arachnoid, and cranial vault outline are omitted.

---

### 3.4 Nephron (`nephron`)

- **NCERT Benchmark:** Class 10 Ch 5 Section 5.4.2 (Fig 5.14 "Structure of a nephron"); Class 11 Ch 19 Section 19.1 (Fig 19.3 "A diagrammatic representation of a nephron showing blood vessels, duct and tubule").
- **Asset Path:** `assets/biology/nephron/` (`build_nephron.py`, `asset.json`).
- **Observed Geometry:** 20 objects, 46,962 vertices, 46,720 faces, 576 non-manifold edges.

#### Discrepancies & Flaws:
1. **Disconnected Open Tubule Mesh Segments:** Every anatomical region of the nephric tubule (`pct`, `henle_desc`, `henle_turn`, `henle_asc`, `dct`, `collecting-duct`, and capillaries) is an independent mesh object converted from an open curve. At every junction, there are open tube ends with non-manifold edges (576 total).
2. **Absence of Juxtaglomerular Apparatus (JGA) Contact:** In NCERT Class 11, the ascending limb/DCT must pass in direct contact between the afferent and efferent arterioles at the vascular pole of Bowman's capsule (forming the macula densa and JG cells, responsible for renin release). In `build_nephron.py`, the DCT looping is offset into free space without contacting the vascular pole.
3. **Missing Corticomedullary Boundary:** The nephron diagram in NCERT specifically illustrates the boundary between the Renal Cortex (containing Bowman's capsule, PCT, DCT) and the Renal Medulla (containing Loop of Henle, collecting duct, vasa recta). The 3D model lacks any demarcation plane, background stratum, or color distinction.
4. **Metadata Desynchronization:** `asset.json` line 16 claims `"Peritubular capillary net omitted to highlight the primary renal nephric tubule pathway."` However, lines 222–280 of `build_nephron.py` *do* include a peritubular capillary network and vasa recta. The metadata contradicts the implementation.

---

### 3.5 Human Respiratory System (`human-respiratory-system`)

- **NCERT Benchmark:** Class 10 Ch 5 Section 5.2.2 (Fig 5.9 "Human respiratory system"); Class 11 Ch 17 Section 17.1 (Fig 17.1 "Diagrammatic view of human respiratory system").
- **Asset Path:** `assets/biology/human-respiratory-system/` (`build_respiratory.py`, `asset.json`).
- **Observed Geometry:** 37 objects, 43,702 vertices, 44,772 faces, 280 non-manifold edges.

#### Discrepancies & Flaws:
1. **Lungs Occlude Internal Bronchial Tree:** Both lungs (`lung-right` and `lung-left`) are solid, opaque lofted meshes. When rendered or exported to GLB, the primary bronchi, secondary lobar bronchi, and bronchioles inside are completely invisible unless the lung objects are manually hidden in a 3D viewer.
2. **Closed O-Rings Instead of C-Shaped Rings:** Line 226 creates 7 tracheal rings as complete, closed cylinders (`cylinder`, `size=(0.0185, 0.018, 0.004)`). Anatomically and in NCERT, tracheal rings are strictly **C-shaped cartilages**, open posteriorly where the smooth trachealis muscle abuts the esophagus to permit swallowing.
3. **Floating Surface Fissures:** Interlobar fissures (oblique on left, oblique + horizontal on right) are modeled as separate 3D tubes floating on the exterior surface of the lung mesh (lines 121–146) with 28 non-manifold edges each, rather than natural anatomical clefts between distinct lobes.
4. **Larynx Primitives:** Thyroid cartilage is a plain cube (`cube`, line 194), Adam's prominence is an unblended cone (line 199), and epiglottis is an unyielding block.
5. **Alveoli Inset Proportions:** The alveolar sac cluster is located at `(0.090, -0.032, 0.040)` directly adjacent to the macroscopic lungs without an inset framing boundary. The capillary network is approximated by two flat tilted cylinders intersecting the spheres rather than an anastomosing plexus.

---

### 3.6 Human Digestive System (`digestive-system`)

- **NCERT Benchmark:** Class 10 Ch 5 Section 5.1.2 (Fig 5.6 "Human alimentary canal"); Class 11 Ch 16 Section 16.1 (Fig 16.1 "The human digestive system", Fig 16.2 "Regions of stomach", Fig 16.3 "Duct systems of liver, gallbladder and pancreas").
- **Asset Path:** `assets/biology/digestive-system/` (`build_digestive.py`, `asset.json`).
- **Observed Geometry:** 25 objects, 18,088 vertices, 19,398 faces.

#### Discrepancies & Flaws:
1. **Small Intestine is 7 Disconnected Spheres:** Lines 90–100 model the 6-meter human small intestine (jejunum and ileum) as 7 discrete, disconnected UV spheres (`small-int-0` through `small-int-6`) hovering in space. This completely abandons anatomical reality and topological continuity.
2. **Colon is 5 Disconnected Rigid Cylinders:** Ascending colon, transverse colon, descending colon, and sigmoid colon are discrete, isolated cylinders intersecting at 90-degree angles without haustrations (sacculations), teniae coli, or continuous lumen.
3. **Stomach is 3 Intersecting Shapes:** Fundus is a sphere, body is a cylinder, pylorus is a cylinder (lines 46–57). It lacks a continuous J-shaped contour, greater/lesser curvatures, and gastric rugae.
4. **Liver is a Rounded Cube:** Line 60 creates the liver as a `cube` with a subdivision modifier. It lacks the falciform ligament dividing right and left lobes, inferior gallbladder fossa, and inferior vena cava groove.
5. **Missing Hepatopancreatic Duct System:**
   - Gallbladder is an isolated sphere with no cystic duct.
   - Liver has no hepatic ducts.
   - Pancreas is a plain cylinder (line 77) with no pancreatic duct (Duct of Wirsung).
   - In NCERT Class 10 and 11, the convergence of the bile duct and pancreatic duct into the **hepatopancreatic ampulla (Ampulla of Vater)** guarded by the **Sphincter of Oddi** entering the duodenal C-loop is the central biochemical concept of lipid and protein digestion. Here, no ducts exist.

---

### 3.7 Human Excretory System (`human-excretory-system`)

- **NCERT Benchmark:** Class 10 Ch 5 Fig 5.13 ("Excretory system in human beings"); Class 11 Ch 19 Fig 19.1 ("Human Urinary system"), Fig 19.2 ("Longitudinal section of kidney").
- **Asset Path:** `assets/biology/human-excretory-system/` (`build_excretory.py`, `asset.json`).
- **Observed Geometry:** 17 objects, 26,474 vertices, 26,928 faces, 168 non-manifold edges.

#### Discrepancies & Flaws:
1. **Missing Internal Renal Pyramids & Calyces:** Although `asset.json` states that internal pyramids are visible on cutaway, both kidneys (`kidney-right`, `kidney-left`) are closed solid bean meshes. There is no longitudinal section revealing the renal cortex, medullary pyramids, renal papillae, and calyces.
2. **Aorta & Vena Cava Abrupt Terminations:** Modeled as straight vertical cylinders terminating at `z = 0.130 +/- 0.090` without common iliac artery and vein bifurcations (which are prominently featured in NCERT Class 10 Fig 5.13).
3. **Ureter Insertion into Bladder:** The ureters terminate at the superior dome of the bladder rather than entering posterolaterally through the bladder wall to form the trigone.
4. **Open Vessels:** 6 renal vessel and ureter tubes have uncapped open ends (168 non-manifold edges).

---

### 3.8 Neuron (`neuron`)

- **NCERT Benchmark:** Class 10 Ch 7 Fig 7.1 ("Structure of neuron"); Class 11 Ch 21 Fig 21.1 ("Structure of a neuron").
- **Asset Path:** `assets/biology/neuron/` (`build_neuron.py`, `asset.json`).
- **Observed Geometry:** 33 objects, 21,970 vertices, 23,808 faces.

#### Discrepancies & Flaws:
1. **Myelin Sheath Modeled as Spherical Beads:** Lines 107–115 generate 6 rounded `uv_sphere` meshes along the axon. Anatomically, myelin sheaths are cylindrical concentric Schwann cell wrappings with flattened Schwann cell nuclei.
2. **Rigid Stick Dendrites:** Primary and secondary dendrites are rigid straight cylinders oriented via quaternion math. They lack organic curvature, tapering, and dendritic spines.
3. **Missing Nissl's Granules:** NCERT Class 10 and 11 diagrams clearly highlight Nissl's granules (ribosome clumps) across the soma and dendrite bases.
4. **Metadata Desynchronization:** `asset.json` lists draft materials with spaces (`"yellow soma"`, `"blue axon"`, `"white myelin"`), while `build_neuron.py` creates `neuron-soma`, `neuron-axon`, `neuron-myelin`.

---

### 3.9 Reflex Arc (`reflex-arc`)

- **NCERT Benchmark:** Class 10 Ch 7 Fig 7.2 ("Reflex arc").
- **Asset Path:** `assets/biology/reflex-arc/` (`build_reflex_arc.py`, `asset.json`).
- **Observed Geometry:** 15 objects, 5,664 vertices, 6,354 faces.

#### Discrepancies & Flaws:
1. **Cubical Gray Matter Wings:** Line 52 models the iconic butterfly-shaped spinal gray matter as two rectangular prisms (`cube`, `size=(0.018, 0.041, 0.028)`). It lacks distinct dorsal horns, ventral horns, central canal, and anterior median fissure.
2. **Segmented Jagged Nerve Pathways:** Sensory and motor pathways are constructed from series of segmented straight cylinders rather than continuous smooth spline curves.
3. **Missing Ascending Pathway to Brain:** NCERT Fig 7.2 explicitly highlights the "Message to brain" relay branch extending superiorly from the spinal cord interneuron.

---

### 3.10 Stomatal Apparatus (`stoma`)

- **NCERT Benchmark:** Class 10 Ch 5 Fig 5.3 ("(a) Open and (b) closed stomatal pore"); Class 11 Ch 6 Fig 6.4 ("Diagrammatic representation of stomatal apparatus").
- **Asset Path:** `assets/biology/stoma/` (`build_stoma.py`, `asset.json`).
- **Observed Geometry:** 32 objects, 37,648 vertices, 38,228 faces, 64 non-manifold edges.

#### Discrepancies & Flaws:
1. **Single Static State (Open Only):** NCERT teaches the stomatal mechanism through the direct visual comparison of an **Open Pore** (turgid guard cells, curved apart) and a **Closed Pore** (flaccid guard cells, straight inner walls in contact). Only the open state is implemented.
2. **Inner Wall as Floating Tube:** The thickened inner cellulosic wall is a separate floating curved tube overlaying the guard cell (lines 181–208), with 32 non-manifold edges per cell, rather than an integrated thickening of the bmesh wall.

---

### 3.11 Flower Anatomy (`flower-anatomy`)

- **NCERT Benchmark:** Class 10 Ch 8 Fig 8.7 ("Longitudinal section of flower"); Class 12 Ch 2 Fig 2.1, 2.3, 2.7 ("Parts of a typical angiosperm flower").
- **Asset Path:** `assets/biology/flower-anatomy/` (`build_flower_anatomy.py`, `asset.json`).
- **Observed Geometry:** 20 objects, 15,224 vertices, 15,584 faces.

#### Discrepancies & Flaws:
1. **Solid Ovary Wall Enclosing Ovules:** The ovary is a solid UV sphere (line 50) and the ovules are solid UV spheres inside it without an interior locule cavity.
2. **Anthers Lack Bilobed / Dithecous Morphology:** Anthers are modeled as single UV spheres rather than bilobed structures with four microsporangia and pollen sacs (core Class 12 benchmark).
3. **Flat Sphere Petals:** Petals are 3 flattened UV spheres (`size=(0.045, 0.010, 0.085)`) rather than curved, delicate petaloid sheets with realistic venation and margins.

---

### 3.12 DNA Double Helix (`dna-double-helix`)

- **NCERT Benchmark:** Class 11 Ch 9 Fig 9.5; Class 12 Ch 6 Fig 6.2, 6.3 ("Double stranded polynucleotide chain and double helix").
- **Asset Path:** `assets/biology/dna-double-helix/` (`build_dna.py`, `asset.json`).
- **Observed Geometry:** 30 objects, 1,930 vertices, 1,488 faces, 80 non-manifold elements.

#### Discrepancies & Flaws:
1. **CRITICAL GEOMETRIC BUG — Vertical Rungs:**
   - In `build_dna.py` lines 78–85:
     ```python
     p_a = kit.primitive_object(..., "cylinder", size=(0.0018, 0.0018, length / 2),
                               location=(mx - dx/4, y, mz - dz/4),
                               rotation_euler=(0.0, 0.0, angle))
     ```
   - A Blender cylinder primitive is oriented along the **Z-axis** by default.
   - The helix axis extends along the **Y-axis**, and the base pairs lie in the **X-Z plane**.
   - Rotating around Z (`rotation_euler=(0.0, 0.0, angle)`) rotates in the X-Y plane, leaving the cylinder standing straight UP along the Z-axis.
   - **Result:** The base pairs do NOT connect the two strands horizontally; they stick up vertically like loose rungs.
2. **Unapplied Skin Modifier & Non-Manifold Wireframe:**
   - Lines 48–51 add a `SKIN` modifier to a 1D vertex-edge polyline, but never apply it.
   - The mesh data in the `.blend` file contains 40 edges and 41 vertices with 0 faces (80 non-manifold elements).
3. **No Major / Minor Grooves:** Strands are separated by exactly $\pi$ (180 degrees), producing symmetric grooves. Natural B-DNA has a distinct Major Groove (2.2 nm) and Minor Groove (1.2 nm).
4. **Hydrogen Bonding Representation:** Watson-Crick base pairing specifies 2 hydrogen bonds between A=T and 3 hydrogen bonds between G≡C. The model uses solid rungs with no indication of hydrogen bonds.

---

### 3.13 Trophic Level Pyramid (`trophic-level-pyramid`)

- **NCERT Benchmark:** Class 10 Ch 15 Fig 15.2; Class 12 Ch 14 Fig 14.4 ("Pyramid of energy").
- **Asset Path:** `assets/biology/trophic-level-pyramid/` (`build_trophic_pyramid.py`, `asset.json`).
- **Observed Geometry:** 10 objects, 260 vertices, 368 faces.

#### Discrepancies & Flaws:
1. **Degenerate Arrowhead Dimension:** Line 51 specifies `size=(0.012, 0.0, 0.018)`. A Y-dimension of `0.0` creates a degenerate flattened cone mesh.
2. **Missing 3D Text Labels:** `asset.json` claims energy values (10,000 J, 1,000 J, 100 J, 10 J) are labeled. No 3D text or textures exist on the model.

---

## 4. Topology & Geometry Defect Inventory

The table below catalogs specific topological and geometric errors identified via automated inspection of the `.blend` and `.glb` files:

| Asset | Object Name | Defect Type | Severity | Impact |
|---|---|---|---|---|
| `dna-double-helix` | `backbone-0`, `backbone-1` | Unapplied `skin` modifier; 1D wireframe with 0 faces | **Critical** | Corrupts geometry; 80 non-manifold edges/verts |
| `dna-double-helix` | `pair-*-a`, `pair-*-b` | Cylinder Z-axis not transformed to horizontal X-Z plane | **Critical** | Rungs point vertically; disconnected from helix |
| `trophic-level-pyramid` | `arrow-head` | Dimension Y = `0.0` | **Major** | Degenerate cone mesh; zero thickness polygon |
| `human-heart` | Great vessels & coronaries (16 objs) | Curve bevel converted with open ends | **Major** | 508 non-manifold open boundary edges |
| `nephron` | Tubules, Henle loops, vessels (18 objs) | Curve bevel converted with open ends | **Major** | 576 non-manifold open boundary edges |
| `human-respiratory-system` | Bronchi & fissures (10 objs) | Curve bevel converted with open ends | **Major** | 280 non-manifold open boundary edges |
| `human-excretory-system` | Renal vessels & ureters (6 objs) | Curve bevel converted with open ends | **Major** | 168 non-manifold open boundary edges |
| `stoma` | `inner-wall-left`, `inner-wall-right` | Open curve bevel | **Moderate** | 64 non-manifold open boundary edges |
| `human-eye` | `sclera`, `retina` | Boolean cutaway on solid spheres | **Major** | Solid intersecting cut planes; non-hollow vitreal cavity |
| `digestive-system` | `small-int-0` to `small-int-6` | Disconnected floating UV spheres | **Critical** | Total failure of anatomical continuity |
| `brain` | `cerebrum`, `cortex`, `cerebellum` | Scaled UV spheres with no surface displacement | **Critical** | Complete absence of gyri, sulci, and folia |

---

## 5. Material, Shader & Design Token Harmonization Plan

### 5.1 Subsurface Scattering (SSS) Upgrade Requirements
Biological tissue exhibits internal light scattering. `edu_asset_kit.py` must be upgraded to support SSS configuration on Principled BSDF nodes:
- `Subsurface Weight`: 0.15–0.35 for vascular tissue, 0.40–0.60 for organ parenchyma.
- `Subsurface Radius`: Red-shifted scatter coefficients `(1.0, 0.2, 0.1)` for blood-rich organs (Heart myocardium, Kidney cortex, Liver, Lungs).
- `Subsurface IOR`: 1.40 for biological soft tissue.

### 5.2 Token Additions for `visual/design-tokens.json`
The following new material definitions must be registered in `visual/design-tokens.json` under `"materials"`:
```json
{
  "tissue_lung_parenchyma": {
    "baseColor": "#8a2432",
    "metallic": 0.04,
    "roughness": 0.35,
    "subsurface": 0.25
  },
  "tissue_kidney_cortex": {
    "baseColor": "#541212",
    "metallic": 0.04,
    "roughness": 0.32,
    "subsurface": 0.20
  },
  "tissue_liver_hepatic": {
    "baseColor": "#4a1c14",
    "metallic": 0.04,
    "roughness": 0.40,
    "subsurface": 0.18
  },
  "tissue_brain_gray_matter": {
    "baseColor": "#c49286",
    "metallic": 0.04,
    "roughness": 0.55,
    "subsurface": 0.30
  },
  "tissue_hyaline_cartilage": {
    "baseColor": "#d4ded4",
    "metallic": 0.02,
    "roughness": 0.28,
    "subsurface": 0.35
  }
}
```

### 5.3 Harmonization of DNA Base Colors
Standardize across `design-tokens.json`, `build_dna.py`, and `asset.json`:
- **Adenine (A):** Green (`#22c55e`, `(0.13, 0.77, 0.37)`)
- **Thymine (T):** Red (`#ef4444`, `(0.94, 0.27, 0.27)`)
- **Guanine (G):** Yellow/Amber (`#f59e0b`, `(0.96, 0.62, 0.04)`)
- **Cytosine (C):** Blue (`#3b82f6`, `(0.23, 0.51, 0.96)`)

---

## 6. Prioritized Action Plan & Implementation Recommendations

### Tier 1: Core Pedagogical Systems (Immediate Implementation)
1. **Heart (`human-heart`):**
   - Provide a coronal cutaway option revealing the **4 distinct internal chambers** (RA, LA, RV, LV).
   - Model the muscular interventricular septum and interatrial septum.
   - Add bicuspid, tricuspid, and semilunar valve leaflets.
   - Cap vessel terminations with smooth convex hemispherical or flanged caps to eliminate 508 non-manifold edges.
   - Apply Subsurface Scattering to myocardium shader.

2. **Eye (`human-eye`):**
   - Insert the **choroid layer** between sclera and retina.
   - Add the **vitreous body** (refractive transparent volume filling posterior cavity).
   - Re-model the pupil as an **actual aperture / opening** in the iris disc.
   - Add suspensory zonule fibers connecting ciliary body to lens equator.
   - Model anterior chamber with aqueous humor.

3. **Brain (`brain`):**
   - Apply procedural displacement (Voronoi / Musgrave noise texture mapped onto cortex bmesh) to sculpt realistic **gyri ridges and sulci grooves**.
   - Delineate the 4 lobes (frontal, parietal, temporal, occipital).
   - Re-model corpus callosum as an authentic C-shaped commissure arch.
   - Add cerebellar folia and *arbor vitae* cross-sectional pattern.
   - Add midbrain (cerebral peduncles and colliculi).

4. **Digestive System (`digestive-system`):**
   - Replace the 7 disconnected spheres with a **continuous looping tubular curve** representing the jejunum and ileum.
   - Connect esophagus, stomach, duodenum, small intestine, caecum, colon, and rectum into a continuous gastrointestinal pathway.
   - Add pancreatic and common bile ducts converging at the duodenal loop (Ampulla of Vater).
   - Add haustrations to the colon.

5. **Respiratory System (`human-respiratory-system`):**
   - Provide a cutaway or transparent mode for the lungs so the bronchial tree and lobar branches are clearly visible.
   - Change tracheal rings from full closed cylinders to **C-shaped cartilages** open posteriorly.
   - Carve interlobar fissures directly into the lung geometry rather than floating surface tubes.

6. **Nephron (`nephron`):**
   - Join/weld adjacent tubule segments to eliminate 576 non-manifold boundary edges.
   - Position DCT in direct anatomical contact with the vascular pole of Bowman's capsule (macula densa / JGA).
   - Add a subtle background plane or material gradient distinguishing the Renal Cortex from the Renal Medulla.

### Tier 2: Physical & Neurological Units (High Priority)
7. **DNA Double Helix (`dna-double-helix`):**
   - Fix the rung orientation math: orient base pairs in the horizontal X-Z plane connecting the two helical backbone strands.
   - Apply the `skin` modifier to eliminate the 80 non-manifold wireframe elements.
   - Adjust strand angular offset to ~120°/240° to introduce realistic Major and Minor Grooves.
   - Synchronize base pair colors with `design-tokens.json`.

8. **Reflex Arc (`reflex-arc`):**
   - Re-model spinal gray matter with an authentic butterfly contour (dorsal and ventral horns).
   - Convert segmented jagged cylinders into smooth Bezier spline nerve tracts.
   - Add the ascending nerve branch signaling to the brain.

9. **Neuron (`neuron`):**
   - Replace spherical myelin beads with cylindrical Schwann cell segments featuring Nodes of Ranvier.
   - Introduce subtle organic branching and curvature to dendrites.
   - Add Nissl granule texturing to soma.

### Tier 3: Environmental & Botanical Assets (Medium Priority)
10. **Stoma (`stoma`):**
    - Support dual state generation: Open Pore vs Closed Pore.
    - Integrate inner wall thickening directly into guard cell bmesh.
11. **Flower Anatomy (`flower-anatomy`):**
    - Carve open the ovary to reveal an authentic locule chamber enclosing ovules.
    - Model anthers with bilobed / dithecous morphology.
12. **Trophic Level Pyramid (`trophic-level-pyramid`):**
    - Fix the degenerate zero-thickness arrow head cone (`size=(0.012, 0.012, 0.018)`).
    - Add 3D text objects or embossed tier labels for 10,000 J, 1,000 J, 100 J, and 10 J.
