import { NextApiRequest, NextApiResponse } from "next";
import axios from "axios";

const BACKEND_URL = "https://song-recommeder-backend-hbyp.onrender.com";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === "GET") {
    const query = (req.query.q as string) || "";

    if (query.trim().length === 0) {
      return res.status(200).json([]);
    }

    try {
      const response = await axios.get(`${BACKEND_URL}/search`, {
        params: { q: query },
      });
      return res.status(200).json(response.data);
    } catch (error: any) {
      console.error("Backend error:", error.response?.data || error.message);
      return res.status(500).json({
        error: "Error fetching suggestions",
        details: error.response?.data || error.message,
      });
    }
  } else if (req.method === "POST") {
    try {
      const response = await axios.post(`${BACKEND_URL}/recommend`, req.body, {
        headers: {
          "Content-Type": "application/json",
        },
      });
      return res.status(200).json(response.data);
    } catch (error: any) {
      console.error("Backend error:", error.response?.data || error.message);
      return res.status(500).json({
        error: "Error getting recommendations",
        details: error.response?.data || error.message,
      });
    }
  } else {
    res.status(405).json({ error: "Method not allowed" });
  }
}
