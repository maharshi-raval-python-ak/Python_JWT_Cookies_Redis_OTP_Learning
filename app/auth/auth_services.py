from datetime import datetime
from fastapi import  HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.auth.auth_utils import create_access_token, create_refresh_token, get_password_hash, verify_password
from app.crud import user_auth_crud
from app.models.refresh_token_model import RefreshToken
from app.schemas.auth_schemas import UserData

def authenticate_user(name: str, password: str, db: Session):
    user = user_auth_crud.get_by_name(db, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def register_service(db: Session, user: UserData):
    hashed_password = get_password_hash(user.password)
    user_in_db = user_auth_crud.get_by_name(db, user.name)
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Username already taken."
        )
    user_auth_crud.create(db, user.name, hashed_password, user.roles)
    return user


def login_service(form_data: OAuth2PasswordRequestForm, db: Session, response: Response):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User not registered"
        )
    token_data = {"sub": str(user.id), "name": user.name, "roles": user.roles}
    generated_token = create_access_token(token_data)
    generated_refresh_token = create_refresh_token(token_data)
    new_db_refresh_token = RefreshToken(
        token=generated_refresh_token,
        user_id=user.id
    )
    db.add(new_db_refresh_token)
    db.commit()
    db.refresh(new_db_refresh_token)
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {generated_token}",
        httponly=True,
        secure=False, #set true when deploying
        samesite="lax", #set strict for preventing cross site attacks
        max_age=30
    )
    response.set_cookie(
        key="refresh_token",
        value=generated_refresh_token,
        httponly=True,
        secure=False, #set true when deploying
        samesite="lax", #set strict for preventing cross site attacks
        max_age=10000
    )
    
    return {
        "message": "Logged in successfully",
        "token_type": "bearer"
    }

def refresh_token_service(refresh_token: str, db: Session, response: Response):
    db_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    
    if not db_token or db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    if db_token.is_revoked:
        db.query(RefreshToken).filter(RefreshToken.family_id == db_token.family_id).update({"is_revoked": True})
        db.commit()
        raise HTTPException(status_code=401, detail="Token reuse detected. All sessions revoked.")

    db_token.is_revoked = True 
    
    user = db_token.user 
    user_data = {
        "sub": str(user.id), 
        "roles": user.roles
    }
    
    new_access = create_access_token(data=user_data)
    new_refresh = create_refresh_token(data=user_data)
    
    new_db_token = RefreshToken(
        token=new_refresh,
        user_id=db_token.user_id,
        family_id=db_token.family_id,
    )
    
    db.add(new_db_token)
    db.commit()
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {new_access}",
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=30 
    )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=10000
    )
    
    return {
        "message": "Tokens refreshed successfully",
        "token_type": "bearer"
    }
    
def logout_service(response: Response, refresh_token):
    if not refresh_token:
        return {"message": "Already Logged out."}
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}
