import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
import sys
import yt_dlp


CLIENT_ID = 'YOUR ID'
CLIENT_SECRET = 'YOUR SECRET'
PLAYLIST_LINK = input('Insert Playlist/Album/Track link to continue or 0 to ESC: ')
if PLAYLIST_LINK == '0':
    sys.exit()

CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
SP = spotipy.Spotify(client_credentials_manager=CLIENT_CREDENTIALS_MANAGER)


def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]


def playlist():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input("Destination folder: ")

    results = SP.playlist_tracks(playlist_uri)
    tracks = results['items']

    while results['next']:
        results = SP.next(results)
        tracks.extend(results['items'])

    for track in tracks:
        song = (track['track']['name'] + ' - ' + track['track']['artists'][0]['name'])
        resultss = YoutubeSearch(song, max_results = 1).to_dict()

        for v in resultss:
            url = ('https://www.youtube.com' + v['url_suffix'])

        download(url,folder,song)
        print('Download of ' + song + ' completed')

    return folder

def album():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')
    tracks = SP.album_tracks(playlist_uri)
    for track in tracks['items']:
        song = (track['name'] + ' - ' + track['artists'][0]['name'])
        resultss = YoutubeSearch(song, max_results = 1).to_dict()
        for v in resultss:
            url = ('https://www.youtube.com' + v['url_suffix'])
        download(url,folder,song)
        print('Download of ' + song + ' completed')

    return folder

def song():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input('Destination folder: ')

    results = SP.track(playlist_uri)
    song = (results['name'] + ' - ' + results['artists'][0]['name'])
    resultss = YoutubeSearch(song, max_results = 1).to_dict()
    for v in resultss:
        url = ('https://www.youtube.com' + v['url_suffix'])
    download(url,folder,song)
    print('Download of ' + song + ' completed')

    return folder

def download(link,folder,song):

    ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': f'{folder}/{song}.%(ext)s',
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
    flag = int(input("Playlist(1), album(2) or song(3)? "))
    if flag == 1:
        playlist()
    elif flag == 2:
        album()
    elif flag == 3:
        song()

main()
