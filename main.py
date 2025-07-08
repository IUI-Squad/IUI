import json
from fastapi import FastAPI
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from fastapi.responses import JSONResponse
import time
from spotipy.exceptions import SpotifyException
from collections import Counter

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

    with open("recently_played.json", "w", encoding="utf-8") as f:
        json.dump({"recently_played": tracks}, f, ensure_ascii=False, indent=4)
     # Count recurring artists and tracks
    artists = [entry["artist"] for entry in tracks]
    track_names = [entry["track"] for entry in tracks]

    artist_counts = Counter(artists)
    track_counts = Counter(track_names)

    recurring_artists = {artist: count for artist, count in artist_counts.items() if count > 1}
    recurring_tracks = {track: count for track, count in track_counts.items() if count > 1}

    # Detect back-to-back plays
    back_to_back_tracks = []
    for i in range(len(tracks) - 1):
        if tracks[i]["track"] == tracks[i + 1]["track"]:
            back_to_back_tracks.append({
                "track": tracks[i]["track"],
                "artist": tracks[i]["artist"],
                "played_at_1": tracks[i]["played_at"],
                "played_at_2": tracks[i + 1]["played_at"]
            })

    # Save recurring + back-to-back results
    with open("recurring_counts.json", "w", encoding="utf-8") as f:
        json.dump({
            "recurring_artists": recurring_artists,
            "recurring_tracks": recurring_tracks,
            "back_to_back_tracks": back_to_back_tracks
        }, f, ensure_ascii=False, indent=4)

    return JSONResponse(content={
        "recently_played": tracks,
        "recurring_artists": recurring_artists,
        "recurring_tracks": recurring_tracks,
        "back_to_back_tracks": back_to_back_tracks
    })
    
@app.get("/top-artists")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='medium_term')
    # Extract artist data
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]

    # Save artist data to JSON file
    with open("top_artists_medium.json", "w", encoding="utf-8") as f:
        json.dump({"top_artists": artists}, f, ensure_ascii=False, indent=4)

    # Flatten list of genres for all artists
    all_genres = [genre for artist in artists for genre in artist["genres"]]

    # Count how often each genre appears
    genre_counts = Counter(all_genres)

    # Save genre counts to separate JSON file
    with open("top_artists_medium_genre_counts.json", "w", encoding="utf-8") as f:
        json.dump(genre_counts, f, ensure_ascii=False, indent=4)

    # Return both artists and genre counts in the response
    return JSONResponse(content={
        "top_artists": artists,
        "genre_counts": genre_counts
    })

@app.get("/top-tracks")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='medium_term')
    
    # Extract track info
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]

    # Save top tracks data to a JSON file
    with open("top_tracks.json", "w", encoding="utf-8") as f:
        json.dump({"top_tracks": tracks}, f, ensure_ascii=False, indent=4)

    # Count how many tracks come from the same artist
    artists = [track["artist"] for track in tracks]
    artist_counts = Counter(artists)

    # Save artist counts to a separate JSON file
    with open("top_tracks_artist_counts.json", "w", encoding="utf-8") as f:
        json.dump(artist_counts, f, ensure_ascii=False, indent=4)

    return JSONResponse(content={
        "top_tracks": tracks,
        "artist_counts": artist_counts
    })

@app.get("/top-artists-long")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='long_term')
    # Extract artist data
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]

    # Save artist data to JSON file
    with open("top_artists_long.json", "w", encoding="utf-8") as f:
        json.dump({"top_artists": artists}, f, ensure_ascii=False, indent=4)

    # Flatten list of genres for all artists
    all_genres = [genre for artist in artists for genre in artist["genres"]]

    # Count how often each genre appears
    genre_counts = Counter(all_genres)

    # Save genre counts to separate JSON file
    with open("top_artists_long_genre_counts.json", "w", encoding="utf-8") as f:
        json.dump(genre_counts, f, ensure_ascii=False, indent=4)

    # Return both artists and genre counts in the response
    return JSONResponse(content={
        "top_artists": artists,
        "genre_counts": genre_counts
    })

@app.get("/top-tracks-long")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='long_term')
    # Extract track info
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]

    # Save top tracks data to a JSON file
    with open("top_tracks_longterm.json", "w", encoding="utf-8") as f:
        json.dump({"top_tracks": tracks}, f, ensure_ascii=False, indent=4)

    # Count how many tracks come from the same artist
    artists = [track["artist"] for track in tracks]
    artist_counts = Counter(artists)

    # Save artist counts to a separate JSON file
    with open("top_tracks_artist_counts_longterm.json", "w", encoding="utf-8") as f:
        json.dump(artist_counts, f, ensure_ascii=False, indent=4)

    return JSONResponse(content={
        "top_tracks": tracks,
        "artist_counts": artist_counts
    })

@app.get("/top-artists-short")
def top_artists():
    results = sp.current_user_top_artists(limit=50, time_range='short_term')

    # Extract artist data
    artists = [{"name": artist["name"], "genres": artist["genres"]} for artist in results['items']]

    # Save artist data to JSON file
    with open("top_artists_short.json", "w", encoding="utf-8") as f:
        json.dump({"top_artists": artists}, f, ensure_ascii=False, indent=4)

    # Flatten list of genres for all artists
    all_genres = [genre for artist in artists for genre in artist["genres"]]

    # Count how often each genre appears
    genre_counts = Counter(all_genres)

    # Save genre counts to separate JSON file
    with open("top_artists_short_genre_counts.json", "w", encoding="utf-8") as f:
        json.dump(genre_counts, f, ensure_ascii=False, indent=4)

    # Return both artists and genre counts in the response
    return JSONResponse(content={
        "top_artists": artists,
        "genre_counts": genre_counts
    })

@app.get("/top-tracks-short")
def top_tracks():
    results = sp.current_user_top_tracks(limit=50, time_range='short_term')
    tracks = [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results['items']]

    # Save top tracks data to a JSON file
    with open("top_tracks_shortterm.json", "w", encoding="utf-8") as f:
        json.dump({"top_tracks": tracks}, f, ensure_ascii=False, indent=4)

    # Count how many tracks come from the same artist
    artists = [track["artist"] for track in tracks]
    artist_counts = Counter(artists)

    # Save artist counts to a separate JSON file
    with open("top_tracks_artist_counts_shortterm.json", "w", encoding="utf-8") as f:
        json.dump(artist_counts, f, ensure_ascii=False, indent=4)

    return JSONResponse(content={
        "top_tracks": tracks,
        "artist_counts": artist_counts
    })



# use with caution
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

