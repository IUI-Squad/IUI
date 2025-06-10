from fastapi import FastAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import JSONResponse

app = FastAPI()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="515f586ed84c4fef90a3482ce155a9a3",
    client_secret="948cf67522ac43fb94bee084d061d283",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-recently-played, user-top-read"
))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/recently-played")
def get_recently_played():
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
    
@app.get("/top-artists")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='medium_term')
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]
    return JSONResponse(content={"top_artists": artists})

@app.get("/top-tracks")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]
    return JSONResponse(content={"top_tracks": tracks})

@app.get("/top-artists-long")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='long_term')
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]
    return JSONResponse(content={"top_artists": artists})

@app.get("/top-tracks-long")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='long_term')
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]
    return JSONResponse(content={"top_tracks": tracks})

@app.get("/top-artists-short")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='short_term')
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]
    return JSONResponse(content={"top_artists": artists})

@app.get("/top-tracks-short")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='short_term')
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]
    return JSONResponse(content={"top_tracks": tracks})