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
async def retrieve_contents(env: str | None = None) -> dict[str, str]:
    """This needs to be a route that will retrieve the processed contents
    of some HDF5 file on the system

    We'll already be authenticated at this point
    This route should just fetch the contents of some async function that does 
    the actual heavy lifting.
    

    Args:
        env (str | None, optional): _description_. Defaults to None.

    Returns:
        dict[str, str]: _description_
    """
    pass