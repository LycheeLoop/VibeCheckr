# -----------------------------------IMPORTS-----------------------------------------#
import html
from datetime import datetime
from config import YOUTUBE_API_KEY
import requests
import re




# ----------------------------- FUNCTION TO GET VIDEO ID FROM VIDEO URL-------------------#
def get_video_id(youtube_url):
    # Regular expression for extracting video ID from YouTube URLs
    regex = (
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})')

    match = re.search(regex, youtube_url)

    if match:
        return match.group(1)
    else:
        return None

# ----------------------------- API FUNCTION TO GET VIDEO COMMENTS USING VIDEO ID-------------------#
def get_video_comments(YOUTUBE_API_KEY, video_id, max_results=80, timeout=50):
    # API endpoint for retrieving comment thread of a video
    url = f"https://www.googleapis.com/youtube/v3/commentThreads"

    # Parameters for API request
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'key': YOUTUBE_API_KEY,
        'maxResults': max_results
    }

    # Make the request
    response = requests.get(url, params=params, timeout=timeout)
    # Check response status
    if response.status_code == 200:
        # Parse the JSON
        data = response.json()

        # Collect all comments into list
        comments = []
        filtered_comments = []
        for item in data['items']:
            # Remove HTML coding
            comment = html.unescape(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            # Remove <br> and similar tags
            comment = re.sub(r"<br\s*/?>", "", comment)
            # Append clean comments to list
            comments.append(comment)
            # Remove any reviews that contain links
            filtered_comments = [item for item in comments if "<a href" not in item]

        # Return list of comments
        return filtered_comments
    else:
        # Print error, return None
        print(f"Error: {response.status_code} - {response.text}")
        return None



# ----------------------------- API FUNCTION TO GET VIDEO DETAILS -------------------#
def get_youtube_details(YOUTUBE_API_KEY, video_id, timeout=50):
    url = f"https://www.googleapis.com/youtube/v3/videos"

    # Parameters for API request
    params = {
        'part': 'snippet,statistics',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }

    # Make the request
    response = requests.get(url, params=params, timeout=timeout)
    # Check response status
    if response.status_code == 200:
        # Parse the JSON
        data = response.json()

        # Extract needed data
        if 'items' in data and len (data['items']) > 0:
            video_data = data['items'][0]

            title = video_data['snippet']['title']
            description = video_data['snippet']['description']
            post_date = video_data['snippet']['publishedAt']
            # Convert string to datetime and extract day
            post_date = datetime.strptime(post_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%Y")
            thumbnail = video_data['snippet']['thumbnails']['high']['url']
            view_count = video_data['statistics'].get('viewCount', 0)
            like_count = video_data['statistics'].get('likeCount', 0)
            comment_count = video_data['statistics'].get('commentCount', 0)

            return{
                'title': title,
                'description': description,
                'thumbnail': thumbnail,
                'post_date': post_date,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count
            }
        else:
            return "Video not found"

    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


