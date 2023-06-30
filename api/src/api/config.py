# mypy: disable-error-code="call-arg"
"""Module to define the main settings class for the API."""
from pydantic import BaseSettings, SecretStr


class Settings(BaseSettings):
    """Class to store typed settings via Pydantic."""

    username: str
    password: SecretStr
    db_url: str

    class Config:
        """Class to set environment variable prefix for pydantic."""

        env_prefix = "virgo_"


def get_settings() -> Settings:
    """Allows lazy loading of Settings.

    Enables testing without environment variables.

    Returns:
        Settings: Class containing VirgoDB username and password
    """
    return Settings()