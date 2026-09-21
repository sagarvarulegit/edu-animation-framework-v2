#!/usr/bin/env python3
"""
Builds a YouTube Shorts (9:16 vertical 1080x1920) mobile-optimized explainer video
for CBSE Class 10 Activity 1.1 (Burning of Magnesium Ribbon).
Features:
- Warm Yellow-Orange educational visual theme with glassmorphic cards
- ElevenLabs AI Voiceover narration for every step
- Background music (BGM) properly ducked under narration with fade in/out
- Total duration < 60s (strict YouTube Shorts compliance)
- Frame-accurate audio-video synchronization
"""

import os
import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
AUDIO_DIR = BASE_DIR / "audio"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR = BASE_DIR / "overlays_916"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR = BASE_DIR / "clips_916"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\cbse_byCodex\videos\chapterready-promo\audio\bgm_loop.mp3")

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Google Material 3 Expressive Color System (Warm Amber / Solar Seed)
M3 = {
    "primary": (255, 183, 77),             # #FFB74D (Tone 80 Amber)
    "onPrimary": (58, 30, 0),              # #3A1E00 (Tone 20 Dark Contrast)
    "primaryContainer": (78, 44, 10),      # #4E2C0A (Tone 30 Container)
    "onPrimaryContainer": (255, 222, 180), # #FFDEB4 (Tone 90 Gold Text)
    "secondary": (255, 140, 0),            # #FF8C00 (Tone 80 Tangerine)
    "secondaryContainer": (88, 44, 20),
    "onSecondaryContainer": (255, 218, 204),
    "tertiary": (255, 215, 64),            # #FFD740 (Tone 85 Solar Yellow)
    "tertiaryContainer": (72, 54, 0),
    "onTertiaryContainer": (255, 225, 160),
    "surface": (20, 16, 12),               # Tone 6 warm obsidian
    "surfaceContainerLowest": (14, 11, 8), # Tone 4
    "surfaceContainerLow": (26, 21, 16),   # Tone 10
    "surfaceContainer": (34, 27, 21),      # Tone 14
    "surfaceContainerHigh": (44, 35, 28),  # Tone 18
    "surfaceContainerHighest": (56, 45, 36),# Tone 22
    "onSurface": (246, 238, 232),          # Tone 90 Warm White
    "onSurfaceVariant": (216, 196, 182),   # Tone 80 Warm Muted Text
    "outline": (158, 139, 126),            # Tone 60
    "outlineVariant": (84, 70, 60),        # Tone 30
}

STEPS_916 = [
    {
        "id": "step1",
        "num": "01",
        "title_short": "1. Clean Magnesium Ribbon",
        "badge": "SURFACE PREPARATION",
        "desc_short": "Rub the ribbon thoroughly with sandpaper.",
        "why_1": "NCERT REASON: Removes unreactive layer of basic",
        "why_2": "magnesium carbonate to ensure clean combustion.",
        "image": "step1_clean_ribbon.jpg",
        "formula": "Mg (s)  [Clean Metallic Surface]",
        "zoom": "in"
    },
    {
        "id": "step2",
        "num": "02",
        "title_short": "2. Hold with Crucible Tongs",
        "badge": "LABORATORY SAFETY",
        "desc_short": "Grip the clean silver ribbon securely with tongs.",
        "why_1": "SAFETY PROTOCOL: Wear eye protection goggles and",
        "why_2": "keep burning ribbon at arm's length.",
        "image": "step2_grip_tongs.jpg",
        "formula": "Mg (s) + Laboratory Crucible Tongs",
        "zoom": "pan"
    },
    {
        "id": "step3",
        "num": "03",
        "title_short": "3. Heat in Bunsen Flame",
        "badge": "ACTIVATION ENERGY",
        "desc_short": "Lower ribbon tip into the hot blue Bunsen cone.",
        "why_1": "THERMAL ACTIVATION: Heating provides energy to",
        "why_2": "reach ignition temperature (~473 °C).",
        "image": "step3_heat_flame.jpg",
        "formula": "Mg (s) + Heat (Δ)",
        "zoom": "in"
    },
    {
        "id": "step4",
        "num": "04",
        "title_short": "4. Dazzling White Flame",
        "badge": "VIGOROUS OXIDATION",
        "desc_short": "Bursts into an intense, dazzling blinding white flame!",
        "why_1": "EXOTHERMIC REACTION: Magnesium reacts vigorously",
        "why_2": "with atmospheric oxygen releasing light & heat.",
        "image": "step4_dazzling_burn.jpg",
        "formula": "2Mg (s) + O₂ (g)  →  2MgO (s) + Light + Heat",
        "zoom": "out"
    },
    {
        "id": "step5",
        "num": "05",
        "title_short": "5. Collect White Ash",
        "badge": "PRODUCT FORMATION",
        "desc_short": "Collect the white powder formed in a watch glass.",
        "why_1": "NEW CHEMICAL IDENTITY: The white ash is Magnesium",
        "why_2": "Oxide (MgO), chemically distinct from Mg.",
        "image": "step5_collect_ash.jpg",
        "formula": "MgO (s)  [White Insoluble Powder]",
        "zoom": "in"
    },
    {
        "id": "step6",
        "num": "06",
        "title_short": "6. Test with Litmus Paper",
        "badge": "CHEMICAL ANALYSIS",
        "desc_short": "Add water to MgO ash and test with red litmus paper.",
        "why_1": "BASIC NATURE: Red litmus turns distinctly BLUE!",
        "why_2": "Proving that metallic oxides are basic in nature.",
        "image": "step6_litmus_test.jpg",
        "formula": "MgO + H₂O  →  Mg(OH)₂  (Basic: pH > 7)",
        "zoom": "in"
    }
]

