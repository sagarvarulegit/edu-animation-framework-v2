#!/usr/bin/env python3
"""
Test Preview Frame Generator for CBSE Class 10 Activity 1.5:
Generates static frame previews of Scene 1, 2, 3, 4 for visual inspection.
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
ARTIFACTS_DIR = Path(r"C:\Users\sunwa\.gemini\antigravity-cli\brain\af617f1a-1b38-4668-bb71-a1b954c9fee3")

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
img_s1 = Image.open(IMG_DIR / "01_hook_flame.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s2 = Image.open(IMG_DIR / "02_setup_droplets.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s3 = Image.open(IMG_DIR / "03_reaction_fumes.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s4 = Image.open(IMG_DIR / "04_takeaway_wafting.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# ---------------------------------------------------------------------------
# SCENE 1: SHOCK CLIMAX HOOK
# ---------------------------------------------------------------------------
def render_scene1_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s1.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube mouth is at x ≈ 500, y ≈ 380; Tube bottom in flame is at x ≈ 505, y ≈ 1480
    mouth_x, mouth_y = 505, 380
    bottom_x, bottom_y = 505, 1480

    # Roaring blue flame pulse
    f_pulse = 0.5 + 0.5 * math.sin(t * 14.0)
    flame_alpha = int(70 + 50 * f_pulse)
    draw.ellipse([bottom_x - 110, bottom_y - 80, bottom_x + 110, bottom_y + 120], fill=(0, 180, 255, flame_alpha))
    draw.ellipse([bottom_x - 60, bottom_y - 40, bottom_x + 60, bottom_y + 60], fill=(255, 100, 30, int(flame_alpha * 0.9)))

    # Thermal micro-sparks inside decomposing crystals
    random.seed(int(t * 40))
    for _ in range(12):
        sx = random.randint(460, 550)
        sy = random.randint(1200, 1460)
        sr = random.randint(2, 5)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 230, 140, 230))

    # Dense billowing sulfur gas plumes escaping mouth
    random.seed(42)
    num_puffs = 35
    for i in range(num_puffs):
        spawn_x = random.randint(480, 530)
        spawn_y = random.randint(340, 420)
        speed = random.uniform(180, 420)
        drift = random.uniform(-40, 40)
        lifetime = random.uniform(1.2, 2.2)
        birth = random.uniform(0, 3.0)

        age = (t + birth) % lifetime
        prog = age / lifetime
        cx = spawn_x + drift * prog + math.sin(age * 5 + i) * 20
        cy = spawn_y - speed * age
        r = int(25 + 90 * prog)
        alpha = int(140 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 160:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 245, 255, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Hook Card
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 82, 82, 220), width=3)
    hud.text((100, 135), "NCERT ACTIVITY 1.5 • CLASS 10 CHEMISTRY", font=get_font(26, bold=True), fill=(255, 82, 82))
    hud.text((100, 172), "NEVER INHALE FROM THIS TUBE!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Heating dry green crystals releases suffocating, toxic gases!", font=get_font(24), fill=(240, 220, 220))

    # Bottom Pill
    hud.rounded_rectangle([60, 1660, 1020, 1800], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1685), "REAL LAB DEMONSTRATION", font=get_font(24, bold=True), fill=(255, 179, 0))
    hud.text((100, 1725), "Thermal Decomposition of Ferrous Sulphate", font=get_font(34, bold=True), fill=(255, 255, 255))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 2: WATER OF CRYSTALLISATION & CONDENSATION
# ---------------------------------------------------------------------------
def render_scene2_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube neck condensation zone: x ≈ 520 to 860, y ≈ 360 to 800 (tilted diagonally)
    # Animated glistening water droplets
    random.seed(77)
    for i in range(25):
        dx = random.randint(540, 840)
        dy = random.randint(380, 820)
        dr = random.randint(4, 10)
        glimmer = 0.5 + 0.5 * math.sin(t * 8.0 + i)
        d_alpha = int(160 + 80 * glimmer)
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(210, 245, 255, d_alpha), outline=(255, 255, 255, 230), width=1)
        draw.ellipse([dx - dr//2, dy - dr//2, dx, dy], fill=(255, 255, 255, 240))

    # Flame flicker under the tube bottom (x ≈ 490, y ≈ 1300 to 1600)
    flame_flicker = math.sin(t * 16.0) * 10
    draw.polygon([(470, 1400), (510 + flame_flicker, 1180), (550, 1400)], fill=(0, 229, 255, 110))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • GENTLE HEATING", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Water of Crystallisation Escapes!", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Liquid droplets condense inside the cool upper test tube walls", font=get_font(24), fill=(180, 215, 235))

    # Bottom Reality Check Card
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: GREEN VITRIOL", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 1698), "FeSO4 · 7H2O loses water → Dirty white FeSO4", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical viva question: Why do water droplets appear?", font=get_font(23), fill=(190, 230, 210))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 3: STRONG HEATING & GAS EVOLUTION
# ---------------------------------------------------------------------------
def render_scene3_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s3.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Tube mouth is at x ≈ 495, y ≈ 420; Bottom in flame is at x ≈ 495, y ≈ 1380
    mouth_x, mouth_y = 495, 420
    bottom_x, bottom_y = 495, 1380

    # Red-hot thermal glow pulse at the decomposing ferric oxide residue
    pulse = 0.5 + 0.5 * math.sin(t * 8.0)
    glow_alpha = int(75 + 50 * pulse)
    draw.ellipse([bottom_x - 90, bottom_y - 120, bottom_x + 90, bottom_y + 60], fill=(255, 70, 20, glow_alpha))

    # Billowing dense sulfur gas plumes (SO2 and SO3)
    random.seed(99)
    num_puffs = 40
    for i in range(num_puffs):
        sx = random.randint(460, 530)
        sy = random.randint(360, 440)
        spd = random.uniform(190, 440)
        drift = random.uniform(-50, 50)
        ltime = random.uniform(1.3, 2.4)
        boff = random.uniform(0, 3.0)

        age = (t + boff) % ltime
        prog = age / ltime
        cx = sx + drift * prog + math.sin(age * 4.5 + i) * 25
        cy = sy - spd * age
        r = int(30 + 110 * prog)
        alpha = int(140 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 180:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 250, 255, alpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 112, 67, 210), width=3)
    hud.text((100, 135), "STEP 2 • STRONG DECOMPOSITION", font=get_font(26, bold=True), fill=(255, 112, 67))
    hud.text((100, 172), "GREEN CRYSTALS TURN RED-BROWN!", font=get_font(40, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Solid breaks down into Ferric Oxide + Pungent choking gases!", font=get_font(24), fill=(240, 210, 200))

    # Balanced Chemical Equation HUD Card
    hud.rounded_rectangle([60, 1580, 1020, 1820], radius=24, fill=(16, 22, 36, 240), outline=(0, 229, 255, 200), width=3)
    hud.text((100, 1605), "BALANCED EQUATION • THERMAL DECOMPOSITION", font=get_font(24, bold=True), fill=(0, 229, 255))
    hud.text((100, 1648), "2FeSO4 (s) → Fe2O3 (s) + SO2 (g) + SO3 (g)", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1702), "Green FeSO4 → Red-Brown Ferric Oxide + Sulfur Oxides", font=get_font(23), fill=(185, 220, 240))
    hud.text((100, 1745), "Sensory Test: Choking smell of burning sulfur!", font=get_font(22, bold=True), fill=(255, 82, 82))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 4: WAFTING SAFETY & RAPID-FIRE QUIZ CTA
# ---------------------------------------------------------------------------
def render_scene4_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s4.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Wafting air stream waves towards face (from tube at x=360, y=500 towards x=540, y=520)
    w_age = (t * 2.5) % 1.0
    for w_off in [0.0, 0.4]:
        prog = (w_age + w_off) % 1.0
        wx = 380 + int(140 * prog)
        wy = 500 + int(20 * math.sin(prog * math.pi))
        w_alpha = int(160 * (1.0 - prog))
        draw.arc([wx - 30, wy - 40, wx + 30, wy + 40], start=-60, end=60, fill=(255, 255, 255, w_alpha), width=3)

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 210), width=3)
    hud.text((100, 135), "STEP 3 • NCERT LAB SAFETY TECHNIQUE", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 172), "WAFT GENTLY • DO NOT INHALE!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Never point test tube at yourself; waft gas fumes with hand", font=get_font(24), fill=(235, 220, 190))

    # Central / Lower RAPID-FIRE QUIZ CTA CARD (The Engagement Driver!)
    hud.rounded_rectangle([60, 1420, 1020, 1830], radius=24, fill=(14, 20, 32, 245), outline=(0, 230, 118, 230), width=4)
    hud.text((100, 1445), "CBSE BOARD RAPID-FIRE QUIZ", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 1488), "What is the reddish-brown residue called?", font=get_font(34, bold=True), fill=(255, 255, 255))

    # Options A & B
    hud.rounded_rectangle([100, 1550, 520, 1630], radius=16, fill=(24, 32, 48, 240), outline=(0, 229, 255, 180), width=2)
    hud.text((120, 1572), "A: FeO (Ferrous Oxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    hud.rounded_rectangle([560, 1550, 980, 1630], radius=16, fill=(24, 32, 48, 240), outline=(255, 179, 0, 180), width=2)
    hud.text((580, 1572), "B: Fe2O3 (Ferric Oxide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    # Options C & D
    hud.rounded_rectangle([100, 1650, 520, 1730], radius=16, fill=(24, 32, 48, 240), outline=(180, 200, 220, 180), width=2)
    hud.text((120, 1672), "C: Fe3O4 (Magnetite)", font=get_font(24, bold=True), fill=(255, 255, 255))

    hud.rounded_rectangle([560, 1650, 980, 1730], radius=16, fill=(24, 32, 48, 240), outline=(180, 200, 220, 180), width=2)
    hud.text((580, 1672), "D: FeS (Iron Sulphide)", font=get_font(24, bold=True), fill=(255, 255, 255))

    # Call to action text
    hud.text((100, 1765), "▼ COMMENT YOUR ANSWER A, B, C, OR D BELOW! ▼", font=get_font(25, bold=True), fill=(255, 235, 59))

    return comp.convert("RGB")

def main():
    print("Generating Activity 1.5 Preview Frames...")
    f1 = render_scene1_frame(1.5, 4.16)
    p1 = ARTIFACTS_DIR / "preview_act15_s1_hook.jpg"
    f1.save(p1, quality=95)
    print(f"Saved: {p1.name}")

    f2 = render_scene2_frame(2.0, 4.26)
    p2 = ARTIFACTS_DIR / "preview_act15_s2_condensation.jpg"
    f2.save(p2, quality=95)
    print(f"Saved: {p2.name}")

    f3 = render_scene3_frame(2.0, 4.27)
    p3 = ARTIFACTS_DIR / "preview_act15_s3_decomposition.jpg"
    f3.save(p3, quality=95)
    print(f"Saved: {p3.name}")

    f4 = render_scene4_frame(2.5, 4.54)
    p4 = ARTIFACTS_DIR / "preview_act15_s4_wafting_quiz.jpg"
    f4.save(p4, quality=95)
    print(f"Saved: {p4.name}")

if __name__ == "__main__":
    main()
