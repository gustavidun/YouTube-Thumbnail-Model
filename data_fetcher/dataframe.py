import pandas as pd
from datetime import datetime, timedelta, timezone, date

from models import Video, Channel
from youtube_api import get_channel, get_video
from config import OUTPUT_PATH, BACKUP_PATH, CHANNELS_PATH, CSV_OUTPUT_PATH

FIELD_NAMES : list[str] = ["title", "view_timeseries", "thumbnail_url", "video_id", "subscribers", "channel_title", "category"]

def fetch_videos() -> list[Video]:
    """Fetch all videos from videos.pkl file"""
    videos_df = pd.read_pickle(OUTPUT_PATH)
    videos : list[Video] = []

    for index, row in videos_df.iterrows():
        videos.append(
            Video(
                id = row["video_id"],
                title = row["title"],
                views_timeseries = row["view_timeseries"],
                thumbnail_url = row["thumbnail_url"],
                channel = Channel(
                    name = row["channel_title"],
                    subscribers = row["subscribers"],
                    video_playlist="",
                    cursor_pos = 0
                ),
                category = row["category"]
            )
        )
    return videos
        
def fetch_channels(n : int, cursor_pos : int) -> list[Channel]:
    """Fetch x channels from channels csv-file at cursor position"""
    channels_df = pd.read_csv(CHANNELS_PATH, sep = '\t')

    df_len : int = len(channels_df)
    end_pos : int = cursor_pos + n
    default_range : tuple[int, int] = (cursor_pos, end_pos)
    print(f"Fetching {n} channels starting at:{cursor_pos}. Channels length: {df_len}")

    remaining_range : tuple[int, int] = (-1, -1)
    if end_pos > df_len:
        remaining_range = (0, end_pos - df_len)

    channels : list[Channel] = []
    for index, row in channels_df.iterrows():
        if index in range(*default_range) or index in range(*remaining_range):
            channel = get_channel(row["channel"], index)
            if channel:
                print(f"Adding channel, {channel.name} ({cursor_pos-index}/{n})")
                channels.append(channel)
            else:
                print(f"Channel doesn't exist. Skipping.")

    return channels

def update_videos(interval):
    try:
        videos = pd.read_pickle(OUTPUT_PATH)
    except: 
        print("No videos to update.")
        return
    
    now : datetime = datetime.now(timezone.utc).date()
    for index, row in videos.iterrows(): #this could be more efficient
        if len(row["view_timeseries"]) > 30:
            print("Video 30 days old. Skipping.")
            continue
        if row["blacklisted"] == True:
            print("Video has been blacklisted. Skipping.")
            continue
        if now - row["view_timeseries"][-1][1].date() >= timedelta(days=interval):
            video = get_video(row["video_id"])
            if video:
                row['view_timeseries'].extend(
                    video.serialized_views
                )
                print(f"Updated video {video.title}. New view count: {video.views_timeseries[-1].views}")
            else:
                print("Video has been deleted. Blacklisting.")
                row["blacklisted"] = True
        else:
            print(f"Video, {row["title"]} up to date...")

    videos.to_pickle(OUTPUT_PATH)
    videos.to_csv(CSV_OUTPUT_PATH)

def write_video(video : Video):
    try:
        df = pd.read_pickle(OUTPUT_PATH)
    except:
        df = pd.DataFrame(columns=FIELD_NAMES)
    
    row = {
        "title": video.title,
        "view_timeseries": video.serialized_views,
        "thumbnail_url": video.thumbnail_url,
        "video_id": video.id,
        "subscribers": video.channel.subscribers,
        "channel_title": video.channel.name,
        "category": video.category,
        "blacklisted": video.blacklisted,
        "duration": video.duration
    }

    df = pd.concat(
        [df, pd.DataFrame([row], columns=FIELD_NAMES)]
    ).reset_index(drop=True)

    df.to_pickle(OUTPUT_PATH)
    df.to_csv(CSV_OUTPUT_PATH)
    print(f"Video {video.title} added.")

def filter_duration(dur : float = 60):
    create_backup()
    try:
        videos = pd.read_pickle(OUTPUT_PATH)
    except: 
        print("No videos.")
        return
    
    for index, row in videos.iterrows(): #this could be more efficient
        if row["blacklisted"] == True:
            continue

        if row["duration"] == None or pd.isna(row["duration"]):
            video = get_video(row["video_id"])
            if video == None:
                print("Video has been deleted.")
                continue
            if video.duration == None:
                print("Couldn't get video duration.")
                continue
            v_dur = pd.Timedelta(video.duration).total_seconds() #convert ISO8601 string to seconds
            row["duration"] = v_dur

            print(f"Video {video.title}, {v_dur}")

    videos.to_pickle(OUTPUT_PATH)
    videos.to_csv(CSV_OUTPUT_PATH)


def create_backup():
    try:
        videos = pd.read_pickle(OUTPUT_PATH)
        videos.to_pickle(BACKUP_PATH)
    except:
        print("No data to backup.")