#!/usr/bin/env python3
"""
Refined Action Composite Renderer for CBSE Class 10 Activity 1.3:
- Scene 2: Realistic tilted pouring beaker + gravity-curved liquid stream + flask-contour fill + splashing ripples
- Scene 3: High-density active bubbling effervescence engine with 3D spherical bubble physics + surface bursting
- Scene 4: Laboratory thermometer probe immersed directly in the liquid + live digital climbing readout + heat pulse
"""

import math
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
PREVIEW_DIR = BASE_DIR / "action_previews"
PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

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

def render_scene2_pouring_frame(t: float, total_dur: float = 3.2) -> Image.Image:
    """Renders Scene 2: Natural curved gravity pour from beaker into conical flask."""
    base = Image.open(IMG_DIR / "02_setup_zinc.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Timing: Beaker appears at t=0, pours from t=0.3s to 2.8s
    pour_active = (t >= 0.25)
    progress = min(1.0, max(0.0, (t - 0.25) / (total_dur * 0.75)))

    # Flask geometry in 02_setup_zinc.jpg:
    # Neck center: (460, 480)
    # Base: left at (260, 1420), right at (640, 1420), bottom y=1420
    # Liquid rises from y=1420 up to y=1230
    fill_h = int(190 * progress)

    # 1. Rising Liquid Layer inside conical flask
    if fill_h > 0:
        fill_y = 1420 - fill_h
        # Conical slope calculation: left wall slopes from (420, 520) to (260, 1420)
        # right wall slopes from (500, 520) to (640, 1420)
        p_slope = fill_h / 900.0
        cur_left = int(260 + (420 - 260) * p_slope)
        cur_right = int(640 - (640 - 500) * p_slope)

        # Translucent acid liquid pool
        liquid_poly = [
            (260, 1420),
            (cur_left, fill_y),
            (cur_right, fill_y),
            (640, 1420)
        ]
        draw.polygon(liquid_poly, fill=(200, 240, 255, 95))
        
        # Subtle meniscus curve and bright highlight
        draw.line([(cur_left + 5, fill_y), (cur_right - 5, fill_y)], fill=(255, 255, 255, 210), width=3)
        draw.ellipse([cur_left, fill_y - 4, cur_right, fill_y + 4], outline=(220, 245, 255, 140), width=2)

        # Expanding ripples where pouring stream hits liquid
        impact_x = 460
        r_age = (t * 4.0) % 1.0
        for r_offset in [0.0, 0.5]:
            r_prog = (r_age + r_offset) % 1.0
            rw = int(20 + 80 * r_prog)
            rh = int(6 + 18 * r_prog)
            ra = int(200 * (1.0 - r_prog))
            draw.ellipse([impact_x - rw, fill_y - rh, impact_x + rw, fill_y + rh], 
                         outline=(255, 255, 255, ra), width=2)

    # 2. Pouring Beaker & Curved Liquid Stream
    # Beaker pouring lip positioned at top-left: (330, 260)
    lip_x, lip_y = 340, 280
    neck_x, neck_y = 465, 480
    impact_y = 1420 - fill_h

    if pour_active:
        # Generate smooth gravity-curved stream using Bézier points
        stream_pts = []
        num_steps = 35
        # Gravity curve from lip (340, 280) through neck (465, 480) down to impact (460, impact_y)
        for i in range(num_steps + 1):
            u = i / float(num_steps)
            if u < 0.4:
                # Segment 1: Beaker lip to flask neck
                v = u / 0.4
                # Cubic Bezier: p0=(340, 280), p1=(420, 290), p2=(465, 380), p3=(465, 480)
                px = (1-v)**3 * lip_x + 3*(1-v)**2 * v * 410 + 3*(1-v) * v**2 * 460 + v**3 * neck_x
                py = (1-v)**3 * lip_y + 3*(1-v)**2 * v * 290 + 3*(1-v) * v**2 * 390 + v**3 * neck_y
            else:
                # Segment 2: Freefall down inside flask
                v = (u - 0.4) / 0.6
                px = neck_x + math.sin(v * math.pi * 3 + t * 18) * 3 # subtle turbulent wobble
                py = neck_y + (impact_y - neck_y) * v
            stream_pts.append((px, py))

        # Draw stream with outer glow, translucent core, and white specular highlight
        for i in range(len(stream_pts) - 1):
            p1 = stream_pts[i]
            p2 = stream_pts[i+1]
            # Width decreases as liquid accelerates downwards (gravity stretching)
            u = i / len(stream_pts)
            w = max(6, int(22 * (1.0 - u * 0.55)))

            # Outer soft refraction
            draw.line([p1, p2], fill=(180, 235, 255, 110), width=w + 6)
            # Inner clear liquid core
            draw.line([p1, p2], fill=(230, 250, 255, 190), width=w)
            # Specular bright edge
            hl_p1 = (p1[0] - w * 0.25, p1[1])
            hl_p2 = (p2[0] - w * 0.25, p2[1])
            draw.line([hl_p1, hl_p2], fill=(255, 255, 255, 240), width=max(2, int(w * 0.28)))

        # Splashing micro-droplets at impact point
        random.seed(int(t * 80))
        for _ in range(10):
            dx = random.randint(-35, 35)
            dy = -random.randint(8, 45)
            dr = random.randint(2, 6)
            draw.ellipse([impact_x + dx - dr, impact_y + dy - dr, impact_x + dx + dr, impact_y + dy + dr],
                         fill=(245, 252, 255, 220))

    # 3. Draw Tilted Glass Beaker pouring the acid (at top-left)
    beaker_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beaker_overlay)
    # Beaker rim polygon tilted ~35 degrees
    bx, by = 280, 240
    # Glass beaker body
    b_pts = [(160, 160), (340, 275), (290, 360), (110, 245)]
    bdraw.polygon(b_pts, fill=(230, 245, 255, 65), outline=(255, 255, 255, 200))
    # Beaker liquid meniscus inside
    b_liq = [(180, 200), (330, 275), (280, 340), (130, 260)]
    bdraw.polygon(b_liq, fill=(200, 240, 255, 140))
    # Beaker measurement marks
    bdraw.line([(220, 230), (240, 245)], fill=(255, 255, 255, 220), width=2)
    bdraw.line([(240, 260), (260, 275)], fill=(255, 255, 255, 220), width=2)
    bdraw.text((150, 120), "DILUTE H2SO4", font=get_font(24, bold=True), fill=(0, 229, 255, 230))
    
    # Composite beaker
    comp = Image.alpha_composite(base, overlay)
    comp = Image.alpha_composite(comp, beaker_overlay)

    # 4. M3 Action HUD Overlays (Clean spacing, zero overlap)
    hud = ImageDraw.Draw(comp)
    # Header card (height 150px)
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 230), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • ADDING REACTANTS", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Pouring Dilute H2SO4 into Flask", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Acid covers the zinc granules at the bottom", font=get_font(24), fill=(180, 210, 230))

    # Reality Check Card at bottom
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: ZINC GRANULES", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Silvery-gray irregular, rough metallic pieces", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation for CBSE Board viva", font=get_font(23), fill=(190, 210, 230))

    return comp

