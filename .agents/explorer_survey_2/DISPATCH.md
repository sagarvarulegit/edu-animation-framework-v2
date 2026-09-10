# Explorer Survey 2 Dispatch

## Mission: Chemistry & Physics Assets Survey & Audit
You are Explorer 2. Your task is to investigate existing Chemistry and Physics 3D models and apparatus in `edu-animation-framework-v2/assets/chemistry/` and `assets/physics/` against CBSE/NCERT Class 9-12 curriculum and physical/chemical benchmarks.

### Working Directory
`/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2`

### Authoritative Context
- Read `/home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md`
- Read `/home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md`

### Scope & Tasks
1. Inspect all asset directories under `assets/chemistry/` (e.g. magnesium, oxygen, magnesium-oxide, burner, test-tube, flask, beaker, etc.) and `assets/physics/` (e.g. battery, resistor, bulb, prism, lens, mirror, circuit apparatus, etc.).
2. Examine their `asset.json`, `build_*.py` procedural generation scripts, and outputs (`out/*.blend`, `out/*.glb`, `out/preview.png`).
3. Benchmark against NCERT Class 9-12 Science/Chemistry/Physics:
   - Laboratory apparatus: realistic dimensions, wall thickness, meniscus for liquids, proper burner flame zones, correct clamps/stands.
   - Molecular models: ball-and-stick or space-filling consistency, CPK coloring rules, bond angles and valencies (e.g. O2 double bond, MgO crystal lattice or ionic pair), documented scale conventions.
   - Physics apparatus: accurate circuit components (symbols vs 3D components, terminal polarities), optical components (refraction index, curvature, glass transmission).
4. Identify discrepancies, missing components, physical inaccuracies, unrealistic materials/shaders, and procedural generation issues.
5. Write your complete findings to `/home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/survey_chem_phys.md` and complete `handoff.md`.

## 2026-09-09T02:49:25Z
You are the Chemistry & Physics Asset Auditor. Read your dispatch instructions at /home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/DISPATCH.md, as well as /home/sagarv/Projects/edu-animation-framework-v2/.agents/ORIGINAL_REQUEST.md and /home/sagarv/Projects/edu-animation-framework-v2/AGENTS.md.
Investigate all existing 3D models and procedural scripts in assets/chemistry/ and assets/physics/. Audit them against NCERT Class 9-12 benchmarks (apparatus, molecules, optics, circuits).
Document all discrepancies, missing features, geometry errors, and shader needs (realistic glass, metals, flames, liquids).
Write your detailed report to /home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/survey_chem_phys.md and write /home/sagarv/Projects/edu-animation-framework-v2/.agents/explorer_survey_2/handoff.md.
Update progress.md in your directory as you work.
When complete, send a message back with your findings.
