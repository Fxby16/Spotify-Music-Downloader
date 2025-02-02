import requests
import re
import json
import urllib.parse

def search_video(title):
    title = urllib.parse.quote_plus(title)
    url = f"https://www.youtube.com/results?search_query={title}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" # Pretend to be a browser
    }

    response = requests.get(url, headers=headers) # GET request to search for the video

    if response.status_code != 200:
        print(f"Error while searching for {title}")
        return None

    match = re.search(r"var ytInitialData = ({.*?});</script>", response.text) # Search for JSON data in the HTML
    if not match:
        print(f"JSON not found for {title}")
        return None

    try:
        data = json.loads(match.group(1))

        # Extract the results from the JSON data
        results = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"] \
                  ["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]

        # Return the first video found
        for item in results:
            if "videoRenderer" in item:
                video = item["videoRenderer"]
                return f"https://www.youtube.com/watch?v={video['videoId']}"

        print(f"No video found for {title}")
        return None

    except Exception as e:
        print(f"Error while parsing JSON for {title}: {e}")
        return None