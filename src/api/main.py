"""Entry point and main file for the FastAPI backend."""

from fastapi import FastAPI
from loguru import logger

from api.routers import auth, file_processing

logger.info("API starting")

app = FastAPI()

app.include_router(file_processing.router)
app.include_router(auth.router)


@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns
    -------
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}
