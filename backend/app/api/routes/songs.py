from fastapi import APIRouter
from app.services.gemini import get_song_suggestions
from app.services.getsongkey import test_search_metallica
from app.core.config import settings

router = APIRouter()

@router.get("/test-getsongkey")
async def test_getsongkey():
    print(f"GETSONGKEY_API_URL: {settings.GETSONGKEY_API_URL}")
    print(f"GETSONGKEY_API_KEY: {settings.GETSONGKEY_API_KEY}")
    return await test_search_metallica()

@router.get("/suggest-songs")
async def suggest_songs(string: str):
    # async with httpx.AsyncClient() as client:
    #     try:
    #         response = await client.get(
    #             f"{GETSONGKEY_API_URL}/songs/{song_id}/suggestions"
    #         )
    #         return response.json()
    #     except Exception as e:
    #         raise HTTPException(status_code=500, detail=str(e))

    response_text = get_song_suggestions(string)
    print(response_text)
    return {"response": response_text}
