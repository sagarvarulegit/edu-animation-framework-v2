#!/usr/bin/env python3
"""
Preview Frame Generator for CBSE Class 10 Activity 1.6:
Thermal Decomposition of Lead Nitrate (Pb(NO3)2).
Tests visual composite layers, particle smoke engine, fonts, and HUD cards.
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"

WIDTH, HEIGHT = 1080, 1920

def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# Load base images resized to 1080x1920
img_s1 = Image.open(IMG_DIR / "01_hook_brown_fumes.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s2 = Image.open(IMG_DIR / "02_setup_dry_powder.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s3 = Image.open(IMG_DIR / "03_reaction_yellow_residue.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s4 = Image.open(IMG_DIR / "04_takeaway_safety_wafting.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# ---------------------------------------------------------------------------
# SCENE 1: SHOCK HOOK
# ---------------------------------------------------------------------------
def render_scene1(t: float = 2.0):
    base = img_s1.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube mouth is at x ≈ 640, y ≈ 420; bottom is at x ≈ 380, y ≈ 1280
    mouth_x, mouth_y = 640, 420
    bottom_x, bottom_y = 380, 1280

    # Crackling micro-sparks from crystal bed
    random.seed(int(t * 30))
    for _ in range(12):
        sx = random.randint(340, 420)
        sy = random.randint(1200, 1340)
        sr = random.randint(2, 6)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 240, 180, 240))

    # Dense reddish-brown NO2 gas plumes billowing from mouth
    random.seed(42)
    for i in range(40):
        spawn_x = random.randint(mouth_x - 30, mouth_x + 30)
        spawn_y = random.randint(mouth_y - 40, mouth_y + 20)
        speed = random.uniform(160, 400)
        drift = random.uniform(20, 80)
        lifetime = random.uniform(1.2, 2.2)
        birth = random.uniform(0, 3.0)

        age = (t + birth) % lifetime
        prog = age / lifetime
        cx = spawn_x + drift * prog + math.sin(age * 5 + i) * 20
        cy = spawn_y - speed * age
        r = int(30 + 100 * prog)
        alpha = int(170 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 140:
            # Rich reddish-brown nitrogen dioxide gas color
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(185, 75, 25, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Hook Card
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 82, 82, 220), width=3)
    hud.text((100, 135), "NCERT ACTIVITY 1.6 • CLASS 10 CHEMISTRY", font=get_font(26, bold=True), fill=(255, 82, 82))
    hud.text((100, 172), "NEVER POINT TUBE AT ANYONE!", font=get_font(40, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Heating white crystals emits suffocating brown toxic gas!", font=get_font(24), fill=(240, 220, 220))

    # Bottom Pill
    hud.rounded_rectangle([60, 1660, 1020, 1800], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1685), "REAL LAB DEMONSTRATION", font=get_font(24, bold=True), fill=(255, 179, 0))
    hud.text((100, 1725), "Thermal Decomposition of Lead Nitrate", font=get_font(34, bold=True), fill=(255, 255, 255))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 2: SETUP & CRYSTALS
# ---------------------------------------------------------------------------
def render_scene2(t: float = 2.0):
    base = img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube bottom is at x ≈ 505, y ≈ 1080
    bottom_x, bottom_y = 505, 1080

    # Decrepitation crackle sparks inside crystal bed
    random.seed(int(t * 30))
    for _ in range(10):
        cx = random.randint(bottom_x - 35, bottom_x + 35)
        cy = random.randint(bottom_y - 45, bottom_y + 10)
        cr = random.randint(2, 5)
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 200, 230))

    # Warm heat aura around boiling tube bottom
    pulse = 0.5 + 0.5 * math.sin(t * 6.0)
    aura_alpha = int(40 + 30 * pulse)
    for ar in [80, 50, 30]:
        draw.ellipse([bottom_x - ar, bottom_y - ar, bottom_x + ar, bottom_y + ar], fill=(255, 140, 20, aura_alpha // 2))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • HEATING DRY CRYSTALS", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Take Dry White Lead Nitrate", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Hold firmly with clamp and heat over blue burner flame", font=get_font(24), fill=(180, 215, 235))

    # Bottom Reality Check Card
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: DECREPITATION", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 1698), "White Pb(NO3)2 crystals produce a crackling sound!", font=get_font(34, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical viva note: Crystals break apart with sound on heating", font=get_font(22), fill=(190, 230, 210))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 3: STRONG DECOMPOSITION & BROWN FUMES
# ---------------------------------------------------------------------------
def render_scene3(t: float = 2.0):
    base = img_s3.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube bottom is at x ≈ 500, y ≈ 1600; mouth is at x ≈ 490, y ≈ 300
    bottom_x, bottom_y = 500, 1600
    mouth_x, mouth_y = 490, 300

    # Molten yellow residue glow pulse
    pulse = 0.5 + 0.5 * math.sin(t * 7.0)
    glow_alpha = int(60 + 40 * pulse)
    for gr in [110, 70, 40]:
        draw.ellipse([bottom_x - gr, bottom_y - gr, bottom_x + gr, bottom_y + gr], fill=(255, 200, 20, glow_alpha // 2))

    # Dense billowing NO2 gas plumes streaming up through tube and into air
    random.seed(88)
    for i in range(45):
        sx = random.randint(mouth_x - 35, mouth_x + 35)
        sy = random.randint(mouth_y - 50, mouth_y + 30)
        spd = random.uniform(190, 440)
        drift = random.uniform(-40, 40)
        ltime = random.uniform(1.3, 2.4)
        boff = random.uniform(0, 3.0)

        age = (t + boff) % ltime
        prog = age / ltime
        cx = sx + drift * prog + math.sin(age * 4.5 + i) * 22
        cy = sy - spd * age
        r = int(32 + 115 * prog)
        alpha = int(160 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 150:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(195, 80, 25, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 112, 67, 210), width=3)
    hud.text((100, 135), "STEP 2 • STRONG DECOMPOSITION", font=get_font(26, bold=True), fill=(255, 112, 67))
    hud.text((100, 172), "WHITE POWDER TURNS YELLOW!", font=get_font(40, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Solid forms yellow Lead Monoxide and dense brown NO2 gas!", font=get_font(24), fill=(240, 210, 200))

    # Balanced Chemical Equation HUD Card
    hud.rounded_rectangle([60, 1580, 1020, 1820], radius=24, fill=(16, 22, 36, 240), outline=(0, 229, 255, 200), width=3)
    hud.text((100, 1605), "BALANCED EQUATION • THERMAL DECOMPOSITION", font=get_font(24, bold=True), fill=(0, 229, 255))
    hud.text((100, 1648), "2Pb(NO3)2 (s) → 2PbO (s) + 4NO2 (g) + O2 (g)", font=get_font(34, bold=True), fill=(255, 255, 255))
    hud.text((100, 1702), "White Powder → Yellow PbO + Brown NO2 Gas + Oxygen", font=get_font(23), fill=(185, 220, 240))
    hud.text((100, 1745), "Observation: Reddish-brown while hot, yellow upon cooling!", font=get_font(22, bold=True), fill=(255, 235, 59))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 4: WAFTING SAFETY & RAPID-FIRE QUIZ CTA
# ---------------------------------------------------------------------------
def render_scene4(t: float = 2.0):
    base = img_s4.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Exhaust hood suction stream ripples
    w_age = (t * 2.0) % 1.0
    for w_off in [0.0, 0.5]:
        prog = (w_age + w_off) % 1.0
        wx = 240 + int(90 * prog)
        wy = 820 - int(120 * prog)
        w_alpha = int(140 * (1.0 - prog))
        draw.arc([wx - 25, wy - 35, wx + 25, wy + 35], start=120, end=260, fill=(0, 229, 255, w_alpha), width=3)

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 210), width=3)
    hud.text((100, 135), "STEP 3 • NCERT LAB SAFETY TECHNIQUE", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 172), "ALWAYS USE FUME HOOD!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Never inhale nitrogen dioxide; point tube away from everyone", font=get_font(24), fill=(235, 220, 190))

    # Central / Lower RAPID-FIRE QUIZ CTA CARD (The Engagement Driver!)
    hud.rounded_rectangle([60, 1420, 1020, 1830], radius=24, fill=(14, 20, 32, 245), outline=(0, 230, 118, 230), width=4)
    hud.text((100, 1445), "CBSE BOARD RAPID-FIRE QUIZ", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 1488), "Which gas produces the brown fumes?", font=get_font(34, bold=True), fill=(255, 255, 255))

    # Options A & B
    hud.rounded_rectangle([100, 1550, 520, 1630], radius=16, fill=(24, 32, 48, 240), outline=(0, 230, 118, 200), width=2)
    hud.text((120, 1572), "A: NO2 (Nitrogen Dioxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    hud.rounded_rectangle([560, 1550, 980, 1630], radius=16, fill=(24, 32, 48, 240), outline=(255, 179, 0, 180), width=2)
    hud.text((580, 1572), "B: N2O (Nitrous Oxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    # Options C & D
    hud.rounded_rectangle([100, 1650, 520, 1730], radius=16, fill=(24, 32, 48, 240), outline=(180, 200, 220, 180), width=2)
    hud.text((120, 1672), "C: NO (Nitric Oxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    hud.rounded_rectangle([560, 1650, 980, 1730], radius=16, fill=(24, 32, 48, 240), outline=(180, 200, 220, 180), width=2)
    hud.text((580, 1672), "D: SO2 (Sulfur Dioxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    # Call to action text
    hud.text((100, 1765), "▼ COMMENT YOUR ANSWER A, B, C, OR D BELOW! ▼", font=get_font(25, bold=True), fill=(255, 235, 59))

    return comp.convert("RGB")

def main():
    print("Generating Activity 1.6 Preview Frames...")
    p1 = render_scene1(1.5)
    p1.save(BASE_DIR / "preview_act16_s1_hook.jpg", quality=95)
    print("Saved: preview_act16_s1_hook.jpg")

    p2 = render_scene2(1.5)
    p2.save(BASE_DIR / "preview_act16_s2_setup.jpg", quality=95)
    print("Saved: preview_act16_s2_setup.jpg")

    p3 = render_scene3(1.5)
    p3.save(BASE_DIR / "preview_act16_s3_decomposition.jpg", quality=95)
    print("Saved: preview_act16_s3_decomposition.jpg")

    p4 = render_scene4(1.5)
    p4.save(BASE_DIR / "preview_act16_s4_safety_quiz.jpg", quality=95)
    print("Saved: preview_act16_s4_safety_quiz.jpg")

if __name__ == "__main__":
    main()
