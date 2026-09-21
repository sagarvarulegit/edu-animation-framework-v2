import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\edu-animation-framework-agent-ready\experiments\activity_1_1_magnesium")
OVERLAYS_M3_DIR = BASE_DIR / "overlays_m3"
OVERLAYS_M3_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR = Path(r"C:\Users\sunwa\.gemini\antigravity-cli\brain\af617f1a-1b38-4668-bb71-a1b954c9fee3")

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Google Material 3 Expressive Tonal Palette (Warm Amber / Solar Seed)
M3 = {
    "primary": (255, 183, 77),             # #FFB74D (Tone 80 Amber)
    "onPrimary": (58, 30, 0),              # #3A1E00 (Tone 20 Dark Brown)
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

def create_m3_step_overlay(step):
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

    # M3 Suggestion Badge (Shape: Small Pill 12px)
    font_badge = get_font(FONT_BOLD, 17)
    badge_w = font_badge.getlength(step["badge"]) + 28
    draw.rounded_rectangle([72, 244, 72 + badge_w, 282], radius=14, fill=M3["secondaryContainer"] + (255,), outline=M3["secondary"], width=1)
    draw.text((72 + badge_w / 2, 263), step["badge"], font=font_badge, fill=M3["onSecondaryContainer"], anchor="mm")

    # 2. Center Image Frame: M3 Surface Container (Extra Large Radius 32px)
    draw.rounded_rectangle([46, 336, 1034, 1264], radius=32, outline=M3["primary"], width=2)
    # Subtle inner accent border for M3 depth
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
    # In M3: Track has rounded ends in surfaceContainerLowest, active bar has rounded pill ends
    track_y = card_y2 - 14
    track_x1, track_x2 = 72, 1008
    total_w = track_x2 - track_x1
    step_idx = int(step["num"])
    active_w = int(total_w * (step_idx / 6))

    # Inactive track
    draw.rounded_rectangle([track_x1, track_y, track_x2, track_y + 8], radius=4, fill=M3["surfaceContainerLowest"] + (255,))
    # Active indicator
    draw.rounded_rectangle([track_x1, track_y, track_x1 + active_w, track_y + 8], radius=4, fill=M3["primary"] + (255,))

    out_file = OVERLAYS_M3_DIR / f"overlay_m3_{step['id']}.png"
    img.save(out_file)
    return out_file

def create_m3_intro_card():
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
    thumb_path = BASE_DIR / "images" / "step4_dazzling_burn.jpg"
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

    out_file = OVERLAYS_M3_DIR / "intro_card_m3.png"
    img.save(out_file)
    img.save(ART_DIR / "test_intro_m3.png")
    return out_file

def create_m3_outro_card():
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

    out_file = OVERLAYS_M3_DIR / "outro_card_m3.png"
    img.save(out_file)
    img.save(ART_DIR / "test_outro_m3.png")
    return out_file

if __name__ == "__main__":
    print("Generating M3 Expressive test cards...")
    create_m3_intro_card()
    create_m3_outro_card()
    
    step4 = {
        "id": "step4",
        "num": "04",
        "title_short": "4. Dazzling White Flame",
        "badge": "VIGOROUS OXIDATION",
        "formula": "2Mg (s) + O₂ (g)  →  2MgO (s) + Light + Heat",
        "desc_short": "Bursts into an intense, dazzling blinding white flame!",
        "why_1": "EXOTHERMIC REACTION: Magnesium vigorously combines",
        "why_2": "with atmospheric oxygen releasing light & heat.",
        "image": "step4_dazzling_burn.jpg"
    }
    ov = create_m3_step_overlay(step4)
    print("Overlay created:", ov)
