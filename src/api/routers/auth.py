from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, Form
from loguru import logger

from ..virgo_auth import SwiftAuthenticator,AuthRequest
from fastapi.security import OAuth2PasswordBearer

logger.info("API starting")

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

def get_authenticator():
    return SwiftAuthenticator()

@router.post("/auth", status_code=status.HTTP_200_OK)
async def authenticate(authenticator: SwiftAuthenticator = Depends(get_authenticator())):
    """
    Authenticate a user.
    
    Args:
    auth_request: An object containing `username` and `password` fields
    
    Returns:
    - A JSON object containing a message indicating the success or failure of the authentication.
    """
    is_authenticated = authenticator.authenticate(AuthRequest)
    if not is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"message": "Authenticated successfully"}

@router.post('/token')
async def get_token(username: str = Form(...), password: str = Form(...), authenticator: SwiftAuthenticator = Depends(get_authenticator)):
    """
    Issues a JWT token after validating the user's credentials.
    
    Args:
        username (str)
        password (str)
        authenticator (SwiftAuthenticator)

    Returns:
        dict: A JSON object containing the issued JWT token.
        
    Raises:
        HTTPException: An HTTP status code 401 (Unauthorized) if authentication fails.
    """
    token = authenticator.generate_token(username, password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    return {"access_token": token, "token_type": "bearer"}