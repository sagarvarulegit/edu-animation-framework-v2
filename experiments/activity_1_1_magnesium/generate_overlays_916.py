import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\edu-animation-framework-agent-ready\experiments\activity_1_1_magnesium")
OVERLAYS_916_DIR = BASE_DIR / "overlays_916"
OVERLAYS_916_DIR.mkdir(parents=True, exist_ok=True)
ART_DIR = Path(r"C:\Users\sunwa\.gemini\antigravity-cli\brain\af617f1a-1b38-4668-bb71-a1b954c9fee3")

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# Yellow-Orange Theme Palette
THEME_BG = (18, 14, 10, 255)
THEME_CARD_BG = (28, 20, 14, 235)
THEME_ORANGE = (249, 115, 22)       # Flame Orange
THEME_AMBER = (245, 158, 11)        # Warm Amber Gold
THEME_YELLOW = (250, 204, 21)       # Solar Yellow
THEME_CREAM = (254, 243, 199)       # Warm Cream White
THEME_MUTED_AMBER = (253, 230, 138) # Soft Muted Amber

def create_intro_card_916():
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), THEME_BG)
    
    # Warm radial glow in center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([100, 300, 980, 1300], fill=(249, 115, 22, 35))
    glow_draw.ellipse([250, 450, 830, 1150], fill=(250, 204, 21, 25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Tag
    font_badge = get_font(FONT_BOLD, 22)
    draw.rounded_rectangle([240, 140, 840, 200], radius=25, fill=(35, 24, 16, 230), outline=THEME_AMBER, width=2)
    draw.text((540, 170), "NCERT CLASS 10 SCIENCE • CH 1", font=font_badge, fill=THEME_YELLOW, anchor="mm")

    # Hook / Title
    font_sub = get_font(FONT_BOLD, 36)
    draw.text((540, 260), "ACTIVITY 1.1", font=font_sub, fill=THEME_ORANGE, anchor="mm")
    font_title = get_font(FONT_BOLD, 54)
    draw.text((540, 330), "Burning of", font=font_title, fill=(255, 255, 255), anchor="mm")
    draw.text((540, 400), "Magnesium Ribbon", font=font_title, fill=THEME_YELLOW, anchor="mm")

    font_caption = get_font(FONT_SEMI, 28)
    draw.text((540, 470), "Complete Lab Demonstration in 6 Steps", font=font_caption, fill=THEME_MUTED_AMBER, anchor="mm")

    # 4 Vertical Goal Cards
    goals = [
        ("01", "Surface Preparation", "Sandpaper removes unreactive MgCO3 layer"),
        ("02", "Thermal Ignition", "Heat in Bunsen flame to ignition temp"),
        ("03", "Vigorous Oxidation", "Blinding white flame + MgO white ash"),
        ("04", "Litmus Analysis", "Red litmus turns blue -> Basic oxide!")
    ]

    card_y = 540
    font_num = get_font(FONT_BOLD, 32)
    font_gt = get_font(FONT_BOLD, 26)
    font_gd = get_font(FONT_REGULAR, 20)

    for num, title, desc in goals:
        draw.rounded_rectangle([60, card_y, 1020, card_y + 160], radius=20, fill=THEME_CARD_BG, outline=(249, 115, 22, 120), width=2)
        # Num circle
        draw.ellipse([90, card_y + 35, 170, card_y + 115], fill=(249, 115, 22, 45), outline=THEME_ORANGE, width=2)
        draw.text((130, card_y + 75), num, font=font_num, fill=THEME_YELLOW, anchor="mm")
        # Text
        draw.text((200, card_y + 45), title, font=font_gt, fill=(255, 255, 255), anchor="lm")
        draw.text((200, card_y + 105), desc, font=font_gd, fill=THEME_MUTED_AMBER, anchor="lm")
        card_y += 190

    # Bottom Branding Pill
    draw.rounded_rectangle([200, 1700, 880, 1760], radius=25, fill=(35, 24, 16, 230), outline=(245, 158, 11, 150), width=2)
    font_bot = get_font(FONT_BOLD, 22)
    draw.text((540, 1730), "CBSE EXPERIMENT LAB • SHORTS", font=font_bot, fill=THEME_YELLOW, anchor="mm")

    out_file = OVERLAYS_916_DIR / "intro_card_916.png"
    img.save(out_file)
    img.save(ART_DIR / "test_intro_916.png")
    return out_file

def create_outro_card_916():
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), THEME_BG)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([100, 300, 980, 1300], fill=(249, 115, 22, 35))
    glow_draw.ellipse([250, 450, 830, 1150], fill=(250, 204, 21, 25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # Top Tag
    font_badge = get_font(FONT_BOLD, 22)
    draw.rounded_rectangle([260, 130, 820, 190], radius=25, fill=(35, 24, 16, 230), outline=THEME_AMBER, width=2)
    draw.text((540, 160), "EXAM RECAP & KEY SUMMARY", font=font_badge, fill=THEME_YELLOW, anchor="mm")

    font_title = get_font(FONT_BOLD, 48)
    draw.text((540, 250), "Activity 1.1 Key Takeaways", font=font_title, fill=(255, 255, 255), anchor="mm")

    cards = [
        ("OBSERVATION", [
            "• Burns with an intense, dazzling white flame",
            "• Dense white fumes of Magnesium Oxide",
            "• White ash collected in watch glass"
        ], THEME_AMBER),
        ("REACTION TYPE", [
            "• Combination: 2Mg (s) + O₂ (g) → 2MgO (s)",
            "• Exothermic: Releases large amount of heat & light",
            "• Two reactants form a single product"
        ], THEME_ORANGE),
        ("CHEMICAL NATURE", [
            "• Metallic oxides are BASIC in nature",
            "• MgO + H₂O → Mg(OH)₂ (Magnesium Hydroxide)",
            "• Turns moist red litmus paper distinct BLUE"
        ], THEME_YELLOW)
    ]

    card_y = 320
    font_ct = get_font(FONT_BOLD, 26)
    font_cb = get_font(FONT_REGULAR, 22)

    for ctitle, lines, col in cards:
        draw.rounded_rectangle([60, card_y, 1020, card_y + 260], radius=20, fill=THEME_CARD_BG, outline=col, width=2)
        # Header banner inside card
        draw.rounded_rectangle([90, card_y + 20, 460, card_y + 68], radius=12, fill=(col[0], col[1], col[2], 50), outline=col, width=1)
        draw.text((275, card_y + 44), ctitle, font=font_ct, fill=col, anchor="mm")

        line_y = card_y + 90
        for l in lines:
            draw.text((90, line_y), l, font=font_cb, fill=THEME_CREAM)
            line_y += 44
        card_y += 290

    # Frequent CBSE Question Box
    draw.rounded_rectangle([60, 1260, 1020, 1540], radius=20, fill=(35, 24, 16, 240), outline=THEME_ORANGE, width=2)
    font_qt = get_font(FONT_BOLD, 26)
    font_qa = get_font(FONT_REGULAR, 22)
    draw.text((100, 1300), "★ FREQUENT CBSE BOARD QUESTION:", font=font_qt, fill=THEME_YELLOW, anchor="lm")
    draw.text((100, 1360), "Q: Why is magnesium ribbon cleaned before burning?", font=font_qa, fill=THEME_CREAM, anchor="lm")
    draw.text((100, 1420), "Ans: To remove the protective layer of basic magnesium", font=font_qa, fill=THEME_MUTED_AMBER, anchor="lm")
    draw.text((100, 1465), "carbonate that prevents contact with oxygen.", font=font_qa, fill=THEME_MUTED_AMBER, anchor="lm")

    # Bottom CTA Pill
    draw.rounded_rectangle([200, 1680, 880, 1750], radius=25, fill=(35, 24, 16, 230), outline=THEME_YELLOW, width=2)
    draw.text((540, 1715), "Subscribe & Follow for Class 10 Practicals!", font=font_badge, fill=THEME_YELLOW, anchor="mm")

    out_file = OVERLAYS_916_DIR / "outro_card_916.png"
    img.save(out_file)
    img.save(ART_DIR / "test_outro_916.png")
    return out_file

def create_step_overlay_916(step):
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Top Header Safe Area
    # Curriculum Badge
    draw.rounded_rectangle([50, 100, 480, 160], radius=16, fill=(25, 18, 13, 235), outline=THEME_AMBER, width=2)
    draw.ellipse([75, 120, 93, 138], fill=THEME_YELLOW)
    font_badge = get_font(FONT_BOLD, 18)
    draw.text((110, 130), "CBSE 10  •  ACTIVITY 1.1", font=font_badge, fill=THEME_CREAM, anchor="lm")

    # Step Pill
    draw.rounded_rectangle([720, 100, 1030, 160], radius=16, fill=(25, 18, 13, 235), outline=THEME_ORANGE, width=2)
    draw.text((750, 130), f"STEP {step['num']} OF 06", font=font_badge, fill=THEME_YELLOW, anchor="lm")

    # Step Title and Badge
    font_step_title = get_font(FONT_BOLD, 36)
    font_badge_cat = get_font(FONT_BOLD, 20)
    draw.text((50, 210), step["title_short"], font=font_step_title, fill=THEME_YELLOW, anchor="lm")
    draw.rounded_rectangle([50, 250, 50 + len(step['badge']) * 14 + 40, 295], radius=10, fill=(249, 115, 22, 50), outline=THEME_ORANGE, width=1)
    draw.text((65, 272), step["badge"], font=font_badge_cat, fill=THEME_ORANGE, anchor="lm")

    # Center Frame for Image (Window is x=50 to 1030, y=340 to 1260 -> 980x920)
    # Draw glowing window frame
    draw.rounded_rectangle([48, 338, 1032, 1262], radius=24, outline=THEME_ORANGE, width=3)

    # Bottom Information Card (y=1290 to 1740)
    card_y = 1290
    draw.rounded_rectangle([50, card_y, 1030, 1740], radius=24, fill=(18, 13, 9, 240), outline=(249, 115, 22, 160), width=2)

    # Chemical Formula Pill inside bottom card
    font_formula = get_font(FONT_BOLD, 26)
    draw.rounded_rectangle([80, card_y + 25, 990, card_y + 85], radius=14, fill=(249, 115, 22, 50), outline=THEME_AMBER, width=2)
    draw.text((540, card_y + 55), step["formula"], font=font_formula, fill=THEME_YELLOW, anchor="mm")

    # Action Description
    font_desc = get_font(FONT_BOLD, 26)
    draw.text((80, card_y + 130), step["desc_short"], font=font_desc, fill=(255, 255, 255), anchor="lm")

    # Scientific Reasoning / Concept
    font_why = get_font(FONT_REGULAR, 22)
    draw.text((80, card_y + 210), step["why_short_1"], font=font_why, fill=THEME_MUTED_AMBER, anchor="lm")
    if "why_short_2" in step:
        draw.text((80, card_y + 255), step["why_short_2"], font=font_why, fill=THEME_MUTED_AMBER, anchor="lm")

    # Progress bar at bottom of card
    step_idx = int(step["num"])
    progress_w = int((980) * (step_idx / 6))
    draw.rounded_rectangle([50, 1732, 50 + progress_w, 1740], radius=4, fill=THEME_AMBER)

    out_file = OVERLAYS_916_DIR / f"overlay_916_{step['id']}.png"
    img.save(out_file)
    return out_file

if __name__ == "__main__":
    print("Testing 9:16 Intro & Outro creation...")
    create_intro_card_916()
    create_outro_card_916()
    print("Done!")
