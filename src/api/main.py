"""Entry point and main file for the FastAPI backend."""

from fastapi import FastAPI, HTTPException
from loguru import logger

from api.virgo_auth import SwiftAuthenticator
from api.config import get_settings
from api.routers import auth

logger.info("API starting")

app = FastAPI()

app.include_router(auth.router)

@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns:
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}


@app.get("/retrieve")
def retrieve_contents(env: str | None = None) -> dict[str, str]:
    pass