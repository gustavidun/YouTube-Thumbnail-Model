from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler  # runs tasks in the background
from apscheduler.triggers.cron import CronTrigger  # allows us to specify a recurring time for execution
from contextlib import asynccontextmanager
from datetime import datetime
import json

from youtube_api import get_videos
from dataframe import write_video, fetch_channels, update_videos, create_backup
from models import Channel, Video
from config import STATE_PATH, CHANNELS_FETCH, DATE_TARGET, VIEW_UPDATE_INTERVAL

def get_cursor_pos() -> int:
    with open(STATE_PATH, "r") as state:
        return json.load(state)["cursor"]

def set_cursor_pos(pos : int):
    with open(STATE_PATH, "r+") as state:
        data = json.load(state)
        data["cursor"] = pos
        state.seek(0)
        json.dump(data, state)
        state.truncate()

def scan_channels():
    cursor_pos : int = get_cursor_pos()
    channels : list[Channel] = fetch_channels(5, cursor_pos)
    vid_count : int = 0

    for channel in channels:
        videos : list[Video] = get_videos(channel, DATE_TARGET)
        if not videos:
            continue
        for video in videos:
            write_video(video)
            vid_count += 1

    set_cursor_pos(cursor_pos+5)
    print(f"Updating cursor after 5 channels. Added videos: {vid_count}")    

def daily_scan():
    print(f"Daily task is running at {datetime.now()}")
    print(f"Creating backup...")
    create_backup()
    print(f"Updating video timeseries data...")
    update_videos(VIEW_UPDATE_INTERVAL)
    print(f"Scanning new channels...")
    """
    for n in range(int(1/(5 / CHANNELS_FETCH))):
        scan_channels()
        n += 1
    """

# scheduler
scheduler = BackgroundScheduler()
trigger = CronTrigger(hour=10, minute=59)
scheduler.add_job(daily_scan, trigger)
scheduler.start()

app = FastAPI()

@app.get("/scan")
def scan():
    daily_scan()
    return {}

# Ensure the scheduler shuts down properly on application exit.
@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    scheduler.shutdown()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
