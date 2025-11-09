import json
import requests

BACKEND_URL = "https://song-recommeder-backend-hbyp.onrender.com"

def handler(request):
    if request.method == "GET":
        query = request.args.get("q", "")
        if not query.strip():
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps([])
            }

        try:
            response = requests.get(f"{BACKEND_URL}/search", params={"q": query})
            response.raise_for_status()
            songs = response.json()
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(songs)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }

    elif request.method == "POST":
        try:
            body = request.get_json(silent=True) or {}
            response = requests.post(f"{BACKEND_URL}/recommend", json=body, headers={"Content-Type": "application/json"})
            response.raise_for_status()
            recs = response.json()
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(recs)
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": str(e)})
            }

    else:
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }
