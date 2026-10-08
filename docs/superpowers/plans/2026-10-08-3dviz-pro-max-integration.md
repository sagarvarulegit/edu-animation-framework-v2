# 3dviz-pro-max Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate the `3dviz-pro-max` 3D visualization skill, headless frame capture verification harness, and authoritative science knowledge into `edu-animation-framework-v2`.

**Architecture:** Install the skill in `.agents/skills/3dviz-pro-max`, adapt cross-platform Python CLI scripts for Windows, port Playwright-based headless frame capture into `tools/`, and mine domain knowledge records (molecular crystal lattices, ray optics, and PBR laboratory lighting) into framework OKF concepts and design tokens.

**Tech Stack:** Python 3.x, Three.js, Playwright / Chromium, Node.js, JSON Schema, Open Knowledge Format (OKF v0.2).

**Spec:** [`docs/superpowers/specs/2026-10-07-3dviz-pro-max-integration-design.md`](../specs/2026-10-07-3dviz-pro-max-integration-design.md)

## Global Constraints

- Keep existing schemas in `schemas/` backward-compatible.
- `node tools/validate.mjs` must pass with 0 errors across all 57 assets and 44 OKF concepts.
- Python scripts must use `pathlib.Path` with POSIX-safe handling for Windows PowerShell compatibility.
- Adhere to Git commit & push discipline: frequent commits and pushes to `origin/master`.

## Review Focus

