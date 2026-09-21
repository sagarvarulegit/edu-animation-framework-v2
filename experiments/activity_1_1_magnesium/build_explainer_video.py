#!/usr/bin/env python3
"""
Stitches the Gemini-generated steps of CBSE Activity 1.1 into an explainer video.
Creates high-contrast educational graphic overlays with PIL and renders smooth
Ken Burns pan/zoom clips with FFmpeg, stitching them into a final 1080p video.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OVERLAYS_DIR = BASE_DIR / "overlays"
OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR = BASE_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

# System fonts
FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Yellow-Orange Theme Color Palette
THEME_BG = (18, 14, 10, 255)            # Warm deep charcoal/dark amber background
THEME_CARD_BG = (28, 20, 14, 230)       # Warm dark amber-charcoal card fill
THEME_ORANGE = (249, 115, 22)           # Vivid Flame Orange
THEME_AMBER = (245, 158, 11)            # Warm Amber Gold
THEME_YELLOW = (250, 204, 21)           # Bright Solar Yellow
THEME_CREAM = (254, 243, 199)           # Warm Cream White
THEME_MUTED_AMBER = (253, 230, 138)     # Soft Sandy Amber

STEPS = [
    {
        "id": "step1",
        "num": "01",
        "title": "STEP 1: CLEANING MAGNESIUM RIBBON",
        "badge": "SURFACE PREPARATION",
        "desc": "Rub the dull magnesium ribbon thoroughly with sandpaper before ignition.",
        "scientific_why": "NCERT REASON: Removes the protective layer of basic magnesium carbonate formed by air.",
        "image": "step1_clean_ribbon.jpg",
        "formula": "Mg (s) [Clean Metallic Surface]",
        "duration": 6,
        "zoom": "in"
    },
    {
        "id": "step2",
        "num": "02",
        "title": "STEP 2: HOLDING WITH CRUCIBLE TONGS",
        "badge": "LABORATORY SAFETY",
        "desc": "Grip the clean silver ribbon securely with tongs; keep a watch glass ready below.",
        "scientific_why": "SAFETY PROTOCOL: Wear eye protection goggles and keep burning ribbon at arm's length.",
        "image": "step2_grip_tongs.jpg",
        "formula": "Mg (s) + Laboratory Crucible Tongs",
        "duration": 6,
        "zoom": "pan_left"
    },
    {
        "id": "step3",
        "num": "03",
        "title": "STEP 3: HEATING IN BUNSEN FLAME",
        "badge": "ACTIVATION ENERGY",
        "desc": "Introduce the tip of the ribbon into the hot blue cone of the Bunsen burner flame.",
        "scientific_why": "THERMAL ACTIVATION: Heating provides activation energy to reach the ignition point (~473 °C).",
        "image": "step3_heat_flame.jpg",
        "formula": "Mg (s) + Heat (Δ)",
        "duration": 6,
        "zoom": "in"
    },
    {
        "id": "step4",
        "num": "04",
        "title": "STEP 4: DAZZLING WHITE FLAME COMBUSTION",
        "badge": "VIGOROUS OXIDATION",
        "desc": "The ribbon bursts into an intense, dazzling blinding white flame with white smoke.",
        "scientific_why": "EXOTHERMIC REACTION: Magnesium reacts vigorously with atmospheric oxygen, releasing high energy.",
        "image": "step4_dazzling_burn.jpg",
        "formula": "2Mg (s) + O₂ (g)  →  2MgO (s) + Light + Heat",
        "duration": 6,
        "zoom": "out"
    },
    {
        "id": "step5",
        "num": "05",
        "title": "STEP 5: COLLECTING MAGNESIUM OXIDE ASH",
        "badge": "PRODUCT FORMATION",
        "desc": "Collect the white powder formed into a watch glass placed on a ceramic pad.",
        "scientific_why": "NEW CHEMICAL IDENTITY: The white powder is Magnesium Oxide (MgO), chemically distinct from Mg.",
        "image": "step5_collect_ash.jpg",
        "formula": "MgO (s) [White Insoluble Powder]",
        "duration": 6,
        "zoom": "in"
    },
    {
        "id": "step6",
        "num": "06",
        "title": "STEP 6: TESTING WITH RED LITMUS PAPER",
        "badge": "CHEMICAL ANALYSIS",
        "desc": "Add a few drops of water to the MgO ash, then test the moist mixture with red litmus paper.",
        "scientific_why": "BASIC NATURE: Red litmus turns BLUE, proving metallic oxides are basic in nature!",
        "image": "step6_litmus_test.jpg",
        "formula": "MgO + H₂O  →  Mg(OH)₂ (Basic: pH > 7)",
        "duration": 7,
        "zoom": "in"
    }
]

def create_intro_card():
    img = Image.new("RGBA", (1920, 1080), THEME_BG)

    # Gradient background glow (radiant warm orange & yellow)
    glow = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([450, 160, 1470, 920], fill=(249, 115, 22, 38))
    glow_draw.ellipse([650, 300, 1270, 780], fill=(250, 204, 21, 25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Tag (Yellow-Orange theme badge)
    font_badge = get_font(FONT_BOLD, 22)
    draw.rounded_rectangle([700, 220, 1220, 270], radius=25, fill=(35, 24, 16, 230), outline=(245, 158, 11, 200), width=2)
    draw.text((960, 245), "NCERT CLASS 10 SCIENCE • CHAPTER 1", font=font_badge, fill=THEME_YELLOW, anchor="mm")

    # Main Title
    font_title = get_font(FONT_BOLD, 64)
    draw.text((960, 360), "Activity 1.1: Burning of Magnesium Ribbon", font=font_title, fill=(255, 255, 255), anchor="mm")

    # Subtitle
    font_sub = get_font(FONT_SEMI, 30)
    draw.text((960, 440), "Step-by-Step Visual Experiment & Chemical Analysis", font=font_sub, fill=THEME_MUTED_AMBER, anchor="mm")

    # Central Card with 4 Key Goals
    draw.rounded_rectangle([360, 520, 1560, 840], radius=20, fill=THEME_CARD_BG, outline=(249, 115, 22, 120), width=2)

    goals = [
        ("01", "Surface Preparation", "Clean Mg ribbon with sandpaper to remove oxide coating"),
        ("02", "Thermal Ignition", "Heat in Bunsen burner to reach ignition temperature"),
        ("03", "Vigorous Oxidation", "Observe dazzling white flame & collect white ash"),
        ("04", "Chemical Litmus Test", "Prove basic nature: Red litmus turns blue with Mg(OH)2")
    ]

    font_num = get_font(FONT_BOLD, 28)
    font_gt = get_font(FONT_BOLD, 22)
    font_gd = get_font(FONT_REGULAR, 16)

    positions = [(400, 560), (980, 560), (400, 690), (980, 690)]
    for (num, title, desc), (x, y) in zip(goals, positions):
        draw.rounded_rectangle([x, y, x + 540, y + 100], radius=14, fill=(45, 32, 22, 170), outline=(245, 158, 11, 90), width=1)
        draw.ellipse([x + 20, y + 26, x + 68, y + 74], fill=(249, 115, 22, 45), outline=THEME_ORANGE, width=2)
        draw.text((x + 44, y + 50), num, font=font_num, fill=THEME_YELLOW, anchor="mm")
        draw.text((x + 85, y + 36), title, font=font_gt, fill=(255, 255, 255))
        draw.text((x + 85, y + 66), desc, font=font_gd, fill=THEME_MUTED_AMBER)

    # Bottom pill
    font_bot = get_font(FONT_REGULAR, 20)
    draw.text((960, 920), "AI-Generated Photographic Steps • Powered by Gemini & Antigravity", font=font_bot, fill=(217, 160, 110), anchor="mm")

    out_file = OVERLAYS_DIR / "intro_card.png"
    img.save(out_file)
    return out_file

def create_step_overlay(step):
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Top Left Badge: Curriculum (Yellow-Orange theme)
    draw.rounded_rectangle([60, 50, 480, 105], radius=16, fill=(25, 18, 13, 235), outline=(245, 158, 11, 190), width=2)
    draw.ellipse([85, 70, 99, 84], fill=THEME_YELLOW)
    font_badge = get_font(FONT_BOLD, 18)
    draw.text((115, 78), "CBSE CLASS 10  •  ACTIVITY 1.1", font=font_badge, fill=THEME_CREAM, anchor="lm")

    # Top Right Badge: Step Number & Phase
    draw.rounded_rectangle([1460, 50, 1860, 105], radius=16, fill=(25, 18, 13, 235), outline=THEME_ORANGE, width=2)
    draw.text((1500, 78), f"STEP {step['num']} / 06  •  {step['badge']}", font=font_badge, fill=THEME_YELLOW, anchor="lm")

    # Bottom Glassmorphic Educational Banner
    banner_y = 800
    # Warm amber/charcoal glassmorphic background
    draw.rounded_rectangle([60, banner_y, 1860, banner_y + 220], radius=24, fill=(18, 13, 9, 238), outline=(249, 115, 22, 160), width=2)

    # Step Title in Bright Solar Yellow
    font_step_title = get_font(FONT_BOLD, 30)
    draw.text((100, banner_y + 40), step["title"], font=font_step_title, fill=THEME_YELLOW, anchor="lm")

    # Chemical Formula Pill on Right of Banner Title (Orange accent)
    font_formula = get_font(FONT_BOLD, 22)
    formula_w = font_formula.getlength(step["formula"]) + 40
    draw.rounded_rectangle([1860 - 40 - formula_w, banner_y + 20, 1860 - 40, banner_y + 65], radius=12, fill=(249, 115, 22, 45), outline=THEME_ORANGE, width=2)
    draw.text((1860 - 40 - formula_w / 2, banner_y + 42), step["formula"], font=font_formula, fill=THEME_YELLOW, anchor="mm")

    # Action Description
    font_desc = get_font(FONT_BOLD, 22)
    draw.text((100, banner_y + 90), step["desc"], font=font_desc, fill=(255, 255, 255), anchor="lm")

    # Scientific Reasoning / Concept
    font_why = get_font(FONT_REGULAR, 20)
    draw.text((100, banner_y + 140), step["scientific_why"], font=font_why, fill=THEME_MUTED_AMBER, anchor="lm")

    # Vibrant Yellow-Orange progress bar at bottom of banner
    step_idx = int(step["num"])
    progress_w = int((1860 - 60) * (step_idx / 6))
    draw.rounded_rectangle([60, banner_y + 214, 60 + progress_w, banner_y + 220], radius=3, fill=THEME_AMBER)

    out_file = OVERLAYS_DIR / f"overlay_{step['id']}.png"
    img.save(out_file)
    return out_file

def create_outro_card():
    img = Image.new("RGBA", (1920, 1080), THEME_BG)

    # Warm solar/amber radiant glow
    glow = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([450, 160, 1470, 920], fill=(249, 115, 22, 38))
    glow_draw.ellipse([650, 300, 1270, 780], fill=(250, 204, 21, 25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Tag
    font_badge = get_font(FONT_BOLD, 22)
    draw.rounded_rectangle([720, 140, 1200, 190], radius=25, fill=(35, 24, 16, 230), outline=(245, 158, 11, 200), width=2)
    draw.text((960, 165), "EXAM RECAP & KEY CONCLUSIONS", font=font_badge, fill=THEME_YELLOW, anchor="mm")

    # Main Title
    font_title = get_font(FONT_BOLD, 52)
    draw.text((960, 250), "Activity 1.1 — Summary & Board Tips", font=font_title, fill=(255, 255, 255), anchor="mm")

    # 3 Summary Cards (Warm Orange, Amber Gold, and Radiant Yellow)
    cards = [
        ("OBSERVATION", [
            "Burns with an intense,",
            "dazzling white flame and",
            "dense white smoke.",
            "",
            "Leaves behind a pure",
            "white powder: Magnesium",
            "Oxide (MgO)."
        ], THEME_AMBER),
        ("REACTION TYPE", [
            "Combination Reaction:",
            "2Mg(s) + O₂(g) → 2MgO(s)",
            "Two reactants combine to",
            "form a single product.",
            "",
            "Exothermic Reaction:",
            "Releases light & heat."
        ], THEME_ORANGE),
        ("CHEMICAL NATURE", [
            "Basic Metallic Oxide:",
            "MgO + H₂O → Mg(OH)₂",
            "(Magnesium Hydroxide)",
            "",
            "Litmus Test Result:",
            "Turns moist RED litmus",
            "distinctly BLUE (pH > 7)."
        ], THEME_YELLOW)
    ]

    font_ct = get_font(FONT_BOLD, 22)
    font_cb = get_font(FONT_REGULAR, 20)

    card_xs = [80, 680, 1280]
    for (ctitle, lines, col), cx in zip(cards, card_xs):
        draw.rounded_rectangle([cx, 330, cx + 560, 790], radius=20, fill=THEME_CARD_BG, outline=col, width=2)
        draw.rounded_rectangle([cx + 30, 355, cx + 530, 410], radius=10, fill=(col[0], col[1], col[2], 40))
        draw.text((cx + 280, 382), ctitle, font=font_ct, fill=col, anchor="mm")
        
        curr_y = 445
        for line in lines:
            draw.text((cx + 40, curr_y), line, font=font_cb, fill=(245, 240, 230))
            curr_y += 36

    # CBSE Tip Banner at bottom (Yellow-Orange theme)
    draw.rounded_rectangle([80, 830, 1840, 930], radius=16, fill=(35, 24, 16, 230), outline=THEME_ORANGE, width=2)
    font_tip = get_font(FONT_BOLD, 20)
    font_tip_desc = get_font(FONT_REGULAR, 19)
    draw.text((120, 858), "★ FREQUENT CBSE QUESTION:", font=font_tip, fill=THEME_YELLOW)
    draw.text((120, 892), "Why is magnesium ribbon cleaned before burning? -> To remove the unreactive layer of basic magnesium carbonate that prevents burning.", font=font_tip_desc, fill=(255, 255, 255))

    out_file = OVERLAYS_DIR / "outro_card.png"
    img.save(out_file)
    return out_file

def render_image_clip(img_path, overlay_path, out_clip_path, duration=6, zoom="in"):
    """
    Renders a single step image into an MP4 clip with smooth Ken Burns camera
    motion and composites the transparent educational overlay on top.
    """
    frames = duration * 30

    if zoom == "in":
        # Slow zoom into center
        filter_str = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"zoompan=z='min(zoom+0.0010,1.10)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
        )
    elif zoom == "out":
        # Slow zoom out
        filter_str = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"zoompan=z='if(lte(zoom,1.0),1.10,max(1.0,zoom-0.0010))':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
        )
    else:
        # Subtle horizontal pan
        filter_str = (
            f"scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,"
            f"zoompan=z='1.06':d={frames}:x='(in/{frames})*(iw-iw/zoom)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=30"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-loop", "1", "-i", str(overlay_path),
        "-filter_complex",
        f"[0:v]{filter_str}[bg];[bg][1:v]overlay=0:0:enable='between(t,0,{duration})'[v]",
        "-map", "[v]",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(out_clip_path)
    ]
    subprocess.run(cmd, check=True)

def render_card_clip(card_img_path, out_clip_path, duration=5):
    """Renders a static card clip with subtle fade in/out."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(card_img_path),
        "-vf", f"scale=1920:1080,fade=t=in:st=0:d=0.5,fade=t=out:st={duration-0.5}:d=0.5",
        "-t", str(duration),
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(out_clip_path)
    ]
    subprocess.run(cmd, check=True)

