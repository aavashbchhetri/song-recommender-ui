import json
from recommend import get_recommendations

def handler(request):
    try:
        body = request.get_json() if request.method == "POST" else {}
        songs = body.get("songs", [])
        recs = get_recommendations(songs, top_k=5)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"recommendations": recs})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
