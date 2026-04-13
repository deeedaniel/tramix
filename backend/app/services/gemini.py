from google import genai
from google.genai import types
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def get_song_suggestions(string):

    # for model in client.models.list():
    #     print('hello')
    #     print(model.name)

    research_query = (
        f"Search for 10 songs similar in genre, mood, and production style to '{string}'. "
        "For each song, provide the Name, Artist, Musical Key, and the 'Intended BPM'. "
        "GUIDELINES TO PREVENT HALLUCINATION: "
        "1. VERIFY BPM: Cross-reference Musicnotes.com or official sheet music to find the 'Project Tempo'. "
        "Use standard 'straight-time' (e.g., if a song feels like 102 BPM, do not report 51 or 204). "
        "2. VERIFY KEY: Check official sheet music. Do not report the relative major/minor "
        "(e.g., if the key is B Major, do not return G# Minor or Ab Minor). "
        "3. SOURCES: Use Google Search to look at Tunebat, SongBPM, and Wikipedia metadata. "
        f"4. EXCLUSION: Do not include '{string}' in the results."
    )

    research_response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=research_query,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    raw_text = research_response.text

    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING"},
                "artist": {"type": "STRING"},
                "bpm": {"type": "INTEGER"},
                "key": {"type": "STRING"},
                "camelot_key": {"type": "STRING"}
            },
            "required": ["name", "artist", "bpm", "key", "camelot_key"]
        }
    }


    formatting_prompt = f"Convert this song list into a JSON array based on the schema: {raw_text}"

    final_response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents=formatting_prompt,
        config=types.GenerateContentConfig(
            system_instruction="Return ONLY the JSON array. Do not include markdown or backticks.",
            response_mime_type="application/json",
            response_schema=schema
        )
    )

    return final_response.text

