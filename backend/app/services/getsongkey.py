import httpx
from fastapi import HTTPException
from app.core.config import settings

async def test_search_metallica():
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "api_key": settings.GETSONGKEY_API_KEY,
                "type": "artist",
                "lookup": "Metallica"
            }
            
            response = await client.get(
                f"{settings.GETSONGKEY_API_URL}/search/", 
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
