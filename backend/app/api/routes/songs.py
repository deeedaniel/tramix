from fastapi import APIRouter
from app.services.gemini import get_song_suggestions
from app.services.getsongkey import test_search_metallica
from app.services.getITunesPreview import getITunesPreview
from app.core.config import settings

router = APIRouter()

@router.get("/test-getsongkey")
async def test_getsongkey():
    print(f"GETSONGKEY_API_URL: {settings.GETSONGKEY_API_URL}")
    print(f"GETSONGKEY_API_KEY: {settings.GETSONGKEY_API_KEY}")
    return await test_search_metallica()

@router.get("/suggest-songs")
async def suggest_songs(string: str):
    response_text = get_song_suggestions(string)
    return await getITunesPreview(response_text)
    #return {"response": response_text}

@router.get("/get-songs-from-itunes")
async def get_songs_from_itunes(string: str):
    # Implementation for fetching songs from iTunes
    pass
