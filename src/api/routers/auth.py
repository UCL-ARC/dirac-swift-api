"""Authentication module.

Handles token based authentication.
"""
from functools import lru_cache

import jwt
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from pydantic import BaseModel

from api.config import Settings
from api.virgo_auth import SwiftAuthenticator

bearer_scheme = HTTPBearer()


@lru_cache
def get_settings() -> Settings:
    """Retrieve an instance of the Settings object.

    Required by FastAPI when used with Depends.

    Returns
    -------
        Settings: Settings object
    """
    return Settings()


router = APIRouter()


class TokenRequest(BaseModel):
    """Pydantic model for token requests.

    Args:
        BaseModel (BaseModel): Pydantic BaseModel
    """

    username: str
    password: str


class CredentialsException(HTTPException):
    """Custom exception for credential errors."""

    def __init__(self, status_code: int, detail: str | None = None):
        """Class constructor.

        Args:
            status_code (int): HTTP status code
            detail (str | None, optional): Error description. Defaults to None.
        """
        if not detail:
            detail = "Error validating credentials."
        headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code, detail=detail, headers=headers)


def decode_jwt(token: str, settings: Settings) -> str:
    """Decode a JWT token.

    Args:
        token (str, optional): JWT token provided by user.
        settings (Settings): Settings object containing JWT the secret key used to encode the token.

    Raises
    ------
        CredentialsException: For invalid users, expired tokens or invalid tokens.

    Returns
    -------
        str: Username of authenticated user
    """
    try:
        payload = jwt.decode(
            str(token),
            settings.jwt_secret_key.get_secret_value(),
            algorithms=["HS256"],
        )
        user = payload.get("sub")
        if not user:
            raise CredentialsException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username/password",
            )
        return user
    except jwt.ExpiredSignatureError as error:
        raise CredentialsException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="JWT token has expired",
        ) from error
    except jwt.InvalidTokenError as error:
        raise CredentialsException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid JWT token",
        ) from error


def get_authenticated_user(
    authorisation: HTTPAuthorizationCredentials = Security(bearer_scheme),
    settings: Settings = get_settings(),
) -> str:
    """Check whether a current user is authenticated.

    Returns a username if so.

    Args:
        authorisation (HTTPAuthorizationCredentials, optional):
            HTTPAuthorizationCredentials data model. Defaults to Security(bearer_scheme).
        settings (Settings, optional): Pydantic Settings object. Defaults to get_settings().

    Raises
    ------
        CredentialsException: Raised if no token provided with request.

    Returns
    -------
        str: Username on successful authentication.
    """
    if not authorisation or not authorisation.credentials:
        raise CredentialsException(
            status_code=401,
            detail="No token provided with request.",
        )
    logger.warning(f"Received token: {authorisation.credentials}")
    return decode_jwt(authorisation.credentials, settings)


@router.post("/token")
def generate_token(
    request: TokenRequest,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Generate a JWT token for a user on successful VirgoDB authentication.

    Args:
        request (TokenRequest): Pydantic model for a token request
        db_url (str, optional):
            Database URL, defined in settings. Defaults to Depends(get_settings).

    Returns
    -------
        dict: Dictionary containing the access token.
    """
    swift_authenticator = SwiftAuthenticator(
        request.username,
        request.password,
        settings,
    )

    token = swift_authenticator.authenticate_and_generate_jwt()
    return {"access_token": token}


@router.get("/protected/")
def protected_endpoint(current_user: str = Depends(get_authenticated_user)):
    """Return a username after requiring a Bearer token.

    Args:
        current_user (str, optional):
            Returns the current authenticated user, if there is one.
            Defaults to Depends(get_authenticated_user).

    Returns
    -------
        dict:
            Information about current authenticated user, or lack of authorisation.
    """
    return {"User": current_user}


@router.get("/unprotected/")
def unprotected_endpoint():
    """Return some text to display an example unauthenticated endpoint.

    Returns
    -------
        dict:
            Text displaying unprotected status, we do not check current user information.
    """
    return {"User": "unauthenticated"}
