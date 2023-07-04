"""Entry point and main file for the FastAPI backend."""

from fastapi import Depends, FastAPI
from loguru import logger

from api.auth import SwiftAuthenticator
from api.config import Settings, get_settings

logger.info("API starting")

app = FastAPI()


@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns:
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}


@app.get("/auth")
async def auth(settings: Settings = Depends(get_settings)) -> int:
    """Authenticate a user against the Virgo DB.

    Returns:
        int: HTTP status code denoting if user was authenticated
    """
    authenticator = SwiftAuthenticator(settings)
    return authenticator.authenticate()
