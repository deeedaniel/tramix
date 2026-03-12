from fastapi import APIRouter, Request
from app.services.gemini import get_song_suggestions
from app.services.getITunesPreview import getITunesPreview
from app.services.checkBPMandKEY import analyze_track
from app.core.config import settings
import asyncio
import json

router = APIRouter()

@router.get("/suggest-songs")
async def suggest_songs(string: str):
    response_text = await get_song_suggestions(string)
    return await getITunesPreview(response_text) ## get all the previewed data (returned as object)

@router.get("/validate-bpm-and-key")
async def validate_songs(request: Request):
    song_list = await request.json()
    tasks = [analyze_track(song) for song in song_list]
    results = await asyncio.gather(*tasks)
    
    return results
