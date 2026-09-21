#!/usr/bin/env python3
"""
Complete Action Composite Master Video Generator for CBSE Class 10 Activity 1.4:
Combines authentic photorealistic chemistry with real procedural experiment action:
1. Explosive Steam Hook (Violent billowing steam plumes + boiling water impact)
2. Adding Reactant (Tilted Pyrex beaker pouring stream into CaO lumps + rising liquid)
3. Vigorous Combination Reaction (360 active bubbles + dense steam waves + balanced equation)
4. Exothermic Rise (Mercury rising in physical lab thermometer to 84.8°C + digital LED readout + whitewashing hack)
Pipes frames directly to FFmpeg at 30fps and mixes ducked laboratory BGM.
"""

import math
import random
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
AUDIO_DIR = BASE_DIR / "audio"
CLIPS_DIR = BASE_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\cbse_byCodex\videos\chapterready-promo\audio\bgm_loop.mp3")

WIDTH, HEIGHT = 1080, 1920
FPS = 30

def get_font(size: int, bold: bool = False):
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def get_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)

# Load base images resized to 1080x1920
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

    impact_x, impact_y = 560, 880

    # Boiling flash pulse at water contact
    pulse = 0.5 + 0.5 * math.sin(t * 12.0)
    flash_alpha = int(80 + 60 * pulse)
    draw.ellipse([impact_x - 110, impact_y - 55, impact_x + 110, impact_y + 55], fill=(255, 255, 255, flash_alpha))
    draw.ellipse([impact_x - 55, impact_y - 25, impact_x + 55, impact_y + 25], fill=(255, 240, 180, int(flash_alpha * 0.8)))

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
        alpha = int(140 * (1.0 - prog) * math.sin(prog * math.pi))

        if alpha > 0 and cy > 250:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(245, 250, 255, alpha))
            draw.ellipse([cx - int(r*0.65), cy - int(r*0.65), cx + int(r*0.65), cy + int(r*0.65)], fill=(255, 255, 255, int(alpha*0.6)))

    # Boiling splatter droplets
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
# SCENE 2: POURING WATER INTO BEAKER
# ---------------------------------------------------------------------------
def render_scene2_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    pour_active = (t >= 0.15)
    progress = min(1.0, max(0.0, (t - 0.15) / (total_dur * 0.80)))
    fill_h = int(170 * progress)

    beaker_left = 335
    beaker_right = 605
    fill_y = 1460 - fill_h

    if fill_h > 0:
        liquid_poly = [(beaker_left, 1460), (beaker_left, fill_y), (beaker_right, fill_y), (beaker_right, 1460)]
        draw.polygon(liquid_poly, fill=(205, 245, 255, 95))
        draw.line([(beaker_left, fill_y), (beaker_right, fill_y)], fill=(255, 255, 255, 220), width=3)
        draw.ellipse([beaker_left, fill_y - 6, beaker_right, fill_y + 6], outline=(230, 250, 255, 160), width=2)

        impact_x = 470
        r_age = (t * 4.5) % 1.0
        for r_offset in [0.0, 0.5]:
            r_prog = (r_age + r_offset) % 1.0
            rw = int(18 + 65 * r_prog)
            rh = int(6 + 16 * r_prog)
            ra = int(210 * (1.0 - r_prog))
            draw.ellipse([impact_x - rw, fill_y - rh, impact_x + rw, fill_y + rh], outline=(255, 255, 255, ra), width=2)

    beaker_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beaker_overlay)
    b_pts = [(230, 360), (410, 470), (350, 560), (170, 450)]
    bdraw.polygon(b_pts, fill=(230, 245, 255, 75), outline=(255, 255, 255, 220))
    b_liq = [(250, 400), (400, 470), (340, 540), (190, 470)]
    bdraw.polygon(b_liq, fill=(200, 240, 255, 150))
    bdraw.line([(280, 430), (300, 445)], fill=(255, 255, 255, 220), width=2)
    bdraw.line([(310, 460), (330, 475)], fill=(255, 255, 255, 220), width=2)
    bdraw.text((220, 320), "WATER (H2O)", font=get_font(24, bold=True), fill=(0, 229, 255, 240))

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

        random.seed(int(t * 60))
        for _ in range(8):
            dx = random.randint(-25, 25)
            dy = -random.randint(6, 35)
            dr = random.randint(2, 5)
            draw.ellipse([impact_x + dx - dr, impact_y + dy - dr, impact_x + dx + dr, impact_y + dy + dr], fill=(245, 252, 255, 220))

    comp = Image.alpha_composite(base, overlay)
    comp = Image.alpha_composite(comp, beaker_overlay)

    hud = ImageDraw.Draw(comp)
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • ADDING REACTANTS", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Slowly Adding Water to Quicklime", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Water begins wetting the solid Calcium Oxide lumps", font=get_font(24), fill=(180, 215, 235))

    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: QUICKLIME (CaO)", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Dry, white irregular lumps in Pyrex beaker", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation for CBSE Board viva", font=get_font(23), fill=(190, 210, 230))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 3: VIGOROUS SLAKING REACTION
