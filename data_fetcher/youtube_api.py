import requests
from datetime import datetime, timezone, timedelta
from time import sleep

from config import API_KEY
from models import Channel, Video, Views

CHANNEL_ENDPOINT : str = "https://www.googleapis.com/youtube/v3/channels" 
PLAYLIST_ENDPOINT : str = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOS_ENDPOINT : str = "https://www.googleapis.com/youtube/v3/videos"
MAX_ERRORS : int = 5

api_index : int = 0
error_counter : int = 0 

def request(url : str, params : dict):
    global api_index
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        if resp:
            return resp.json()
        else:
            return
    except requests.exceptions.HTTPError as e:
        print("HTTP error...")
        if e.response.status_code == 403:
            print(f"API index {api_index} reached quota.")
            if (api_index + 1 < len(API_KEY)):
                api_index += 1
                params.update({"key": API_KEY[api_index]})
                request(url, params)
            else:
                raise Exception("Quota exceeded.")
        if e.response.status_code == 400:
            print("Bad request.")
            return
    except requests.exceptions.Timeout:
        print("Connection timed out. Trying again in 3 seconds...")
        sleep(3)
        if error_counter <= MAX_ERRORS:
            request(url, params)
    except requests.exceptions.ConnectionError:
        print("Connection failed. Trying again in 5 seconds...")
        sleep(5)
        if error_counter <= MAX_ERRORS:
            request(url, params)

def get_channel(id : str, cursor_pos : int) -> Channel | None:
    resp = request(CHANNEL_ENDPOINT, params={
        "key": API_KEY[api_index],
        "part": "contentDetails, snippet, statistics",
        "maxResults": 1,
        "id": id         
    })

    if not resp:
        return
    if not "items" in resp:
        return
    
    cr = resp["items"][0]
    return Channel(
        name = cr["snippet"]["title"],
        subscribers = int(cr["statistics"]["subscriberCount"]),
        video_playlist = cr["contentDetails"]["relatedPlaylists"]["uploads"],
        cursor_pos=cursor_pos
    )

def get_video(id : str, channel : Channel | None = None):
    video_resp = request(VIDEOS_ENDPOINT, params = {
        "key": API_KEY[api_index],
        "part": "contentDetails, snippet, statistics",
        "id": id
    })
    if not video_resp:
        return
    if "items" in video_resp:
        try:
            vr = video_resp["items"][0]
            return Video(
                id=id,
                channel=channel,
                title=vr["snippet"]["title"],
                views_timeseries = [Views(
                    views = int(vr["statistics"]["viewCount"]), 
                    date = datetime.now(timezone.utc)
                )],
                thumbnail_url=vr["snippet"]["thumbnails"]["medium"]["url"],
                category=vr["snippet"]["categoryId"],
                duration=vr["contentDetails"]["duration"],
                blacklisted=None
            ) 
        except:
            return
    else:
        return

def get_videos(channel : Channel, date) -> list[Video] | None:
    playlist_resp = request(PLAYLIST_ENDPOINT, params={
        "key": API_KEY[api_index],
        "part": "contentDetails, snippet",
        "maxResults": 50,
        "playlistId": channel.video_playlist
    })
    try:
        if not "items" in playlist_resp:
            return
    except:
        print("Upload playlist doesn't exist.")
        return
    
    videos : list[Video] = []
    for video in playlist_resp["items"]:
        published_at = datetime.fromisoformat(
            video["contentDetails"]["videoPublishedAt"]
        )
        if published_at.date() == date:
            vr = get_video(video["contentDetails"]["videoId"], channel)
            if not vr:
                continue
            videos.append(vr)

    if len(videos) == 0:
        print("No videos matching the criteria.")
        return
    return videos

#channel = get_channel("UCi_AR7WqvXa6LEnRn_7ES7A")
#videos = get_videos(channel, datetime.now(timezone.utc).date() - timedelta(days=1))

#for video in videos:
    #print(video.title)