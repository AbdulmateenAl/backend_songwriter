from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json
import time
from dotenv import load_dotenv

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()

music_api = os.getenv("MUSICAPI_API")

@app.post("/generate_music_with_lyrics")
async def generate_music_with_lyrics(prompt: str = Form(...), lyrics: str = Form(...)):
    url = "https://api.musicapi.ai/api/v1/studio/create"
    headers = {"Authorization": f"Bearer {music_api}"}

    payload = json.dumps({
        "prompt": prompt,
        "lyrics": lyrics,
        "lyrics_type": "user",
        "bypass_prompt_optimization": False,
        "seed": -1,
        "song_section_start": 0,
        "song_section_end": 1,
        "lyrics_placement_start": 0,
        "lyrics_placement_end": 0.95,
        "prompt_strength": 0.5,
        "clarity_strength": 0.25,
        "lyrics_strength": 0.5,
        "generation_quality": 0.75,
        "negative_prompt": "",
        "model_type": "studio130-v1.5",
        "config": {"mode": "regular"}
    })

    response = requests.post(url, headers=headers, data=payload)
    jsonResponse = response.json()

    if jsonResponse["code"] == "success":
        task_id = jsonResponse["data"]
        return JSONResponse(content={"task_id": task_id}, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to generate music"}, status_code=500)


@app.post("/generate_music_without_lyrics")
async def generate_music_without_lyrics(prompt: str = Form(...)):
    url = "https://api.musicapi.ai/api/v1/studio/create"

    payload = json.dumps({
        "prompt": prompt,
        "lyrics_type": "generate",
        "bypass_prompt_optimization": False,
        "seed": -1,
        "prompt_strength": 0.5,
        "clarity_strength": 0.25,
        "lyrics_strength": 0.5,
        "generation_quality": 0.75,
        "negative_prompt": "",
        "model_type": "studio32-v1.5",
        "config": {
            "mode": "regular"
        }
    })
    headers = {"Authorization": f"Bearer {music_api}",
               "Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=payload)
    jsonResponse = response.json()
    print(jsonResponse)

    if jsonResponse["code"] == "success":
        task_id = jsonResponse["data"]
        return JSONResponse(content={"task_id": task_id}, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to generate music"}, status_code=500)


@app.get("/get_audio/{task_id}")
async def get_audio(task_id: str):
    url = f"https://api.musicapi.ai/api/v1/studio/task/{task_id}"
    headers = {"Authorization": f"Bearer {music_api}"}

    time.sleep(10)
    for _ in range(5):
        response = requests.get(url, headers=headers)
        data = response.json()

        if data["handledData"]["data"]["songs"][0]["song_path"]:
            song_path = data["handledData"]["data"]["songs"][0]["song_path"]
            print(f"SOng_url: {song_path}")
            if song_path:
                return JSONResponse(content={"song_url": song_path}, status_code=200)
        time.sleep(10)

    return JSONResponse(content={"error": "Music generation in progress, try again later"}, status_code=202)
