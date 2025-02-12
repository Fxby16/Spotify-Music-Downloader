# Spotify Music Downloader

## Description
Spotify Music Downloader allows you to download tracks, albums, and playlists from Spotify by fetching the corresponding YouTube links and downloading the audio.

## Requirements
- `spotipy`
- `yt_dlp`
- `ffmpeg`
- `mutagen`
- Spotify developer credentials (you can get them at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard))

## Installation
1. Install the required packages.

2. Replace lines 28-29 in [spotifydownloader.py](./spotifydownloader.py) with your Spotify developer credentials:
    ```python
    CLIENT_ID = 'YOUR CLIENT ID'
    CLIENT_SECRET = 'YOUR CLIENT SECRET'
    ```

## Usage
1. Run the script:
    ```sh
    python3 spotifydownloader.py
    ```

2. Follow the prompts:
    - **Spotify URL**: Paste any Spotify URL (can be an album, playlist, or track).
    - **Concurrent Searches**: If the URL doesn't represent a track, enter the number of concurrent searches. (Note: Setting this number too high may cause your PC to crash.)
    - **Concurrent Downloads**: If the URL doesn't represent a track, enter the number of concurrent downloads. (Note: Setting this number too high may cause your PC to crash.)
    - **Output Folder**: Choose the destination folder for the downloaded tracks.

3. The program will start downloading the tracks.

## Disclaimer
Downloads might not work due to YouTube and Spotify updates. In this case, open an issue and I'll fix it.