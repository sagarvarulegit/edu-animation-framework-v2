# Project Understanding

This file acts as the persistent memory for AI agents working on this project. It contains high-level context, architectural decisions, and important constraints.

---

## Core Purpose
Production of viral, high-retention vertical YouTube Shorts (9:16) and interactive/cinematic 3D STEM animations for CBSE Class 9–12 practical science experiments for ChapterReady.in.
The primary initial target is **CBSE Class 10 Chemistry (Chapter 1: Chemical Reactions and Equations)**, designed to teach concepts with rigorous scientific correctness, practical lab authenticity, and algorithmic optimization for YouTube Shorts.

---

## Architecture & Tech Stack

1. **Real-World Action Composite Engine (Primary Video Pipeline)**:
   - High-resolution photorealistic laboratory base imagery generated via Imagen 3 / Gemini.
   - Procedural physical experiment action layers generated in Python (`PIL`, `numpy`, `cv2`):
     * Tilted glass beakers with cubic Bézier gravity-curved pouring streams and rising liquid levels.
     * High-density active bubbling effervescence particle systems (300+ 3D spherical bubble entities with buoyancy, turbulence wobble, and surface bursting).
     * Immersed laboratory stem thermometers with climbing red mercury columns and real-time digital LED readouts with dynamic temperature color shifts.
   - Direct rawvideo pipe to FFmpeg `stdin` (`-f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i -`) for zero disk I/O, instant 30fps rendering at **₹0.00 cloud cost**.

2. **Native 3D & Procedural Framework (`edu-animation-framework-v2`)**:
   - Headless Blender scripts (`build_*.py`) generating deterministic `.blend` and `.glb` assets under `assets/<discipline>/<asset-id>/`.
   - Three.js interactive viewer (`apps/interactive-viewer/`).
   - Remotion React video composer (`apps/video-composer/`).

3. **Audio Synthesis & Post-Processing**:
   - Voiceover: ElevenLabs Multilingual v2 (`eleven_multilingual_v2`), speaking rate 1.1x–1.2x.
   - Automated silence compression: FFmpeg `silenceremove` stripping pauses > 0.25s to keep total video runtime strictly under 28 seconds.
   - Audio ducking: Laboratory ambient/upbeat background music ducked to -18dB to -22dB under speech.

4. **Agent Memory & Context System**:
   - Local rules and skills: `.agents/rules/youtube_shorts_retention.md` and `.agents/skills/cbse-science-shorts/SKILL.md`.
   - Mem0 integration: Connected under user `sunwa`, project `local-edu-animation-framework-agent-ready-bea3d03e80`.

---

## Key Conventions & Non-Negotiable Rules

1. **The Procedural Action Invariant (No Pan & Zoom)**:
   - Never rely on static camera pan, tilt, or zoom (Ken Burns effect) over still images for experiment scenes. A slideshow of still beakers causes rapid swipe-aways by second 11.
   - Every scene must depict an active, physical experiment action:
     * *Act 1 (Hook):* High-energy reaction event (e.g. flame ignition pop, precipitate bloom).
     * *Act 2 (Setup/Addition):* Active reactant addition (e.g. pouring liquid stream, solids dropping).
     * *Act 3 (Reaction):* Continuous physical/chemical action (e.g. dense bubble effervescence).
     * *Act 4 (Observation):* Active measurement/verification (e.g. immersed thermometer climbing from 25°C to 85°C).

2. **Pedagogical Material Authenticity**:
   - Preserve authentic photorealistic lab textures (rough silvery-gray zinc granules, dull magnesium ribbon, Pyrex glassware, clear colorless acid solutions) so students recognize actual materials for CBSE practical viva questions. Do not rely solely on abstract low-poly cartoon 3D shapes.

3. **Absolute Zero-Bracket Policy for YouTube Metadata**:
   - **The YouTube Studio Bug:** YouTube's validator misidentifies ANY bracket as an angled bracket.
   - All YouTube descriptions, titles, tags, and pinned comments must contain **ABSOLUTELY ZERO BRACKETS**: no `(`, `)`, `[`, `]`, `{`, `}`, `<`, `>`.
   - Never use ASCII arrows `->` or `-->` (contain `>`). Always use Unicode arrow `→` (U+2192) or plain text (`yields`, `forms`).
   - Write state symbols without parentheses (e.g. `CaO solid Quicklime + H2O → CaOH 2 Slaked Lime + Heat`).

