#!/usr/bin/env python3
"""
Complete Action Composite Master Video Generator for CBSE Class 10 Activity 1.3:
Combines authentic photorealistic chemistry with real procedural experiment action:
1. Pop Sound Hook (Veo match ignition)
2. Pouring Dilute Acid (Tilted beaker + gravity stream + rising liquid + reality check)
3. Vigorous Effervescence (380 active 3D bubbles + frothing + balanced equation)
4. Exothermic Rise (Thermometer immersed in liquid + climbing mercury & digital readout)
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
VID_RAW_DIR = BASE_DIR / "videos_raw"
OVERLAYS_DIR = BASE_DIR / "overlays_m3"
CLIPS_DIR = BASE_DIR / "clips_action"
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

# ---------------------------------------------------------------------------
# SCENE 1: RENDER VEO HOOK CLIP
# ---------------------------------------------------------------------------
def render_scene1(out_path: Path, audio_path: Path) -> Path:
    dur = get_duration(audio_path)
    print(f"[Scene 1] Assembling Veo Match Pop Hook (dur={dur:.2f}s)...")
    veo_vid = VID_RAW_DIR / "01_hook_pop.mp4"
    overlay = OVERLAYS_DIR / "overlay_01_hook.png"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(veo_vid),
        "-i", str(overlay),
        "-i", str(audio_path),
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vbase];"
        "[vbase][1:v]overlay=0:0[vout]",
        "-map", "[vout]", "-map", "2:a",
        "-t", str(dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_path

# ---------------------------------------------------------------------------
# SCENE 2: PROCEDURAL POURING ACID FRAME
# ---------------------------------------------------------------------------
base_img_s2 = Image.open(IMG_DIR / "02_setup_zinc.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

def render_scene2_frame(t: float, total_dur: float) -> Image.Image:
    base = base_img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    pour_active = (t >= 0.25)
    progress = min(1.0, max(0.0, (t - 0.25) / (total_dur * 0.75)))
    fill_h = int(190 * progress)

    if fill_h > 0:
        fill_y = 1420 - fill_h
        p_slope = fill_h / 900.0
        cur_left = int(260 + (420 - 260) * p_slope)
        cur_right = int(640 - (640 - 500) * p_slope)

        liquid_poly = [(260, 1420), (cur_left, fill_y), (cur_right, fill_y), (640, 1420)]
        draw.polygon(liquid_poly, fill=(200, 240, 255, 95))
        draw.line([(cur_left + 5, fill_y), (cur_right - 5, fill_y)], fill=(255, 255, 255, 210), width=3)
        draw.ellipse([cur_left, fill_y - 4, cur_right, fill_y + 4], outline=(220, 245, 255, 140), width=2)

        impact_x = 460
        r_age = (t * 4.0) % 1.0
        for r_offset in [0.0, 0.5]:
            r_prog = (r_age + r_offset) % 1.0
            rw = int(20 + 80 * r_prog)
            rh = int(6 + 18 * r_prog)
            ra = int(200 * (1.0 - r_prog))
            draw.ellipse([impact_x - rw, fill_y - rh, impact_x + rw, fill_y + rh], outline=(255, 255, 255, ra), width=2)

    lip_x, lip_y = 340, 280
    neck_x, neck_y = 465, 480
    impact_y = 1420 - fill_h

    if pour_active:
        stream_pts = []
        num_steps = 35
        for i in range(num_steps + 1):
            u = i / float(num_steps)
            if u < 0.4:
                v = u / 0.4
                px = (1-v)**3 * lip_x + 3*(1-v)**2 * v * 410 + 3*(1-v) * v**2 * 460 + v**3 * neck_x
                py = (1-v)**3 * lip_y + 3*(1-v)**2 * v * 290 + 3*(1-v) * v**2 * 390 + v**3 * neck_y
            else:
                v = (u - 0.4) / 0.6
                px = neck_x + math.sin(v * math.pi * 3 + t * 18) * 3
                py = neck_y + (impact_y - neck_y) * v
            stream_pts.append((px, py))

        for i in range(len(stream_pts) - 1):
            p1, p2 = stream_pts[i], stream_pts[i+1]
            u = i / len(stream_pts)
            w = max(6, int(22 * (1.0 - u * 0.55)))
            draw.line([p1, p2], fill=(180, 235, 255, 110), width=w + 6)
            draw.line([p1, p2], fill=(230, 250, 255, 190), width=w)
            hl_p1 = (p1[0] - w * 0.25, p1[1])
            hl_p2 = (p2[0] - w * 0.25, p2[1])
            draw.line([hl_p1, hl_p2], fill=(255, 255, 255, 240), width=max(2, int(w * 0.28)))

        random.seed(int(t * 80))
        for _ in range(10):
            dx = random.randint(-35, 35)
            dy = -random.randint(8, 45)
            dr = random.randint(2, 6)
            draw.ellipse([impact_x + dx - dr, impact_y + dy - dr, impact_x + dx + dr, impact_y + dy + dr], fill=(245, 252, 255, 220))

    # Tilted Beaker
    beaker_overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beaker_overlay)
    b_pts = [(160, 160), (340, 275), (290, 360), (110, 245)]
    bdraw.polygon(b_pts, fill=(230, 245, 255, 65), outline=(255, 255, 255, 200))
    b_liq = [(180, 200), (330, 275), (280, 340), (130, 260)]
    bdraw.polygon(b_liq, fill=(200, 240, 255, 140))
    bdraw.line([(220, 230), (240, 245)], fill=(255, 255, 255, 220), width=2)
    bdraw.line([(240, 260), (260, 275)], fill=(255, 255, 255, 220), width=2)
    bdraw.text((150, 120), "DILUTE H2SO4", font=get_font(24, bold=True), fill=(0, 229, 255, 230))

    comp = Image.alpha_composite(base, overlay)
    comp = Image.alpha_composite(comp, beaker_overlay)

    # Overlays
    hud = ImageDraw.Draw(comp)
    hud.rounded_rectangle([60, 110, 1020, 270], radius=24, fill=(16, 22, 36, 230), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 135), "STEP 1 • ADDING REACTANTS", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 172), "Pouring Dilute H2SO4 into Flask", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 224), "Acid covers the zinc granules at the bottom", font=get_font(24), fill=(180, 210, 230))

    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "LAB REALITY CHECK: ZINC GRANULES", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Silvery-gray irregular, rough metallic pieces", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation for CBSE Board viva", font=get_font(23), fill=(190, 210, 230))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 3: PROCEDURAL ACTIVE EFFERVESCENCE FRAME
# ---------------------------------------------------------------------------
base_img_s3 = Image.open(IMG_DIR / "03_reaction_effervescence.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# Pre-calculate 380 bubble parameters for deterministic physics
random.seed(42)
NUM_BUBBLES = 380
BUBBLE_PARAMS = []
for i in range(NUM_BUBBLES):
    spawn_x = random.randint(180, 900)
    spawn_y = random.randint(1250, 1780)
    speed = random.uniform(220, 520)
    radius = random.uniform(3.0, 15.0)
    wobble_freq = random.uniform(5.0, 12.0)
    wobble_amp = random.uniform(5.0, 20.0)
    phase = random.uniform(0, 2 * math.pi)
    lifetime = (spawn_y - 360) / speed
    birth_offset = random.uniform(0, lifetime)
    BUBBLE_PARAMS.append((spawn_x, spawn_y, speed, radius, wobble_freq, wobble_amp, phase, lifetime, birth_offset))

def render_scene3_frame(t: float, total_dur: float) -> Image.Image:
    base = base_img_s3.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for bp in BUBBLE_PARAMS:
        spawn_x, spawn_y, speed, radius, wobble_freq, wobble_amp, phase, lifetime, birth_offset = bp
        age = (t + birth_offset) % lifetime
        cur_y = spawn_y - (speed * age)
        cur_x = spawn_x + math.sin(age * wobble_freq + phase) * wobble_amp
        cur_r = radius * (1.0 + 0.3 * (age / lifetime))

        draw.ellipse([cur_x - cur_r, cur_y - cur_r, cur_x + cur_r, cur_y + cur_r],
                     fill=(215, 248, 255, 115), outline=(255, 255, 255, 185), width=int(max(1, cur_r * 0.16)))
        hl_r = max(1.5, cur_r * 0.36)
        hl_x = cur_x - cur_r * 0.32
        hl_y = cur_y - cur_r * 0.32
        draw.ellipse([hl_x - hl_r, hl_y - hl_r, hl_x + hl_r, hl_y + hl_r], fill=(255, 255, 255, 230))

    random.seed(int(t * 30))
    for _ in range(20):
        fx = random.randint(240, 840)
        fy = random.randint(370, 430)
        fr = random.randint(4, 14)
        draw.ellipse([fx - fr, fy - fr, fx + fr, fy + fr], outline=(255, 255, 255, 170), width=2)

    comp = Image.alpha_composite(base, overlay)

    hud = ImageDraw.Draw(comp)
    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 230), outline=(0, 230, 118, 190), width=3)
    hud.text((100, 135), "STEP 2 • VIGOROUS REACTION", font=get_font(26, bold=True), fill=(0, 230, 118))
    hud.text((100, 172), "RAPID H2 EFFERVESCENCE!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Bubbles of Hydrogen gas fizz violently off Zinc metal", font=get_font(24), fill=(190, 225, 210))

    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(0, 229, 255, 190), width=3)
    hud.text((100, 1655), "BALANCED CHEMICAL EQUATION", font=get_font(26, bold=True), fill=(0, 229, 255))
    hud.text((100, 1698), "Zn solid + H2SO4 → ZnSO4 + H2 ↑", font=get_font(38, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Zinc + Dilute Sulphuric Acid → Zinc Sulphate + Hydrogen Gas", font=get_font(23), fill=(185, 215, 235))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# SCENE 4: PROCEDURAL EXOTHERMIC THERMOMETER FRAME
# ---------------------------------------------------------------------------
base_img_s4 = Image.open(IMG_DIR / "04_takeaway_exothermic.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

def render_scene4_frame(t: float, total_dur: float) -> Image.Image:
    base = base_img_s4.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    progress = min(1.0, t / (total_dur * 0.85))
    smooth_p = 1.0 - math.cos(progress * math.pi * 0.5)
    current_temp = 24.5 + (48.6 - 24.5) * smooth_p

    if current_temp < 36.0:
        r_col = int(0 + (current_temp - 24.5) / 11.5 * 255)
        g_col = int(220 - (current_temp - 24.5) / 11.5 * 60)
        b_col = int(255 - (current_temp - 24.5) / 11.5 * 200)
    else:
        r_col = 255
        g_col = int(160 - (current_temp - 36.0) / 12.6 * 120)
        b_col = int(55 - (current_temp - 36.0) / 12.6 * 55)
    temp_color = (r_col, g_col, b_col)

    pulse_alpha = int(50 + math.sin(t * 6) * 30)
    draw.ellipse([450, 1250, 850, 1600], fill=(255, 80, 20, pulse_alpha))

    tx = 645
    t_top = 460
    t_bottom = 1380
    stem_w = 20

    draw.rounded_rectangle([tx - stem_w//2, t_top, tx + stem_w//2, t_bottom], radius=10, 
                           fill=(235, 248, 255, 90), outline=(255, 255, 255, 200), width=2)
    bulb_r = 22
    draw.ellipse([tx - bulb_r, t_bottom - 20, tx + bulb_r, t_bottom + bulb_r * 2 - 20], fill=temp_color)

    mercury_y = int(1300 - (current_temp - 20.0) / 30.0 * 720)
    draw.rounded_rectangle([tx - 5, mercury_y, tx + 5, t_bottom], radius=5, fill=temp_color)

    for deg in [20, 30, 40, 50]:
        ty = int(1300 - (deg - 20.0) / 30.0 * 720)
        draw.line([(tx - 24, ty), (tx - 12, ty)], fill=(255, 255, 255, 210), width=2)
        draw.text((tx - 76, ty - 12), f"{deg}°C", font=get_font(20, bold=True), fill=(255, 255, 255, 220))

    comp = Image.alpha_composite(base, overlay)

    hud = ImageDraw.Draw(comp)
    meter_box = [80, 680, 520, 940]
    hud.rounded_rectangle(meter_box, radius=20, fill=(14, 20, 32, 235), outline=temp_color, width=4)
    hud.text((110, 705), "FLASK TEMPERATURE", font=get_font(22, bold=True), fill=(180, 200, 220))
    hud.text((110, 742), f"{current_temp:.1f} °C", font=get_font(64, bold=True), fill=temp_color)
    delta = current_temp - 24.5
    hud.text((110, 835), f"▲ +{delta:.1f}°C RISE", font=get_font(28, bold=True), fill=(255, 87, 34))
    hud.text((110, 880), "Exothermic heat released", font=get_font(22), fill=(200, 210, 225))

    hud.rounded_rectangle([60, 110, 1020, 290], radius=24, fill=(16, 22, 36, 230), outline=(255, 87, 34, 190), width=3)
    hud.text((100, 135), "STEP 3 • TEMPERATURE OBSERVATION", font=get_font(26, bold=True), fill=(255, 87, 34))
    hud.text((100, 172), "EXOTHERMIC REACTION!", font=get_font(42, bold=True), fill=(255, 255, 255))
    hud.text((100, 232), "Flask becomes distinctly warm to the touch", font=get_font(24), fill=(225, 200, 200))

    hud.rounded_rectangle([60, 1630, 1020, 1810], radius=24, fill=(16, 22, 36, 235), outline=(255, 179, 0, 190), width=3)
    hud.text((100, 1655), "CLASS 10 BOARD EXAM TAKEAWAY", font=get_font(26, bold=True), fill=(255, 179, 0))
    hud.text((100, 1698), "Exothermic Reaction: Heat is Released", font=get_font(36, bold=True), fill=(255, 255, 255))
    hud.text((100, 1750), "Direct practical observation: Temperature rises during reaction", font=get_font(23), fill=(195, 215, 230))

    return comp.convert("RGB")

# ---------------------------------------------------------------------------
# RENDER PROCEDURAL VIDEO CLIP PIPED DIRECTLY TO FFMPEG
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
    print("STARTING ACTIVITY 1.3 REAL-WORLD ACTION COMPOSITE ASSEMBLY")
    print("=================================================================\n")

    clips = []

    # Scene 1: Real Veo Match Pop Hook
    c1 = CLIPS_DIR / "01_hook_action.mp4"
    render_scene1(c1, AUDIO_DIR / "01_hook.mp3")
    clips.append(c1)

    # Scene 2: Acid Pouring Action
    c2 = CLIPS_DIR / "02_setup_action.mp4"
    render_procedural_clip(render_scene2_frame, AUDIO_DIR / "02_setup.mp3", c2, "Scene 2 Pouring Acid")
    clips.append(c2)

    # Scene 3: Vigorous Effervescence Action
    c3 = CLIPS_DIR / "03_reaction_action.mp4"
    render_procedural_clip(render_scene3_frame, AUDIO_DIR / "03_reaction.mp3", c3, "Scene 3 Bubbling Effervescence")
    clips.append(c3)

    # Scene 4: Exothermic Thermometer Action
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
    master_video = OUT_DIR / "CBSE-Class-10-Science-Activity-1.3-Zinc-Acid-Real-Action-Shorts.mp4"
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
