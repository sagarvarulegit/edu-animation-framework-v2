#!/usr/bin/env python3
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
        "text": "Bring a flame near this test tube... POP! What explosive gas just ignited?"
    },
    {
        "id": "02_setup",
        "text": "We took pure zinc granules and added dilute sulphuric acid."
    },
    {
        "id": "03_reaction",
        "text": "Instantly, hydrogen gas boils off vigorously! Zinc displaces hydrogen: Zn plus H2SO4 yields ZnSO4 plus H2!"
    },
    {
        "id": "04_takeaway",
        "text": "Exam tip: Touch the flask, it turns hot! This is BOTH Single Displacement and Exothermic! Comment below!"
    }
]

def generate_voiceover(voice_id="IKne3meq5aSn9XLyUdCD"): # Charlie - energetic
    if not API_KEY:
        raise ValueError("ELEVEN_LABS_API_KEY is not set!")
        
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    generated_files = []
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
            # Remove awkward silence pauses and boost tempo slightly
            cmd = [
                'ffmpeg', '-y', '-i', str(out_path),
                '-af', 'silenceremove=stop_periods=-1:stop_duration=0.20:stop_threshold=-40dB,atempo=1.10',
                str(tight_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            dur = subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(tight_path)]).decode().strip()
            print(f"Saved: {tight_path.name} ({float(dur):.2f}s)")
            generated_files.append(tight_path)
        else:
            print(f"Error {res.status_code}: {res.text}")
            raise RuntimeError(f"ElevenLabs TTS failed for {item['id']}")

    return generated_files

if __name__ == "__main__":
    generate_voiceover()
