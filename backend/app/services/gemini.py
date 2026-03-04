from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_song_suggestions(string: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=f"Suggest 5 songs that have similar BPMs and are in the same key as: {string}. Return the songs in a JSON array of objects with the following properties: name, artist, bpm, key. Only return the JSON array, no other text."
    )
    return response.text
