from pydantic import BaseModel, Field
from typing import Union
from datetime import datetime

class Views(BaseModel):
    views : int
    date : datetime

class Channel(BaseModel):
    name : str
    subscribers : int
    video_playlist : str
    cursor_pos : int

    def __str__(self):
        return f"Name: {self.name}, subscribers: {self.subscribers}, playlist_id: {self.video_playlist}"

class Video(BaseModel):
    id : str
    channel : Channel | None
    title : str
    views_timeseries : list[Views]
    thumbnail_url : str
    category : str
    blacklisted : Union[None, bool] = Field(default=None)
    duration : Union[None, str] = Field(default=None)

    @property
    def serialized_views(self):
        output = []
        for views in self.views_timeseries:
            output.append((views.views, views.date))
        return output
    