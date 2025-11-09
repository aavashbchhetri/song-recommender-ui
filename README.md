# Next.js Music Recommender

A web application that provides personalized song recommendations based on user-selected songs using machine learning.

## Features

- Search and select songs from a database
- Get personalized recommendations using audio features and ML algorithms
- Modern React frontend with TypeScript and Tailwind CSS
- Python backend with scikit-learn for recommendations

  <img width="1920" height="1387" alt="image" src="https://github.com/user-attachments/assets/468a2703-955f-4d73-9b20-46a6e50241b5" />


## Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: Python, FastAPI, scikit-learn, pandas, numpy
- **APIs**: RESTful endpoints for song search and recommendations

## Usage

1. Search for songs or artists in the search bar
2. Add songs to your selection
3. Click "Recommend" to get personalized song suggestions
4. View your recommendations in the results section

## API Endpoints

- `GET /api/songs?q=<query>` - Search for songs
- `POST /api/recommendations` - Get recommendations based on selected songs

## Deployment

The application is deployed on Vercel at https://songrecommender-beta.vercel.app/
