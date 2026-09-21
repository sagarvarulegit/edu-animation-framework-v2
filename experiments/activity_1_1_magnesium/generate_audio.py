import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUDIO_DIR = BASE_DIR / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("ELEVEN_LAB_API_KEY") or os.environ.get("ELEVEN_LABS_API_KEY")

VOICE_SCRIPTS = [
    {
        "id": "00_intro",
        "text": "What happens when you burn magnesium in air? Here is CBSE Class 10 Activity 1.1 in six quick steps!"
    },
    {
        "id": "01_step1",
        "text": "Step one: Rub the ribbon with sandpaper to remove the dull protective layer of basic magnesium carbonate."
    },
    {
        "id": "02_step2",
        "text": "Step two: Grip the clean ribbon securely with tongs. Always wear safety goggles in the lab!"
    },
    {
        "id": "03_step3",
        "text": "Step three: Hold the tip into the hot blue Bunsen flame until it reaches its ignition point."
    },
    {
        "id": "04_step4",
        "text": "Step four: It bursts into a dazzling, blinding white flame! Magnesium reacts vigorously with atmospheric oxygen."
    },
    {
        "id": "05_step5",
        "text": "Step five: Collect the white powder in a watch glass. This new substance is Magnesium Oxide, MgO."
    },
    {
        "id": "06_step6",
        "text": "Step six: Add water and test with red litmus paper. It turns bright blue, proving metallic oxides are basic!"
    },
    {
        "id": "07_outro",
        "text": "Key board takeaway: Two Mg plus O2 yields two MgO — a classic combination and exothermic reaction!"
    }
]

def generate_voiceover(voice_id="IKne3meq5aSn9XLyUdCD"): # Charlie - confident, energetic
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
                "stability": 0.45,
                "similarity_boost": 0.80,
                "speaking_rate": 1.15
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
