import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import yt_dlp
import concurrent.futures
from multiprocessing import Pool
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests
from youtube import search_video
import os

PLAYLIST_LINK = input('Insert Playlist/Album/Track link to continue or 0 to ESC: ')

MAX_CONCURRENT_SEARCHES = 1
MAX_CONCURRENT_DOWNLOADS = 1

if '/track/' not in PLAYLIST_LINK:
    MAX_CONCURRENT_SEARCHES = input("Max concurrent searches: ")
    assert MAX_CONCURRENT_SEARCHES.isdigit(), "Invalid input" # Ensure input is a number
    MAX_CONCURRENT_SEARCHES = int(MAX_CONCURRENT_SEARCHES)

    MAX_CONCURRENT_DOWNLOADS = input("Max concurrent downloads: ")
    assert MAX_CONCURRENT_DOWNLOADS.isdigit(), "Invalid input" # Ensure input is a number
    MAX_CONCURRENT_DOWNLOADS = int(MAX_CONCURRENT_DOWNLOADS)

# Spotify API credentials
CLIENT_ID = 'ed9fa7b0a4e94db28e584d797b1d35aa'
CLIENT_SECRET = '193d017ff6ad482fb6aeed1e72960577'

# Spotify client
CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
SP = spotipy.Spotify(client_credentials_manager = CLIENT_CREDENTIALS_MANAGER)

def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]

def download_worker(args):
    url, folder, track = args
    print("Starting download worker to download", track['title'] + " - " + track['artists'])
    download(url, folder, track)

def search_youtube(track, folder):
    title_to_search = f"{track['title']} - {track['artists']}"

    if os.path.exists(f"{folder}/{title_to_search}.mp3"):
        print(f"Track {title_to_search} already exists in {folder}. Skipping download.")
        return None

    try:
        url = search_video(track)

        if url is None:
            print(f"Search returned no result for {title_to_search}")
            return None  

        return url, folder, track  

    except Exception as e:
        print(f"Search failed for {title_to_search}: {e}")

    return None  

def fetch_and_download(tracks, folder):
    download_tasks = []

    print("Searching YouTube for tracks...")

    # Search for YouTube links concurrently (up to MAX_CONCURRENT_SEARCHES at a time)
    with concurrent.futures.ThreadPoolExecutor(max_workers = MAX_CONCURRENT_SEARCHES) as executor:
        futures = {executor.submit(search_youtube, track, folder): track for track in tracks}
        
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                download_tasks.append(result)  # Add valid searches to the task list

    print(f"Found {len(download_tasks)} valid YouTube links. Starting downloads...")

    # Download tracks concurrently (up to MAX_CONCURRENT_DOWNLOADS at a time). 
    # Done in separate process due to yt_dlp not being thread-safe.
    with Pool(processes = MAX_CONCURRENT_DOWNLOADS) as pool:
        pool.map(download_worker, download_tasks)

def playlist():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input("Destination folder: ")
    
    print("Fetching playlist tracks...")

    # Extract track information from the playlist
    results = SP.playlist_tracks(playlist_uri)
    
    tracks = []
    for track in results['items']:
        track_info = track['track']
        track_name = track_info['name']
        artists = ', '.join(artist['name'] for artist in track_info['artists'])
        album = track_info['album']['name']
        thumbnail_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None

        tracks.append({
            "title": track_name,
            "artists": artists,
            "album": album,
            "thumbnail": thumbnail_url
        })

    # Fetch other pages of tracks and add them to the list
    while results['next']:
        results = SP.next(results)
        
        for track in results['items']:
            track_info = track['track']
            track_name = track_info['name']
            artists = ', '.join(artist['name'] for artist in track_info['artists'])
            album = track_info['album']['name']
            thumbnail_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None

            tracks.append({
                "title": track_name,
                "artists": artists,
                "album": album,
                "thumbnail": thumbnail_url
            })

    print(f"Playlist has {len(tracks)} tracks")

    global MAX_CONCURRENT_SEARCHES, MAX_CONCURRENT_DOWNLOADS
    MAX_CONCURRENT_SEARCHES = min(MAX_CONCURRENT_SEARCHES, len(tracks)) # Limit searches to the number of tracks
    MAX_CONCURRENT_DOWNLOADS = min(MAX_CONCURRENT_DOWNLOADS, len(tracks)) # Limit downloads to the number of tracks
    
    fetch_and_download(tracks, folder) # Fetch YouTube links and download tracks
    
    return folder

