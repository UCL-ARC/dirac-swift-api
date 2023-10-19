"""Entry point and main file for the FastAPI backend."""

from importlib import metadata

import uvicorn
from fastapi import FastAPI
from loguru import logger

from api.routers import auth, file_processing

logger.info("API starting")

description = """
SWIFTsimIO API provides read-only access to SWIFT data via HTTP requests.

Authenticated users can access

* Masked data
* Unmasked data
* Metadata
* Units

Users must have existing access to [VirgoDB](https://virgodb.dur.ac.uk/)
"""

app = FastAPI(
    title="SWIFTsimIO API",
    description=description,
    version=metadata.version("dirac-swift-api"),
)

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


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
