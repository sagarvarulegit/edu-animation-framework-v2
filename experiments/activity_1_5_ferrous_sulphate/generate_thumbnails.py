#!/usr/bin/env python3
"""
Viral Thumbnail Generator for CBSE Class 10 Activity 1.5:
Thermal Decomposition of Ferrous Sulphate Crystals
Generates:
1. 9:16 Vertical Thumbnail (1080x1920) for YouTube Shorts feed & mobile
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
    base = Image.open(IMG_DIR / "01_hook_flame.jpg").convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
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
    hud.text((90, 138), "CBSE CLASS 10 • ACTIVITY 1.5", font=get_font(30, bold=True), fill=(255, 179, 0))
    hud.text((90, 185), "NEVER INHALE FROM", font=get_font(52, bold=True), fill=(255, 255, 255))
    hud.text((90, 248), "THIS TUBE?!", font=get_font(68, bold=True), fill=(255, 82, 82))

    # Floating curiosity badge
    hud.rounded_rectangle([50, 380, 560, 440], radius=16, fill=(255, 179, 0, 245))
    hud.text((70, 392), "WHY DOES GREEN TURN BROWN?!", font=get_font(26, bold=True), fill=(10, 15, 26))

    # Bottom Takeaway Card
    hud.rounded_rectangle([50, 1580, 1030, 1830], radius=28, fill=(16, 22, 36, 240), outline=(0, 229, 255, 220), width=4)
    hud.text((90, 1605), "THERMAL DECOMPOSITION REACTION", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((90, 1648), "Green Crystals → Red-Brown Ferric Oxide", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((90, 1702), "2FeSO4 → Fe2O3 + SO2 + SO3 Gases", font=get_font(30, bold=True), fill=(255, 215, 0))
    hud.text((90, 1755), "Suffocating Burning Sulfur Fumes • Board Viva #1 Question", font=get_font(22), fill=(190, 220, 240))

    out1 = OUT_DIR / "act15_thumbnail_shorts_916.jpg"
    out_art = ARTIFACTS_DIR / "act15_thumbnail_shorts_916.jpg"
    comp.convert("RGB").save(out1, quality=96)
    comp.convert("RGB").save(out_art, quality=96)
    print(f"Saved: {out1.name}")

def create_landscape_thumbnail():
    s1 = Image.open(IMG_DIR / "01_hook_flame.jpg").convert("RGBA")
    s4 = Image.open(IMG_DIR / "04_takeaway_wafting.jpg").convert("RGBA")

    canvas = Image.new("RGBA", (1920, 1080), (12, 16, 26, 255))

    # Left visual: Flame & Crystal Hook
    w1, h1 = s1.size
    crop1 = s1.crop((0, int(h1 * 0.15), w1, int(h1 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop1, (0, 0))

    # Right visual: NCERT Safety Wafting
    w4, h4 = s4.size
    crop4 = s4.crop((0, int(h4 * 0.15), w4, int(h4 * 0.85))).resize((960, 1080), Image.Resampling.LANCZOS)
    canvas.paste(crop4, (960, 0))

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
    hud.text((85, 52), "CBSE CLASS 10 • ACTIVITY 1.5", font=get_font(34, bold=True), fill=(10, 15, 26))

    # Big Headline on Left
    hud.rounded_rectangle([60, 120, 940, 310], radius=24, fill=(16, 22, 36, 235), outline=(255, 82, 82, 220), width=4)
    hud.text((90, 140), "NEVER INHALE FROM", font=get_font(44, bold=True), fill=(255, 255, 255))
    hud.text((90, 195), "THIS TUBE?!", font=get_font(64, bold=True), fill=(255, 82, 82))

    # Top Right Badge
    hud.rounded_rectangle([1320, 40, 1860, 110], radius=16, fill=(255, 60, 30, 245))
    hud.text((1350, 55), "DANGER: CHOKING SULFUR GAS!", font=get_font(32, bold=True), fill=(255, 255, 255))

    # Bottom Wide Card
    hud.rounded_rectangle([60, 860, 1860, 1020], radius=24, fill=(16, 22, 36, 245), outline=(0, 229, 255, 220), width=4)
    hud.text((100, 880), "THERMAL DECOMPOSITION: HEATING FERROUS SULPHATE CRYSTALS", font=get_font(28, bold=True), fill=(0, 229, 255))
    hud.text((100, 924), "2FeSO4 → Fe2O3 (Red-Brown Solid) + SO2 + SO3 (Pungent Gases)  •  NCERT Wafting Safety", font=get_font(32, bold=True), fill=(255, 255, 255))
    hud.text((100, 975), "Class 10 Board Exam 100% Repeated Viva Questions & Practical Observations", font=get_font(22), fill=(255, 215, 0))

    out2 = OUT_DIR / "act15_thumbnail_landscape_169.jpg"
    out_art2 = ARTIFACTS_DIR / "act15_thumbnail_landscape_169.jpg"
    comp.convert("RGB").save(out2, quality=96)
    comp.convert("RGB").save(out_art2, quality=96)
    print(f"Saved: {out2.name}")

def main():
    print("Generating Activity 1.5 Thumbnails...")
    create_shorts_thumbnail()
    create_landscape_thumbnail()
    print("Thumbnails generated successfully!")

if __name__ == "__main__":
    main()
