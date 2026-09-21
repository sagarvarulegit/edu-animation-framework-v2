#!/usr/bin/env python3
"""
Generates AI video clips from still images using Google Veo 3.1 Fast
via the Gemini API / google-genai SDK.
Tracks exact generation latency, output video seconds, and cost incurred.
"""

import os
import time
import requests
from pathlib import Path
from google import genai
from google.genai import types

BASE_DIR = Path(__file__).resolve().parent
IMG_DIR = BASE_DIR / "images"
VID_DIR = BASE_DIR / "videos_raw"
VID_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set!")

client = genai.Client(api_key=API_KEY)

# Veo 3.1 Fast Pricing: ~$0.10 to $0.12 per output video second
VEO_COST_PER_SEC = 0.12 

SCENES = [
    {
        "id": "01_hook_pop",
        "title": "Act 1: Hydrogen Pop Sound Hook",
        "image": IMG_DIR / "01_hook_pop.jpg",
        "prompt": "The burning match flame at the mouth of the test tube flickers dynamically and produces a rapid pop flash of ignited hydrogen gas with a subtle smoke wisp, slow motion laboratory shot, cinema lighting.",
        "duration": 4
    },
    {
        "id": "02_setup_zinc",
        "title": "Act 2: Zinc Granules & Acid Setup",
        "image": IMG_DIR / "02_setup_zinc.jpg",
        "prompt": "Gentle cinematic camera tilt down focusing on the metallic silver zinc granules inside the conical flask on the lab table, subtle reflections on glassware.",
        "duration": 4
    },
    {
        "id": "03_reaction_effervescence",
        "title": "Act 3: Vigorous Hydrogen Bubbling",
        "image": IMG_DIR / "03_reaction_effervescence.jpg",
        "prompt": "Intense rapid chemical effervescence as hundreds of tiny hydrogen gas bubbles continuously boil and fizz off the silver zinc granules, rushing upwards through clear liquid in high-speed macro.",
        "duration": 4
    },
    {
        "id": "04_takeaway_exothermic",
        "title": "Act 4: Exothermic Heat & Delivery Tube",
        "image": IMG_DIR / "04_takeaway_exothermic.jpg",
        "prompt": "A gloved scientist hand rests against the warm base of the conical flask, faint heat vapor rising as the camera smoothly pulls back slightly, authentic laboratory atmosphere.",
        "duration": 4
    }
]

def download_video(uri: str, out_path: Path):
    headers = {"x-goog-api-key": API_KEY}
    r = requests.get(uri, headers=headers)
    if r.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(r.content)
        print(f"Downloaded video ({len(r.content)} bytes) to: {out_path.name}")
    else:
        raise RuntimeError(f"Failed to download video from {uri}: status {r.status_code} {r.text}")

def main():
    print("=================================================================")
    print("STARTING GOOGLE VEO 3.1 IMAGE-TO-VIDEO GENERATION PIPELINE")
    print(f"Model: veo-3.1-fast-generate-preview")
    print(f"Estimated Cost Rate: ${VEO_COST_PER_SEC:.2f} / second")
    print("=================================================================\n")

    total_video_seconds = 0
    total_latency_seconds = 0.0
    results = []

    for i, scene in enumerate(SCENES):
        out_video = VID_DIR / f"{scene['id']}.mp4"
        print(f"[{i+1}/{len(SCENES)}] Processing: {scene['title']}...")
        print(f" - Source Image: {scene['image'].name}")
        print(f" - Motion Prompt: \"{scene['prompt']}\"")
        print(f" - Requested Duration: {scene['duration']}s (9:16 vertical)")

        img = types.Image.from_file(location=str(scene["image"]))
        start_time = time.time()

        operation = client.models.generate_videos(
            model="veo-3.1-fast-generate-preview",
            source=types.GenerateVideosSource(
                prompt=scene["prompt"],
                image=img
            ),
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                duration_seconds=scene["duration"]
            )
        )
        print(f" - Operation initiated: {operation.name}")
        print(" - Waiting for Veo rendering to complete...")

        while not operation.done:
            time.sleep(8)
            operation = client.operations.get(operation=operation)

        elapsed = time.time() - start_time
        total_latency_seconds += elapsed
        print(f" - Rendered in {elapsed:.1f}s!")

        if operation.error:
            print(f" - ERROR: {operation.error}")
            raise RuntimeError(f"Veo generation failed for {scene['id']}")

        v_obj = operation.result.generated_videos[0].video
        download_video(v_obj.uri, out_video)

        total_video_seconds += scene["duration"]
        cost = scene["duration"] * VEO_COST_PER_SEC
        results.append({
            "id": scene["id"],
            "title": scene["title"],
            "file": out_video.name,
            "duration": scene["duration"],
            "latency": elapsed,
            "cost": cost
        })
        print(f" - Scene Cost: ${cost:.2f}\n")

    total_cost = total_video_seconds * VEO_COST_PER_SEC
    print("=================================================================")
    print("*** ALL SCENE VIDEOS GENERATED SUCCESSFULLY! ***")
    print(f"Total Video Output Seconds: {total_video_seconds} seconds")
    print(f"Total Cloud Rendering Time: {total_latency_seconds:.1f} seconds")
    print(f"TOTAL VEO 3.1 FAST COST: ${total_cost:.2f} USD")
    print("=================================================================")

if __name__ == "__main__":
    main()
