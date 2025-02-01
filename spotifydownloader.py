import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import yt_dlp
import time
import threading
import concurrent.futures
import aiotube

PLAYLIST_LINK = input('Insert Playlist/Album/Track link to continue or 0 to ESC: ')

CLIENT_ID = 'YOUR CLIENT ID'
CLIENT_SECRET = 'YOUR CLIENT SECRET'

CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)

def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]

def download_worker(lock, url, folder, track):
    with lock:
        download(url, folder, track)

def search_youtube(track, folder, lock, threads):
    try:
        video = aiotube.Search.video(track)
        url = video.metadata.get('url')

        if url:
            download_thread = threading.Thread(target=download_worker, args=(lock, url, folder, track))
            download_thread.start()
            threads.append(download_thread)

    except Exception as e:
        print(f"Search failed for {track}: {e}")

def fetch_youtube_links(tracks, folder, lock):
    futures = []
    threads = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for track in tracks:
            future = executor.submit(search_youtube, track, folder, lock, threads)
            futures.append(future)

    print("Waiting for all searches to finish...")
    concurrent.futures.wait(futures)
    print("All searches finished")

    print("Waiting for all downloads to finish...")
    for thread in threads:
        thread.join()
    print("All downloads finished")
        

def playlist():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input("Destination folder: ")
    
    print("Fetching playlist tracks...")

    results = SP.playlist_tracks(playlist_uri)
    
    tracks = [
        track['track']['name'] + ' - ' + ', '.join(artist['name'] for artist in track['track']['artists'])
        for track in results['items']
    ]

    while results['next']:
        results = SP.next(results)
        tracks.extend(
            track['track']['name'] + ' - ' + ', '.join(artist['name'] for artist in track['track']['artists'])
            for track in results['items']
        )

    print(f"Playlist has {len(tracks)} tracks")
    
    lock = threading.Lock()
    fetch_youtube_links(tracks, folder, lock)
    
    return folder

def album():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching album tracks...')

    results = SP.album_tracks(playlist_uri)
    tracks = [
        track['name'] + ' - ' + ', '.join(artist['name'] for artist in track['artists'])
        for track in results['items']
    ]

    while results['next']:
        results = SP.next(results)
        tracks.extend(
            track['name'] + ' - ' + ', '.join(artist['name'] for artist in track['artists'])
            for track in results['items']
        )

    print(f'Album has {len(tracks)} tracks')

    lock = threading.Lock()
    fetch_youtube_links(tracks, folder, lock)

    return folder

def track():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    print('Fetching track...')

    results = SP.track(playlist_uri)
    track = results['name'] + ' - ' + ', '.join(artist['name'] for artist in results['artists'])
    
    video = aiotube.Search.video(track)
    url = video.metadata.get('url')

    download(url, folder ,track)

    return folder

def download(link, folder, track):
    start = time.time()
    
    ydl_opts = {
        'format': 'bestaudio',
        'extractaudio': True,
        'outtmpl': f'{folder}/{track}.%(ext)s',
        'quiet': False,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as yt:
        yt.download([link])
    
    end = time.time()
    print(f"Download of {track} took {end - start} seconds")

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

main()