def get_audio_duration(audio_file):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)

def create_intro_card_916():
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), M3["surface"] + (255,))

    # Ambient M3 Expressive Radial Tonal Bloom
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([60, 180, 1020, 1320], fill=M3["primaryContainer"] + (70,))
    glow_draw.ellipse([200, 320, 880, 1120], fill=M3["tertiaryContainer"] + (60,))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top M3 Pill Chip
    font_chip = get_font(FONT_BOLD, 20)
    draw.rounded_rectangle([230, 130, 850, 190], radius=30, fill=M3["surfaceContainerHighest"] + (255,), outline=M3["outlineVariant"], width=1)
    draw.ellipse([255, 150, 275, 170], fill=M3["primary"])
    draw.text((550, 160), "NCERT CLASS 10 SCIENCE • CH 1", font=font_chip, fill=M3["onSurface"], anchor="mm")

    # M3 Display Typography
    font_act = get_font(FONT_BOLD, 36)
    draw.text((540, 250), "ACTIVITY 1.1", font=font_act, fill=M3["primary"], anchor="mm")
    font_title = get_font(FONT_BOLD, 54)
    draw.text((540, 325), "Burning of", font=font_title, fill=M3["onSurface"], anchor="mm")
    draw.text((540, 395), "Magnesium Ribbon", font=font_title, fill=M3["tertiary"], anchor="mm")

    font_sub = get_font(FONT_SEMI, 28)
    draw.text((540, 465), "Complete Lab Demonstration in 6 Steps", font=font_sub, fill=M3["onSurfaceVariant"], anchor="mm")

    # Center Preview Thumbnail with M3 Extra Large Card
    thumb_path = IMG_DIR / "step4_dazzling_burn.jpg"
    if thumb_path.exists():
        thumb = Image.open(thumb_path).convert("RGB")
        thumb = thumb.resize((960, 540), Image.Resampling.LANCZOS)
        mask = Image.new("L", (960, 540), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, 960, 540], radius=28, fill=255)
        img.paste(thumb, (60, 520), mask)
        draw.rounded_rectangle([58, 518, 1022, 1062], radius=28, outline=M3["primary"], width=2)
        # M3 Badge over thumb
        draw.rounded_rectangle([90, 550, 490, 600], radius=16, fill=M3["surfaceContainerHighest"] + (240,), outline=M3["outlineVariant"], width=1)
        draw.text((290, 575), "LAB EXPERIMENT PREVIEW", font=get_font(FONT_BOLD, 19), fill=M3["tertiary"], anchor="mm")

    # 4 M3 Expressive List Items (Tonal cards with pill badges)
    goals = [
        ("01", "Surface Preparation", "Clean with sandpaper to remove oxide"),
        ("02", "Thermal Ignition", "Heat in blue Bunsen flame to ignition temp"),
        ("03", "Vigorous Combustion", "Blinding dazzling white flame & smoke"),
        ("04", "Litmus Analysis", "Moist red litmus turns blue (Basic oxide)")
    ]

    card_y = 1100
    font_num = get_font(FONT_BOLD, 24)
    font_gt = get_font(FONT_BOLD, 24)
    font_gd = get_font(FONT_REGULAR, 20)

    for i, (num, title, desc) in enumerate(goals):
        y = card_y + (i * 125)
        draw.rounded_rectangle([60, y, 1020, y + 105], radius=20, fill=M3["surfaceContainerHigh"] + (255,), outline=M3["outlineVariant"], width=1)
        # M3 Avatar / Tonal Circle
        draw.ellipse([85, y + 20, 145, y + 80], fill=M3["primaryContainer"] + (255,), outline=M3["primary"], width=1)
        draw.text((115, y + 50), num, font=font_num, fill=M3["onPrimaryContainer"], anchor="mm")
        draw.text((170, y + 36), title, font=font_gt, fill=M3["onSurface"], anchor="lm")
        draw.text((170, y + 74), desc, font=font_gd, fill=M3["onSurfaceVariant"], anchor="lm")

    # Bottom Branding Pill
    draw.rounded_rectangle([240, 1680, 840, 1745], radius=30, fill=M3["surfaceContainerHighest"] + (255,), outline=M3["outlineVariant"], width=1)
    draw.text((540, 1712), "MATERIAL 3 EXPRESSIVE • SHORTS", font=font_chip, fill=M3["primary"], anchor="mm")

    out_file = OVERLAYS_DIR / "intro_card_916.png"
    img.save(out_file)
    return out_file

