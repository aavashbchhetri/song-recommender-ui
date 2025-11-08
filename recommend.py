import sys
import json
import os
import io
import pickle
import requests
import cloudpickle 
import joblib
import pandas as pd
import numpy as np
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity

# Default public URLs (from Supabase storage) - can be overridden with env vars
DEFAULT_NN_MODEL_URL = os.getenv(
    "NN_MODEL_URL",
"https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/nn_model.pkl",)
DEFAULT_SCALER_URL = os.getenv(
    "SCALER_URL",
"https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/scaler.pkl",)
DEFAULT_DATASET_URL = os.getenv(
    "DATASET_URL",
"https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/songs_data.csv",)


def load_pickle_local_or_url(local_path: str, url: str):
    """Load a pickle (cloudpickle-compatible) from a local file or from a URL."""
    # Try local first
    if os.path.exists(local_path):
        with open(local_path, "rb") as f:
            return cloudpickle.load(f)

    # Otherwise download from URL
    resp = requests.get(url)
    resp.raise_for_status()
    return cloudpickle.loads(resp.content)

def load_csv_local_or_url(local_path: str, url: str) -> pd.DataFrame:
    if os.path.exists(local_path):
        return pd.read_csv(local_path)
    # allow pandas to read directly from URL
    return pd.read_csv(url)


def get_recommendations(input_songs: List[str], top_k: int = 5) -> List[str]:
    """Return top_k recommendations given a list of song names.

    Behavior:
    - Loads dataset and scaler/model from local files if available, otherwise from the public URLs.
    - Uses the scaler (if present) to scale song feature vectors.
    - Computes cosine similarity between the mean vector of the selected songs and all songs.
    - Returns the top_k most similar tracks, excluding the selected songs.
    - If input_songs is empty, returns the first top_k tracks from the dataset as a fallback.
    """
    # Paths (local)
    local_model_path = "nn_model.pkl"
    local_scaler_path = "scaler.pkl"
    local_dataset_path = "songs_data.csv"

    # Load dataset
    try:
        songs_df = load_csv_local_or_url(local_dataset_path, DEFAULT_DATASET_URL)
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        return []

    if "track_name" not in songs_df.columns:
        # try to find a possible name column
        possible = [c for c in songs_df.columns if "track" in c.lower() or "name" in c.lower()]
        if possible:
            songs_df = songs_df.rename(columns={possible[0]: "track_name"})
        else:
            print("Dataset does not contain a 'track_name' column.", file=sys.stderr)
            return []

    # Extract numeric feature columns (exclude track_name)
    numeric_cols = songs_df.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        # fallback: try all columns except track_name and coerce to numeric
        numeric_cols = [c for c in songs_df.columns if c != "track_name"]

    try:
        features_all = songs_df[numeric_cols].apply(pd.to_numeric, errors="coerce").fillna(0).values.astype(float)
    except Exception as e:
        print(f"Error extracting numeric features: {e}", file=sys.stderr)
        return []

    # Load scaler if available
    scaler = None
    try:
        scaler = load_pickle_local_or_url(local_scaler_path, DEFAULT_SCALER_URL)
    except Exception as e:
        # not fatal; continue without scaler
        print(f"Warning: could not load scaler ({e}), proceeding without scaling", file=sys.stderr)

    # Scale features if scaler is present and has transform
    try:
        if scaler is not None and hasattr(scaler, "transform"):
            features_all_scaled = scaler.transform(features_all)
        else:
            features_all_scaled = features_all
    except Exception as e:
        print(f"Error scaling features: {e}", file=sys.stderr)
        features_all_scaled = features_all

    # Ensure track names are strings and lowercase-safe
    track_names = songs_df["track_name"].fillna("").astype(str).values
    try:
        lowered = np.char.lower(track_names)
    except Exception:
        lowered = np.array([str(x).lower() for x in track_names])

    # If no input songs provided, return top_k first tracks as fallback
    if not input_songs:
        return track_names[:top_k].tolist()

    # Find indices for selected songs (case-insensitive match)
    selected_indices = []
    for s in input_songs:
        s_lower = s.strip().lower()
        matches = np.where(lowered == s_lower)[0]

        if len(matches) == 0:
            # try substring match
            matches = np.where([s_lower in t for t in lowered])[0]
        if len(matches) > 0:
            selected_indices.extend(matches.tolist())

    if len(selected_indices) == 0:
        print("No selected songs found in dataset (check exact names). Returning top tracks.", file=sys.stderr)
        return track_names[:top_k].tolist()

    # Compute query vector as mean of selected song vectors
    query_vec = np.mean(features_all_scaled[selected_indices, :], axis=0).reshape(1, -1)

    # Compute cosine similarity
    try:
        sims = cosine_similarity(features_all_scaled, query_vec).reshape(-1)
    except Exception as e:
        print(f"Error computing similarity: {e}", file=sys.stderr)
        return []

    # Exclude selected indices
    sims[selected_indices] = -np.inf

    # Get top_k indices
    top_idx = np.argsort(sims)[-top_k:][::-1]
    recommendations = track_names[top_idx].tolist()
    return recommendations


if __name__ == "__main__":
    # Accept either:
    # - a single JSON array string: python recommend.py '["song a","song b"]'
    # - multiple plain args: python recommend.py "song a" "song b"
    args = sys.argv[1:]
    input_songs = []

    if not args:
        input_songs = []
    elif len(args) == 1:
        # try to parse single arg as JSON array, otherwise treat as single song name
        single = args[0]
        try:
            parsed = json.loads(single)
            if isinstance(parsed, list):
                input_songs = [str(x) for x in parsed]
            else:
                input_songs = [str(parsed)]
        except Exception:
            input_songs = [single]
    else:
        # multiple args -> treat each as a song name
        input_songs = [str(a) for a in args]

    # normalize whitespace
    input_songs = [s.strip() for s in input_songs if s and s.strip()]

    recs = get_recommendations(input_songs, top_k=5)
    print(json.dumps(recs))