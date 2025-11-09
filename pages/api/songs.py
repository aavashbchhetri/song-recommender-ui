import json
import requests
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://xsfhvuvvyofxqudqnbyi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzZmh2dXZ2eW9meHF1ZHFuYnlpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjU3NzM5NywiZXhwIjoyMDc4MTUzMzk3fQ.3yRwCCMfGQqxByDDpBBr7i3T_n60dmtpXn4tO58we1E"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Import recommendation function
from recommendations import get_recommendations

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
            response = supabase.table("songs").select("track_name").ilike("track_name", f"%{query}%").limit(10).execute()
            songs = [row["track_name"] for row in response.data if row.get("track_name")]
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
            songs = body.get("songs", [])
            if not isinstance(songs, list):
                songs = [str(songs)]
            recs = get_recommendations(songs, top_k=5)
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
