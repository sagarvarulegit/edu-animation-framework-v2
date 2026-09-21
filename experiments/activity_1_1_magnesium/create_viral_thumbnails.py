import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\edu-animation-framework-agent-ready\experiments\activity_1_1_magnesium")
IMG_DIR = BASE_DIR / "images"
OUT_DIR = BASE_DIR / "output"
ART_DIR = Path(r"C:\Users\sunwa\.gemini\antigravity-cli\brain\af617f1a-1b38-4668-bb71-a1b954c9fee3")

FONT_REGULAR = "C:/Windows/Fonts/segoeui.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# M3 Expressive Amber/Yellow/Orange Palette
PRIMARY = (255, 183, 77)       # Amber Gold #FFB74D
TERTIARY = (255, 215, 64)      # Solar Yellow #FFD740
SECONDARY = (255, 140, 0)      # Tangerine #FF8C00
BG_DARK = (18, 14, 10, 255)
CARD_BG = (35, 26, 18, 240)
CREAM = (255, 255, 255)
AMBER_MUTED = (255, 222, 180)

def create_shorts_thumbnail_916():
    """Generates 1080x1920 YouTube Shorts / Reels Cover Thumbnail."""
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), BG_DARK)

    # 1. Background image (Step 4 combustion flame)
    src_img = Image.open(IMG_DIR / "step4_dazzling_burn.jpg").convert("RGB")
    # Ambient blurred background
    bg = src_img.resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(35))
    # Darken slightly for contrast
    dimmer = Image.new("RGBA", (W, H), (14, 10, 8, 160))
    img.paste(bg, (0, 0))
    img = Image.alpha_composite(img, dimmer)
    draw = ImageDraw.Draw(img)

    # 2. Main featured image in center
    feat = src_img.resize((1000, 940), Image.Resampling.LANCZOS)
    mask = Image.new("L", (1000, 940), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, 1000, 940], radius=36, fill=255)
    img.paste(feat, (40, 360), mask)

    # Double glowing border around featured image
    draw.rounded_rectangle([38, 358, 1042, 1302], radius=38, outline=PRIMARY, width=4)
    draw.rounded_rectangle([42, 362, 1038, 1298], radius=34, outline=SECONDARY, width=2)

    # 3. Top Hook Card (M3 Expressive)
    draw.rounded_rectangle([40, 90, 1040, 330], radius=30, fill=CARD_BG, outline=PRIMARY, width=2)
    # NCERT Chip
    draw.rounded_rectangle([70, 115, 520, 170], radius=25, fill=(55, 38, 25, 255), outline=PRIMARY, width=1)
    draw.ellipse([90, 133, 108, 151], fill=PRIMARY)
    draw.text((125, 142), "NCERT CLASS 10 CHEMISTRY", font=get_font(FONT_BOLD, 20), fill=CREAM, anchor="lm")

    # Activity Pill
    draw.rounded_rectangle([780, 115, 1010, 170], radius=25, fill=PRIMARY, outline=SECONDARY, width=1)
    draw.text((895, 142), "ACTIVITY 1.1", font=get_font(FONT_BOLD, 22), fill=(58, 30, 0), anchor="mm")

    # Big Headline
    draw.text((70, 225), "BURNING MAGNESIUM", font=get_font(FONT_BOLD, 46), fill=TERTIARY, anchor="lm")
    draw.text((70, 285), "RIBBON IN AIR!", font=get_font(FONT_BOLD, 44), fill=CREAM, anchor="lm")

    # Flame tag over photo
    draw.rounded_rectangle([80, 400, 520, 465], radius=16, fill=(18, 14, 10, 230), outline=TERTIARY, width=2)
    draw.text((300, 432), "DAZZLING WHITE FLAME!", font=get_font(FONT_BOLD, 22), fill=TERTIARY, anchor="mm")

    # 4. Bottom Exam Hook Card
    draw.rounded_rectangle([40, 1330, 1040, 1780], radius=32, fill=CARD_BG, outline=SECONDARY, width=3)

    # Chemical formula banner
    draw.rounded_rectangle([70, 1360, 1010, 1435], radius=20, fill=(65, 36, 15, 255), outline=PRIMARY, width=2)
    draw.text((540, 1397), "2Mg (s) + O₂ (g)  →  2MgO (s)", font=get_font(FONT_BOLD, 34), fill=TERTIARY, anchor="mm")

    # Question hook
    draw.text((70, 1490), "MOST ASKED BOARD EXAM QUESTION:", font=get_font(FONT_BOLD, 25), fill=PRIMARY, anchor="lm")
    draw.text((70, 1550), "Why clean the ribbon with sandpaper first?", font=get_font(FONT_BOLD, 30), fill=CREAM, anchor="lm")

    # Answer highlight pill
    draw.rounded_rectangle([70, 1610, 1010, 1690], radius=18, fill=(45, 30, 20, 255), outline=TERTIARY, width=1)
    draw.text((540, 1650), "To remove basic magnesium carbonate layer!", font=get_font(FONT_BOLD, 24), fill=AMBER_MUTED, anchor="mm")

    # Bottom badge
    draw.rounded_rectangle([250, 1715, 830, 1765], radius=20, fill=PRIMARY, outline=SECONDARY, width=1)
    draw.text((540, 1740), "STEP-BY-STEP LAB DEMONSTRATION", font=get_font(FONT_BOLD, 20), fill=(58, 30, 0), anchor="mm")

    out_file = OUT_DIR / "thumbnail_shorts_916.jpg"
    img.convert("RGB").save(out_file, quality=95)
    img.convert("RGB").save(ART_DIR / "thumbnail_shorts_916.jpg", quality=95)
    print("Saved 9:16 Shorts Thumbnail:", out_file)
    return out_file

