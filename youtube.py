from ytmusicapi import YTMusic

ytmusic = YTMusic()

def search_video(track):
    res = ytmusic.search(track["title"] + " " + track["artists"], "songs", None, 5)
    out = res[0]

    for song in res:
        artist_names = ", ".join(artist["name"] for artist in song["artists"])
        #print("Title:", song["title"], "Artists:", artist_names)
        #print(track["artists"])

        song_artists_set = set(a.strip().lower() for a in artist_names.split(","))
        track_artists_set = set(a.strip().lower() for a in track["artists"].split(","))

        if (
            song["title"].lower() == track["title"].lower()
            and song_artists_set == track_artists_set
        ):
            out = song
            break

    print("Found:", out["title"], "by", ", ".join(artist["name"] for artist in out["artists"]))
    print("Expected:", track["title"], "by", track["artists"])

    return f"https://music.youtube.com/watch?v={out['videoId']}"