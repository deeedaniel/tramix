from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_song_suggestions(string: str) -> str:
    system_prompt = (
        "Return ONLY JSON. No markdown code blocks. No backticks. "
        "The output must begin with '[' and end with ']'."
    )
    
    user_query = (
        f"Suggest 20 songs with similar BPM (±10) and genre to: {string}. "
        "Feel free to use the same artist if it makes sense."
        "JSON keys: name, artist, bpm, key."
    )
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview", 
        contents=user_query,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING"},
                        "artist": {"type": "STRING"},
                        "bpm": {"type": "INTEGER"},
                        "key": {"type": "STRING"},
                    },
                    "required": ["name", "artist", "bpm", "key"]
                }
            }
        }
    )

    return response.text
