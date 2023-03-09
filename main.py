from functools import lru_cache

import requests
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, BaseSettings

app = FastAPI(docs_url=None, redoc_url=None)


class Alert(BaseModel):
    status: str = "firing"
    receiver: str
    externalURL: str


class Settings(BaseSettings):
    env_name: str = "Local"
    base_url: str = "http://127.0.0.1:8000"
    base_uuid: str = "00000000-0000-0000-0000-000000000000"
    kuma_url: str = "http://127.0.0.1:3001"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


@app.post("/{uuid}")
def forward(uuid: str, settings: Settings = Depends(get_settings)):
    if uuid == settings.base_uuid:
        kuma = requests.get(settings.kuma_url)
        return kuma.json()
    else:
        raise HTTPException(status_code=404, detail="Wrong API key!")
