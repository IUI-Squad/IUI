from fastapi import FastAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import JSONResponse

app = FastAPI()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="515f586ed84c4fef90a3482ce155a9a3",
    client_secret="948cf67522ac43fb94bee084d061d283",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-recently-played"
))

@app.get("/recently-played")
def get_recently_played():
    try:
        results = sp.current_user_recently_played(limit=10)
        tracks = []

        for item in results['items']:
            track = item['track']
            played_at = item['played_at']
            tracks.append({
                "track": track['name'],
                "artist": track['artists'][0]['name'],
                "played_at": played_at
            })

        return JSONResponse(content={"recently_played": tracks})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
