# mypy: disable-error-code="call-arg"
"""Module to define the main settings class for the API."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Class to store typed settings via Pydantic."""

    db_url: str = "http://virgodb.dur.ac.uk:8080/Eagle/"
    jwt_secret_key: SecretStr

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