# ---------------------------------------------------------------------------
random.seed(101)
NUM_BUBBLES_S3 = 360
BUBBLE_PARAMS_S3 = []
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

    # Billowing Steam clouds
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

    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 135), "STEP 2 • VIGOROUS REACTION", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 172), "VIOLENT HISSING & BOILING!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Two substances combine into ONE single product: Slaked Lime!", font=get_font(24), fill=(195, 235, 215))

    hud.rounded_rectangle([60, 1580, 1020, 1820], radius=24, fill=(16, 22, 36, 240), outline=(0, 229, 255, 200), width=3)
    hud.text((100, 1605), "BALANCED CHEMICAL EQUATION • COMBINATION REACTION", font=get_font(24, bold=True), fill=(0, 229, 255))
    hud.text((100, 1648), "CaO (s) + H2O (l) → Ca(OH)2 (aq) + Heat", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1702), "Quicklime + Water → Slaked Lime (Calcium Hydroxide)", font=get_font(23), fill=(185, 220, 240))
    hud.text((100, 1745), "Key Concept: Multiple reactants yield a single product!", font=get_font(22, bold=True), fill=(255, 215, 0))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 4: THERMOMETER ALIGNED EXACTLY TO CAPILLARY (X=546)
# ---------------------------------------------------------------------------
def render_scene4_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s4.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    progress = min(1.0, t / (total_dur * 0.85))
    smooth_p = 1.0 - math.cos(progress * math.pi * 0.5)
    current_temp = 24.5 + (84.8 - 24.5) * smooth_p

    if current_temp < 45.0:
        temp_color = (0, 229, 255)
    elif current_temp < 65.0:
        temp_color = (255, 179, 0)
    else:
        temp_color = (255, 60, 30)

    # Thermal pulse at gloved hand contact
    pulse_alpha = int(55 + math.sin(t * 6) * 30)
    draw.ellipse([480, 1200, 800, 1560], fill=(255, 70, 20, pulse_alpha))

    # Real thermometer capillary is at x=546
    tx = 546
    t_bulb_y = 1250 # inside milky slurry
    # Scale in photo: 0°C is at y ≈ 1180, 85°C is at y ≈ 480
    mercury_top_y = int(1180 - (current_temp / 100.0) * 820)

    # Glowing red mercury column inside physical capillary
    draw.rounded_rectangle([tx - 3, mercury_top_y, tx + 3, t_bulb_y], radius=2, fill=(255, 30, 20, 235))
    draw.line([(tx, mercury_top_y), (tx, t_bulb_y)], fill=(255, 160, 140, 245), width=1)
    # Bulb glow inside slurry
    draw.ellipse([tx - 10, t_bulb_y - 10, tx + 10, t_bulb_y + 10], fill=(255, 40, 20, 240))

    # Temperature indicator pointer
    draw.line([(tx + 8, mercury_top_y), (tx + 45, mercury_top_y)], fill=temp_color, width=3)
    draw.polygon([(tx + 10, mercury_top_y), (tx + 22, mercury_top_y - 6), (tx + 22, mercury_top_y + 6)], fill=temp_color)
    draw.text((tx + 52, mercury_top_y - 18), f"{current_temp:.1f}°C", font=get_font(26, bold=True), fill=temp_color)

    comp = Image.alpha_composite(base, overlay)
    hud = ImageDraw.Draw(comp)

    # Floating Digital LED Readout Box
    meter_box = [70, 680, 480, 930]
    hud.rounded_rectangle(meter_box, radius=20, fill=(14, 20, 32, 235), outline=temp_color, width=4)
    hud.text((100, 705), "SLURRY TEMPERATURE", font=get_font(22, bold=True), fill=(180, 205, 225))
    hud.text((100, 740), f"{current_temp:.1f} °C", font=get_font(62, bold=True), fill=temp_color)
    delta = current_temp - 24.5
    hud.text((100, 830), f"▲ +{delta:.1f}°C HEAT SPIKE!", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 872), "Extreme exothermic energy release", font=get_font(20), fill=(200, 215, 230))

    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 235), outline=(255, 87, 34, 190), width=3)
    hud.text((100, 135), "STEP 3 • OBSERVATION & INFERENCE", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 172), "EXOTHERMIC COMBINATION!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Beaker becomes burning hot to the touch as heat is liberated!", font=get_font(24), fill=(225, 205, 205))

    hud.rounded_rectangle([60, 1590, 1020, 1810], radius=24, fill=(16, 22, 36, 240), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1612), "CLASS 10 BOARD EXAM 100% HACK", font=get_font(24, bold=True), fill=(255, 179, 0))
    hud.text((100, 1650), "Whitewashing: Slaked lime Ca(OH)2 on walls", font=get_font(34, bold=True), fill=(255, 255, 255))
    hud.text((100, 1700), "Reacts with air CO2 to form shiny marble CaCO3 in 2-3 days", font=get_font(23), fill=(195, 220, 235))
    hud.text((100, 1742), "Exam Question: Why do whitewashed walls shine after 2 days?", font=get_font(21, bold=True), fill=(0, 229, 255))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# PROCEDURAL VIDEO CLIP PIPED DIRECTLY TO FFMPEG
