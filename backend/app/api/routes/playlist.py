from typing import Optional
from fastapi import APIRouter, HTTPException
from app.core.supabase import supabase
from pydantic import BaseModel

router = APIRouter()

class Playlist(BaseModel):
    name: str
    description: str
    user_id: str
    image: str


class PlaylistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    user_id: Optional[str] = None
    image: Optional[str] = None

@router.post("/create-playlist")
async def create_playlist(playlist: Playlist):
    return supabase.table("playlists").insert(playlist.model_dump()).execute().data

@router.get("/get-playlist/{playlist_id}")
async def get_playlist(playlist_id: str):
    return supabase.table("playlists").select("*").eq("id", playlist_id).execute().data[   0]

@router.put("/update-playlist/{playlist_id}")
async def update_playlist(playlist_id: str, playlist: PlaylistUpdate):
    updates = playlist.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    result = supabase.table("playlists").update(updates).eq("id", playlist_id).execute().data
    if not result:
        raise HTTPException(status_code=404, detail="Playlist not found")
    return result[0]
