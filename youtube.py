from ytmusicapi import YTMusic

language = "it"
location = "IT"
ytmusic = YTMusic(language=language, location=location)

def common_words(youtube_title, spotify_title):
    """Check if YouTube title contains enough words from Spotify title"""
    
    youtube_words = set(word.lower().strip() for word in youtube_title.split() if len(word) > 2)
    spotify_words = set(word.lower().strip() for word in spotify_title.split() if len(word) > 2)
    
    common_stopwords = {'the', 'and', 'or', 'but', 'feat', 'ft', 'with', 'by', 'remix', 'version', 'visual'}
    youtube_words -= common_stopwords
    spotify_words -= common_stopwords
    
    matching_words = youtube_words & spotify_words
    return len(matching_words)

def has_common_words(youtube_title, spotify_title, min_common=2):
    return common_words(youtube_title, spotify_title) >= min_common

def search_video(track):
    res = ytmusic.search(track["title"] + " " + track["artists"], "songs", None, 5)
    res2 = ytmusic.search(track["title"] + " " + track["artists"], "videos", None, 5)

    #print(res)
    out = res[0]

    skip_check = False
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
            #print(song)
            out = song
            skip_check = True
            break

    if not skip_check and not has_common_words(out["title"], track["title"], 1) and common_words(out["title"], track["title"]) < common_words(res2[0]["title"], track["title"]):
        print(out["title"], out["artists"], "----", res2[0]["title"])
        out = res2[0] 

    print("Found:", out["title"], "by", ", ".join(artist["name"] for artist in out["artists"]))
    print("Expected:", track["title"], "by", track["artists"])

    return f"https://music.youtube.com/watch?v={out['videoId']}"