def main():
    print("1. Creating Graphic Overlays and Title Cards...")
    intro_card = create_intro_card()
    outro_card = create_outro_card()

    clip_paths = []

    # Render Intro Clip
    intro_clip = CLIPS_DIR / "00_intro.mp4"
    print("2. Rendering Intro Clip...")
    render_card_clip(intro_card, intro_clip, duration=5)
    clip_paths.append(intro_clip)

    # Render each Step Clip
    for i, step in enumerate(STEPS):
        print(f"3.{i+1} Rendering Step {step['num']}: {step['title']}...")
        overlay = create_step_overlay(step)
        img_file = IMG_DIR / step["image"]
        step_clip = CLIPS_DIR / f"{step['num']}_{step['id']}.mp4"
        render_image_clip(img_file, overlay, step_clip, duration=step["duration"], zoom=step["zoom"])
        clip_paths.append(step_clip)

    # Render Outro Clip
    outro_clip = CLIPS_DIR / "07_outro.mp4"
    print("4. Rendering Outro Clip...")
    render_card_clip(outro_card, outro_clip, duration=6)
    clip_paths.append(outro_clip)

    # Stitch all clips together
    print("5. Stitching all clips into master video...")
    concat_list = CLIPS_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            # Escape path for FFmpeg concat demuxer
            safe_p = str(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    final_video = OUT_DIR / "activity_1_1_burning_magnesium_ribbon.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        str(final_video)
    ]
    subprocess.run(cmd_concat, check=True)
    print(f"\n=======================================================")
    print(f"*** MASTER VIDEO CREATED SUCCESSFULLY! ***")
    print(f"File: {final_video}")
    print(f"Total Size: {final_video.stat().st_size / (1024*1024):.2f} MB")
    print(f"=======================================================\n")

if __name__ == "__main__":
    main()
