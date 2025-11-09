import sys
import json
import requests
import cloudpickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Global variables (cold start)
# -----------------------------
SCALER = None
MODEL = None
SONGS_DF = None
FEATURES_ALL = None
FEATURES_ALL_SCALED = None
TRACK_NAMES = None
LOWERED = None

# -----------------------------
# Supabase URLs
# -----------------------------
DEFAULT_NN_MODEL_URL = "https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/nn_model.pkl"
DEFAULT_SCALER_URL = "https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/scaler.pkl"
DEFAULT_DATASET_URL = "https://xsfhvuvvyofxqudqnbyi.supabase.co/storage/v1/object/public/song-recommender-model/songs_data.csv"

# -----------------------------
# Preload function
# -----------------------------
def preload():
    global SCALER, MODEL, SONGS_DF, FEATURES_ALL, FEATURES_ALL_SCALED, TRACK_NAMES, LOWERED

    # Load scaler
    try:
        resp = requests.get(DEFAULT_SCALER_URL)
        resp.raise_for_status()
        SCALER = cloudpickle.loads(resp.content)
    except Exception as e:
        print(f"Error loading scaler: {e}", file=sys.stderr)
        SCALER = None

    # Load model (optional, if used)
    try:
        resp = requests.get(DEFAULT_NN_MODEL_URL)
        resp.raise_for_status()
        MODEL = cloudpickle.loads(resp.content)
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        MODEL = None

    # Load dataset
    try:
        SONGS_DF = pd.read_csv(DEFAULT_DATASET_URL)
        numeric_cols = SONGS_DF.select_dtypes(include=[np.number]).columns.tolist()
        FEATURES_ALL = SONGS_DF[numeric_cols].fillna(0).values.astype(float)
        FEATURES_ALL_SCALED = SCALER.transform(FEATURES_ALL) if SCALER else FEATURES_ALL

        TRACK_NAMES = SONGS_DF["track_name"].fillna("").astype(str).values
        try:
            LOWERED = np.char.lower(TRACK_NAMES)
        except Exception:
            LOWERED = np.array([str(x).lower() for x in TRACK_NAMES])
    except Exception as e:
        print(f"Error loading dataset: {e}", file=sys.stderr)
        SONGS_DF = pd.DataFrame()
        FEATURES_ALL = FEATURES_ALL_SCALED = np.zeros((0,0))
        TRACK_NAMES = LOWERED = np.array([])

# Run preload at cold start
preload()

# -----------------------------
# Recommendation function
# -----------------------------
def get_recommendations(input_songs, top_k=5):
    global FEATURES_ALL_SCALED, TRACK_NAMES, LOWERED

    if FEATURES_ALL_SCALED is None or TRACK_NAMES is None or len(TRACK_NAMES) == 0:
        return []

    if not input_songs:
        return TRACK_NAMES[:top_k].tolist()

    # Find indices for selected songs (case-insensitive)
    selected_indices = []
    for s in input_songs:
        s_lower = s.strip().lower()
        matches = np.where(LOWERED == s_lower)[0]
        if len(matches) == 0:
            # try substring match
            matches = np.where([s_lower in t for t in LOWERED])[0]
        if len(matches) > 0:
            selected_indices.extend(matches.tolist())

    if len(selected_indices) == 0:
        return TRACK_NAMES[:top_k].tolist()

    # Compute mean feature vector of selected songs
    query_vec = np.mean(FEATURES_ALL_SCALED[selected_indices, :], axis=0).reshape(1, -1)

    # Compute cosine similarity
    try:
        sims = cosine_similarity(FEATURES_ALL_SCALED, query_vec).reshape(-1)
    except Exception as e:
        print(f"Error computing similarity: {e}", file=sys.stderr)
        return TRACK_NAMES[:top_k].tolist()

    # Exclude selected songs
    sims[selected_indices] = -np.inf

    # Get top_k recommendations
    top_idx = np.argsort(sims)[-top_k:][::-1]
    return TRACK_NAMES[top_idx].tolist()

# -----------------------------
# Main entrypoint for PythonShell
# -----------------------------
if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        if args:
            try:
                input_songs = json.loads(args[0])
                if not isinstance(input_songs, list):
                    input_songs = [str(input_songs)]
            except Exception:
                input_songs = [args[0]]
        else:
            input_songs = []

        input_songs = [s.strip() for s in input_songs if s.strip()]
        recs = get_recommendations(input_songs, top_k=5)

        # Always output valid JSON
        print(json.dumps(recs))

    except Exception as e:
        # Catch any error and output JSON
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
