from fastapi import FastAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth

app = FastAPI()

@app.get("/recently-played")
def get_recently_played():
    return {"message": "This route works!"}