import httpx
import asyncio
import librosa
import numpy as np
import tempfile
import os
import subprocess
from loguru import logger
from pydantic import BaseModel, Field, TypeAdapter
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=8)

class Song(BaseModel):
    name: str = Field(description="The name of the song")
    artist: str = Field(description="The artist of the song")
    bpm: int = Field(description="The bpm of the song")
    key: str = Field(description="The key of the song")
    camelot_key: str = Field(description="The camelot key of the song")
    previewURL: str = Field(description="The preview URL of the song")
    artworkURL: str = Field(description="The artwork URL of the song")

song_adapter = TypeAdapter(Song)


async def analyze_track(song: dict):
    """
    Downloads and analyzes a single track. 
    Uses ThreadPool for CPU-bound tasks to ensure true parallelism.
    """

    validated_song = song_adapter.validate_python(song)

    url = validated_song.previewURL
    name = validated_song.name
    artist = validated_song.artist
    start_bpm = validated_song.bpm

    tmp_m4a_path = None
    tmp_wav_path = None
    loop = asyncio.get_event_loop()
    
    try:
        # 1. ASYNC DOWNLOAD (Non-blocking)
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            # Tip: Apple previews are small, but we can cap it with a Range header if needed
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            audio_bytes = response.content

        # 2. SAVE TO TEMP (Sync but fast)
        with tempfile.NamedTemporaryFile(suffix=".m4a", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_m4a_path = tmp.name

        # 3. CPU INTENSIVE: FFMPEG (Offload to Thread)
        tmp_wav_path = tmp_m4a_path.replace(".m4a", ".wav")
        ffmpeg_cmd = ["ffmpeg", "-y", "-i", tmp_m4a_path, "-ar", "11025", "-ac", "1", tmp_wav_path]
        
        await loop.run_in_executor(
            executor, 
            lambda: subprocess.run(ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        )

        # 4. CPU INTENSIVE: LIBROSA LOAD & ANALYZE (Offload to Thread)
        # We wrap the math-heavy parts in a helper function to run in the executor
        def perform_analysis(path):
            y, sr = librosa.load(path, sr=11025, mono=True, offset=5.0, duration=30.0)
            tempo_result, _ = librosa.beat.beat_track(y=y, sr=sr, start_bpm=start_bpm)
            # detect_key must be defined in your scope!
            key_name, mode, camelot = detect_key(y, sr) 
            return float(tempo_result[0]), key_name, mode, camelot

        tempo, key_name, mode, camelot = await loop.run_in_executor(executor, perform_analysis, tmp_wav_path)

        logger.info(f"✅ Analyzed: {tempo:.1f} BPM | {key_name} {mode}")
        return {"bpm": tempo, "key": key_name, "mode": mode, "camelot": camelot, "name": name, "artist": artist}

    except Exception as e:
        print(f"❌ Error on {url}: {e}")
        return {"error": str(e)}
    
    finally:
        # Cleanup
        for path in [tmp_m4a_path, tmp_wav_path]:
            if path and os.path.exists(path):
                try: os.remove(path)
                except: pass
                
# Camelot wheel mapping (key_index, is_major) -> Camelot notation
CAMELOT = {
    (0,  True):  "8B",  # C major
    (1,  True):  "3B",  # C# major
    (2,  True):  "10B", # D major
    (3,  True):  "5B",  # D# major
    (4,  True):  "12B", # E major
    (5,  True):  "7B",  # F major
    (6,  True):  "2B",  # F# major
    (7,  True):  "9B",  # G major
    (8,  True):  "4B",  # G# major
    (9,  True):  "11B", # A major
    (10, True):  "6B",  # A# major
    (11, True):  "1B",  # B major
    (0,  False): "5A",  # C minor
    (1,  False): "12A", # C# minor
    (2,  False): "7A",  # D minor
    (3,  False): "2A",  # D# minor
    (4,  False): "9A",  # E minor
    (5,  False): "4A",  # F minor
    (6,  False): "11A", # F# minor
    (7,  False): "6A",  # G minor
    (8,  False): "1A",  # G# minor
    (9,  False): "8A",  # A minor
    (10, False): "3A",  # A# minor
    (11, False): "10A", # B minor
}

KEY_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def detect_key(y, sr): 
    # Compute chromagram using harmonic component only (more accurate)
    y_harmonic = librosa.effects.harmonic(y)
    chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
    
    # Sum chroma energy across time
    chroma_mean = np.mean(chromagram, axis=1)
    
    # Krumhansl-Schmuckler key profiles (reference: https://rnhart.net/articles/key-finding/)
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                               2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                               2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    major_scores = []
    minor_scores = []

    for i in range(12):
        rotated = np.roll(chroma_mean, -i)
        major_scores.append(np.corrcoef(rotated, major_profile)[0, 1])
        minor_scores.append(np.corrcoef(rotated, minor_profile)[0, 1])

    best_major = np.argmax(major_scores)
    best_minor = np.argmax(minor_scores)

    if major_scores[best_major] >= minor_scores[best_minor]:
        key_idx, is_major = int(best_major), True
    else:
        key_idx, is_major = int(best_minor), False

    key_name = KEY_NAMES[key_idx]
    mode = "major" if is_major else "minor"
    camelot = CAMELOT[(key_idx, is_major)]
    
    return key_name, mode, camelot