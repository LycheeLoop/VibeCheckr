# -----------------------------------IMPORTS-----------------------------------------#
import requests
import time
from config import REDDIT_SECRET, REDDIT_CLIENT_ID
import re
from datetime import datetime

# ----------------------------- FUNCTION TO GET REDDIT POST ID-------------------#

def extract_post_id(reddit_post_url):
    match = re.search(r"comments/([a-zA-Z0-9]+)", reddit_post_url)
    if match:
        return match.group(1)
    else:
        print("Could not extract post ID from the URL.")
        return None



# ----------------------------- GET ACCESS TOKEN and COMMENTS-------------------#

class RedditAPI:
    def __init__(self):
        self.token = None
        self.token_expiry = 0

    def get_access_token(self):
        # If token is expired or missing, request a new one
        if not self.token or time.time() >= self.token_expiry:
            auth = requests.auth.HTTPBasicAuth(REDDIT_CLIENT_ID, REDDIT_SECRET)
            data = {'grant_type': 'client_credentials'}
            headers = {'User-Agent': 'vibecheckr/0.1 (web app for sentiment analysis)'}

            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth, data=data, headers=headers
            )
            token_data = response.json()
            self.token = token_data.get('access_token')
            self.token_expiry = time.time() + token_data.get('expires_in', 3600)  # Default 1 hour expiry
        return self.token

    def get_reddit_comments_and_info(self, post_id, max_comments=100):
        # Fetch comments for a specific post
        headers = {
            'Authorization': f'bearer {self.get_access_token()}',
            'User-Agent': 'vibecheckr/0.1 (web app for sentiment analysis)'
        }

        params = {
            'limit': max_comments  # Set maximum number of comments
        }

        response = requests.get(f'https://oauth.reddit.com/comments/{post_id}', headers=headers, params=params)

        if response.status_code == 200:
            comments_data = response.json()

            # Extract post details
            post_data = comments_data[0]['data']['children'][0]['data']
            post_title = post_data.get('title')
            comment_count = post_data.get('num_comments')
            upvote_count = post_data.get('ups')
            score = post_data.get('score')
            downvote_count = upvote_count - score
            post_date = datetime.fromtimestamp(post_data.get('created_utc')).strftime('%d-%m-%Y')
            subreddit_name = post_data.get('subreddit')

            # Fetch subreddit details for member count
            subreddit_response = requests.get(f'https://oauth.reddit.com/r/{subreddit_name}/about', headers=headers)
            if subreddit_response.status_code == 200:
                subreddit_data = subreddit_response.json()
                subreddit_members = subreddit_data['data'].get('subscribers', 0)
            else:
                print(f"Failed to retrieve subreddit info: {subreddit_response.status_code}")
                subreddit_members = None  # Set to None if request fails



            # Extract comments
            comments = []
            for comment in comments_data[1]['data']['children']:
                if 'body' in comment['data']:
                    raw_comment = comment['data']['body']

                    # Clean the comment
                    cleaned_comment = raw_comment.encode('ascii', 'ignore').decode('ascii')
                    cleaned_comment = re.sub(r"\\u[\dA-Fa-f]{4}", "", cleaned_comment)
                    cleaned_comment = cleaned_comment.replace("\\", "")
                    cleaned_comment = re.sub(r"http\S+|www\S+", "", cleaned_comment)
                    cleaned_comment = cleaned_comment.replace("\n", " ").strip()

                    comments.append(cleaned_comment)

            # Return post info and comments
            return {
                'title': post_title,
                'comment_count': comment_count,
                'upvotes': upvote_count,
                'score': score,
                'downvotes': downvote_count,
                'post_date': post_date,
                'subreddit': subreddit_name,
                'subreddit_members': subreddit_members,
                'comments': comments
            }
        else:
            print(f"Failed to retrieve comments: {response.status_code}")
            return None

