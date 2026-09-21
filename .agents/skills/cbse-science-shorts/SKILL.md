---
name: cbse-science-shorts
description: >-
  Use this skill to produce viral, high-retention YouTube Shorts (9:16 vertical explainer videos)
  for CBSE Class 9-12 science experiments, lab activities, and concepts.
---

# CBSE Science Shorts Production Runbook

This skill outlines the complete end-to-end workflow for authoring, animating, narrating, and packaging high-retention vertical YouTube Shorts for CBSE Science topics.

---

## Phase 1: Scripting with Climax Inversion (20–28 Seconds Max)

1. **Identify the Visual Shock / Climax**:
   - Determine the most visually arresting moment of the experiment (e.g., dazzling white combustion flame, color transition from blue to colorless, violent fizzing, vivid yellow precipitate bloom).
2. **Draft the 4-Act Retention Script**:
   - **Act 1 (0–3s) The Hook**: Visual climax preview + Curiosity-gap warning/question.
   - **Act 2 (3–9s) The Setup**: Ultra-fast apparatus and context (single beat, zero lecture preamble).
   - **Act 3 (9–20s) The Reaction & Science**: Direct observation and formula explanation.
   - **Act 4 (20–26s) The Exam Takeaway & Loop**: The single key exam question answered + loop prompt.

---

## Phase 2: Audio Synthesis & Pacing

1. **ElevenLabs TTS**:
   - Use `ELEVEN_LABS_API_KEY` (or `ELEVEN_LAB_API_KEY`) from environment variables.
   - Select an energetic, authoritative voice model (e.g., `eleven_multilingual_v2` with `stability=0.50`, `similarity_boost=0.85`, natural speaking rate 1.0x to 1.05x).
   - **No Compounded Speedup**: NEVER stack high ElevenLabs speaking_rate with FFmpeg `atempo`. Preserve natural human diction and syllable clarity. Achieve the **18–21s runtime envelope** via tight copywriting (8–12 words per beat) and gentle silence trimming (`stop_duration=0.20-0.25`).
2. **Audio Ducking & SFX**:
   - Duck upbeat background music to -18dB to -22dB under speech.
   - Add micro-SFX (whoosh on title drops, sizzle/pop on reaction triggers, ding on exam tips).

---

## Phase 3: Visual System (Material 3 Expressive)

1. **Canvas**: 1080x1920 (9:16 vertical full-bleed).
2. **Color Tokens**:
   - Primary: Amber `#FFB300` / Tangerine `#FF6F00`
   - Background: Dark Obsidian `#121212` with subtle radial warmth
   - Accents: Electric Yellow `#FFEA00`, Coral Red `#FF3D00`
   - Containers: Glassmorphic dark surface with rounded corners (radius 32px).
3. **Typography & Safe Zones**:
   - Word Chunking: 1–3 words per kinetic burst. Never show paragraphs of text.
   - Safe Zone: Keep text strictly between Y = 250px and Y = 1550px.

---

## Phase 4: Assembly & Real-World Action Composite Engine

Do NOT use static camera zoompan over still images. Use the **Real-World Action Composite** architecture:
1. **Layer 1 (Photorealistic Lab Base)**:
   - High-resolution photorealistic imagery showing authentic materials (real zinc granules with rough metallic texture, real magnesium ribbon, real Pyrex glassware).
2. **Layer 2 (Procedural Experiment Action)**:
   - *Pouring*: Tilted glass beaker with cubic Bézier gravity-curved liquid stream, rising meniscus, and surface ripples.
   - *Effervescence / Reaction*: Continuous particle engine (300+ 3D spherical bubbles nucleating off solids with upward buoyancy, wobble, and surface bursting froth).
   - *Exothermic Heat*: Laboratory thermometer immersed in liquid with live rising red mercury column and real-time digital LED temperature readout shifting color from cyan to hot red.
3. **Layer 3 (Material 3 HUD & Reality Anchor)**:
   - Top action card (e.g., `STEP 1 • ADDING REACTANTS`).
   - Bottom `LAB REALITY CHECK` card explaining physical appearance for CBSE practical viva questions.
4. **Fast Zero-Cost Compilation**:
   - Pipe raw RGB24 frames directly from Python (`PIL`/`NumPy`/`cv2`) to FFmpeg `stdin` (`-f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i -`).
   - Renders 500+ frames in under 15 seconds at ₹0.00 cloud cost.

---

## Phase 5: Packaging & YouTube Publishing Kit

Generate a complete publishing kit for every video:
1. **File Name**: Format as `CBSE-Class-{Grade}-Science-Activity-{Num}-{Topic}-Shorts.mp4`.
2. **Title**: Under 60 characters with high-CTR curiosity hook and emojis.
3. **Description Formatting (ABSOLUTE ZERO-BRACKET POLICY)**:
   - **CRITICAL YOUTUBE BUG**: YouTube Studio validator has a bug that misidentifies ANY bracket as an angle bracket.
   - Forbid ALL brackets: `(`, `)`, `[`, `]`, `{`, `}`, `<`, `>`.
   - Never use ASCII arrows `->` or `-->` (contain `>`). Always use Unicode right arrow `→` (U+2192) or words (`yields`, `gives`, `forms`).
   - Write state symbols without parentheses (e.g., `Zn solid + H2SO4 dilute → ZnSO4 aqueous + H2 gas + Heat`).
   - Replace parentheses with dashes (` - `), colons (`:`), or commas.
