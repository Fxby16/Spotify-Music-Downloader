# Spotify Music Downloader
  
## LAST UPDATE: 05/06/2023  
  
## REQUIREMENTS
- python (link to the official website: https://www.python.org/downloads/) 
- to install the packages just run the .bat file if you are on windows or run the .sh file if you are on linux  
- If after you installed everything the program crashes try to replace the file yt_dlp\extractor\youtube.py with the one provided in the REQUIREMENTS folder. one change was made at line 3705 (try only if you are on windows, on Linux it should already be fixed)  
- spotify client id and client secret(you can get them by logging here: https://developer.spotify.com/dashboard/login)  
- put the client id and the client secret in "spotifydownloader.py" (lines 8-9)  
  
- install ffmpeg
    - follow this [guide](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/) if you are on windows
    - run ` sudo apt install ffmpeg` if you are on linux