4. **Climax Inversion & Duration Invariant**:
   - Total runtime must strictly be **between 20 and 28 seconds** (never exceed 30s).
   - Frame 0 must immediately display the visual shock/climax; never start with lecture intro cards or "Aim/Objectives".

5. **Strict Thumbnail-Topic Consistency**:
   - Uploaded thumbnails must strictly match the exact activity and visual hook of that specific video. Never reuse or mismatch thumbnails.

---

## Ongoing Decisions & Discoveries

- **2026-09-14 (Activity 1.1 - Magnesium Ribbon)**: Baseline release. Runtime ~50s, letterboxed; resulted in 93 views and 20.5% APV (catastrophic drop-off). Established the necessity of Climax Inversion and sub-30s duration.
- **2026-09-16 (Activity 1.2 - Lead Iodide Precipitation)**: Implemented Climax Inversion, 24.65s runtime, full-bleed 9:16 vertical framing, and curiosity-hook title (`2 CLEAR Liquids = YELLOW EXPLOSION?!`). Views reached 128 in 20 hours (3x velocity) and APV more than doubled to 45.2% (Rank #2).
- **2026-09-16 (Activity 1.3 - Zinc Granules & Google Veo Video Generation)**:
  - Evaluated Google Veo 3.1 Fast video generation (`veo-3.1-fast-generate-preview`). Measured unit costs: ~$0.12/sec (~₹160/clip or ~₹800–₹1,000 per Short).
  - Clarified Google AI Studio billing: Tier Caps represent monthly spending ceilings, not loans. Accounts operate on strict Prepay; negative balances halt the API with `429 RESOURCE_EXHAUSTED`.
  - Discovered that pure Image-to-Video without explicit action prompts defaults to camera pan/tilt, failing the procedural experiment test.
- **2026-09-16 (Real-World Action Composite Breakthrough)**: Developed the local Python/OpenCV/Pillow Action Composite engine (pouring liquid stream, 380 bubble particle engine, immersed thermometer with climbing mercury and digital LED readout) piped directly to FFmpeg `stdin` at ₹0.00 cloud cost.
- **2026-09-18 (Activity 1.3 Analytics & Delayed Shelf Discovery)**:
  - Analytics on Activity 1.3 revealed **97.1% YouTube Search traffic** and **48.7% APV** (retention climbed again).
  - Established that for new channels, YouTube often holds Shorts in a 24–72 hour delayed testing queue before pushing to the Shorts Feed, while immediately indexing and ranking strong SEO terms in Search.
- **2026-09-18 (Mem0 Memory Sync)**: Synchronized all 6 core architectural and algorithmic learnings into the Mem0 cloud memory graph for user `sunwa` under project `edu-animation-framework-agent-ready`.
- **2026-09-18 (Activity 1.4 - Action of Water on Quicklime)**:
  - Produced 22.67s high-retention Real-World Action Composite Short at `experiments/activity_1_4_quicklime/output/CBSE-Class-10-Science-Activity-1.4-Quicklime-Water-Shorts.mp4`.
  - Implemented authentic procedural physics in every scene: explosive steam plumes on cold water contact, tilted Pyrex pouring stream into CaO lumps, 360-bubble churning slurry with balanced combination equation, and red mercury rising along the photo's real laboratory thermometer capillary to 84.8°C with digital LED telemetry and board exam whitewashing hack.
  - Generated matched 9:16 & 16:9 thumbnails and verified 100% bracket-free publishing kit.
- **2026-09-21 (Activity 1.4 Analytics & Pacing Invariant Breakthrough)**:
  - YouTube Studio at 2d 18h showed **183 views (Rank #1 of 10 on channel)** and **46.6% APV**.
  - Identified the "10.6s Mid-Video Retention Cliff": Scene 3 was 9.15s long (nearly 40% of the video), causing viewer drop-off right before the Scene 4 climax.
  - Codified two non-negotiable production invariants:
    1. **Strict 4.5-Second Scene Ceiling**: Never hold any single scene > 4.5s; split longer explanations into two rapid visual cuts.
    2. **Runtime Compression (18–21s)**: Compressing total duration to 18–21s boosts a 13s watch time from 56% to **68.4%+ APV** (qualifying for the global Shorts Feed push).
    3. **Active Closing CTA**: Add explicit verbal and visual quiz call-to-action in the final 2.5s to drive like and comment velocity.
- **2026-09-21 (Activity 1.5 - Thermal Decomposition of Ferrous Sulphate)**:
  - Produced under the upgraded **18–21s high-retention envelope**.
  - Total video duration: **19.10 seconds** (Scene 1: 4.83s, Scene 2: 4.88s, Scene 3: 4.42s, Scene 4: 5.02s).
  - **Narration Speed Correction**: Identified that stacking ElevenLabs high `speaking_rate` (>1.10) with ffmpeg `atempo` (>1.0) created a compounded 1.4x speedup, making speech sound rushed and unintelligible for students learning technical chemical names. Codified the invariant: Keep speech tempo natural (1.0x to 1.05x), no ffmpeg `atempo` speed distortion, and achieve the 18–21s envelope purely through tight copywriting (8–12 words per beat) and gentle silence trimming (`stop_duration=0.20-0.25`).
  - Procedural physical actions: Micro-particle crackle in roaring blue flame, glistening water droplet condensation inside cooler upper tube neck, dark reddish-brown ferric oxide residue with billowing sulfur gas plumes, and NCERT wafting safety technique with rapid-fire interactive quiz CTA.
  - Master video rendered at [`CBSE-Class-10-Science-Activity-1.5-Ferrous-Sulphate-Decomposition-Shorts.mp4`](file:///C:/Sagar/Projects/CBSE/ChapterReady.in/edu-animation-framework-agent-ready/edu-animation-framework-v2/experiments/activity_1_5_ferrous_sulphate/output/CBSE-Class-10-Science-Activity-1.5-Ferrous-Sulphate-Decomposition-Shorts.mp4).
- **2026-09-21 (Activity 1.6 - Thermal Decomposition of Lead Nitrate)**:
  - Fully produced adhering to the **18–21s envelope, 4.5s scene ceiling, and natural educational pacing (1.0x, zero atempo distortion)**.
  - Total video duration: **18.57 seconds** (Scene 1: 4.59s, Scene 2: 4.12s, Scene 3: 4.06s, Scene 4: 5.86s with quiz CTA reading tail).
  - Procedural physical actions: Thermal crackle micro-sparks from crystal decrepitation, dense billowing reddish-brown Nitrogen Dioxide (NO2) plumes escaping tube mouth, molten yellow Lead Monoxide (PbO) residue glow pulse, and modern laboratory fume hood exhaust streamlines.
  - Master video rendered at [`CBSE-Class-10-Science-Activity-1.6-Lead-Nitrate-Decomposition-Shorts.mp4`](file:///C:/Sagar/Projects/CBSE/ChapterReady.in/edu-animation-framework-agent-ready/edu-animation-framework-v2/experiments/activity_1_6_lead_nitrate/output/CBSE-Class-10-Science-Activity-1.6-Lead-Nitrate-Decomposition-Shorts.mp4).
- **2026-09-21 (Channel Strategic Expansion: 4-Subject Rotation, Tips & Tricks, Platform Promotion)**:
  - **4-Pillar Subject Rotation Invariant**: Codified systematic rotation across all 4 CBSE Class 10 STEM subjects (Physics, Mathematics, Biology, Chemistry) to eliminate visual monotony and capture wider exam search traffic. Never publish >2 consecutive videos of one subject.
  - **Dual Content Formats**: Established two complementary formats: Format A (NCERT Lab Practicals & Viva Hacks) and Format B (18–21s Board Exam Tips & Tricks / Speed Shortcuts).
  - **ChapterReady.in Platform Promotion Invariant**: Codified mandatory 4-touchpoint brand promotion across all deliverables: (1) Persistent top safe-zone watermark pill (`chapterready-watermark.png` + `ChapterReady.in`), (2) Value-linked closing audio & visual CTA in Scene 4, (3) Permanent SEO conversion links in description first line & pinned comment quiz, (4) Thumbnail brand seal.



