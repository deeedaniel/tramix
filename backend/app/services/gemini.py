from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

def get_song_suggestions(string: str) -> str:
    # PROMPT UPDATE: Be extremely literal.
    system_prompt = (
        "Return ONLY JSON. No markdown code blocks. No backticks. "
        "The output must begin with '[' and end with ']'."
    )
    
    user_query = (
        f"Suggest 5 songs with similar BPM (±10) and genre to: {string}. "
        "JSON keys: name, artist, bpm, key."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
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