def create_outro_card_916():
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), M3["surface"] + (255,))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([60, 180, 1020, 1320], fill=M3["primaryContainer"] + (70,))
    glow_draw.ellipse([200, 320, 880, 1120], fill=M3["tertiaryContainer"] + (60,))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Tag
    font_chip = get_font(FONT_BOLD, 20)
    draw.rounded_rectangle([250, 120, 830, 180], radius=30, fill=M3["surfaceContainerHighest"] + (255,), outline=M3["outlineVariant"], width=1)
    draw.text((540, 150), "EXAM RECAP & KEY SUMMARY", font=font_chip, fill=M3["primary"], anchor="mm")

    font_title = get_font(FONT_BOLD, 46)
    draw.text((540, 230), "Activity 1.1 Key Takeaways", font=font_title, fill=M3["onSurface"], anchor="mm")

    cards = [
        ("OBSERVATION", [
            "• Burns with an intense, dazzling white flame",
            "• Dense white fumes of Magnesium Oxide",
            "• Pure white ash collected in watch glass"
        ], M3["primary"]),
        ("REACTION TYPE", [
            "• Combination: 2Mg (s) + O₂ (g) → 2MgO (s)",
            "• Exothermic: Releases high thermal & light energy",
            "• Two reactants combine to form a single product"
        ], M3["secondary"]),
        ("CHEMICAL NATURE", [
            "• Metallic oxides are BASIC in nature",
            "• MgO + H₂O → Mg(OH)₂ (Magnesium Hydroxide)",
            "• Turns moist red litmus paper distinct BLUE"
        ], M3["tertiary"])
    ]

    card_y = 290
    font_ct = get_font(FONT_BOLD, 22)
    font_cb = get_font(FONT_REGULAR, 21)

    for ctitle, lines, col in cards:
        draw.rounded_rectangle([60, card_y, 1020, card_y + 245], radius=24, fill=M3["surfaceContainerHigh"] + (255,), outline=M3["outlineVariant"], width=1)
        # M3 Header Pill inside card
        draw.rounded_rectangle([90, card_y + 18, 440, card_y + 64], radius=16, fill=M3["surfaceContainerHighest"] + (255,), outline=col, width=1)
        draw.text((265, card_y + 41), ctitle, font=font_ct, fill=col, anchor="mm")

        line_y = card_y + 85
        for l in lines:
            draw.text((90, line_y), l, font=font_cb, fill=M3["onSurface"])
            line_y += 44
        card_y += 275

    # Frequent CBSE Question Box (M3 High Emphasis Card)
    draw.rounded_rectangle([60, 1140, 1020, 1500], radius=24, fill=M3["surfaceContainerHighest"] + (255,), outline=M3["primary"], width=2)
    font_qt = get_font(FONT_BOLD, 24)
    font_qa = get_font(FONT_REGULAR, 21)
    draw.text((100, 1180), "CBSE BOARD EXAM FREQUENT QUESTION", font=font_qt, fill=M3["tertiary"], anchor="lm")
    draw.text((100, 1240), "Q: Why is magnesium ribbon cleaned before burning?", font=font_qa, fill=M3["onSurface"], anchor="lm")
    draw.text((100, 1310), "Ans: To remove the protective layer of basic magnesium", font=font_qa, fill=M3["onSurfaceVariant"], anchor="lm")
    draw.text((100, 1360), "carbonate that prevents direct contact with oxygen.", font=font_qa, fill=M3["onSurfaceVariant"], anchor="lm")
    draw.text((100, 1420), "Equation: 2Mg (s) + O₂ (g) → 2MgO (s)", font=get_font(FONT_BOLD, 22), fill=M3["primary"], anchor="lm")

    # Bottom CTA Pill
    draw.rounded_rectangle([180, 1620, 900, 1690], radius=30, fill=M3["primaryContainer"] + (255,), outline=M3["primary"], width=1)
    draw.text((540, 1655), "Subscribe & Follow for Class 10 Practicals!", font=font_chip, fill=M3["onPrimaryContainer"], anchor="mm")

    out_file = OVERLAYS_DIR / "outro_card_916.png"
    img.save(out_file)
    return out_file

