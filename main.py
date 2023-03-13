from datetime import datetime
from functools import lru_cache

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, BaseSettings

app = FastAPI(docs_url=None, redoc_url=None)


class Labels(BaseModel):
    alertname: str | None = None
    dc: str | None = None
    instance: str | None = None
    job: str | None = None


class Annotations(BaseModel):
    description: str | None = None


class SingleAlert(BaseModel):
    annotations: Annotations | None = None
    labels: Labels | None = None
    status: str | None = None
    generatorURL: str | None
    startsAt: datetime | None = None
    endsAt: datetime | None = None


class Alerts(BaseModel):
    receiver: str | None = None
    status: str | None = None
    alerts: list[SingleAlert] | None = None
    groupLabels: Labels | None = None
    commonLabels: Labels | None = None
    commonAnnotations: Annotations | None = None
    externalURL: str | None = None
    version: int | None = None
    groupKey: str | None = None


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
