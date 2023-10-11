"""Entry point and main file for the FastAPI backend."""

from fastapi import FastAPI, HTTPException, status, Depends, Form
from loguru import logger

from api.routers import file_processing
from .virgo_auth import SwiftAuthenticator,AuthRequest
from fastapi.security import OAuth2PasswordBearer

logger.info("API starting")

app = FastAPI()

app.include_router(file_processing.router)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns
    -------
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}


def get_authenticator():
    return SwiftAuthenticator()

@app.post("/auth", status_code=status.HTTP_200_OK)
async def authenticate(authenticator: SwiftAuthenticator = Depends(get_authenticator)):
    
    is_authenticated = authenticator.authenticate(AuthRequest)
    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"message": "Authenticated successfully"}

@app.post('/token')
async def get_token(username: str = Form(...), password: str = Form(...), authenticator: SwiftAuthenticator = Depends(get_authenticator)):
    token = authenticator.generate_token(username, )
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"access_token": token, "token_type": "bearer"}