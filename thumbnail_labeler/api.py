from typing import Union
from pydantic import BaseModel
import pandas as pd

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

#allow frontend to consume
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Thumbnail(BaseModel):
    url : str
    title : str
    id : str
    question : bool
    text : bool
    conflict : bool
    faces : str
    arrows : bool
    monochrony : bool
    juxtaposition : bool
    cliffhanger : bool
    reviewed : bool
    
@app.get("/items/{index}")
def get_thumbnail(index : int) -> Thumbnail:
    df = pd.read_pickle("data.pkl")
    return Thumbnail(**df.loc[index])

@app.post("/items/{index}")
def write_thumbnail(index: int, thumbnail : Thumbnail) -> None:
    df = pd.read_pickle("data.pkl")
    df.loc[index] = thumbnail.model_dump()
    df.to_pickle("data.pkl")
    print(f"Thumbnail written at {index}")
    return 
