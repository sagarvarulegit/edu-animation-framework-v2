#!/usr/bin/env python3
"""
Refined Test Preview Frame Generator for CBSE Class 10 Activity 1.4:
Implements pixel-perfect alignments based on the actual photographs:
- Scene 1: Billowing steam plumes + sizzle ripples + violent splashing droplets
- Scene 2: Exact beaker bounds (330-610) with tilted pouring beaker + stream + rising water
- Scene 3: Constrained bubbles (230-740) + massive steam waves + balanced equation
- Scene 4: Mercury aligned exactly with the real physical thermometer in photo (x=508)
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

# Load base images
img_s1 = Image.open(IMG_DIR / "01_hook_steam.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s2 = Image.open(IMG_DIR / "02_setup_quicklime.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s3 = Image.open(IMG_DIR / "03_reaction_slaking.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s4 = Image.open(IMG_DIR / "04_takeaway_exothermic.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# ---------------------------------------------------------------------------
# SCENE 1: EXPLOSIVE STEAM HOOK
# ---------------------------------------------------------------------------
def render_scene1_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s1.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Impact point at the top foam rim: x=560, y=880
    impact_x, impact_y = 560, 880

    # Boiling flash pulse at impact
    pulse = 0.5 + 0.5 * math.sin(t * 12.0)
    flash_alpha = int(90 + 70 * pulse)
    draw.ellipse([impact_x - 120, impact_y - 60, impact_x + 120, impact_y + 60], fill=(255, 255, 255, flash_alpha))
    draw.ellipse([impact_x - 60, impact_y - 30, impact_x + 60, impact_y + 30], fill=(255, 240, 180, int(flash_alpha * 0.8)))

    # Rising dense steam clouds escaping upwards
    random.seed(42)
    num_puffs = 45
    for i in range(num_puffs):
        spawn_x = random.randint(340, 780)
        spawn_y = random.randint(750, 950)
        speed = random.uniform(220, 520)
        drift = random.uniform(-60, 60)
        lifetime = random.uniform(1.2, 2.5)
        birth = random.uniform(0, 3.0)

        age = (t + birth) % lifetime
        prog = age / lifetime
        cx = spawn_x + drift * prog + math.sin(age * 6 + i) * 20
        cy = spawn_y - speed * age
        r = int(35 + 130 * prog)
        alpha = int(150 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 250:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 250, 255, alpha))
            draw.ellipse([cx - int(r*0.65), cy - int(r*0.65), cx + int(r*0.65), cy + int(r*0.65)], fill=(255, 255, 255, int(alpha*0.6)))

    # Violent boiling splatter droplets
    random.seed(int(t * 50))
    for _ in range(16):
        dx = random.randint(-140, 140)
        dy = -random.randint(15, 160)
        dr = random.randint(2, 7)
        draw.ellipse([impact_x + dx - dr, impact_y + dy - dr, impact_x + dx + dr, impact_y + dy + dr], fill=(255, 255, 255, 230))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Top Hook Card
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 210), width=3)
    hud.text((100, 135), "NCERT ACTIVITY 1.4 • CLASS 10 CHEMISTRY", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 172), "COLD WATER MAKES ROCKS BOIL?!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Pouring plain water on dry quicklime triggers instant hissing steam!", font=get_font(24), fill=(220, 235, 245))

    # Bottom Pill
    hud.rounded_rectangle([60, 1660, 1020, 1800], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 1685), "REAL LAB DEMONSTRATION", font=get_font(24, bold=True), fill=(0, 229, 255))
    hud.text((100, 1725), "Action of Water on Quicklime (Calcium Oxide)", font=get_font(34, bold=True), fill=(255, 255, 255))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 2: POURING WATER INTO BEAKER (ACCURATE BEAKER BOUNDS)
# ---------------------------------------------------------------------------
def render_scene2_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    pour_active = (t >= 0.15)
    progress = min(1.0, max(0.0, (t - 0.15) / (total_dur * 0.80)))
    fill_h = int(170 * progress)

    # Beaker inner bounds: x: 335 to 605, bottom: 1460, rim: 1040
    beaker_left = 335
    beaker_right = 605
    fill_y = 1460 - fill_h

    if fill_h > 0:
        # Liquid fill polygon inside the beaker glass
        liquid_poly = [(beaker_left, 1460), (beaker_left, fill_y), (beaker_right, fill_y), (beaker_right, 1460)]
        draw.polygon(liquid_poly, fill=(205, 245, 255, 95))
        draw.line([(beaker_left, fill_y), (beaker_right, fill_y)], fill=(255, 255, 255, 220), width=3)
        draw.ellipse([beaker_left, fill_y - 6, beaker_right, fill_y + 6], outline=(230, 250, 255, 160), width=2)

        # Impact ripples around stream target (x=470)
        impact_x = 470
        r_age = (t * 4.5) % 1.0
        for r_offset in [0.0, 0.5]:
            r_prog = (r_age + r_offset) % 1.0
            rw = int(18 + 65 * r_prog)
            rh = int(6 + 16 * r_prog)
            ra = int(210 * (1.0 - r_prog))
            draw.ellipse([impact_x - rw, fill_y - rh, impact_x + rw, fill_y + rh], outline=(255, 255, 255, ra), width=2)

    # Tilted Pouring Beaker in upper left (x: 230 to 410, y: 380 to 520)
    beaker_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beaker_overlay)
    b_pts = [(230, 360), (410, 470), (350, 560), (170, 450)]
    bdraw.polygon(b_pts, fill=(230, 245, 255, 75), outline=(255, 255, 255, 220))
    b_liq = [(250, 400), (400, 470), (340, 540), (190, 470)]
    bdraw.polygon(b_liq, fill=(200, 240, 255, 150))
    bdraw.line([(280, 430), (300, 445)], fill=(255, 255, 255, 220), width=2)
    bdraw.line([(310, 460), (330, 475)], fill=(255, 255, 255, 220), width=2)
    bdraw.text((220, 320), "WATER (H2O)", font=get_font(24, bold=True), fill=(0, 229, 255, 240))

    # Flowing Water Stream
    spout_x, spout_y = 410, 475
    impact_x = 470
    impact_y = 1460 - fill_h

    if pour_active:
        stream_pts = []
        num_steps = 35
        for i in range(num_steps + 1):
            u = i / float(num_steps)
            if u < 0.35:
                v = u / 0.35
                px = (1-v)**2 * spout_x + 2*(1-v)*v * 450 + v**2 * 470
                py = (1-v)**2 * spout_y + 2*(1-v)*v * 510 + v**2 * 680
            else:
                v = (u - 0.35) / 0.65
                px = 470 + math.sin(v * math.pi * 3 + t * 18) * 3
                py = 680 + (impact_y - 680) * v
            stream_pts.append((px, py))

        for i in range(len(stream_pts) - 1):
            p1, p2 = stream_pts[i], stream_pts[i+1]
            u = i / len(stream_pts)
            w = max(6, int(20 * (1.0 - u * 0.45)))
            draw.line([p1, p2], fill=(180, 235, 255, 120), width=w + 5)
            draw.line([p1, p2], fill=(235, 250, 255, 200), width=w)
            hl_p1 = (p1[0] - w * 0.25, p1[1])
            hl_p2 = (p2[0] - w * 0.25, p2[1])
            draw.line([hl_p1, hl_p2], fill=(255, 255, 255, 245), width=max(2, int(w * 0.28)))

        # Splashes
        random.seed(int(t * 60))
        for _ in range(8):
            dx = random.randint(-25, 25)
            dy = -random.randint(6, 35)
            dr = random.randint(2, 5)
            draw.ellipse([impact_x + dx - dr, impact_y + dy - dr, impact_x + dx + dr, impact_y + dy + dr], fill=(245, 252, 255, 220))

    comp = Image.alpha_composite(base, overlay)
    comp = Image.alpha_composite(comp, beaker_overlay)

    hud = ImageDraw.Draw(comp)
    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • ADDING REACTANTS", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Slowly Adding Water to Quicklime", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Water begins wetting the solid Calcium Oxide lumps", font=get_font(24), fill=(180, 215, 235))

    # Bottom Reality Check Card
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: QUICKLIME (CaO)", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Dry, white irregular lumps in Pyrex beaker", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation for CBSE Board viva", font=get_font(23), fill=(190, 210, 230))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 3: VIGOROUS SLAKING REACTION (CONSTRAINED BUBBLES & STEAM)
# ---------------------------------------------------------------------------
random.seed(101)
NUM_BUBBLES_S3 = 360
BUBBLE_PARAMS_S3 = []
# Constrain bubbles strictly to beaker interior: x: 240 to 730, y: 880 to 1650
for _ in range(NUM_BUBBLES_S3):
    sx = random.randint(240, 730)
    sy = random.randint(1100, 1650)
    spd = random.uniform(220, 520)
    r = random.uniform(3.5, 13.0)
    w_freq = random.uniform(6.0, 14.0)
    w_amp = random.uniform(5.0, 16.0)
    ph = random.uniform(0, 2 * math.pi)
    ltime = (sy - 840) / spd
    boff = random.uniform(0, ltime)
    BUBBLE_PARAMS_S3.append((sx, sy, spd, r, w_freq, w_amp, ph, ltime, boff))

def render_scene3_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s3.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bubbles inside beaker
    for bp in BUBBLE_PARAMS_S3:
        sx, sy, spd, r, w_freq, w_amp, ph, ltime, boff = bp
        age = (t + boff) % ltime
        cy = sy - (spd * age)
        cx = sx + math.sin(age * w_freq + ph) * w_amp
        cur_r = r * (1.0 + 0.3 * (age / ltime))

        if 230 <= cx <= 740 and cy >= 840:
            draw.ellipse([cx - cur_r, cy - cur_r, cx + cur_r, cy + cur_r],
                         fill=(245, 250, 255, 125), outline=(255, 255, 255, 190), width=int(max(1, cur_r * 0.16)))
            hl_r = max(1.5, cur_r * 0.35)
            hl_x = cx - cur_r * 0.32
            hl_y = cy - cur_r * 0.32
            draw.ellipse([hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r], fill=(255, 255, 255, 240))

    # Billowing Steam clouds rising out of beaker rim into air
    random.seed(55)
    num_steam = 40
    for i in range(num_steam):
        ssx = random.randint(260, 720)
        ssy = random.randint(750, 900)
        sspd = random.uniform(180, 420)
        slife = random.uniform(1.4, 2.8)
        sboff = random.uniform(0, 2.8)
        sage = (t + sboff) % slife
        sprog = sage / slife
        scx = ssx + math.sin(sage * 3.5 + i) * 35
        scy = ssy - sspd * sage
        sr = int(35 + 120 * sprog)
        salpha = int(125 * (1.0 - sprog) * math.sin(sprog * math.pi))
        if salpha > 0 and scy > 260:
            draw.ellipse([scx - sr, scy - sr, scx + sr, scy + sr], fill=(245, 250, 255, salpha))

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Step HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 135), "STEP 2 • VIGOROUS REACTION", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 172), "VIOLENT HISSING & BOILING!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Two substances combine into ONE single product: Slaked Lime!", font=get_font(24), fill=(195, 235, 215))

    # Balanced Chemical Equation HUD Card
    hud.rounded_rectangle([60, 1580, 1020, 1820], radius=24, fill=(16, 22, 36, 240), outline=(0, 229, 255, 200), width=3)
    hud.text((100, 1605), "BALANCED CHEMICAL EQUATION • COMBINATION REACTION", font=get_font(24, bold=True), fill=(0, 229, 255))
    hud.text((100, 1648), "CaO (s) + H2O (l) → Ca(OH)2 (aq) + Heat", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1702), "Quicklime + Water → Slaked Lime (Calcium Hydroxide)", font=get_font(23), fill=(185, 220, 240))
    hud.text((100, 1745), "Key Concept: Multiple reactants yield a single product!", font=get_font(22, bold=True), fill=(255, 215, 0))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 4: THERMOMETER ALIGNED EXACTLY TO PHOTO (X=508)
# ---------------------------------------------------------------------------
def render_scene4_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s4.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    progress = min(1.0, t / (total_dur * 0.85))
    smooth_p = 1.0 - math.cos(progress * math.pi * 0.5)
    current_temp = 24.5 + (84.8 - 24.5) * smooth_p

    # Color transition from cyan (room temp) to bright fiery orange/red (84.8°C)
    if current_temp < 45.0:
        temp_color = (0, 229, 255)
    elif current_temp < 65.0:
        temp_color = (255, 179, 0)
    else:
        temp_color = (255, 60, 30)

    # Thermal heat pulse around where the gloved hand touches beaker (x: 520 to 760, y: 1250 to 1550)
    pulse_alpha = int(55 + math.sin(t * 6) * 30)
    draw.ellipse([480, 1200, 800, 1560], fill=(255, 70, 20, pulse_alpha))

    # Real thermometer in photo is at x=508
    tx = 508
    t_bulb_y = 1250 # inside milky slurry
    # Scale in photo: 0°C is around y=1180, 100°C is around y=360
    # 20°C corresponds to y ≈ 1020, 85°C corresponds to y ≈ 480
    mercury_top_y = int(1180 - (current_temp / 100.0) * 820)

    # Glowing red mercury column inside the physical glass tube
    draw.rounded_rectangle([tx - 4, mercury_top_y, tx + 4, t_bulb_y], radius=3, fill=(255, 30, 20, 230))
    draw.line([(tx - 1, mercury_top_y), (tx - 1, t_bulb_y)], fill=(255, 150, 130, 240), width=2) # specular highlight
    # Thermometer bulb glow inside liquid
    draw.ellipse([tx - 12, t_bulb_y - 12, tx + 12, t_bulb_y + 12], fill=(255, 40, 20, 240))

    # Glowing temperature indicator bracket pointing to the meniscus
    draw.line([(tx + 8, mercury_top_y), (tx + 50, mercury_top_y)], fill=temp_color, width=3)
    draw.polygon([(tx + 12, mercury_top_y), (tx + 24, mercury_top_y - 6), (tx + 24, mercury_top_y + 6)], fill=temp_color)
    draw.text((tx + 58, mercury_top_y - 18), f"{current_temp:.1f}°C", font=get_font(26, bold=True), fill=temp_color)

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Floating Digital LED Readout Box on the left (clear of bottles)
    meter_box = [70, 680, 480, 930]
    hud.rounded_rectangle(meter_box, radius=20, fill=(14, 20, 32, 235), outline=temp_color, width=4)
    hud.text((100, 705), "SLURRY TEMPERATURE", font=get_font(22, bold=True), fill=(180, 205, 225))
    hud.text((100, 740), f"{current_temp:.1f} °C", font=get_font(62, bold=True), fill=temp_color)
    delta = current_temp - 24.5
    hud.text((100, 830), f"▲ +{delta:.1f}°C HEAT SPIKE!", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 872), "Extreme exothermic energy release", font=get_font(20), fill=(200, 215, 230))

    # Top HUD
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 87, 34, 190), width=3)
    hud.text((100, 135), "STEP 3 • OBSERVATION & INFERENCE", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 172), "EXOTHERMIC COMBINATION!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Beaker becomes burning hot to the touch as heat is liberated!", font=get_font(24), fill=(225, 205, 205))

    # Bottom Board Exam Takeaway Card (WHITEWASHING HACK)
    hud.rounded_rectangle([60, 1590, 1020, 1810], radius=24, fill=(16, 22, 36, 240), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1612), "CLASS 10 BOARD EXAM 100% HACK", font=get_font(24, bold=True), fill=(255, 179, 0))
    hud.text((100, 1650), "Whitewashing: Slaked lime Ca(OH)2 on walls", font=get_font(34, bold=True), fill=(255, 255, 255))
    hud.text((100, 1700), "Reacts with air CO2 to form shiny marble CaCO3 in 2-3 days", font=get_font(23), fill=(195, 220, 235))
    hud.text((100, 1742), "Exam Question: Why do whitewashed walls shine after 2 days?", font=get_font(21, bold=True), fill=(0, 229, 255))

    return comp.convert("RGB")

def main():
    print("Generating refined frame previews...")
    f1 = render_scene1_frame(1.5, 3.79)
    p1 = ARTIFACTS_DIR / "preview_act14_s1_steam_hook.jpg"
    f1.save(p1, quality=95)

    f2 = render_scene2_frame(1.8, 2.69)
    p2 = ARTIFACTS_DIR / "preview_act14_s2_pouring_water.jpg"
    f2.save(p2, quality=95)

    f3 = render_scene3_frame(4.5, 9.15)
    p3 = ARTIFACTS_DIR / "preview_act14_s3_slaking_reaction.jpg"
    f3.save(p3, quality=95)

    f4 = render_scene4_frame(5.5, 7.08)
    p4 = ARTIFACTS_DIR / "preview_act14_s4_exothermic_thermometer.jpg"
    f4.save(p4, quality=95)
    print("Done! All 4 refined previews saved.")

if __name__ == "__main__":
    main()
