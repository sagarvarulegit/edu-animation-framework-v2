#!/usr/bin/env python3
"""
Generates high-energy, tightly-paced voiceover for CBSE Class 10 Activity 1.4
(Action of Water on Quicklime - Combination & Exothermic Reaction)
using ElevenLabs Multilingual v2 with silence stripping.
"""

import os
import requests
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("ELEVEN_LAB_API_KEY") or os.environ.get("ELEVEN_LABS_API_KEY")

VOICE_SCRIPTS = [
    {
        "id": "01_hook",
        "text": "Pouring cold water on a dry rock makes it BOIL?! What crazy chemistry is this?"
    },
    {
        "id": "02_setup",
        "text": "Take solid quicklime in a beaker, and slowly add water."
    },
    {
        "id": "03_reaction",
        "text": "Watch it hiss and boil! Two substances combine into one single product: Slaked Lime! Calcium oxide plus water forms calcium hydroxide plus intense heat!"
    },
    {
        "id": "04_takeaway",
        "text": "Board exam hack: The beaker gets burning hot! It is an Exothermic Combination reaction used for whitewashing! Quick quiz pinned below!"
    }
]

def generate_voiceover(voice_id="IKne3meq5aSn9XLyUdCD"): # Charlie - energetic, authoritative
    if not API_KEY:
        raise ValueError("ELEVEN_LABS_API_KEY is not set!")
        
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    generated_files = []
    total_dur = 0.0

    for item in VOICE_SCRIPTS:
        out_path = AUDIO_DIR / f"{item['id']}_raw.mp3"
        tight_path = AUDIO_DIR / f"{item['id']}.mp3"
        print(f"Generating VO for {item['id']}...")
        payload = {
            "text": item["text"],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.40,
                "similarity_boost": 0.85,
                "speaking_rate": 1.20
            }
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(res.content)
            # Remove awkward pauses and boost tempo slightly for high retention
            cmd = [
                'ffmpeg', '-y', '-i', str(out_path),
                '-af', 'silenceremove=stop_periods=-1:stop_duration=0.20:stop_threshold=-40dB,atempo=1.10',
                str(tight_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(tight_path)]).decode().strip())
            print(f"Saved: {tight_path.name} ({dur:.2f}s)")
            total_dur += dur
            generated_files.append(tight_path)
        else:
            print(f"Error {res.status_code}: {res.text}")

    print(f"\nTotal VO Duration: {total_dur:.2f} seconds (Target: 20-25s)")
    return generated_files

if __name__ == "__main__":
    generate_voiceover()