def create_step_overlay_916(step):
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. M3 Expressive Top App Bar Container (Shape: Extra Large 28px)
    bar_y1, bar_y2 = 90, 310
    draw.rounded_rectangle([48, bar_y1, 1032, bar_y2], radius=28, fill=M3["surfaceContainerHigh"] + (245,), outline=M3["outlineVariant"], width=1)

    # M3 Assist Chip: Curriculum Tag (Shape: Full Pill)
    draw.rounded_rectangle([72, 112, 460, 164], radius=26, fill=M3["surfaceContainerHighest"] + (255,), outline=M3["outlineVariant"], width=1)
    draw.ellipse([92, 130, 108, 146], fill=M3["primary"])
    font_chip = get_font(FONT_BOLD, 17)
    draw.text((122, 138), "CBSE 10  •  ACTIVITY 1.1", font=font_chip, fill=M3["onSurface"], anchor="lm")

    # M3 Status Filter Chip: Step indicator (Shape: Full Pill)
    draw.rounded_rectangle([750, 112, 1008, 164], radius=26, fill=M3["primaryContainer"] + (255,), outline=M3["primary"], width=1)
    draw.text((879, 138), f"STEP {step['num']} OF 06", font=font_chip, fill=M3["onPrimaryContainer"], anchor="mm")

    # Step Title: Headline Medium (M3 typography)
    font_title = get_font(FONT_BOLD, 33)
    draw.text((72, 208), step["title_short"], font=font_title, fill=M3["tertiary"], anchor="lm")

    # M3 Suggestion Badge (Shape: Small Pill 14px)
    font_badge = get_font(FONT_BOLD, 17)
    badge_w = font_badge.getlength(step["badge"]) + 28
    draw.rounded_rectangle([72, 244, 72 + badge_w, 282], radius=14, fill=M3["secondaryContainer"] + (255,), outline=M3["secondary"], width=1)
    draw.text((72 + badge_w / 2, 263), step["badge"], font=font_badge, fill=M3["onSecondaryContainer"], anchor="mm")

    # 2. Center Image Frame: M3 Surface Container (Extra Large Radius 32px)
    draw.rounded_rectangle([46, 336, 1034, 1264], radius=32, outline=M3["primary"], width=2)
    draw.rounded_rectangle([48, 338, 1032, 1262], radius=30, outline=M3["outlineVariant"], width=1)

    # 3. Bottom M3 Elevated Educational Card (Extra Large Radius 32px)
    card_y1, card_y2 = 1290, 1750
    draw.rounded_rectangle([48, card_y1, 1032, card_y2], radius=32, fill=M3["surfaceContainerHigh"] + (248,), outline=M3["outlineVariant"], width=1)

    # Chemical Formula Pill (M3 Tonal Capsule 24px)
    font_formula = get_font(FONT_BOLD, 25)
    draw.rounded_rectangle([72, card_y1 + 24, 1008, card_y1 + 84], radius=24, fill=M3["primaryContainer"] + (255,), outline=M3["primary"], width=1)
    draw.text((540, card_y1 + 54), step["formula"], font=font_formula, fill=M3["tertiary"], anchor="mm")

    # Action Description: M3 Title Medium
    font_desc = get_font(FONT_BOLD, 25)
    draw.text((72, card_y1 + 128), step["desc_short"], font=font_desc, fill=M3["onSurface"], anchor="lm")

    # Scientific Reason: M3 Body Medium
    font_why = get_font(FONT_REGULAR, 22)
    draw.text((72, card_y1 + 202), step["why_1"], font=font_why, fill=M3["onSurfaceVariant"], anchor="lm")
    draw.text((72, card_y1 + 246), step["why_2"], font=font_why, fill=M3["onSurfaceVariant"], anchor="lm")

    # 4. M3 Expressive Linear Progress Indicator
    track_y = card_y2 - 14
    track_x1, track_x2 = 72, 1008
    total_w = track_x2 - track_x1
    step_idx = int(step["num"])
    active_w = int(total_w * (step_idx / 6))

    # Inactive track
    draw.rounded_rectangle([track_x1, track_y, track_x2, track_y + 8], radius=4, fill=M3["surfaceContainerLowest"] + (255,))
    # Active indicator
    draw.rounded_rectangle([track_x1, track_y, track_x1 + active_w, track_y + 8], radius=4, fill=M3["primary"] + (255,))

    out_file = OVERLAYS_DIR / f"overlay_916_{step['id']}.png"
    img.save(out_file)
    return out_file

