import type { NextApiRequest, NextApiResponse } from "next";
import axios from "axios";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const response = await axios.post(
      "https://song-recommeder-backend-hbyp.onrender.com/recommend",
      req.body,
      {
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    return res.status(200).json(response.data);
  } catch (error: any) {
    console.error("Backend error:", error.response?.data || error.message);
    return res.status(500).json({
      error: "Error fetching recommendations",
      details: error.response?.data || error.message,
    });
  }
}
