from datetime import datetime
from functools import lru_cache

import requests
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, BaseSettings

app = FastAPI(docs_url=None, redoc_url=None)


class Labels(BaseModel):
    alertname: str
    prometheus: str | None = None
    severity: str | None = None


class Annotations(BaseModel):
    description: str
    runbook_url: str
    summary: str


class SingleAlert(BaseModel):
    status: str
    labels: Labels
    annotations: Annotations
    startsAt: datetime | None = None
    endsAt: datetime | None = None
    generatorURL: str
    fingerprint: str | None = None


class Alerts(BaseModel):
    receiver: str
    status: str
    alerts: list[SingleAlert]
    groupLabels: Labels
    commonLabels: Labels
    commonAnnotations: Annotations
    externalURL: str
    version: int
    groupKey: str
    truncatedAlerts: int | None = None


class Settings(BaseSettings):
    env_name: str = "Local"
    kuma_url: str = "http://127.0.0.1:3001"
    kuma_tokens: list[str] = ["AAaaAaAaaa"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()


# Incoming alerts debugging (POST request body printing)
# NOTE: Need Request in fastapi import
# @app.post("/{token}")
# async def inspect(token: str, r: Request, s: Settings = Depends(get_settings)):
#     body = await r.json()
#     print(body)
#     return body


@app.get("/", response_class=RedirectResponse, status_code=302)
def redirect():
    return "https://github.com/hadret/forwardly"


@app.post("/{token}")
def forward(am: Alerts, token: str, settings: Settings = Depends(get_settings)):
    if token in settings.kuma_tokens:
        kuma = requests.get(f"{settings.kuma_url}/{token}")
        return am, kuma.json()
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
