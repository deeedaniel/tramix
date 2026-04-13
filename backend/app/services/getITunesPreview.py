import re
import requests
import json
from loguru import logger

def _normalize_artist(artist: str) -> str:
    # Strip featured artists (ft., feat., featuring, with, x, &) and normalize
    artist = re.sub(r'\s*(ft\.?|feat\.?|featuring|with)\s+.+', '', artist, flags=re.IGNORECASE)
    artist = re.sub(r'\s*[&x]\s+.+', '', artist)
    return artist.strip().lower()

def _normalize_title(title: str) -> str:
    # Strip parenthetical/bracketed suffixes like (feat. ...), [Radio Edit], etc.
    title = re.sub(r'\s*[\(\[].*?[\)\]]', '', title)
    return title.strip().lower()

def _artist_match(json_artist: str, itunes_artist: str) -> bool:
    a = _normalize_artist(json_artist)
    b = _normalize_artist(itunes_artist)
    return a == b or a in b or b in a

def _title_match(json_name: str, itunes_track: str) -> bool:
    a = _normalize_title(json_name)
    b = _normalize_title(itunes_track)
    return a == b or a in b or b in a


def _strip_cr(s: str) -> str:
    """Remove stray CR characters models sometimes insert (e.g. C\\rmajor)."""
    return re.sub(r"\r+", "", s)


async def getITunesPreview(jsonString: str) -> list[dict]:
    logger.info(f"recieved jsonString: {jsonString}")
    song_data = json.loads(jsonString)
    if not song_data or not isinstance(song_data, list):
        raise ValueError("Invalid JSON format or missing 'previewUrl' key.")

    songs = []
    for song in song_data:

        #parameters required for itunes search
        name = song.get('name')
        artist = song.get('artist')

        itunes_url = f"https://itunes.apple.com/search?term={name}&entity=song&attribute=artistTerm&limit=25"
        response = requests.get(itunes_url)
        if response.status_code != 200:
            print(f"Failed to fetch data from iTunes API for {name} by {artist}. Status code: {response.status_code}")
            continue

        #strip CR characters from key and replace in song dictionary
        k = song.get("key")
        if isinstance(k, str):
            song["key"] = _strip_cr(k) #replace key with stripped key
        
        data = response.json()["results"] #itunes data
        matches = [
            track for track in data
            if _artist_match(artist, track["artistName"])
            and _title_match(name, track["trackName"])
            and track.get("previewUrl")
        ]
        if matches:
            track = matches[0]
            song["previewURL"] = track["previewUrl"]
            song["artworkURL"] = track.get("artworkUrl100", "").replace("100x100", "600x600")
            songs.append(song)

    logger.info(f"itnues songs returned: {songs}")
    return songs