def render_scene3_effervescence_frame(t: float, total_dur: float = 8.2) -> Image.Image:
    """Renders Scene 3: High-density active bubbling effervescence engine."""
    base = Image.open(IMG_DIR / "03_reaction_effervescence.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # 380 active bubbles nucleating on zinc granules at bottom and surging upward
    NUM_BUBBLES = 380
    random.seed(42)
    
    bubble_params = []
    for i in range(NUM_BUBBLES):
        # Spawning across bottom zinc granule zone
        spawn_x = random.randint(180, 900)
        spawn_y = random.randint(1250, 1780)
        speed = random.uniform(220, 520)     # upward pixels/sec
        radius = random.uniform(3.0, 15.0)   # bubble radius
        wobble_freq = random.uniform(5.0, 12.0)
        wobble_amp = random.uniform(5.0, 20.0)
        phase = random.uniform(0, 2 * math.pi)
        lifetime = (spawn_y - 360) / speed   # reaches top around y=360
        birth_offset = random.uniform(0, lifetime)
        bubble_params.append((spawn_x, spawn_y, speed, radius, wobble_freq, wobble_amp, phase, lifetime, birth_offset))

    # Render each bubble with 3D spherical shading
    for bp in bubble_params:
        spawn_x, spawn_y, speed, radius, wobble_freq, wobble_amp, phase, lifetime, birth_offset = bp
        age = (t + birth_offset) % lifetime
        cur_y = spawn_y - (speed * age)
        cur_x = spawn_x + math.sin(age * wobble_freq + phase) * wobble_amp
        
        # Grow as hydrostatic pressure decreases
        cur_r = radius * (1.0 + 0.3 * (age / lifetime))

        # Translucent aqua bubble sphere
        draw.ellipse([cur_x - cur_r, cur_y - cur_r, cur_x + cur_r, cur_y + cur_r],
                     fill=(215, 248, 255, 115), outline=(255, 255, 255, 185), width=int(max(1, cur_r * 0.16)))
        
        # 3D Specular highlight crescent in upper-left
        hl_r = max(1.5, cur_r * 0.36)
        hl_x = cur_x - cur_r * 0.32
        hl_y = cur_y - cur_r * 0.32
        draw.ellipse([hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r],
                     fill=(255, 255, 255, 230))

    # Meniscus Froth & Bursting Rings at liquid surface (y ≈ 360 to 440)
    random.seed(int(t * 30))
    for _ in range(20):
        fx = random.randint(240, 840)
        fy = random.randint(370, 430)
        fr = random.randint(4, 14)
        draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], outline=(255, 255, 255, 170), width=2)

    comp = Image.alpha_composite(base, overlay)

    # Clean M3 Overlays (No text collision)
    hud = ImageDraw.Draw(comp)
    # Header card (height 170px)
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 230), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 135), "STEP 2 • VIGOROUS REACTION", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 172), "RAPID H2 EFFERVESCENCE!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Bubbles of Hydrogen gas fizz violently off Zinc metal", font=get_font(24), fill=(190, 225, 210))

    # Equation Card at bottom
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 1655), "BALANCED CHEMICAL EQUATION", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 1698), "Zn solid + H2SO4 → ZnSO4 + H2 ↑", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Zinc + Dilute Sulphuric Acid → Zinc Sulphate + Hydrogen Gas", font=get_font(23), fill=(185, 215, 235))

    return comp

