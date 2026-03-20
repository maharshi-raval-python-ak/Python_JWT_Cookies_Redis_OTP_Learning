from typing import Annotated, Optional

from fastapi.security import OAuth2PasswordBearer
from fastapi import Cookie, HTTPException, Depends, status
import jwt
from jose import JWTError
from app.core.config import settings
from app.models.auth_user import UserAuth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def get_current_user(access_token_cookie: Annotated[Optional[str], Cookie(alias="access_token")] = None, access_token_header: Annotated[Optional[str], Depends(oauth2_scheme)] = None):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = access_token_cookie or access_token_header

    if not token:
        raise credentials_exception

    try:
        # Strip "Bearer " if it's coming from your Cookie 00(Swagger's OAuth2 scheme strips it automatically for the header)
        if token.startswith("Bearer "):
            token = token.replace("Bearer ", "")

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        return {
            "id": int(user_id), 
            "name": payload.get("name"), 
            "roles": payload.get("roles")
        }
        
    except (JWTError, Exception):
        raise credentials_exception

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
        
    def __call__(self, user: UserAuth = Depends(get_current_user)):
        if not any(role in self.allowed_roles for role in user["roles"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have the required permissions")
        return user
    