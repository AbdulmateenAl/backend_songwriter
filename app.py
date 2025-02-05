from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import json
import time
from dotenv import load_dotenv
import re

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

# def format_lyrics(lyrics):
#     # Splitting the lyrics into lines
#     lines = lyrics.split("\n")
    
#     formatted_lyrics = []
#     verse_count = 1
#     is_chorus = False
    
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
        
#         # Detecting a chorus (if a line is repeated multiple times)
#         if lines.count(line) > 2 and not is_chorus:
#             formatted_lyrics.append("\n[Chorus]")
#             is_chorus = True
#         elif is_chorus and lines.count(line) <= 2:
#             is_chorus = False
#             verse_count += 1
        
#         # Assigning verses
#         if not is_chorus:
#             formatted_lyrics.append(f"\n[Verse {verse_count}]")

#         formatted_lyrics.append(line)

#     return "\n".join(formatted_lyrics)


@app.post("/generate_music_with_lyrics")
async def generate_music_with_lyrics(prompt: str = Form(...), lyrics: str = Form(...)):
    url = "https://api.musicapi.ai/api/v1/sonic/create"
    headers = {"Authorization": f"Bearer {music_api}"}

    payload = json.dumps({
        "custom_mode": True,
        "prompt": lyrics,
        "title": "Starts",
        "tags": prompt,
        "negative_tags": "piano",
        "gpt_description_prompt": "",
        "make_instrumental": False,
        "mv": "sonic-v3-5"
    })

    response = requests.post(url, headers=headers, data=payload)
    jsonResponse = response.json()

    if jsonResponse["message"] == "success":
        task_id = jsonResponse["task_id"]
        return JSONResponse(content={"task_id": task_id}, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to generate music"}, status_code=500)

@app.get("/get_audio_with_lyrics/{task_id}")
async def get_audio(task_id: str):
    url = f"https://api.musicapi.ai/api/v1/sonic/task/{task_id}"
    headers = {"Authorization": f"Bearer {music_api}"}

    response = requests.get(url, headers=headers)

    data = response.json()
    status_code = data["message"]

    if status_code == "success":
        song_path = data["data"][0]["audio_url"]
        print(f"Song_url: {song_path}")
        if song_path:
            return JSONResponse(content={"song_url": song_path}, status_code=200)
    elif status_code != "success":
        time.sleep(70)
        return JSONResponse(content={"error": "Music generation in progress, try again later"}, status_code=202)
    return JSONResponse(
        content={
            "error": "Music generation is taking too long to be continued, try again later"},
        status_code=408,
    )

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




@app.get("/get_audio_without_lyrics/{task_id}")
async def get_audio(task_id: str):
    url = f"https://api.musicapi.ai/api/v1/studio/task/{task_id}"
    headers = {"Authorization": f"Bearer {music_api}"}

    response = requests.get(url, headers=headers)

    time.sleep(30)

    data = response.json()
    finished = data["handledData"]["data"]["songs"][0]["finished"]

    if finished == True:
        song_path = data["handledData"]["data"]["songs"][0]["song_path"]
        print(f"SOng_url: {song_path}")
        if song_path:
            return JSONResponse(content={"song_url": song_path}, status_code=200)
    elif finished == False:
        time.sleep(70)
        return JSONResponse(content={"error": "Music generation in progress, try again later"}, status_code=202)
    return JSONResponse(
        content={
            "error": "Music generation is taking too long to be continued, try again later"},
        status_code=408,
    )

    # while True:
    #     start_time = time.time()
    #     timeout = 120
    #     if time.time() - start_time > timeout:
    #         return JSONResponse(
    #             content={"error": "Music generation timed out, try again later"},
    #             status_code=408,
    #         )
    #     if finished == True:
    #         song_path = data["handledData"]["data"]["songs"][0]["song_path"]
    #         print("Value is true")
    #         print(f"Song_url: {song_path}")
    #         if song_path:
    #             return JSONResponse(content={"song_url": song_path}, status_code=200)

    #     elif finished == False:
    #         print("Value is false")
    #         print("Music generation still in progress, retrying...")
    #         continue  # Continue looping to check again
