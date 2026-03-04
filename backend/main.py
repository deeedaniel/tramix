from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import httpx
import asyncio
import os
from google import genai

app = FastAPI()

load_dotenv()

GETSONGKEY_API_URL = os.getenv("GETSONGKEY_API_URL")
GETSONGKEY_API_KEY = os.getenv("GETSONGKEY_API_KEY")

client = genai.Client()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@app.get("/test-getsongkey")
async def test_getsongkey():
    print(f"GETSONGKEY_API_URL: {GETSONGKEY_API_URL}")
    print(f"GETSONGKEY_API_KEY: {GETSONGKEY_API_KEY}")
    async with httpx.AsyncClient() as client:
        try:

            params = {
                "api_key": GETSONGKEY_API_KEY,
                "type": "artist",
                "lookup": "Metallica"
            }
            
            response = await client.get(
                f"{GETSONGKEY_API_URL}/search/", 
                params=params)
            
            # Catch 401 (Unauthorized) if key is bad 
            response.raise_for_status() 
            
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, 
                detail=f"API Error: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggest-songs")
async def suggest_songs(string: str):
    # async with httpx.AsyncClient() as client:
    #     try:
    #         response = await client.get(
    #             f"{GETSONGKEY_API_URL}/songs/{song_id}/suggestions"
    #         )
    #         return response.json()
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=f"Suggest 5 songs that have similar BPMs and are in the same key as: {string}. Return the songs in a JSON array of objects with the following properties: name, artist, bpm, key. Only return the JSON array, no other text."
    )

    print(response.text)

    return {"response": response.text}