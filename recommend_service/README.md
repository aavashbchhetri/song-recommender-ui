Minimal recommendation service wrapper

What this does

- Provides a tiny FastAPI endpoint POST /recommend that forwards the request to the repository's `recommend.py` script.

Usage (local)

1. cd to `recommend_service` and create a virtualenv
2. pip install -r requirements.txt
3. Ensure `recommend.py` and any model files (nn_model.pkl, scaler.pkl, etc.) are present in the same folder.
4. Run locally: uvicorn recommend_api:app --host 0.0.0.0 --port 8080

Deployment

- Deploy to Render/Railway or any container host using the provided Dockerfile. After deploying, set the Next.js environment variable `RECOMMEND_API_URL` to `https://your-service/recommend` in Vercel.

Notes

- This wrapper expects the underlying `recommend.py` to accept a single JSON argument (stringified list of selected songs) and to print JSON to stdout representing the recommendations.
