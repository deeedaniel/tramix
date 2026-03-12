import requests
import json

maxSongs = 5 # set max songs generated to 5

async def getITunesPreview(jsonString: str) -> None:
    print("recieved jsonString: ", jsonString)
    # Parse the JSON string to extract the preview URL
    songData = json.loads(jsonString)
    if not songData or not isinstance(songData, list):
        raise ValueError("Invalid JSON format or missing 'previewUrl' key.")

    songs = []
    for song in songData:
        name = song.get('name')
        artist = song.get('artist')
        itunes_url = f"https://itunes.apple.com/search?term={name}&entity=song&attribute=artistTerm&limit=25"
        response = requests.get(itunes_url)
        if response.status_code != 200:
            print(f"Failed to fetch data from iTunes API for {name} by {artist}. Status code: {response.status_code}")
            continue

        data = response.json()["results"]
        res = [track["previewUrl"] for track in data if track["artistName"].lower() == artist.lower()]
        if res: 
            song["previewURL"] = res[0]
            songs.append(song)  
        if len(songs) == 5: # if 5 itunes previews sucessfully generated, break
            break

    return songs