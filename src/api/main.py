"""Entry point and main file for the FastAPI backend."""

from fastapi import FastAPI, HTTPException, status, Depends, Form
from loguru import logger

from api.routers import file_processing, auth
from fastapi.security import OAuth2PasswordBearer


logger.info("API starting")

app = FastAPI()

app.include_router(file_processing.router)
app.include_router(auth.router)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns
    -------
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}


