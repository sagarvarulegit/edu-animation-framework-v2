# YouTube Shorts High-Retention Constraints & Invariants

These non-negotiable rules apply whenever generating or editing short-form vertical videos (YouTube Shorts, Reels, TikTok) for educational content:

## 1. Duration & Algorithmic Math
- **Target Runtime Envelope**: 18–21 seconds maximum. Never exceed 22 seconds for standard CBSE practical shorts.
- **The APV Math**:
  - A 13s average view on a 23s video is only 56.5% APV.
  - The same 13s view on a 19s video delivers **68.4% APV** (the threshold for the global Shorts Feed batch queue).
  - Pacing must be dense, compressed, and ruthless.

## 2. The Rule of Climax Inversion (0–3s Hook)
- **Zero Lecture Intro Cards**: NEVER start with an "Aim", "Objectives", "Topic Title", or static bullet-point card in the first 3 seconds.
- **Visual Climax Hook (Frame 0)**: The very first frame must show the high-energy reaction, mystery, or climax (e.g., the dazzling flame, vigorous bubbling, rapid color change, or sudden reaction).
- **Curiosity-Gap Verbal Hook**: The first spoken sentence must pose a mystery or warning (e.g., *"Do NOT look directly at this dazzling white flame without safety goggles! Here is why:"*).

## 3. Sequencing & Pacing
- **The 4.5-Second Scene Hard Ceiling**:
  - NO single scene or visual framing may exceed **4.5 seconds**. Holding any static or semi-static framing past 4.5s triggers a subconscious viewer swipe-away (the "mid-video retention cliff").
  - If a reaction or chemical explanation requires 7–9 seconds, **split it into two distinct visual cuts** (e.g. Cut A: Macro color/physical change at 3.5s → Cut B: Secondary test/gas fumes/equation at 3.5s).
- **Eliminate / Compress Mundane Prep**: Never dedicate > 1.5 seconds to mundane prep (e.g., cleaning with sandpaper). Either flash it in 1 second or mention it in passing during the main reaction.
- **Step Pacing**: Scene switches must occur every 2.5–3.5 seconds.
- **Active Engagement CTA (Final 2.5s)**:
  - Never end on a passive conclusion card. The final 2.5 seconds must feature an explicit verbal and visual call-to-action (e.g. rapid-fire quiz question with options A/B/C/D) prompting viewers to comment their answer.

## 4. Visual Layout & Theming
- **Aspect Ratio**: Exact 9:16 (1080x1920).
- **Edge-to-Edge Bleed**: Use full-bleed background and prominent high-resolution visuals. Avoid small framed inner cards.
- **Design System**: Use Material 3 Expressive palette (Yellow-Orange tones: Coral/Amber/Gold `#FF9800`, `#FFB300`, `#FFF8E1`, `#212121`).
- **Kinetic Text**: Avoid static multi-line paragraphs. Render large, punchy phrases (1–3 words per beat) with pill badges, synced to speech.
- **Safe Zones**: Keep critical text and UI elements within the central 80% safe zone (top 15% clear of channel header, bottom 20% clear of title/audio overlay).

## 5. Audio & Sound Design
- **Voiceover Pace & Comprehension Invariant**:
  - Keep delivery natural, authoritative, and educational (standard 1.0x to 1.05x speech tempo).
  - **No Compounded Speedup**: NEVER stack ElevenLabs high `speaking_rate` (> 1.10) with ffmpeg `atempo` (> 1.0). Compounding speed (> 1.25x) results in breathless, auctioneer-style delivery where students cannot comprehend technical scientific names.
  - **Tight Copywriting Over Speedup**: Always achieve the 18–21s runtime envelope through ruthless script conciseness (8–12 words per beat) and gentle silence trimming (`stop_duration=0.20-0.25`), NOT by pitch-shifting or speeding up speech.
- **Background Music**: Ducked to -18dB to -22dB under speech.
- **Micro-SFX**: Transitions, reveals, and key scientific events must have micro-SFX (whoosh, pop, sizzle, sparkle).

## 6. Publishing & Metadata Invariants (CRITICAL YOUTUBE BUG RULE)
- **ABSOLUTE ZERO-BRACKET POLICY FOR YOUTUBE METADATA**:
  - **The YouTube Bug**: YouTube Studio's validator has a known bug where standard parentheses `(` and `)`, square brackets `[` and `]`, and curly braces `{` and `}` trigger a generic and misleading error: *"Angled bracket not allowed"*.
  - **The Invariant**: All YouTube descriptions, titles, and comments must be **100% BRACKET-FREE**.
    - Forbid: `(`, `)`, `[`, `]`, `{`, `}`, `<`, `>`.
    - Also forbid ASCII arrows `->`, `-->`, `=>` (as they contain `>`).
    - Use Unicode arrow `→` (U+2192) for chemical reactions or words (`yields`, `gives`, `to`).
    - Replace parentheses with dashes (` - `), colons (`:`), or commas.
    - Write state symbols and chemical formulas without parentheses (e.g., `PbNO3 2 aqueous`, `PbI2 yellow precipitate`).
- **File Naming**: Always name the rendered video file with full SEO keywords (e.g., `CBSE-Class-10-Science-Activity-1.2-Precipitation-Lead-Iodide-Shorts.mp4`).
- **Publishing Package**: Every deliverable must include a complete metadata kit: High-CTR Title, Tag list, Clean Bracket-Free Description, Pinned Question Comment, and dedicated 9:16 & 16:9 Thumbnail assets.