def create_landscape_thumbnail_169():
    """Generates 1280x720 16:9 Standard YouTube Thumbnail / Community Post Card."""
    W, H = 1280, 720
    img = Image.new("RGBA", (W, H), BG_DARK)

    src_img = Image.open(IMG_DIR / "step4_dazzling_burn.jpg").convert("RGB")
    # Crop right side image
    right_img = src_img.resize((680, 680), Image.Resampling.LANCZOS)
    mask = Image.new("L", (680, 680), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, 680, 680], radius=28, fill=255)
    img.paste(right_img, (570, 20), mask)

    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([568, 18, 1252, 702], radius=30, outline=PRIMARY, width=3)

    # Left content area card
    draw.rounded_rectangle([30, 20, 545, 700], radius=28, fill=CARD_BG, outline=SECONDARY, width=2)

    # Badge
    draw.rounded_rectangle([50, 45, 450, 95], radius=20, fill=(55, 38, 25, 255), outline=PRIMARY, width=1)
    draw.text((250, 70), "NCERT CLASS 10 • ACTIVITY 1.1", font=get_font(FONT_BOLD, 18), fill=TERTIARY, anchor="mm")

    # Main Headline
    draw.text((50, 140), "BURNING OF", font=get_font(FONT_BOLD, 36), fill=CREAM, anchor="lm")
    draw.text((50, 190), "MAGNESIUM", font=get_font(FONT_BOLD, 46), fill=TERTIARY, anchor="lm")
    draw.text((50, 240), "RIBBON", font=get_font(FONT_BOLD, 46), fill=PRIMARY, anchor="lm")

    # Formula pill
    draw.rounded_rectangle([50, 290, 525, 355], radius=16, fill=(65, 36, 15, 255), outline=TERTIARY, width=2)
    draw.text((287, 322), "2Mg + O₂  →  2MgO + Light", font=get_font(FONT_BOLD, 22), fill=TERTIARY, anchor="mm")

    # Key Question Box
    draw.rounded_rectangle([50, 385, 525, 570], radius=20, fill=(45, 30, 20, 255), outline=PRIMARY, width=1)
    draw.text((70, 415), "CBSE BOARD EXAM QUESTION:", font=get_font(FONT_BOLD, 18), fill=PRIMARY, anchor="lm")
    draw.text((70, 460), "Why clean with sandpaper?", font=get_font(FONT_BOLD, 22), fill=CREAM, anchor="lm")
    draw.text((70, 510), "Removes inert carbonate layer!", font=get_font(FONT_BOLD, 19), fill=AMBER_MUTED, anchor="lm")

    # Bottom Pill
    draw.rounded_rectangle([50, 600, 525, 665], radius=22, fill=PRIMARY, outline=SECONDARY, width=1)
    draw.text((287, 632), "WATCH STEP-BY-STEP EXPERIMENT", font=get_font(FONT_BOLD, 20), fill=(58, 30, 0), anchor="mm")

    # Badge on top of image
    draw.rounded_rectangle([600, 50, 960, 105], radius=16, fill=(18, 14, 10, 230), outline=TERTIARY, width=2)
    draw.text((780, 77), "DAZZLING WHITE FLAME!", font=get_font(FONT_BOLD, 20), fill=TERTIARY, anchor="mm")

    out_file = OUT_DIR / "thumbnail_landscape_169.jpg"
    img.convert("RGB").save(out_file, quality=95)
    img.convert("RGB").save(ART_DIR / "thumbnail_landscape_169.jpg", quality=95)
    print("Saved 16:9 Landscape Thumbnail:", out_file)
    return out_file

if __name__ == "__main__":
    create_shorts_thumbnail_916()
    create_landscape_thumbnail_169()
    print("Thumbnails successfully created!")