def render_step_clip_916(img_path, overlay_path, vo_path, out_clip_path, duration=6.0, zoom="in"):
    """
    Renders a 9:16 mobile clip with:
    - Blurred full-bleed background
    - Sharp center image with subtle Ken Burns zoom/pan
    - Yellow-Orange transparent UI overlay
    - Synced voiceover audio padded to duration
    """
    frames = int(duration * 30)

    if zoom == "in":
        fg_zoom = f"zoompan=z='min(zoom+0.0008,1.08)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=988x928:fps=30"
    elif zoom == "out":
        fg_zoom = f"zoompan=z='if(lte(zoom,1.0),1.08,max(1.0,zoom-0.0008))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=988x928:fps=30"
    else:
        fg_zoom = f"zoompan=z='1.05':d={frames}:x='(in/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s=988x928:fps=30"

    filter_complex = (
        # 1. Background: scale to 1080x1920, heavy blur, M3 scrim tone
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=40,colorlevels=rimax=0.55:gimax=0.55:bimax=0.55[bg];"
        # 2. Foreground: scale to 988x928, apply smooth Ken Burns
        f"[0:v]scale=988:928:force_original_aspect_ratio=increase,crop=988:928,{fg_zoom}[fg];"
        # 3. Composite fg onto bg at (46, 336)
        f"[bg][fg]overlay=46:336[stage];"
        # 4. Composite M3 UI overlay on top
        f"[stage][1:v]overlay=0:0[vout];"
        # 5. Audio pad to exact duration
        f"[2:a]apad=whole_dur={duration}[aout]"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-loop", "1", "-i", str(overlay_path),
        "-i", str(vo_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(out_clip_path)
    ]
    subprocess.run(cmd, check=True)

def render_card_clip_916(card_img_path, vo_path, out_clip_path, duration=7.0):
    """Renders a static 9:16 card clip with fade-in and audio."""
    filter_complex = (
        f"[0:v]scale=1080:1920,fade=t=in:st=0:d=0.4,fade=t=out:st={duration-0.4}:d=0.4[vout];"
        f"[1:a]apad=whole_dur={duration}[aout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(card_img_path),
        "-i", str(vo_path),
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(out_clip_path)
    ]
    subprocess.run(cmd, check=True)

def main():
    print("================================================================")
    print(">> BUILDING YOUTUBE SHORTS (9:16) FOR ACTIVITY 1.1")
    print("================================================================")

    # 1. Check audio files and measure durations
    vo_files = {
        "00_intro": AUDIO_DIR / "00_intro.mp3",
        "01_step1": AUDIO_DIR / "01_step1.mp3",
        "02_step2": AUDIO_DIR / "02_step2.mp3",
        "03_step3": AUDIO_DIR / "03_step3.mp3",
        "04_step4": AUDIO_DIR / "04_step4.mp3",
        "05_step5": AUDIO_DIR / "05_step5.mp3",
        "06_step6": AUDIO_DIR / "06_step6.mp3",
        "07_outro": AUDIO_DIR / "07_outro.mp3"
    }

    durations = {}
    total_vo_dur = 0
    for k, v in vo_files.items():
        if not v.exists():
            raise FileNotFoundError(f"Missing audio file: {v}")
        dur = get_audio_duration(v)
        # Add 0.15s buffer for natural pause
        clip_dur = round(dur + 0.15, 2)
        durations[k] = clip_dur
        total_vo_dur += clip_dur
        print(f" - {k}: VO={dur:.2f}s -> Clip={clip_dur:.2f}s")

    print(f"\nTotal Target Video Duration: {total_vo_dur:.2f}s (< 60.0s Shorts limit)")
    if total_vo_dur >= 60.0:
        raise ValueError(f"Total duration {total_vo_dur:.2f}s exceeds 60s YouTube Shorts limit!")

    # 2. Generate 9:16 Overlays and Cards
    print("\n1. Generating 9:16 Visual Cards & Overlays...")
    intro_card = create_intro_card_916()
    outro_card = create_outro_card_916()

    clip_paths = []

    # 3. Render Intro Clip
    print("\n2. Rendering Intro Clip...")
    intro_clip = CLIPS_DIR / "00_intro_916.mp4"
    render_card_clip_916(intro_card, vo_files["00_intro"], intro_clip, duration=durations["00_intro"])
    clip_paths.append(intro_clip)

    # 4. Render Step Clips
    for i, step in enumerate(STEPS_916):
        k = f"{step['num']}_{step['id']}"
        print(f"3.{i+1} Rendering {step['num']}: {step['title_short']} (dur={durations[k]}s)...")
        overlay = create_step_overlay_916(step)
        img_file = IMG_DIR / step["image"]
        step_clip = CLIPS_DIR / f"{k}_916.mp4"
        render_step_clip_916(
            img_file, overlay, vo_files[k], step_clip,
            duration=durations[k], zoom=step["zoom"]
        )
        clip_paths.append(step_clip)

    # 5. Render Outro Clip
    print(f"\n4. Rendering Outro Clip (dur={durations['07_outro']}s)...")
    outro_clip = CLIPS_DIR / "07_outro_916.mp4"
    render_card_clip_916(outro_card, vo_files["07_outro"], outro_clip, duration=durations["07_outro"])
    clip_paths.append(outro_clip)

    # 6. Concat clips
    print("\n5. Concatenating all 9:16 clips...")
    concat_list = CLIPS_DIR / "concat_list_916.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            safe_p = str(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    concatenated_temp = OUT_DIR / "temp_concatenated_916.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(concatenated_temp)
    ]
    subprocess.run(cmd_concat, check=True)

    # 7. Mix Background Music (BGM)
    final_shorts_video = OUT_DIR / "activity_1_1_magnesium_ribbon_shorts.mp4"
    print(f"\n6. Mixing Background Music ({BGM_PATH.name}) ducked under narration...")

    actual_dur = get_audio_duration(concatenated_temp)
    print(f"Master Video Duration: {actual_dur:.2f} seconds")

    # BGM ducked at volume=0.12 (-18dB) with fade in and fade out
    filter_music = (
        f"[0:a]volume=1.0[vo];"
        f"[1:a]aloop=loop=-1:size=2e+09,volume=0.12,"
        f"afade=t=in:st=0:d=1.5,"
        f"afade=t=out:st={actual_dur-2.5}:d=2.5[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(concatenated_temp),
        "-i", str(BGM_PATH),
        "-filter_complex", filter_music,
        "-map", "0:v", "-map", "[aout]",
        "-t", str(actual_dur),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(final_shorts_video)
    ]
    subprocess.run(cmd_mix, check=True)

    # Clean up temp file
    if concatenated_temp.exists():
        concatenated_temp.unlink()

    print("\n================================================================")
    print("*** YOUTUBE SHORTS MASTER VIDEO CREATED SUCCESSFULLY! ***")
    print(f"File: {final_shorts_video}")
    print(f"Resolution: 1080x1920 (9:16 Vertical)")
    print(f"Duration: {actual_dur:.2f} seconds (< 60s Shorts limit)")
    print(f"Size: {final_shorts_video.stat().st_size / (1024*1024):.2f} MB")
    print("================================================================")

if __name__ == "__main__":
    main()