## 7. The Procedural Experiment Action Invariant (No Pan & Zoom)
- **Forbidden**: Never rely solely on camera pan, tilt, or zoom (Ken Burns effect) over static images for experiment scenes. A slideshow of still beakers causes rapid swipe-aways by second 11.
- **Mandatory Action Per Scene**: Every scene must depict an active, physical experiment action:
  - *Act 1 (The Hook)*: High-energy physical reaction event (e.g., flame ignition pop, sudden precipitate flash).
  - *Act 2 (The Setup / Addition)*: Active reactant addition (e.g., streaming liquid pouring from a beaker, granules falling, rising liquid level).
  - *Act 3 (The Reaction)*: Continuous active physical process (e.g., dense rising bubble effervescence, active color bloom).
  - *Act 4 (The Observation)*: Active measurement/verification (e.g., thermometer immersed in liquid with live rising mercury & digital LED readout).

## 8. Pedagogical Authenticity & Thumbnail Consistency
- **Real-World Appearance**: Preserve authentic photorealistic lab textures (real Pyrex glass, real rough metallic zinc granules, real reagent bottles) so students recognize actual substances for CBSE practical viva exams.
- **Strict Thumbnail Matching**: The uploaded thumbnail must strictly match the exact activity and hook visual of that video. Never reuse or misalign thumbnails, as visual-title mismatch collapses CTR and triggers algorithm suppression.

## 9. YouTube Studio Educational Taxonomy & Search Indexing
- **Category & Type Invariant**:
  - Category must always be set to `Education`.
  - Type must be set to `Science Experiment`.
- **Target Grade Consistency Guardrail**:
  - `Academic system`: `India`.
  - `Level`: `Class 10`.
  - `Exam, course, or standard`: `CBSE Class 10` or `CBSE Class 10 Board Exam`.
  - **Forbidden**: Never leave it blank or let it default/mistype to `class 12`. Algorithmic mis-targeting to 12th graders destroys APV.
- **The "Problems" Field Invariant (Search Indexing)**:
  - Every publishing kit must supply 2–3 timecoded board exam questions answered by the video formatted as:
    `[mm:ss] [Exact student search query / question]`
  - Example:
    `0:00 Why does cold water make quicklime boil?`
    `0:07 What type of reaction is quicklime and water?`
    `0:16 Why do whitewashed walls shine after 2 to 3 days?`
  - Google and YouTube Search parse these questions to feature the video directly in organic search results.
- **Shorts Remixing Policy**:
  - `Allow video and audio remixing`: Recommended for maximum viral reach; allows students and study accounts to remix/react with permanent attribution links back to the channel.
  - `Allow only audio remixing`: Select when protecting original procedural visuals from low-effort rip-and-repost channels.

## 10. Pre-Upload Filename & Asset Verification Check
- Before publishing, verify that the `Filename:` shown in YouTube Studio matches the active activity video (e.g. `CBSE-Class-10-Science-Activity-1.4-...` vs `Activity-1.3`). Never publish mismatched video files under new thumbnails.
- **Dual-Location Publishing Kit**: Always write the publishing kit markdown file directly to `experiments/<activity_id>/youtube_publishing_kit_<activity_id>.md` as well as the Antigravity artifact directory.

## 11. Multi-Subject Rotation & Format Invariants
- **4-Pillar Subject Rotation**: Never upload more than two consecutive videos of the same subject. Systematically interleave:
  - ⚡ **Physics**: High-contrast optics (lasers, prisms), electricity, and magnetism.
  - 📐 **Mathematics**: Speed math hacks, formula traps, and geometric shortcuts.
  - 🧬 **Biology**: Starch tests, stomata, respiration, and life processes.
  - 🧪 **Chemistry**: NCERT reaction mechanisms, gas tests, and precipitate identification.
- **Dual Content Formats**:
  - *Format A (NCERT Lab Practicals)*: Real-World Action Composite (real lab base + procedural physics engine + viva hacks).
  - *Format B (Board Exam Tips & Tricks)*: 18–21s kinetic whiteboard/animated HUD visual breakdown of shortcuts, mnemonics, and mental calculation tricks.

## 12. ChapterReady.in Platform Promotion Invariant
Every short-form video deliverable must actively promote the `ChapterReady.in` platform without hurting audience retention:
1. **Persistent Visual Brand Bug**: A discreet brand badge in the upper safe zone featuring the official open-book checkmark icon (`chapterready-watermark.png`) and `ChapterReady.in`.
2. **Value-Linked Closing CTA (Scene 4, Final 2.0s)**:
   - Verbal outro linked to immediate student value (*"Get free chapter notes and cheatsheets on ChapterReady.in!"* / *"Practice chapter mock tests on ChapterReady.in!"*).
   - High-contrast visual end-card: `🌐 ChapterReady.in • Free Class 10 Notes & AI Mock Tests`.
3. **YouTube Metadata Funnel (Zero-Bracket)**:
   - First line of description (above the fold): `Master CBSE Class 10 with free interactive notes, virtual labs, and AI mock tests on https://chapterready.in`
   - Pinned comment quiz link directly below options: `👉 Test your chapter preparation and download free cheatsheets: https://chapterready.in`
4. **Thumbnail Brand Seal**: Include a subtle, clean `ChapterReady.in` watermark badge on all 9:16 Shorts and 16:9 Landscape thumbnails.


