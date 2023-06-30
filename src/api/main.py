"""Entry point and main file for the FastAPI backend."""
from fastapi import FastAPI
from loguru import logger

from api.auth import SwiftAuthenticator

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
async def auth() -> bool:
    """Authenticate a user against the Virgo DB.

    Returns:
        bool: Simple True/False if user was authenticated
    """
    authenticator = SwiftAuthenticator()
    return authenticator.authenticate()
