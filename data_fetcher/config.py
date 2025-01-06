from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
import json

load_dotenv("../")

API_KEY = json.loads(os.environ.get("API_KEY"))
OUTPUT_PATH : str = "data_fetcher/data/videos.pkl"
CSV_OUTPUT_PATH : str = "data_fetcher/data/videos.csv"
BACKUP_PATH : str = f"data_fetcher/data/backup/videos-{datetime.today().toordinal()}.pkl"
CHANNELS_PATH : str = "data_fetcher/data/df_channels_shuffled.tsv"
STATE_PATH : str = "data_fetcher/data/state.json"

CHANNELS_FETCH : int = 5000 # number of channels to fetch with each scan
DATE_TARGET : datetime = datetime.now(timezone.utc).date() - timedelta(days=1) #date to scan videos from
VIEW_UPDATE_INTERVAL : int = 1 # interval in days to update views of monitored videos