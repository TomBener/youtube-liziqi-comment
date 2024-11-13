from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from datetime import datetime, timezone
import time
import csv
import re


def setup_youtube_api(api_key):
    """Initialize YouTube API client"""
    return build('youtube', 'v3', developerKey=api_key)


def get_video_details(youtube, video_id):
    """Fetch video description and basic details"""
    try:
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()

        if not response['items']:
            return None

        return response['items'][0]['snippet']
    except HttpError as e:
        print(f"Error fetching video details: {e}")
        return None


def get_video_comments(youtube, video_id):
    """Fetch all comments and their replies for a video"""
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet,replies",
            videoId=video_id,
            maxResults=100
        )

        page_count = 0
        while request:
            time.sleep(0.1)
            response = request.execute()
            page_count += 1

            for item in response['items']:
                # Get main comment
                comment = item['snippet']['topLevelComment']['snippet']
                published_at = datetime.strptime(
                    comment['publishedAt'],
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)

                # Clean text by removing HTML tags
                clean_text = comment['textDisplay'].replace('<br>', '\n')
                # Remove any remaining HTML tags using a simple regex
                clean_text = re.sub(r'<[^>]+>', '', clean_text)

                # Store main comment
                comments.append({
                    'comment_id': item['id'],
                    'author': comment['authorDisplayName'],
                    'text': clean_text,  # Use cleaned text
                    'likes': comment['likeCount'],
                    'published_at': published_at,
                    'updated_at': comment['updatedAt'],
                    'viewer_rating': comment.get('viewerRating', 'none'),
                    'language': comment.get('textOriginalLanguageCode', ''),
                    'is_reply': False,
                    'parent_id': '',
                    'reply_count': item['snippet']['totalReplyCount']
                })

                # Get replies if they exist
                if item['snippet']['totalReplyCount'] > 0 and 'replies' in item:
                    for reply in item['replies']['comments']:
                        reply_snippet = reply['snippet']
                        reply_published_at = datetime.strptime(
                            reply_snippet['publishedAt'],
                            '%Y-%m-%dT%H:%M:%SZ'
                        ).replace(tzinfo=timezone.utc)

                        # Clean reply text
                        clean_reply_text = reply_snippet['textDisplay'].replace('<br>', '\n')
                        clean_reply_text = re.sub(r'<[^>]+>', '', clean_reply_text)

                        comments.append({
                            'comment_id': reply['id'],
                            'author': reply_snippet['authorDisplayName'],
                            'text': clean_reply_text,  # Use cleaned text
                            'likes': reply_snippet['likeCount'],
                            'published_at': reply_published_at,
                            'updated_at': reply_snippet['updatedAt'],
                            'viewer_rating': reply_snippet.get('viewerRating', 'none'),
                            'language': reply_snippet.get('textOriginalLanguageCode', ''),
                            'is_reply': True,
                            'parent_id': reply_snippet['parentId'],
                            'reply_count': 0  # Replies can't have replies
                        })

            request = youtube.commentThreads().list_next(request, response)
            print(f"Fetched page {page_count}, total comments: {len(comments)}")

        return comments
    except HttpError as e:
        print(f"Error fetching comments: {e}")
        return comments


def save_data_csv(video_id, details, comments):
    """Save fetched data to CSV file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save video details
    if details:
        details_file = f"{timestamp}_details.json"
        with open(details_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, ensure_ascii=False, indent=2)

    # Save comments to CSV
    if comments:
        comments_file = f"{timestamp}_comments.csv"
        with open(comments_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'comment_id', 'author', 'text', 'likes',
                'published_at', 'updated_at', 'viewer_rating',
                'language', 'is_reply', 'parent_id', 'reply_count'
            ])
            writer.writeheader()
            writer.writerows(comments)
        print(f"Saved {len(comments)} comments to {comments_file}")


def main():
    # Load API key from environment variable
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    if not API_KEY:
        print("Please set the YOUTUBE_API_KEY environment variable")
        return

    VIDEO_ID = "IrXjnw8BpM0"

    youtube = setup_youtube_api(API_KEY)

    # Fetch video details
    details = get_video_details(youtube, VIDEO_ID)
    if not details:
        print("Could not fetch video details")
        return

    print("Fetching comments (this may take a while)...")
    comments = get_video_comments(youtube, VIDEO_ID)

    # Save the data
    save_data_csv(VIDEO_ID, details, comments)
    print(f"Completed! Found {len(comments)} comments for video {VIDEO_ID}")


if __name__ == "__main__":
    main()
