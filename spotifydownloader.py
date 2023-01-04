import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtube_search import YoutubeSearch
from pytube import YouTube
import os
import moviepy
import glob
import moviepy.editor
import sys

CLIENT_ID = 'YOUR ID'
CLIENT_SECRET = "YOUR SECRET"
PLAYLIST_LINK = input("Insert Playlist/Album/Track link to continue or 0 to ESC: ")
if PLAYLIST_LINK == '0':
    sys.exit()

CLIENT_CREDENTIALS_MANAGER = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
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
        song = (track['track']['name'] + ' - ' + track["track"]["artists"][0]["name"])
        resultss = YoutubeSearch(song, max_results = 1).to_dict()

        for v in resultss:
            url = ('https://www.youtube.com' + v['url_suffix'])

        download(url,folder)
        print("Download of " + song + " completed")

    converter(folder)

    return folder

def album():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input("Destination folder: ")
    tracks = SP.album_tracks(playlist_uri)
    for track in tracks['items']:
        song = (track['name'] + ' - ' + track["artists"][0]["name"])
        resultss = YoutubeSearch(song, max_results = 1).to_dict()
        for v in resultss:
            url = ('https://www.youtube.com' + v['url_suffix'])
        download(url,folder)
        print("Download of " + song + " completed")

    converter(folder)

    return folder

def song():
    playlist_uri = get_playlist_uri(PLAYLIST_LINK)
    folder = input("Destination folder: ")

    results = SP.track(playlist_uri)
    song = (results['name'] + ' - ' + results["artists"][0]["name"])
    resultss = YoutubeSearch(song, max_results = 1).to_dict()
    for v in resultss:
        url = ('https://www.youtube.com' + v['url_suffix'])
    download(url,folder)
    print("Download of " + song + " completed")

    converter(folder)

    return folder


def converter(folder):
    mp4_filenames_list = glob.glob(os.path.join(folder, "*.mp4"))

    for filename in mp4_filenames_list:
        video = moviepy.editor.VideoFileClip(filename)
        audio = video.audio

        if audio is not None:
            mp3_file_name = filename.replace('.mp4', '.mp3')
            audio.write_audiofile(mp3_file_name)

        video.close()

        os.unlink(filename)



def download(link,folder):

    yt = YouTube(link)
    video = yt.streams.filter(file_extension='mp4').order_by('abr').desc().first().download(folder)


def main():
    flag = int(input("Playlist(1), album(2) or song(3)? "))
    if flag == 1:
        playlist()
    elif flag == 2:
        album()
    elif flag == 3:
        song()

main()