1. Windows path separator issues (`\` vs `/`) when `search.py` or `resolve.py` resolves JSON data records.
2. Missing Playwright browser binaries when executing headless capture on Windows.
3. Angle backend compatibility (`--use-angle=d3d11`) when capturing WebGL frames on Windows.
4. Schema mismatch if new OKF concepts or tokens omit mandatory fields.
5. Accidental overwriting of existing `.agents/skills/cbse-science-shorts/` or working Blender assets.

---

### Task 1: Populate `.agents/skills/3dviz-pro-max`

**Files:**
- Create: `.agents/skills/3dviz-pro-max/SKILL.md`
- Create: `.agents/skills/3dviz-pro-max/data/` (all records and catalog-summary.json)
- Create: `.agents/skills/3dviz-pro-max/references/` (guides and notes)
- Create: `.agents/skills/3dviz-pro-max/scripts/` (python CLI helpers)

**Interfaces:**
- Consumes: Raw repository assets from `https://github.com/viettranx/3dviz-pro-max`.
- Produces: Complete skill directory in `.agents/skills/3dviz-pro-max/`.

- [ ] **Step 1: Clone or fetch repository contents to temporary scratch directory**
  Download or clone the `viettranx/3dviz-pro-max` repository into a local scratch directory (`.scratch/3dviz-pro-max` or shallow git clone).

- [ ] **Step 2: Copy skills/3dviz-pro-max contents to .agents/skills/3dviz-pro-max**
  Copy `SKILL.md`, `data/`, `scripts/`, and `references/` into `.agents/skills/3dviz-pro-max/`.

- [ ] **Step 3: Clean up scratch directory**
  Remove temporary clone directory.

- [ ] **Step 4: Verify directory integrity**
  Confirm `.agents/skills/3dviz-pro-max/SKILL.md` and `.agents/skills/3dviz-pro-max/data/catalog-summary.json` exist and are readable.

- [ ] **Step 5: Commit and push**
  ```bash
  git add .agents/skills/3dviz-pro-max/
  git commit -m "feat(skills): install 3dviz-pro-max skill and knowledge base"
  git push origin master
  ```

---

### Task 2: Validate & Adapt Python CLIs for Windows

**Files:**
- Modify: `.agents/skills/3dviz-pro-max/scripts/search.py`
- Modify: `.agents/skills/3dviz-pro-max/scripts/resolve.py`
- Modify: `.agents/skills/3dviz-pro-max/scripts/design-context.py`
- Modify: `.agents/skills/3dviz-pro-max/scripts/host-probe.py`
- Test: Run search and resolve CLI tests via PowerShell

**Interfaces:**
- Consumes: Python 3 runtime on Windows.
- Produces: Functional CLI outputs for `search.py` and `resolve.py`.

- [ ] **Step 1: Test `search.py` on Windows**
  Run: `python .agents/skills/3dviz-pro-max/scripts/search.py "crystal lattice"`
  Verify stdout returns matching records without path encoding or syntax crashes.

- [ ] **Step 2: Test `resolve.py` on Windows**
  Run: `python .agents/skills/3dviz-pro-max/scripts/resolve.py <record-id>` on a discovered record.
  Verify record metadata and defaults are displayed properly.

- [ ] **Step 3: Test `host-probe.py` on Windows**
  Run: `python .agents/skills/3dviz-pro-max/scripts/host-probe.py`
  Verify it detects Blender 5.2 at `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe` and reports system GPU.

- [ ] **Step 4: Commit any path or encoding fixes**
  ```bash
  git add .agents/skills/3dviz-pro-max/scripts/
  git commit -m "fix(skills): ensure 3dviz-pro-max scripts run cleanly on Windows"
  git push origin master
  ```

---

### Task 3: Port Headless Frame Capture & View-Quality Harness

**Files:**
- Create: `tools/capture.py`
- Create: `tools/capture_view_quality.py`
- Modify: `tools/capture_viewport.mjs` (provide cross-platform browser discovery or defer to `capture.py`)

**Interfaces:**
- Consumes: Playwright / Chromium with ANGLE backend.
- Produces: PNG screenshots in target directory and `capture-log.json` with contrast and luminance quality metrics.

- [ ] **Step 1: Install Playwright Python package if not present**
  Check `python -c "import playwright"` and install/ensure chromium driver is available.

- [ ] **Step 2: Copy and configure `capture.py` and `capture_view_quality.py` into `tools/`**
  Set default `--use-angle=d3d11` for Windows platform execution.

- [ ] **Step 3: Verify standalone frame capture test**
  Run a test capture against a local URL or test page.
  Verify `capture-log.json` records renderer, dimensions, and view quality scores.

- [ ] **Step 4: Update `tools/capture_viewport.mjs`**
  Replace hardcoded `/usr/bin/google-chrome` with dynamic executable detection (Chrome, Edge, or Playwright Chromium) so legacy node scripts also work on Windows.

- [ ] **Step 5: Commit and push**
  ```bash
  git add tools/capture.py tools/capture_view_quality.py tools/capture_viewport.mjs
  git commit -m "feat(tools): add headless frame capture and view-quality harness"
  git push origin master
  ```

---

### Task 4: Expose Visual Verification Script in Framework

**Files:**
- Modify: `package.json`
- Test: Run `npm run test:visual -- --help` or smoke run

**Interfaces:**
- Consumes: `tools/capture.py`.
- Produces: `test:visual` script in `package.json`.

- [ ] **Step 1: Add script to `package.json`**
  Add `"test:visual": "python tools/capture.py"` to `"scripts"`.

- [ ] **Step 2: Run verification**
  Run `npm run test:visual -- --help` and verify options are printed without error.

- [ ] **Step 3: Commit and push**
  ```bash
  git add package.json
  git commit -m "feat(scripts): expose npm run test:visual script"
  git push origin master
  ```

---

### Task 5: Mine Domain Knowledge into OKF & Design Tokens

**Files:**
- Query: Use `.agents/skills/3dviz-pro-max/scripts/search.py` for "lattice", "optics", "lighting"
- Modify: `visual/design-tokens.json` (add calibrated PBR lighting / studio light tokens)
- Create or Modify: OKF concept in `knowledge/` (e.g. `crystal-lattice-structure.md` or enhancing `magnesium-oxide-synthesis.md`)

**Interfaces:**
- Consumes: Calibrated numeric defaults from `3dviz-pro-max`.
- Produces: Validated OKF markdown concepts and design token updates.

- [ ] **Step 1: Query and resolve target records**
  Run `search.py` to inspect records for unit cell ratios, PBR studio lighting parameters, and ray optics.

- [ ] **Step 2: Integrate calibrated lighting tokens in `visual/design-tokens.json`**
  Add standard key/fill/rim intensity ratios and studio Kelvin values without breaking existing token schema.

- [ ] **Step 3: Enrich OKF concept with structural parameters**
  Update or add OKF concept documentation with precise physical dimensions and representation conventions.

- [ ] **Step 4: Run OKF compilation**
  Run `node tools/okf/compile-okf.mjs` to regenerate runtime TypeScript bindings.

- [ ] **Step 5: Run full validation suite**
  Run `node tools/validate.mjs` and confirm all design tokens, OKF concepts, and assets validate.

- [ ] **Step 6: Commit and push**
  ```bash
  git add visual/design-tokens.json knowledge/ tools/okf/
  git commit -m "feat(knowledge): integrate calibrated crystal lattice & PBR lighting tokens from 3dviz-pro-max"
  git push origin master
  ```
