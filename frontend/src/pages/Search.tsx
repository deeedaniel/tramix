import { useState, useRef } from "react";
import { API_BASE_URL } from "../config";

interface Song {
  name: string;
  artist: string;
  bpm: number;
  key: string;
  camelot_key: string;
  previewURL: string;
  artworkURL?: string;
}

export default function Search() {
  const [userSong, setUserSong] = useState("");
  const [suggestResponse, setSuggestResponse] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);
  const [playingIndex, setPlayingIndex] = useState<number | null>(null);
  const audioRefs = useRef<(HTMLAudioElement | null)[]>([]);

  const togglePlay = (index: number) => {
    const audio = audioRefs.current[index];
    if (!audio) return;

    if (playingIndex === index) {
      audio.pause();
      setPlayingIndex(null);
    } else {
      if (playingIndex !== null) {
        audioRefs.current[playingIndex]?.pause();
      }
      audio.play();
      setPlayingIndex(index);
    }
  };

  const handleSuggest = (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!userSong) return;

    setLoading(true);

    fetch(`${API_BASE_URL}/suggest-songs?string=${userSong}`)
      .then((response) => response.json())
      .then((json) => {
        setSuggestResponse(json);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setLoading(false);
      });
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col items-center px-4 py-16">
      <div className="w-full max-w-xl">
        <h1 className="text-2xl font-semibold tracking-tight mb-1 text-white">
          tramix
        </h1>
        <p className="text-sm text-neutral-500 mb-6">
          find songs that mix well together
        </p>

        <form onSubmit={handleSuggest} className="flex gap-2 mb-6">
          <input
            placeholder="enter a song name..."
            value={userSong}
            onChange={(e) => setUserSong(e.target.value)}
            className="flex-1 bg-neutral-800 rounded-full px-4 py-2.5 text-sm text-white placeholder-neutral-600 outline-none focus:border-neutral-600 transition-colors"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-white text-black text-sm font-medium px-5 py-2.5 rounded-full hover:bg-neutral-200 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? "searching..." : "search"}
          </button>
        </form>

        {loading && (
          <div className="space-y-2">
            <p className="text-xs text-neutral-400 tracking-widest mb-2">
              suggestions:
            </p>
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="bg-neutral-900 rounded-xl p-3 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 shrink-0 rounded-md bg-neutral-800 animate-pulse" />
                  <div className="space-y-2">
                    <div className="h-3.5 w-32 bg-neutral-800 rounded animate-pulse" />
                    <div className="h-3 w-20 bg-neutral-800 rounded animate-pulse" />
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <div className="h-6 w-16 bg-neutral-800 rounded-md animate-pulse" />
                  <div className="h-6 w-10 bg-neutral-800 rounded-md animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && suggestResponse.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs text-neutral-400 tracking-widest mb-2">
              suggestions:
            </p>
            {suggestResponse.map((song, index) => (
              <div
                key={song.name}
                className="bg-neutral-900 rounded-xl p-3 flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => togglePlay(index)}
                    className="relative w-12 h-12 shrink-0 rounded-md overflow-hidden group focus:outline-none"
                    aria-label={playingIndex === index ? "Pause" : "Play"}
                  >
                    {song.artworkURL && (
                      <img
                        src={song.artworkURL}
                        alt={`${song.name} artwork`}
                        className="w-full h-full object-cover"
                      />
                    )}
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                      {playingIndex === index ? (
                        <svg
                          className="w-5 h-5 text-white"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <rect x="6" y="4" width="4" height="16" rx="1" />
                          <rect x="14" y="4" width="4" height="16" rx="1" />
                        </svg>
                      ) : (
                        <svg
                          className="w-5 h-5 text-white"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      )}
                    </div>
                    {playingIndex === index && (
                      <div className="absolute inset-0 bg-black/20 flex items-center justify-center">
                        <svg
                          className="w-5 h-5 text-white"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <rect x="6" y="4" width="4" height="16" rx="1" />
                          <rect x="14" y="4" width="4" height="16" rx="1" />
                        </svg>
                      </div>
                    )}
                  </button>
                  <audio
                    ref={(el) => {
                      audioRefs.current[index] = el;
                    }}
                    src={song.previewURL}
                    onEnded={() => setPlayingIndex(null)}
                  />
                  <div>
                    <p className="font-medium text-sm text-white leading-snug">
                      {song.name}
                    </p>
                    <p className="text-sm text-neutral-500 mt-0.5">
                      {song.artist}
                    </p>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <span className="text-xs bg-neutral-800 text-neutral-300 px-2.5 py-1 rounded-md font-mono">
                    {song.bpm} BPM
                  </span>
                  <span className="text-xs bg-neutral-800 text-neutral-300 px-2.5 py-1 rounded-md font-mono">
                    {song.camelot_key}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
