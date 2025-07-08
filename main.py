from fastapi import FastAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import JSONResponse
import time
from spotipy.exceptions import SpotifyException

def safe_spotify_call(func, *args, **kwargs):
    while True:
        try:
            return func(*args, **kwargs)
        except SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers.get("Retry-After", 5))
                print(f"Rate limit hit. Sleeping for {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                raise


app = FastAPI()

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="515f586ed84c4fef90a3482ce155a9a3",
    client_secret="948cf67522ac43fb94bee084d061d283",
    redirect_uri="http://127.0.0.1:8888/callback",
    scope="user-read-recently-played, user-top-read,user-library-read"
))

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/recently-played")
def get_recently_played():
    results = sp.current_user_recently_played(limit=50)
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

@app.get("/saved-tracks")
def get_saved_tracks():
    saved_tracks = []
    limit = 50
    offset = 0

    initial_result = safe_spotify_call(sp.current_user_saved_tracks, limit=1)
    total = initial_result['total']

    all_tracks = []
    artist_ids = []

    while True:
        results = safe_spotify_call(sp.current_user_saved_tracks, limit=limit, offset=offset)
        items = results['items']
        if not items:
            break

        for item in items:
            track = item['track']
            artist = track['artists'][0]
            artist_ids.append(artist['id'])
            all_tracks.append({
                "name": track['name'],
                "artist_id": artist['id'],
                "artist_name": artist['name'],
                "album": track['album']['name']
            })

        offset += limit

    # Remove duplicate artist IDs
    unique_artist_ids = list(set(artist_ids))

    # Batch request artist genres with retry logic
    artist_genre_map = {}
    for i in range(0, len(unique_artist_ids), 50):
        batch_ids = unique_artist_ids[i:i+50]
        artists = safe_spotify_call(sp.artists, batch_ids)['artists']
        for artist in artists:
            artist_genre_map[artist['id']] = artist.get('genres', [])

    # Build final track list
    for track in all_tracks:
        genres = artist_genre_map.get(track['artist_id'], [])
        saved_tracks.append({
            "name": track["name"],
            "artist": track["artist_name"],
            "genres": genres,
            "album": track["album"]
        })

    return JSONResponse(content={
        "total_saved_tracks": total,
        "saved_tracks": saved_tracks
    })


@app.get("/playlist-tracks-with-genres")
def get_all_playlist_tracks_with_genres():
    all_tracks = []
    artist_cache = {}  # Cache to avoid repeating artist API calls

    playlists = sp.current_user_playlists(limit=50)
    
    for playlist in playlists['items']:
        playlist_name = playlist['name']
        playlist_id = playlist['id']
        offset = 0

        while True:
            tracks_response = sp.playlist_tracks(playlist_id, limit=100, offset=offset)
            items = tracks_response['items']
            if not items:
                break

            for item in items:
                track = item['track']
                if track:
                    artist = track['artists'][0]
                    artist_id = artist['id']

                    # Get artist genres (use cache if available)
                    if artist_id in artist_cache:
                        genres = artist_cache[artist_id]
                    else:
                        try:
                            artist_info = sp.artist(artist_id)
                            genres = artist_info.get('genres', [])
                            artist_cache[artist_id] = genres
                        except Exception as e:
                            genres = []

                    all_tracks.append({
                        "playlist": playlist_name,
                        "track": track['name'],
                        "artist": artist['name'],
                        "album": track['album']['name'],
                        "genres": genres
                    })

            offset += 100

    return JSONResponse(content={"playlist_tracks": all_tracks})