# ---------------------------------------------------------------------------
def render_procedural_clip(render_fn, audio_path: Path, out_path: Path, scene_name: str) -> Path:
    dur = get_duration(audio_path)
    total_frames = int(dur * FPS)
    print(f"[{scene_name}] Rendering {total_frames} frames ({dur:.2f}s at {FPS}fps) directly to FFmpeg...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-", # stdin
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "veryfast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]

    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for frame_idx in range(total_frames):
        t = frame_idx / float(FPS)
        img = render_fn(t, dur)
        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"[{scene_name}] Done -> {out_path.name}")
    return out_path

# ---------------------------------------------------------------------------
# MAIN ASSEMBLY
# ---------------------------------------------------------------------------
def main():
    print("=================================================================")
    print("STARTING ACTIVITY 1.4 REAL-WORLD ACTION COMPOSITE ASSEMBLY")
    print("=================================================================\n")

    clips = []

    # Scene 1: Explosive Steam Hook
    c1 = CLIPS_DIR / "01_hook_action.mp4"
    render_procedural_clip(render_scene1_frame, AUDIO_DIR / "01_hook.mp3", c1, "Scene 1 Steam Hook")
    clips.append(c1)

    # Scene 2: Pouring Water
    c2 = CLIPS_DIR / "02_setup_action.mp4"
    render_procedural_clip(render_scene2_frame, AUDIO_DIR / "02_setup.mp3", c2, "Scene 2 Pouring Water")
    clips.append(c2)

    # Scene 3: Vigorous Slaking Reaction
    c3 = CLIPS_DIR / "03_reaction_action.mp4"
    render_procedural_clip(render_scene3_frame, AUDIO_DIR / "03_reaction.mp3", c3, "Scene 3 Slaking Reaction")
    clips.append(c3)

    # Scene 4: Exothermic Thermometer Rise
    c4 = CLIPS_DIR / "04_takeaway_action.mp4"
    render_procedural_clip(render_scene4_frame, AUDIO_DIR / "04_takeaway.mp3", c4, "Scene 4 Exothermic Heat")
    clips.append(c4)

    # Concatenate clips
    concat_list = CLIPS_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in clips:
            safe_p = str(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    temp_concat = OUT_DIR / "temp_action_concat.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(temp_concat)
    ]
    subprocess.run(cmd_concat, check=True)

    # Mix BGM ducked at -19dB
    master_video = OUT_DIR / "CBSE-Class-10-Science-Activity-1.4-Quicklime-Water-Shorts.mp4"
    actual_dur = get_duration(temp_concat)
    print(f"\nMixing Background Music ducked under speech for {actual_dur:.2f}s...")

    filter_music = (
        f"[0:a]volume=1.0[vo];"
        f"[1:a]aloop=loop=-1:size=2e+09,volume=0.11,"
        f"afade=t=in:st=0:d=1.0,"
        f"afade=t=out:st={actual_dur-2.0}:d=2.0[bgm];"
        f"[vo][bgm]amix=inputs=2:duration=first:dropout_transition=2[aout]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(temp_concat),
        "-i", str(BGM_PATH),
        "-filter_complex", filter_music,
        "-map", "0:v", "-map", "[aout]",
        "-t", str(actual_dur),
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(master_video)
    ]
    subprocess.run(cmd_mix, check=True)

    if temp_concat.exists():
        temp_concat.unlink()

    size_mb = master_video.stat().st_size / (1024 * 1024)
    print("\n=================================================================")
    print("*** REAL-WORLD ACTION COMPOSITE SHORTS RENDERED SUCCESSFULLY! ***")
    print(f"File: {master_video.name}")
    print(f"Path: {master_video}")
    print(f"Duration: {actual_dur:.2f} seconds")
    print(f"File Size: {size_mb:.2f} MB")
    print("=================================================================")

if __name__ == "__main__":
    main()
