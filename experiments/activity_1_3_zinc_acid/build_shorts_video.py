#!/usr/bin/env python3
"""
Master Video Assembly Script for CBSE Class 10 Science Activity 1.3
(Zinc Granules + Dilute Acid -> Hydrogen Gas & Exothermic Reaction) YouTube Short.

Combines:
1. Google Veo 3.1 Fast AI-generated video clips (Acts 1 & 2)
2. High-speed scientific photography with dynamic motion (Acts 3 & 4)
3. Material 3 Expressive transparent overlays (100% bracket-free)
4. ElevenLabs AI Voiceover (Charlie)
5. Ducked Background Music (-19dB)
"""

import os
import subprocess
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
VID_DIR = BASE_DIR / "videos_raw"
AUDIO_DIR = BASE_DIR / "audio"
OVERLAYS_DIR = BASE_DIR / "overlays_m3"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR = BASE_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\cbse_byCodex\videos\chapterready-promo\audio\bgm_loop.mp3")

def get_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)

def render_veo_clip(video_path: Path, overlay_path: Path, audio_path: Path, out_path: Path) -> Path:
    """Renders a Veo AI video clip scaled to 1080x1920 with overlay and synced audio."""
    dur = get_duration(audio_path)
    print(f"Rendering Veo video clip: {video_path.name} (dur={dur:.2f}s)...")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(overlay_path),
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

def render_image_clip(image_path: Path, overlay_path: Path, audio_path: Path, out_path: Path, zoom_filter: str) -> Path:
    """Renders an image with composite overlay and Ken Burns zoompan with synced audio."""
    dur = get_duration(audio_path)
    print(f"Rendering animated image clip: {image_path.name} (dur={dur:.2f}s)...")
    
    # Pre-composite image + overlay for smooth high-res rendering
    base_img = Image.open(image_path).convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    ov = Image.open(overlay_path).convert("RGBA")
    comp = Image.alpha_composite(base_img, ov).convert("RGB")
    temp_comp = CLIPS_DIR / f"temp_{image_path.stem}.jpg"
    comp.save(temp_comp, quality=95)
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(temp_comp),
        "-i", str(audio_path),
        "-vf", zoom_filter,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_path)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if temp_comp.exists():
        temp_comp.unlink()
    return out_path

def main():
    print("=================================================================")
    print("STARTING ACTIVITY 1.3 YOUTUBE SHORTS ASSEMBLY PIPELINE")
    print("=================================================================\n")

    clip_paths = []

    # Scene 1: Veo AI Video (Pop Sound Hook)
    c1 = CLIPS_DIR / "01_hook_clip.mp4"
    render_veo_clip(
        VID_DIR / "01_hook_pop.mp4",
        OVERLAYS_DIR / "overlay_01_hook.png",
        AUDIO_DIR / "01_hook.mp3",
        c1
    )
    clip_paths.append(c1)

    # Scene 2: Veo AI Video (Setup Zinc & Acid)
    c2 = CLIPS_DIR / "02_setup_clip.mp4"
    render_veo_clip(
        VID_DIR / "02_setup_zinc.mp4",
        OVERLAYS_DIR / "overlay_02_setup.png",
        AUDIO_DIR / "02_setup.mp3",
        c2
    )
    clip_paths.append(c2)

    # Scene 3: Animated Image (Effervescence Reaction)
    c3 = CLIPS_DIR / "03_reaction_clip.mp4"
    render_image_clip(
        IMG_DIR / "03_reaction_effervescence.jpg",
        OVERLAYS_DIR / "overlay_03_reaction.png",
        AUDIO_DIR / "03_reaction.mp3",
        c3,
        zoom_filter="scale=1080:1920,zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih*0.45-(ih/zoom*0.45)':d=260:s=1080x1920:fps=30"
    )
    clip_paths.append(c3)

    # Scene 4: Animated Image (Exothermic Takeaway)
    c4 = CLIPS_DIR / "04_takeaway_clip.mp4"
    render_image_clip(
        IMG_DIR / "04_takeaway_exothermic.jpg",
        OVERLAYS_DIR / "overlay_04_takeaway.png",
        AUDIO_DIR / "04_takeaway.mp3",
        c4,
        zoom_filter="scale=1080:1920,zoompan=z='if(lte(zoom,1.0),1.05,max(1.0,zoom-0.0005))':x='iw/2-(iw/zoom/2)':y='ih*0.5-(ih/zoom*0.5)':d=180:s=1080x1920:fps=30"
    )
    clip_paths.append(c4)

    # Concat clips
    concat_list = CLIPS_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            safe_p = str(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")

    temp_concat = OUT_DIR / "temp_concat.mp4"
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
    master_video = OUT_DIR / "CBSE-Class-10-Science-Activity-1.3-Zinc-Acid-Hydrogen-Gas-Shorts.mp4"
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
    print("*** ACTIVITY 1.3 MASTER YOUTUBE SHORTS CREATED SUCCESSFULLY! ***")
    print(f"File: {master_video.name}")
    print(f"Path: {master_video}")
    print(f"Duration: {actual_dur:.2f} seconds (Ultra-high retention sweet spot!)")
    print(f"Resolution: 1080x1920 (9:16 Vertical Full-Bleed)")
    print(f"File Size: {size_mb:.2f} MB")
    print("=================================================================")

if __name__ == "__main__":
    main()
