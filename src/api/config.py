# mypy: disable-error-code="call-arg"
"""Module to define the main settings class for the API."""

from loguru import logger
from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Class to store typed settings via Pydantic."""

    username: str
    password: SecretStr
    db_url: str

    class Config:
        """Class to set environment variable prefix for pydantic."""

        env_prefix = "virgo_"
        env_file = ".env"


def get_settings() -> Settings:
    """Allows lazy loading of Settings.

    Enables testing without environment variables.


    Returns:
        Settings: Settings object containing VirgoDB
            username, password and DB url. If settings fails to load,
            returns a Settings object showing missing fields.
    """
    try:
        return Settings()
    except ValidationError as error:
        errors_dict = error.errors()
        errors_msg = {}

        for error_dict in errors_dict:
            error_field = str(error_dict["loc"][0])
            error_type = str(error_dict["type"].split(".")[-1])
            error_msg = {error_field: error_type}
            errors_msg.update(error_msg)

        error_settings = Settings(username="", password="", db_url="")

        possible_missing_attributes = list(error_settings.__dict__.keys())

        for error_type in list(errors_msg.keys()):
            if str(error_type) in possible_missing_attributes:
                error_settings.__dict__[str(error_type)] = "missing"

        logger.error(
            f"Validation error on settings load. Missing {list(errors_msg.keys())}.",
        )
        return error_settings
