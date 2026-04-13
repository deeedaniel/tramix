import { useState } from "react";

interface Song {
  name: string;
  artist: string;
  bpm: number;
  key: string;
  camelot_key: string;
  previewURL: string;
}

export default function Search() {
  const [userSong, setUserSong] = useState("");
  const [suggestResponse, setSuggestResponse] = useState<Song[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSuggest = (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!userSong) return;

    setLoading(true);

    // Using test data to avoid pinging endpoint
    // TODO: Change this to the real endpoint
    fetch(`/data/suggest-endpoint-response.json?q=${userSong}`)
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
    <div className="flex h-screen justify-center items-center flex-col">
      <form onSubmit={handleSuggest}>
        <input
          placeholder="Enter a Song Name"
          value={userSong}
          onChange={(e) => setUserSong(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>

      {loading && <p>Searching...</p>}

      <div className="results">
        {suggestResponse.map((song) => (
          <div key={song.name}>
            <strong>{song.name}</strong> by {song.artist}
            <audio controls>
              <source src={song.previewURL} />
            </audio>
          </div>
        ))}
      </div>
    </div>
  );
}
