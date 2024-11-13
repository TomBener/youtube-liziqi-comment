from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
from datetime import datetime

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
    """Fetch all comments for a video"""
    comments = []
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        
        while request:
            response = request.execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment['authorDisplayName'],
                    'text': comment['textDisplay'],
                    'likes': comment['likeCount'],
                    'published_at': comment['publishedAt']
                })
            
            request = youtube.commentThreads().list_next(request, response)
            
        return comments
    except HttpError as e:
        print(f"Error fetching comments: {e}")
        return comments

def save_data(video_id, details, comments):
    """Save fetched data to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "youtube_data"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save video details
    if details:
        details_file = f"{output_dir}/{video_id}_{timestamp}_details.json"
        with open(details_file, 'w', encoding='utf-8') as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
    
    # Save comments
    if comments:
        comments_file = f"{output_dir}/{video_id}_{timestamp}_comments.json"
        with open(comments_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=2)

def main():
    # Replace with your API key
    API_KEY = "AIzaSyAW8GIcWTghaDU8RBQkui48fnijVPRLE9A"
    # Replace with the video ID you want to fetch
    VIDEO_ID = "IrXjnw8BpM0"
    
    youtube = setup_youtube_api(API_KEY)
    
    # Fetch video details
    details = get_video_details(youtube, VIDEO_ID)
    if not details:
        print("Could not fetch video details")
        return
    
    # Fetch comments
    comments = get_video_comments(youtube, VIDEO_ID)
    
    # Save the data
    save_data(VIDEO_ID, details, comments)
    print(f"Saved data for video {VIDEO_ID}")
    print(f"Found {len(comments)} comments")

if __name__ == "__main__":
    main()
