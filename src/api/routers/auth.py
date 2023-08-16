from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Annotated, Any

from datetime import timedelta, datetime
from jose import jwt, JWTError

from loguru import logger

from api.config import get_settings
from api.virgo_auth import SwiftAuthenticator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
settings = get_settings()

router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class CredentialsException(HTTPException):
    def __init__(self, status_code: int, detail: str | None = None):
        if not detail:
            detail = "Error validating credentials."
        headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(status_code, detail = detail, headers = headers)


def authenticate_user(username: str, password: str, db_url: str) -> dict[str, str]:
    """Authenticate a user against the Virgo DB.

    Args:
        settings (Settings, optional): Pydantic settings object.

    Raises:
        HTTPException: Raise a 422 Unprocessable Entity code if
            the settings objects does not return successfully.

    Returns:
        dict[str, str]: HTTP status code denoting if user was authenticated
    """
   
    authenticator = SwiftAuthenticator(username, password, db_url)
    return {"status_code": str(authenticator.authenticate())}

class JWTBearer(HTTPBearer):
    def __init__(self):
        super().__init__()
    
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise CredentialsException(status_code=status.HTTP_400_BAD_REQUEST)
            if not self.verify_jwt(credentials.credentials):
                raise CredentialsException(status_code=status.HTTP_401_UNAUTHORIZED)
            return credentials.credentials
        else:
            raise CredentialsException(status_code=status.HTTP_403_FORBIDDEN)
        

    def verify_jwt(self, token: str) -> bool:
        token_is_valid = False
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms = [settings.algorithm])
            username = payload.get("sub")

            if username is None:
                raise CredentialsException(status.HTTP_401_UNAUTHORIZED)
            token_is_valid = True
        except JWTError:
            payload = None
            raise CredentialsException(status.HTTP_401_UNAUTHORIZED)

        return token_is_valid

def create_access_token(data: dict, secret_key: str, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=settings.algorithm)
    return encoded_jwt

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    username = form_data.username
    password = form_data.password

    if "missing" in list(settings.__dict__.values()):
        missing_values = [
            field
            for field in settings.__dict__
            if settings.__dict__[field] == "missing"
        ]
        error_message = f"Missing fields for authentication: {missing_values}"
        raise HTTPException(status_code=422, detail=error_message)
    
    auth_result = authenticate_user(username, password, settings.db_url)
    logger.info(f"{auth_result=}")

    if int(auth_result["status_code"]) != status.HTTP_200_OK:
        raise HTTPException(status_code=401, detail="Authentication failed")
    

    token_expiry = timedelta(minutes=settings.access_token_expiry_mins)
    access_token = create_access_token(
        data = {"sub": username}, secret_key = settings.secret_key, expires_delta = token_expiry
    )
    logger.info(f"{access_token=}")
    return access_token

@router.get("/me", dependencies=[Depends(JWTBearer())])
async def get_my_details():
    return {
        "data": "A test user"
    }
