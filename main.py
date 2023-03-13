from functools import lru_cache

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, BaseSettings

app = FastAPI(docs_url=None, redoc_url=None)


class Alert(BaseModel):
    status: str = "firing"
    receiver: str
    externalURL: str


class Settings(BaseSettings):
    env_name: str = "Local"
    kuma_url: str = "http://127.0.0.1:3001"
    kuma_tokens: list[str] = ["AAaaAaAaaa"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


@app.get("/", response_class=RedirectResponse, status_code=302)
def redirect():
    return "https://github.com/hadret/forwardly"


@app.post("/{token}")
def forward(am: Alerts, token: str, settings: Settings = Depends(get_settings)):
    if token in settings.kuma_tokens:
        kuma = requests.get(f"{settings.kuma_url}/{token}")
        return am, kuma.json()
    else:
        raise HTTPException(status_code=401, detail="Unauthorized”")