4. **Pinned Comment**: A concept check question to immediately spur comments and algorithmic engagement.
5. **Thumbnails**: Both 9:16 (1080x1920) and 16:9 (1920x1080) high-contrast hook thumbnails. Verify thumbnail strictly matches video topic.

---

## Phase 6: Cloud AI Video Economics & Quota Management

1. **Google Veo 3.1 Pricing Realities**:
   - Veo Fast rate: ~$0.10–$0.15 per video second (~₹160 – ₹170 INR per 4s clip).
   - A 4-scene AI video Short costs **~₹800 – ₹1,000 INR (~$10–$12 USD)** per video.
2. **Google AI Studio Prepay Rules**:
   - Accounts operate under strict Prepay enforcement.
   - "Billing Account Tier Cap" is a maximum monthly spending ceiling, NOT a loan or credit line.
   - A positive balance above ₹0 is required to prevent `429 RESOURCE_EXHAUSTED` errors.
3. **Recommended Production Pipeline**:
   - Use the local **Real-World Action Composite Engine** (Phase 4) for daily production (₹0.00 cost, 100% reproducible, zero quota blocks).
   - Reserve cloud AI video strictly for complex fluid-gas combustion macro shots when funded.

---

## Phase 7: Post-Launch Algorithmic Diagnostics

1. **Traffic Source Breakdown**:
   - **High Search (>80%) + Low Feed (<10%)**: Indicates the video is successfully indexed for organic YouTube Search, but YouTube's Shorts Feed batch testing queue has not triggered yet ("delayed shelf" phenomenon, common in the first 24–72 hours for new channels). Do not delete or re-upload.
2. **Retention (APV) Benchmark & Mid-Video Cliff Analysis**:
   - `< 30%`: Critical drop-off (slow intro, letterboxed bars).
   - `45% – 50%`: Healthy baseline engagement (strong hook, viewers staying 10–12s).
   - `70% – 85%+`: Algorithmic sweet spot required for viral Shorts Feed explosion.
   - **The Mid-Video Retention Cliff**: If APV is hovering at ~46%–48% on a 22–24s video, inspect the exact visual playing at second 10–12. If any single scene was held longer than 4.5 seconds (e.g. Scene 3 in Activity 1.4 was 9.15s), viewers swiped due to visual stagnation. **Enforce the strict 4.5-second scene ceiling** by splitting long reaction steps into two rapid cuts.
3. **Thumbnail & Title Alignment**:
   - Confirm the uploaded thumbnail matches the exact activity. A mismatched thumbnail crushes CTR and triggers algorithm suppression.

---

## Phase 8: YouTube Publishing Kit & Educational Taxonomy Package

Generate a complete, copy-paste-ready publishing kit and save it to **both** locations:
1. `experiments/<activity_id>/youtube_publishing_kit_<activity_id>.md` (Project directory)
2. Antigravity Artifacts directory (`brain/<conversation_id>/...`)

The kit must include:
1. **Zero-Bracket SEO Metadata**:
   - Titles: 3 high-CTR options (Climax Hook, Syllabus/SEO, Board Question).
   - Description: 100% bracket-free text with state symbols written without brackets (e.g. `CaO solid + H2O → CaOH 2 + Heat`), timestamps, and hashtags.
   - Pinned Interactive Quiz: Rapid-fire board question with multiple choices A, B, C, D to drive comment signals.
   - Tags: Exhaustive comma-separated tags (< 500 chars).
2. **Educational Taxonomy & Problems Table**:
   - Category: `Education`
   - Type: `Science Experiment`
   - Problems: 2–3 timecoded board exam questions formatted for Google & YouTube Search indexing:
     `[mm:ss] [Exact question / problem solved]`
   - Academic system: `India`
   - Level: `Class 10`
   - Exam, course, or standard: `CBSE Class 10 Board Exam` (Guardrail: Never let it default to Class 12!).
   - Shorts Remixing recommendation (`Allow video and audio remixing` for viral reach vs `Allow only audio remixing` for asset protection).
3. **Automated Pre-Upload Verification**:
   - Run automated regex verification on the publishing kit markdown file to ensure zero `(`, `)`, `[`, `]`, `{`, `}`, `<`, `>`.
   - Verify that the video file uploaded to YouTube Studio matches the active activity.

---

## Phase 9: ChapterReady.in Platform Promotion & Multi-Subject Extension

1. **Brand Asset Integration**:
   - Logo path: `C:\Sagar\Projects\CBSE\ChapterReady.in\cbse_byCodex\logo\chapterready-watermark.png`
   - Overlay a semi-transparent brand pill on every scene composite (`Image.alpha_composite`).
2. **Multi-Subject Scene Templates**:
   - *Physics*: Laser ray tracing, light dispersion, magnetic field lines, mirror reflections.
   - *Maths*: Step-by-step kinetic equation breakdowns, trigonometric finger tricks, geometric proofs.
   - *Biology*: Starch color blooms, microscopic peels, biological cycle flowcharts.
3. **Publishing Kit Promotion Section**:
   - Automatically inject the verified bracket-free https://chapterready.in conversion links into the description header and pinned comment quiz template.

