from google import genai
from google.genai import types
from app.core.config import settings
import json
from loguru import logger

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def get_song_suggestions(string: str) -> list[dict]:
    # Step 1: Grounded research — search tools, plain text output
    research_prompt = f"""
    You are a music metadata researcher. Find 20 songs similar in genre, mood, and 
    production style to '{string}'. Do NOT include '{string}' itself.

    For EACH song you MUST use Google Search to verify:
    1. BPM — check Tunebat, SongBPM, or Musicnotes. Use straight-time BPM only.
    If you cannot verify, write BPM: UNKNOWN.
    2. Key — check official sheet music or Wikipedia. Return the tonic key, not the 
    relative major/minor. If you cannot verify, write Key: UNKNOWN.
    3. Camelot Key — derive from the verified key (e.g. B Major = 1B, G# Minor = 1A).
    If key is UNKNOWN, write Camelot: UNKNOWN.

    Format each result exactly like this:
    SONG: <name> | ARTIST: <artist> | BPM: <value or UNKNOWN> | KEY: <value or UNKNOWN> | CAMELOT: <value or UNKNOWN>
    """

    research_response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=research_prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )

    # Step 2: Structured extraction — NO tools, NO hallucination gap
    schema = {
        "type": "ARRAY",
        "items": {
            "type": "OBJECT",
            "properties": {
                "name":         {"type": "STRING"},
                "artist":       {"type": "STRING"},
                "bpm":          {"type": "INTEGER"},
                "key":          {"type": "STRING"},
                "camelot_key":  {"type": "STRING"},
            },
            "required": ["name", "artist", "bpm", "key", "camelot_key"]
        }
    }

    formatting_prompt = f"""
    Convert the following verified song list into a JSON array.

    RULES:
    - Copy values EXACTLY as they appear. Do NOT guess or infer missing data.
    - If BPM is UNKNOWN, use 0.
    - If KEY or CAMELOT is UNKNOWN, use the string "Unknown".
    - Do not add songs not present in the list below.

    SONG LIST:
    {research_response.text}
    """

    final_response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=formatting_prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a data formatter. Return ONLY the JSON array. No markdown, no explanation, no backticks.",
            response_mime_type="application/json",
            response_schema=schema,
        )
    )

    # Dict `response_schema` is parsed by the SDK into `parsed` (already a Python list).
    # Do not json.loads(parsed) — that passes a list into json.loads and raises TypeError.
    if final_response.parsed is not None:
        songs = final_response.parsed
    elif final_response.text:
        songs = json.loads(final_response.text)
    else:
        raise ValueError("Empty Gemini response (no parsed JSON and no text).")

    if not isinstance(songs, list):
        raise ValueError(f"Expected a JSON array of songs, got {type(songs).__name__}")

    logger.info(f"gemini songs returned: {len(songs)} items")

    return [
        s for s in songs
        if s["bpm"] != 0
        and s["key"] != "Unknown"
        and s["camelot_key"] != "Unknown"
    ]