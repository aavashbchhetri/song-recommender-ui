import { NextApiRequest, NextApiResponse } from "next";
import path from "path";
import { PythonShell } from "python-shell";
import { createClient } from "@supabase/supabase-js";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "GET") {
    const query = (req.query.q as string) || "";

    if (query.trim().length === 0) {
      return res.status(200).json([]);
    }

    // Supabase project credentials (provided)
    const SUPABASE_URL = "https://xsfhvuvvyofxqudqnbyi.supabase.co";
    const SUPABASE_KEY =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhzZmh2dXZ2eW9meHF1ZHFuYnlpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjU3NzM5NywiZXhwIjoyMDc4MTUzMzk3fQ.3yRwCCMfGQqxByDDpBBr7i3T_n60dmtpXn4tO58we1E";

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

    try {
      // Query the `songs` table for matching track_name values
      const { data, error } = await supabase
        .from("songs")
        .select("track_name")
        .ilike("track_name", `%${query}%`)
        .limit(10);

      if (error) {
        console.error("Supabase error:", error);
        return res.status(500).json({ error: "Error querying Supabase" });
      }

      const songs = (data || [])
        .map((row: { track_name?: string }) => row.track_name ?? "")
        .filter(Boolean);
      return res.status(200).json(songs);
    } catch (err) {
      console.error("Server error:", err);
      return res.status(500).json({ error: "Server error" });
    }
  } else if (req.method === "POST") {
    const selectedSongs = req.body.songs;

    if (!selectedSongs || selectedSongs.length === 0) {
      return res.status(400).json({ error: "No songs selected" });
    }

    try {
      const options = {
        mode: "text" as const,
        pythonPath: "python",
        pythonOptions: ["-u"],
        // model files are now in the same directory as the Next.js app
        scriptPath: process.cwd(),
        args: [JSON.stringify(selectedSongs)],
      };

      PythonShell.run("recommend.py", options)
        .then((results) => {
          const recommendations = JSON.parse(results[0]);
          res.status(200).json(recommendations);
        })
        .catch((err) => {
          console.error("Python error:", err);
          res.status(500).json({ error: "Error getting recommendations" });
        });
    } catch (error) {
      console.error("Server error:", error);
      res.status(500).json({ error: "Server error" });
    }
  } else {
    res.status(405).json({ error: "Method not allowed" });
  }
}
