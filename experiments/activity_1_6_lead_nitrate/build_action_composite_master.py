#!/usr/bin/env python3
"""
Complete Action Composite Master Video Generator for CBSE Class 10 Activity 1.6:
Thermal Decomposition of Lead Nitrate (Pb(NO3)2).

Strictly adheres to:
1. 18-21s High-Retention Runtime Envelope (Total: ~18.6s)
2. Strict ~4.5s Scene Duration Ceiling
3. Natural, educational voiceover pacing (zero ffmpeg atempo distortion)
4. Procedural Physical Action per scene (Zero static slideshow)
5. Closing Rapid-Fire Quiz Call-To-Action (Driving comment and like velocity)
Pipes raw RGB24 frames directly to FFmpeg stdin at 30fps and mixes ducked laboratory BGM.
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
img_s1 = Image.open(IMG_DIR / "01_hook_brown_fumes.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s2 = Image.open(IMG_DIR / "02_setup_dry_powder.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s3 = Image.open(IMG_DIR / "03_reaction_yellow_residue.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
img_s4 = Image.open(IMG_DIR / "04_takeaway_safety_wafting.jpg").convert("RGBA").resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)

# ---------------------------------------------------------------------------
# SCENE 1: SHOCK HOOK (4.59s)
# ---------------------------------------------------------------------------
def render_scene1_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s1.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

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
# SCENE 2: SETUP & CRYSTALS (4.12s)
# ---------------------------------------------------------------------------
def render_scene2_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s2.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

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
# SCENE 3: STRONG DECOMPOSITION & BROWN FUMES (4.06s)
# ---------------------------------------------------------------------------
def render_scene3_frame(t: float, total_dur: float) -> Image.Image:
    base = img_s3.copy()
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

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
# SCENE 4: WAFTING SAFETY & RAPID-FIRE QUIZ CTA (4.86s + 1.0s tail)
# ---------------------------------------------------------------------------
def render_scene4_frame(t: float, total_dur: float) -> Image.Image:
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

# ---------------------------------------------------------------------------
# RENDER PROCEDURAL VIDEO CLIP DIRECT TO FFMPEG
# ---------------------------------------------------------------------------
def render_procedural_clip(render_fn, audio_path: Path, out_path: Path, scene_name: str, pad_seconds: float = 0.0) -> Path:
    dur = get_duration(audio_path) + pad_seconds
    total_frames = int(dur * FPS)
    print(f"[{scene_name}] Rendering {total_frames} frames ({dur:.2f}s at {FPS}fps) directly to FFmpeg...")

    # If pad_seconds > 0, pad audio with silence so video and audio match exactly
    if pad_seconds > 0:
        padded_audio = audio_path.parent / f"{audio_path.stem}_padded.mp3"
        subprocess.run([
            "ffmpeg", "-y", "-i", str(audio_path),
            "-af", f"apad=pad_dur={pad_seconds}",
            str(padded_audio)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        active_audio = padded_audio
    else:
        active_audio = audio_path

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{WIDTH}x{HEIGHT}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-", # stdin
        "-i", str(active_audio),
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
    print("STARTING ACTIVITY 1.6 REAL-WORLD ACTION COMPOSITE ASSEMBLY")
    print("=================================================================\n")

    clips = []

    # Scene 1: Shock Climax Hook (4.59s)
    c1 = CLIPS_DIR / "01_hook_action.mp4"
    render_procedural_clip(render_scene1_frame, AUDIO_DIR / "01_hook.mp3", c1, "Scene 1 Shock Hook")
    clips.append(c1)

    # Scene 2: Dry Crystals & Decrepitation (4.12s)
    c2 = CLIPS_DIR / "02_setup_action.mp4"
    render_procedural_clip(render_scene2_frame, AUDIO_DIR / "02_setup.mp3", c2, "Scene 2 Setup")
    clips.append(c2)

    # Scene 3: Strong Decomposition & Brown Fumes (4.06s)
    c3 = CLIPS_DIR / "03_reaction_action.mp4"
    render_procedural_clip(render_scene3_frame, AUDIO_DIR / "03_reaction.mp3", c3, "Scene 3 Decomposition")
    clips.append(c3)

    # Scene 4: Safety & Quiz CTA (4.86s + 1.0s visual tail for comment conversion = ~5.86s)
    c4 = CLIPS_DIR / "04_takeaway_action.mp4"
    render_procedural_clip(render_scene4_frame, AUDIO_DIR / "04_takeaway.mp3", c4, "Scene 4 Safety Quiz CTA", pad_seconds=1.0)
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
    master_video = OUT_DIR / "CBSE-Class-10-Science-Activity-1.6-Lead-Nitrate-Decomposition-Shorts.mp4"
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
    print(f"Duration: {actual_dur:.2f} seconds (Target: 18 - 21s)")
    print(f"File Size: {size_mb:.2f} MB")
    print("=================================================================")

if __name__ == "__main__":
    main()
