#!/usr/bin/env python3
"""
Viral Thumbnail Generator for CBSE Class 10 Activity 1.6:
Thermal Decomposition of Lead Nitrate (Pb(NO3)2).
Generates:
1. 9:16 Vertical Thumbnail (1080x1920) for YouTube Shorts shelf & feed
2. 16:9 Landscape Thumbnail (1920x1080) for desktop & search results
Ensures strict visual matching to the hook visual.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR = Path(r"C:\Users\sunwa\.gemini\antigravity-cli\brain\af617f1a-1b38-4668-bb71-a1b954c9fee3")

def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def create_shorts_thumbnail():
    base = Image.open(IMG_DIR / "01_hook_brown_fumes.jpg").convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(base)
    base = enhancer.enhance(1.15)

    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top dark vignette
    for y in range(480):
        alpha = int(220 * (1.0 - y / 480.0)**1.4)
        draw.line([(0, y), (1080, y)], fill=(10, 15, 26, alpha))

    # Bottom dark vignette
    for y in range(1480, 1920):
        alpha = int(230 * ((y - 1480) / 440.0)**1.2)
        draw.line([(0, y), (1080, y)], fill=(10, 15, 26, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Hook Card
    hud.rounded_rectangle([50, 110, 1030, 360], radius=28, fill=(16, 22, 36, 240), outline=(255, 82, 82, 230), width=4)
    hud.text((90, 138), "CBSE CLASS 10 • ACTIVITY 1.6", font=get_font(30, bold=True), fill=(255, 179, 0))
    hud.text((90, 185), "NEVER POINT THIS TUBE", font=get_font(50, bold=True), fill=(255, 255, 255))
    hud.text((90, 248), "AT ANYONE?!", font=get_font(68, bold=True), fill=(255, 82, 82))

    # Floating curiosity badge
    hud.rounded_rectangle([50, 380, 600, 440], radius=16, fill=(255, 179, 0, 245))
    hud.text((70, 392), "WHY DO WHITE CRYSTALS TURN BROWN?!", font=get_font(25, bold=True), fill=(10, 15, 26))

    # Bottom Takeaway Card
    hud.rounded_rectangle([50, 1580, 1030, 1830], radius=28, fill=(16, 22, 36, 240), outline=(0, 229, 255, 220), width=4)
    hud.text((90, 1605), "THERMAL DECOMPOSITION REACTION", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((90, 1648), "White Powder → Yellow PbO + Brown NO2 Fumes", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((90, 1702), "2Pb(NO3)2 → 2PbO + 4NO2 + O2 Gas", font=get_font(30, bold=True), fill=(255, 215, 0))
    hud.text((90, 1755), "Toxic Nitrogen Dioxide Gas • High-Yield Board Viva Question", font=get_font(22), fill=(190, 220, 240))

    out1 = OUT_DIR / "act16_thumbnail_shorts_916.jpg"
    out_art = ARTIFACTS_DIR / "act16_thumbnail_shorts_916.jpg"
    comp.convert("RGB").save(out1, quality=96)
    comp.convert("RGB").save(out_art, quality=96)
    print(f"Saved: {out1.name}")

def create_landscape_thumbnail():
    s1 = Image.open(IMG_DIR / "01_hook_brown_fumes.jpg").convert("RGBA")
    s3 = Image.open(IMG_DIR / "03_reaction_yellow_residue.jpg").convert("RGBA")

    canvas = Image.new("RGBA", (1920, 1080), (12, 16, 26, 255))

    # Left visual: Flame & NO2 Plume Hook
    w1, h1 = s1.size
    crop1 = s1.crop((0, int(h1 * 0.10), w1, int(h1 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop1, (0, 0))

    # Right visual: Macro Yellow Residue
    w3, h3 = s3.size
    crop3 = s3.crop((0, int(h3 * 0.10), w3, int(h3 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop3, (960, 0))

    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Center blend line
    for x in range(920, 1000):
        alpha = int(180 * (1.0 - abs(x - 960) / 40.0))
        draw.line([(x, 0), (x, 1080)], fill=(12, 16, 26, alpha))

    # Dark header vignette
    for y in range(260):
        alpha = int(220 * (1.0 - y / 260.0)**1.3)
        draw.line([(0, y), (1920, y)], fill=(12, 16, 26, alpha))

    # Dark footer vignette
    for y in range(860, 1080):
        alpha = int(230 * ((y - 860) / 220.0)**1.2)
        draw.line([(0, y), (1920, y)], fill=(12, 16, 26, alpha))

    comp = Image.alpha_composite(canvas, overlay)
    hud = ImageDraw.Draw(comp)

    # Big Headline Card Left
    hud.rounded_rectangle([60, 60, 1100, 220], radius=24, fill=(16, 22, 36, 240), outline=(255, 82, 82, 220), width=3)
    hud.text((90, 80), "CBSE CLASS 10 SCIENCE • ACTIVITY 1.6", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((90, 122), "HEATING LEAD NITRATE: TOXIC BROWN FUMES!", font=get_font(42, bold=True), fill=(255, 255, 255))

    # Right Tag
    hud.rounded_rectangle([1520, 60, 1860, 140], radius=20, fill=(255, 179, 0, 245))
    hud.text((1545, 82), "EXAM SPECIAL", font=get_font(28, bold=True), fill=(12, 16, 26))

    # Bottom Equation Card
    hud.rounded_rectangle([60, 890, 1860, 1030], radius=24, fill=(16, 22, 36, 245), outline=(0, 229, 255, 220), width=3)
    hud.text((100, 915), "2Pb(NO3)2 (s) → 2PbO (s, Yellow) + 4NO2 (g, Brown Fumes) + O2 (g)", font=get_font(34, bold=True), fill=(255, 255, 255))
    hud.text((100, 968), "Thermal Decomposition • Decrepitation Crackle • Nitrogen Dioxide Gas", font=get_font(24), fill=(0, 229, 255))

    out2 = OUT_DIR / "act16_thumbnail_landscape_169.jpg"
    out2_art = ARTIFACTS_DIR / "act16_thumbnail_landscape_169.jpg"
    comp.convert("RGB").save(out2, quality=96)
    comp.convert("RGB").save(out2_art, quality=96)
    print(f"Saved: {out2.name}")

if __name__ == "__main__":
    create_shorts_thumbnail()
    create_landscape_thumbnail()
