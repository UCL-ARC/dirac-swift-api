"""Entry point and main file for the FastAPI backend."""
from fastapi import APIRouter, FastAPI
from loguru import logger

logger.info("API starting")

app = FastAPI()

# Define a mock router for testing
mock_router = APIRouter(
    prefix="/mock",
)

# Include the mock router in the main router
app.include_router(mock_router)


@app.get("/ping")
def ping() -> dict[str, str]:
    """Define an API route for testing purposes.

    Returns:
        dict[str, str]: Some example content
    """
    return {"ping": "pong"}
