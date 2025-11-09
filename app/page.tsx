"use client";

import { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {
  const [search, setSearch] = useState<string>("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [selectedSongs, setSelectedSongs] = useState<string[]>([]);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (search.trim().length > 0) {
        try {
          const response = await axios.get(
            `/api/songs?q=${encodeURIComponent(search)}`
          );
          setSuggestions(response.data);
        } catch (error) {
          console.error("Error fetching suggestions:", error);
          setSuggestions([]);
        }
      } else {
        setSuggestions([]);
      }
    };

    const debounceTimer = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounceTimer);
  }, [search]);

  const handleSongSelect = (song: string) => {
    if (!selectedSongs.includes(song)) {
      setSelectedSongs([...selectedSongs, song]);
    }
    setSearch("");
    setSuggestions([]);
  };

  const handleRemoveSong = (song: string) => {
    setSelectedSongs(selectedSongs.filter((s) => s !== song));
  };

  const handleGetRecommendations = async () => {
    if (selectedSongs.length === 0) return;

    setLoading(true);
    try {
      const response = await axios.post(
        "/api/songs",
        { songs: selectedSongs },
        {
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
        }
      );
      if (response.data && Array.isArray(response.data)) {
        setRecommendations(response.data);
      } else if (
        response.data &&
        Array.isArray(response.data.recommendations)
      ) {
        setRecommendations(response.data.recommendations);
      } else {
        setRecommendations([]);
        console.error("Unexpected response format:", response.data);
      }
    } catch (error) {
      console.error("Error getting recommendations:", error);
      if (axios.isAxiosError(error)) {
        console.error("Response details:", {
          status: error.response?.status,
          data: error.response?.data,
          headers: error.response?.headers,
        });
      }
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  const clearSelection = () => {
    setSelectedSongs([]);
    setRecommendations([]);
    setSearch("");
  };

  return (
    <main className="min-h-screen bg-slate-900 text-slate-100">
      <div className="max-w-5xl mx-auto px-6 py-20">
        <header className="flex items-center justify-between mb-10">
          <div className="flex items-center gap-4">
            <div>
              <h1 className="text-4xl font-extrabold tracking-tight mb-5">
                Song Recommender
              </h1>
              <p className="text-sm text-slate-400">
                Type, add, and discover — built with audio-features and ML.
              </p>
            </div>
          </div>
        </header>

        <section className="bg-slate-800/50 rounded-3xl p-8 shadow-xl">
          <div className="flex flex-col lg:flex-row items-start gap-8">
            <div className="flex-1">
              <h2 className="text-2xl lg:text-3xl font-bold mb-2 text-slate-100">
                Find your vibe — instantly
              </h2>
              <p className="text-slate-400 mb-6">
                Search for songs, add them to "My Jams" and click Recommend to
                get a personalized playlist.
              </p>

              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-5 h-5 text-white/70"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15z"
                    />
                  </svg>
                </div>
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search for songs or artists"
                  className="w-full lg:w-3/4 pl-12 pr-4 py-3 rounded-full bg-slate-700/50 border border-slate-600 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-500 transition"
                />{" "}
                {suggestions.length > 0 && (
                  <div className="absolute z-50 mt-2 w-full lg:w-3/4 bg-slate-800 rounded-xl shadow-lg border border-slate-700 text-slate-100 text-sm">
                    {suggestions.map((song, index) => (
                      <button
                        key={index}
                        onClick={() => handleSongSelect(song)}
                        className="w-full text-left px-4 py-3 hover:bg-slate-700 border-b border-slate-700 last:border-b-0"
                      >
                        {song}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {selectedSongs.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm text-slate-400 mb-2">My Jams</h3>
                  <div className="flex flex-wrap gap-3">
                    {selectedSongs.map((song, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-2 bg-slate-700/50 px-3 py-2 rounded-full shadow-sm"
                      >
                        <span className="text-sm">{song}</span>
                        <button
                          onClick={() => handleRemoveSong(song)}
                          className="w-6 h-6 bg-slate-600 rounded-full flex items-center justify-center hover:bg-slate-500"
                        >
                          <span className="text-xs">×</span>
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6 lg:mt-8 flex items-center gap-4">
                <button
                  onClick={handleGetRecommendations}
                  disabled={selectedSongs.length === 0 || loading}
                  className={`inline-flex items-center gap-3 px-6 py-3 rounded-full text-sm font-semibold transition ${
                    selectedSongs.length === 0
                      ? "bg-slate-700 text-slate-400 cursor-not-allowed"
                      : "bg-slate-600 hover:bg-slate-500 text-slate-100 hover:scale-[1.02]"
                  }`}
                >
                  {loading ? (
                    <>
                      <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24">
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                          fill="none"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                        ></path>
                      </svg>
                      <span>Getting Recommendations...</span>
                    </>
                  ) : (
                    <>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="w-4 h-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M14 5l7 7m0 0l-7 7m7-7H3"
                        />
                      </svg>
                      <span>Recommend</span>
                    </>
                  )}
                </button>

                <button
                  onClick={clearSelection}
                  className="text-sm text-slate-400 hover:text-slate-200"
                >
                  Clear
                </button>
              </div>
            </div>
          </div>
        </section>

        {recommendations.length > 0 && (
          <section className="mt-8">
            <h3 className="text-lg font-bold mb-4">Recommended Songs</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recommendations.map((song, i) => (
                <div
                  key={i}
                  className="bg-slate-800/50 rounded-xl p-4 hover:scale-105 transition"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-slate-700 rounded-md flex items-center justify-center">
                      🎵
                    </div>
                    <div>
                      <div className="font-medium text-slate-100">{song}</div>
                      <div className="text-sm text-slate-400">
                        Recommended for you
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
