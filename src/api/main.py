"""Entry point and main file for the FastAPI backend."""

from fastapi import FastAPI, HTTPException
from loguru import logger

from api.auth import SwiftAuthenticator
from api.config import get_settings

logger.info("API starting")

app = FastAPI()


@app.get("/ping")
async def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns:
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}


@app.post("/auth")
def auth(env: str | None = None) -> dict[str, str]:
    """Authenticate a user against the Virgo DB.

    Args:
        settings (Settings, optional): Pydantic settings object.

    Raises:
        HTTPException: Raise a 422 Unprocessable Entity code if
            the settings objects does not return successfully.

    Returns:
        dict[str, str]: HTTP status code denoting if user was authenticated
    """
    if env == "test":
        settings = get_settings(_env_file="tests/data/.env.test")
    else:
        settings = get_settings()

    if "missing" in list(settings.__dict__.values()):
        missing_values = [
            field
            for field in settings.__dict__
            if settings.__dict__[field] == "missing"
        ]
        error_message = f"Missing fields for authentication: {missing_values}"
        raise HTTPException(status_code=422, detail=error_message)

    authenticator = SwiftAuthenticator(settings)
    return {"auth_result_status": str(authenticator.authenticate())}
