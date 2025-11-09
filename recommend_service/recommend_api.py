from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import json
import os
from typing import List

app = FastAPI()


class Songs(BaseModel):
    songs: List[str]


@app.post("/recommend")
def recommend(songs: Songs):
    # This minimal wrapper runs the existing recommend.py script in the same folder.
    # Assumes recommend.py accepts a single JSON string arg (list of songs) and
    # prints a JSON array of recommended song names to stdout.
    try:
        cwd = os.path.dirname(__file__)
        arg = json.dumps(songs.songs)
        # run recommend.py; ensure Python and model files are present in deployment
        proc = subprocess.run(
            ["python", "recommend.py", arg],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

        if proc.returncode != 0:
            raise HTTPException(status_code=500, detail=f"recommend.py error: {proc.stderr}")

        out = proc.stdout.strip()
        if not out:
            return {"recommendations": []}

        try:
            data = json.loads(out)
        except Exception:
            # If the script prints logging + JSON, try to find the first JSON array/object
            idx = out.find("[")
            if idx == -1:
                raise HTTPException(status_code=500, detail="Invalid output from recommend.py")
            data = json.loads(out[idx:])

        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
