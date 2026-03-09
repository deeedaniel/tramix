# Tramix Backend

## DATA FLOW FOR PLAYLIST GENERATION

1. Generate a list of songs through gemini prompting (will get bpm and key)
2. One by one search each song in itunes
3. If exists, grab song preview link (.m4a) from api
4. Using our script, generate keys and bpms of songs from that .m4a file
    * Might have to run on docker to run asynchrnously for faster speeds
5. Validate result into gemini's result within a margin
6. Meaningfully order the songs such that there won't be significant key misalignment (suggest key changes if key synchro not possible)