def album():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching album details...')
    album_data = SP.album(playlist_uri)  # Fetch album metadata

    album_name = album_data['name']
    thumbnail_url = album_data['images'][0]['url'] if album_data['images'] else None

    print('Fetching album tracks...')

    # Extract track information from the album
    results = SP.album_tracks(playlist_uri)
    
    tracks = []
    for track in results['items']:
        track_name = track['name']
        artists = ', '.join(artist['name'] for artist in track['artists'])

        tracks.append({
            "title": track_name,
            "artists": artists,
            "album": album_name,
            "thumbnail": thumbnail_url
        })

    # Fetch other pages of tracks and add them to the list
    while results['next']:
        results = SP.next(results)
        for track in results['items']:
            track_name = track['name']
            artists = ', '.join(artist['name'] for artist in track['artists'])

            tracks.append({
                "title": track_name,
                "artists": artists,
                "album": album_name,
                "thumbnail": thumbnail_url
            })

    print(f'Album "{album_name}" has {len(tracks)} tracks')

    global MAX_CONCURRENT_SEARCHES, MAX_CONCURRENT_DOWNLOADS
    MAX_CONCURRENT_SEARCHES = min(MAX_CONCURRENT_SEARCHES, len(tracks)) # Limit searches to the number of tracks
    MAX_CONCURRENT_DOWNLOADS = min(MAX_CONCURRENT_DOWNLOADS, len(tracks)) # Limit downloads to the number of tracks

    fetch_and_download(tracks, folder) # Fetch YouTube links and download tracks

    return folder

def track():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching track...')

    # Extract track name in format "track_name - artist1, artist2, ..."
    results = SP.track(playlist_uri)
    track = { 
        "title": results['name'],
        "artists": ', '.join(artist['name'] for artist in results['artists']),
        "album": results['album']['name'],
        "thumbnail": results['album']['images'][0]['url'] if results['album']['images'] else None
    }

    title_to_search = f"{track['title']} - {track['artists']}"

    # Directly search and download the track since there is only one
    url = search_video(track)

    print(f'Starting download for {title_to_search}')

    if os.path.exists(f"{folder}/{title_to_search}.mp3"):
        print(f"Track {title_to_search} already exists in {folder}. Skipping download.")
    else:
        download(url, folder ,track)

    return folder

def sanitize_filename(filename):
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    return filename.strip() 

def download(link, folder, track):
    filename = sanitize_filename(f"{track['title']} - {track['artists']}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{folder}/{filename}.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }


    try:
        with yt_dlp.YoutubeDL(ydl_opts) as yt:
            yt.download([link])
    except Exception as e:
        print(f"Download failed for {track['title']} - {track['artists']}: {e}")
        return

    mp3_file = f'{folder}/{filename}.mp3'
    audio = EasyID3(mp3_file)

    # Add metadata to the downloaded track
    audio['title'] = track['title']
    audio['artist'] = track['artists']
    audio['album'] = track['album']
    audio.save()

    # Get the thumbnail and add it to the track
    if track['thumbnail']:
        response = requests.get(track['thumbnail'])
        if response.status_code == 200:
            image_data = response.content
            audio = ID3(mp3_file)
            audio.add(APIC(
                encoding = 3,  # UTF-8
                mime = 'image/jpeg',  # Image format
                type = 3,  # Front cover
                desc = 'Cover',
                data = image_data
            ))
            audio.save()

def main():
    if PLAYLIST_LINK == '0':
        sys.exit()

    if '/playlist/' in PLAYLIST_LINK:
        playlist()
    elif '/track/' in PLAYLIST_LINK:
        track()
    elif '/album/' in PLAYLIST_LINK:
        album()
    else:
        print('Invalid link')

if __name__ == '__main__':
    main()
