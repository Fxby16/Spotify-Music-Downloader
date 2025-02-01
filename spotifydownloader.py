import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import yt_dlp
import concurrent.futures
import aiotube
from multiprocessing import Pool

PLAYLIST_LINK = input('Insert Playlist/Album/Track link to continue or 0 to ESC: ')

MAX_CONCURRENT_SEARCHES = input("Max concurrent searches: ")
assert MAX_CONCURRENT_SEARCHES.isdigit(), "Invalid input" # Ensure input is a number
MAX_CONCURRENT_SEARCHES = int(MAX_CONCURRENT_SEARCHES)

MAX_CONCURRENT_DOWNLOADS = input("Max concurrent downloads: ")
assert MAX_CONCURRENT_DOWNLOADS.isdigit(), "Invalid input" # Ensure input is a number
MAX_CONCURRENT_DOWNLOADS = int(MAX_CONCURRENT_DOWNLOADS)

# Spotify API credentials
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

# Spotify client
CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(client_id = CLIENT_ID, client_secret = CLIENT_SECRET)
SP = spotipy.Spotify(client_credentials_manager = CLIENT_CREDENTIALS_MANAGER)

def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]

def download_worker(args):
    url, folder, track = args
    print("Starting download worker to download", track)
    download(url, folder, track)

def search_youtube(track, folder):
    try:
        video = aiotube.Search.video(track)

        if video is None:
            print(f"Search returned no result for {track}")
            return None  

        url = video._url

        if url:
            return url, folder, track  

    except Exception as e:
        print(f"Search failed for {track}: {e}")

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

    results = SP.playlist_tracks(playlist_uri)
    
    # Extract track names in format "track_name - artist1, artist2, ..."
    tracks = [
        track['track']['name'] + ' - ' + ', '.join(artist['name'] for artist in track['track']['artists'])
        for track in results['items']
    ]

    # Fetch other pages of tracks and add them to the list
    while results['next']:
        results = SP.next(results)
        tracks.extend(
            track['track']['name'] + ' - ' + ', '.join(artist['name'] for artist in track['track']['artists'])
            for track in results['items']
        )

    print(f"Playlist has {len(tracks)} tracks")
    
    fetch_and_download(tracks, folder) # Fetch YouTube links and download tracks
    
    return folder

def album():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching album tracks...')

    # Extract track names in format "track_name - artist1, artist2, ..."
    results = SP.album_tracks(playlist_uri)
    tracks = [
        track['name'] + ' - ' + ', '.join(artist['name'] for artist in track['artists'])
        for track in results['items']
    ]

    # Fetch other pages of tracks and add them to the list
    while results['next']:
        results = SP.next(results)
        tracks.extend(
            track['name'] + ' - ' + ', '.join(artist['name'] for artist in track['artists'])
            for track in results['items']
        )

    print(f'Album has {len(tracks)} tracks')

    fetch_and_download(tracks, folder) # Fetch YouTube links and download tracks

    return folder

def track():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching track...')

    # Extract track name in format "track_name - artist1, artist2, ..."
    results = SP.track(playlist_uri)
    track = results['name'] + ' - ' + ', '.join(artist['name'] for artist in results['artists'])
    
    # Directly search and download the track since there is only one
    video = aiotube.Search.video(track)
    url = video._url

    download(url, folder ,track)

    return folder

def download(link, folder, track):
    ydl_opts = {
        'format': 'bestaudio',
        'extractaudio': True,
        'outtmpl': f'{folder}/{track}.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as yt:
        yt.download([link])

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
