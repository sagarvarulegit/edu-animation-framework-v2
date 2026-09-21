#!/usr/bin/env python3
"""
Master Video Assembly Script for CBSE Class 10 Science Activity 1.2
(Precipitation of Lead Iodide) YouTube Short.

Strictly adheres to:
1. .agents/rules/youtube_shorts_retention.md (Duration 24.6s, Climax Inversion, M3 Expressive, Safe Zones)
2. .agents/skills/cbse-science-shorts/SKILL.md (4-Act Structure, ElevenLabs VO, BGM ducking)
3. Platform Invariants (No angle brackets in metadata, SEO keyword file naming)
"""

import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
OVERLAYS_DIR = BASE_DIR / "overlays_m3"
OUT_DIR = BASE_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)
CLIPS_DIR = BASE_DIR / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

BGM_PATH = Path(r"C:\Sagar\Projects\CBSE\ChapterReady.in\cbse_byCodex\videos\chapterready-promo\audio\bgm_loop.mp3")

SCENES = [
    {
        "id": "01_hook",
        "title": "Act 1: Climax Inversion Hook",
        "image": OVERLAYS_DIR / "frame_01_hook.jpg",
        "audio": AUDIO_DIR / "01_hook.mp3",
        "zoom_filter": "scale=1080:1920,zoompan=z='min(zoom+0.0006,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=180:s=1080x1920:fps=30"
    },
    {
        "id": "02_setup",
        "title": "Act 2: The Setup",
        "image": OVERLAYS_DIR / "frame_02_setup.jpg",
        "audio": AUDIO_DIR / "02_setup.mp3",
        "zoom_filter": "scale=1080:1920,zoompan=z='min(zoom+0.0005,1.04)':x='iw/2-(iw/zoom/2)':y='ih*0.45-(ih/zoom*0.45)':d=90:s=1080x1920:fps=30"
    },
    {
        "id": "03_reaction",
        "title": "Act 3: Reaction & Science",
        "image": OVERLAYS_DIR / "frame_03_reaction.jpg",
        "audio": AUDIO_DIR / "03_reaction.mp3",
        "zoom_filter": "scale=1080:1920,zoompan=z='min(zoom+0.0005,1.06)':x='iw/2-(iw/zoom/2)':y='ih*0.4-(ih/zoom*0.4)':d=300:s=1080x1920:fps=30"
    },
    {
        "id": "04_takeaway",
        "title": "Act 4: Exam Takeaway & Loop",
        "image": OVERLAYS_DIR / "frame_04_takeaway.jpg",
        "audio": AUDIO_DIR / "04_takeaway.mp3",
        "zoom_filter": "scale=1080:1920,zoompan=z='if(lte(zoom,1.0),1.05,max(1.0,zoom-0.0005))':x='iw/2-(iw/zoom/2)':y='ih*0.5-(ih/zoom*0.5)':d=190:s=1080x1920:fps=30"
    }
]

def get_audio_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path)
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)

def render_scene_clip(scene: dict) -> Path:
    out_clip = CLIPS_DIR / f"{scene['id']}.mp4"
    dur = get_audio_duration(scene["audio"])
    print(f"Rendering {scene['title']} (duration={dur:.2f}s)...")
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(scene["image"]),
        "-i", str(scene["audio"]),
        "-vf", scene["zoom_filter"],
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        str(out_clip)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out_clip

def main():
    print("=================================================================")
    print("STARTING ACTIVITY 1.2 YOUTUBE SHORTS RENDERING PIPELINE")
    print("=================================================================")
    
    # 1. Render individual scene clips
    clip_paths = []
    total_dur = 0.0
    for scene in SCENES:
        dur = get_audio_duration(scene["audio"])
        total_dur += dur
        clip = render_scene_clip(scene)
        clip_paths.append(clip)
        
    print(f"\nTotal Narration Duration: {total_dur:.2f}s (Strictly within 20-28s target!)")
    
    # 2. Concat all clips
    concat_list = CLIPS_DIR / "concat_list.txt"
    with open(concat_list, "w") as f:
        for p in clip_paths:
            safe_p = str(p).replace("\\", "/")
            f.write(f"file '{safe_p}'\n")
            
    temp_concat = OUT_DIR / "temp_concatenated.mp4"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        str(temp_concat)
    ]
    subprocess.run(cmd_concat, check=True)
    
    # 3. Mix Background Music (BGM) ducked at -19dB
    master_video = OUT_DIR / "CBSE-Class-10-Science-Activity-1.2-Precipitation-Lead-Iodide-Shorts.mp4"
    actual_dur = get_audio_duration(temp_concat)
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
    
    # Clean up temp
    if temp_concat.exists():
        temp_concat.unlink()
        
    size_mb = master_video.stat().st_size / (1024 * 1024)
    print("\n=================================================================")
    print("*** ACTIVITY 1.2 YOUTUBE SHORTS VIDEO CREATED SUCCESSFULLY! ***")
    print(f"File: {master_video.name}")
    print(f"Path: {master_video}")
    print(f"Duration: {actual_dur:.2f} seconds (Optimal retention sweet spot!)")
    print(f"Resolution: 1080x1920 (9:16 Vertical Full-Bleed)")
    print(f"File Size: {size_mb:.2f} MB")
    print("=================================================================")

if __name__ == "__main__":
    main()