def render_scene4_exothermic_frame(t: float, total_dur: float = 5.6) -> Image.Image:
    """Renders Scene 4: Laboratory thermometer probe immersed in flask liquid."""
    base = Image.open(IMG_DIR / "04_takeaway_exothermic.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Temperature calculation (climbs smoothly from 24.5°C to 48.6°C)
    progress = min(1.0, t / (total_dur * 0.85))
    smooth_p = 1.0 - math.cos(progress * math.pi * 0.5)
    current_temp = 24.5 + (48.6 - 24.5) * smooth_p

    # Dynamic temperature color shift
    if current_temp < 36.0:
        r_col = int(0 + (current_temp - 24.5) / 11.5 * 255)
        g_col = int(220 - (current_temp - 24.5) / 11.5 * 60)
        b_col = int(255 - (current_temp - 24.5) / 11.5 * 200)
    else:
        r_col = 255
        g_col = int(160 - (current_temp - 36.0) / 12.6 * 120)
        b_col = int(55 - (current_temp - 36.0) / 12.6 * 55)
    temp_color = (r_col, g_col, b_col)

    # 1. Warm thermal pulse around bottom of flask
    pulse_alpha = int(50 + math.sin(t * 6) * 30)
    draw.ellipse([450, 1250, 850, 1600], fill=(255, 80, 20, pulse_alpha))

    # 2. Laboratory Stem Thermometer Immersed in Flask Liquid
    # Flask in 04_takeaway_exothermic.jpg: liquid is around x=640, y=1200-1420
    tx = 645
    t_top = 460
    t_bottom = 1380
    stem_w = 20

    # Outer glass capillary
    draw.rounded_rectangle([tx - stem_w//2, t_top, tx + stem_w//2, t_bottom], radius=10, 
                           fill=(235, 248, 255, 90), outline=(255, 255, 255, 200), width=2)
    # Bulb submerged in liquid
    bulb_r = 22
    draw.ellipse([tx - bulb_r, t_bottom - 20, tx + bulb_r, t_bottom + bulb_r * 2 - 20], fill=temp_color)

    # Mercury liquid column rising: 20°C at y=1300, 50°C at y=580
    mercury_y = int(1300 - (current_temp - 20.0) / 30.0 * 720)
    draw.rounded_rectangle([tx - 5, mercury_y, tx + 5, t_bottom], radius=5, fill=temp_color)

    # Graduation tick marks & labels
    for deg in [20, 30, 40, 50]:
        ty = int(1300 - (deg - 20.0) / 30.0 * 720)
        draw.line([(tx - 24, ty), (tx - 12, ty)], fill=(255, 255, 255, 210), width=2)
        draw.text((tx - 76, ty - 12), f"{deg}°C", font=get_font(20, bold=True), fill=(255, 255, 255, 220))

    comp = Image.alpha_composite(base, overlay)

    # 3. Active Digital Temperature Meter Card (Left side, clear of hands)
    hud = ImageDraw.Draw(comp)
    meter_box = [80, 680, 520, 940]
    hud.rounded_rectangle(meter_box, radius=20, fill=(14, 20, 32, 235), outline=temp_color, width=4)
    hud.text((110, 705), "FLASK TEMPERATURE", font=get_font(22, bold=True), fill=(180, 200, 220))
    hud.text((110, 742), f"{current_temp:.1f} °C", font=get_font(64, bold=True), fill=temp_color)
    delta = current_temp - 24.5
    hud.text((110, 835), f"▲ +{delta:.1f}°C RISE", font=get_font(28, bold=True), fill=(255, 87, 34))
    hud.text((110, 880), "Exothermic heat released", font=get_font(22), fill=(200, 210, 225))

    # Header badge (height 170px)
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 230), outline=(255, 87, 34, 190), width=3)
    hud.text((100, 135), "STEP 3 • TEMPERATURE OBSERVATION", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 172), "EXOTHERMIC REACTION!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Flask becomes distinctly warm to the touch", font=get_font(24), fill=(225, 200, 200))

    # Takeaway Card at bottom
    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "CLASS 10 BOARD EXAM TAKEAWAY", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Exothermic Reaction: Heat is Released", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation: Temperature rises during reaction", font=get_font(23), fill=(195, 215, 230))

    return comp

def main():
    print("Generating refined action composite frames...")
    s2 = render_scene2_pouring_frame(1.8).convert("RGB")
    s2.save(PREVIEW_DIR / "preview_scene2_pouring.jpg", quality=95)
    print("Saved preview_scene2_pouring.jpg")

    s3 = render_scene3_effervescence_frame(3.5).convert("RGB")
    s3.save(PREVIEW_DIR / "preview_scene3_effervescence.jpg", quality=95)
    print("Saved preview_scene3_effervescence.jpg")

    s4 = render_scene4_exothermic_frame(3.8).convert("RGB")
    s4.save(PREVIEW_DIR / "preview_scene4_exothermic.jpg", quality=95)
    print("Saved preview_scene4_exothermic.jpg")

if __name__ == "__main__":
    main()
