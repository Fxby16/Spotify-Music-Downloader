# Spotify Music Downloader

## Description
Spotify Music Downloader allows you to download tracks, albums, and playlists from Spotify by fetching the corresponding YouTube links and downloading the audio.

## Last Update
01/02/2025

## Requirements
- `spotipy`
- `yt_dlp`
- `aiotube`
- `ffmpeg`
- Spotify developer credentials (you can get them at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))

## Installation
1. Install the required packages.

2. Replace lines 12-13 in [spotifydownloader.py](./spotifydownloader.py) with your Spotify developer credentials:
    ```python
    CLIENT_ID = 'YOUR CLIENT ID'
    CLIENT_SECRET = 'YOUR CLIENT SECRET'
    ```

## Usage
1. Run the script:
    ```sh
    python3 spotifydownloader.py
    ```

2. The program will ask for a Spotify URL. Paste any Spotify URL (can be an album, playlist, or track).

## Disclaimer
Downloads might not work due to YouTube and Spotify updates. In this case, open an issue and I'll fix it.