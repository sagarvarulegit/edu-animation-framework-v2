#!/usr/bin/env python3
"""
Viral Thumbnail Generator for CBSE Class 10 Activity 1.4:
Generates:
1. 9:16 Vertical Thumbnail (1080x1920) for YouTube Shorts shelf & feed
2. 16:9 Landscape Thumbnail (1920x1080) for desktop & YouTube search
Ensures strict visual matching to the hook (steaming quicklime rocks).
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
OUT_DIR = BASE_DIR / "output"
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
    # 9:16 Vertical (1080x1920)
    base = Image.open(IMG_DIR / "01_hook_steam.jpg").convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    enhancer = ImageEnhance.Contrast(base)
    base = enhancer.enhance(1.15)

    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Top Dark Gradient Vignette for text contrast
    for y in range(480):
        alpha = int(220 * (1.0 - y / 480.0)**1.4)
        draw.line([(0, y), (1080, y)], fill=(10, 15, 26, alpha))

    # Bottom Dark Gradient Vignette
    for y in range(1500, 1920):
        alpha = int(230 * ((y - 1500) / 420.0)**1.2)
        draw.line([(0, y), (1080, y)], fill=(10, 15, 26, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Hook Card
    hud.rounded_rectangle([50, 110, 1030, 360], radius=28, fill=(16, 22, 36, 240), outline=(255, 179, 0, 230), width=4)
    hud.text((90, 138), "CBSE CLASS 10 • ACTIVITY 1.4", font=get_font(30, bold=True), fill=(255, 179, 0))
    hud.text((90, 185), "COLD WATER MAKES", font=get_font(52, bold=True), fill=(255, 255, 255))
    hud.text((90, 248), "ROCKS BOIL?!", font=get_font(68, bold=True), fill=(255, 82, 82))

    # Floating curiosity badge
    hud.rounded_rectangle([50, 380, 520, 440], radius=16, fill=(255, 179, 0, 245))
    hud.text((70, 392), "WHY DOES IT BOIL?!", font=get_font(26, bold=True), fill=(10, 15, 26))

    # Bottom Takeaway Card
    hud.rounded_rectangle([50, 1600, 1030, 1830], radius=28, fill=(16, 22, 36, 240), outline=(0, 229, 255, 220), width=4)
    hud.text((90, 1625), "EXOTHERMIC COMBINATION REACTION", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((90, 1668), "Quicklime + Water → Slaked Lime", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((90, 1722), "CaO + H2O → Ca(OH)2 + Massive Heat", font=get_font(30, bold=True), fill=(255, 215, 0))
    hud.text((90, 1775), "Class 10 Board Exam Most Repeated Question", font=get_font(22), fill=(190, 220, 240))

    out1 = OUT_DIR / "act14_thumbnail_shorts_916.jpg"
    out_art = ARTIFACTS_DIR / "act14_thumbnail_shorts_916.jpg"
    comp.convert("RGB").save(out1, quality=96)
    comp.convert("RGB").save(out_art, quality=96)
    print(f"Saved: {out1.name}")

def create_landscape_thumbnail():
    # 16:9 Landscape (1920x1080)
    # Using Scene 1 and Scene 3 combined / side-by-side or wide composite
    s1 = Image.open(IMG_DIR / "01_hook_steam.jpg").convert("RGBA")
    s3 = Image.open(IMG_DIR / "03_reaction_slaking.jpg").convert("RGBA")
    s4 = Image.open(IMG_DIR / "04_takeaway_exothermic.jpg").convert("RGBA")

    # Crop and place side-by-side
    canvas = Image.new("RGBA", (1920, 1080), (12, 16, 26, 255))

    # Left visual: Steam Hook (01_hook_steam.jpg)
    w1, h1 = s1.size
    crop1 = s1.crop((0, int(h1 * 0.15), w1, int(h1 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop1, (0, 0))

    # Right visual: Slaking Boiling & Thermometer (03_reaction_slaking.jpg)
    w3, h3 = s3.size
    crop3 = s3.crop((0, int(h3 * 0.15), w3, int(h3 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop3, (960, 0))

    # Dark overlay / gradient in center and bottom for punchy typography
    overlay = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Center blend line
    for x in range(920, 1000):
        alpha = int(180 * (1.0 - abs(x - 960) / 40.0))
        draw.line([(x, 0), (x, 1080)], fill=(12, 16, 26, alpha))

    # Dark header vignette
    for y in range(260):
        alpha = int(220 * (1.0 - y / 260.0)**1.3)
        draw.line([(0, y), (1920, y)], fill=(10, 15, 26, alpha))

    # Dark footer vignette
    for y in range(800, 1080):
        alpha = int(230 * ((y - 800) / 280.0)**1.2)
        draw.line([(0, y), (1920, y)], fill=(10, 15, 26, alpha))

    comp = Image.alpha_composite(canvas, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Left Badge
    hud.rounded_rectangle([60, 40, 680, 100], radius=16, fill=(255, 179, 0, 245))
    hud.text((85, 52), "CBSE CLASS 10 • ACTIVITY 1.4", font=get_font(34, bold=True), fill=(10, 15, 26))

    # Big Headline on Left
    hud.rounded_rectangle([60, 120, 940, 310], radius=24, fill=(16, 22, 36, 235), outline=(255, 82, 82, 220), width=4)
    hud.text((90, 140), "COLD WATER MAKES", font=get_font(44, bold=True), fill=(255, 255, 255))
    hud.text((90, 195), "ROCKS BOIL?!", font=get_font(64, bold=True), fill=(255, 82, 82))

    # Floating temperature spike alert badge
    hud.rounded_rectangle([1380, 40, 1860, 120], radius=16, fill=(255, 60, 30, 245))
    hud.text((1410, 58), "▲ 84.8°C HEAT SPIKE!", font=get_font(36, bold=True), fill=(255, 255, 255))

    # Bottom Wide Card
    hud.rounded_rectangle([60, 860, 1860, 1020], radius=24, fill=(16, 22, 36, 245), outline=(0, 229, 255, 220), width=4)
    hud.text((100, 880), "EXOTHERMIC COMBINATION REACTION: QUICKLIME + WATER → SLAKED LIME", font=get_font(28, bold=True), fill=(0, 229, 255))
    hud.text((100, 924), "CaO + H2O → Ca(OH)2 + Intense Heat Released  •  Board Exam 100% Viva Takeaway", font=get_font(32, bold=True), fill=(255, 255, 255))
    hud.text((100, 975), "Whitewashing Reaction: Ca(OH)2 reacts with air CO2 to form shiny marble CaCO3 in 2-3 days", font=get_font(22), fill=(255, 215, 0))

    out2 = OUT_DIR / "act14_thumbnail_landscape_169.jpg"
    out_art2 = ARTIFACTS_DIR / "act14_thumbnail_landscape_169.jpg"
    comp.convert("RGB").save(out2, quality=96)
    comp.convert("RGB").save(out_art2, quality=96)
    print(f"Saved: {out2.name}")

def main():
    print("Generating Activity 1.4 Thumbnails...")
    create_shorts_thumbnail()
    create_landscape_thumbnail()
    print("Thumbnails generated successfully!")

if __name__ == "__main__":
    main()
