#!/usr/bin/env python3
import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("ELEVEN_LAB_API_KEY") or os.environ.get("ELEVEN_LABS_API_KEY")

# Ruthlessly tight, fast-paced high-retention script (targeting ~22-24s total)
VOICE_SCRIPTS = [
    {
        "id": "01_hook",
        "text": "Two crystal-clear liquids... the instant they touch: BOOM! What made this vivid yellow cloud?"
    },
    {
        "id": "02_setup",
        "text": "Clear Lead Nitrate meets colorless Potassium Iodide."
    },
    {
        "id": "03_reaction",
        "text": "Instantly, Lead and Potassium swap partners! Insoluble yellow Lead Iodide precipitates out. Pb(NO3)2 plus 2KI yields PbI2 plus 2KNO3!"
    },
    {
        "id": "04_takeaway",
        "text": "Exam tip: This is BOTH a Double Displacement and Precipitation reaction! What happened to Potassium? Comment below!"
    }
]

def generate_voiceover(voice_id="IKne3meq5aSn9XLyUdCD"): # Charlie - confident, energetic
    if not API_KEY:
        raise ValueError("ELEVEN_LABS_API_KEY or ELEVEN_LAB_API_KEY is not set!")
        
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    generated_files = []
    for item in VOICE_SCRIPTS:
        out_path = AUDIO_DIR / f"{item['id']}.mp3"
        print(f"Generating VO for {item['id']}...")
        payload = {
            "text": item["text"],
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.40,
                "similarity_boost": 0.85,
                "speaking_rate": 1.22
            }
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(res.content)
            print(f"Saved: {out_path.name} ({len(res.content)} bytes)")
            generated_files.append(out_path)
        else:
            print(f"Error {res.status_code}: {res.text}")
            raise RuntimeError(f"ElevenLabs TTS failed for {item['id']}")

    return generated_files

if __name__ == "__main__":
    generate_voiceover()
