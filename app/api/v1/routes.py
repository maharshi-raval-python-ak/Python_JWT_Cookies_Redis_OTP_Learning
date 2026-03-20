from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import send_otp_email
from app.core.database import get_db
from app.dependencies import RoleChecker, get_current_user
from app.schemas.auth_schemas import UserData
from app.auth.auth_services import logout_service, register_service, login_service, refresh_token_service
from app.services.otp_services import create_otp, verify_otp_logic

router = APIRouter()


@router.post("/register")
def register(user: UserData, db: Session = Depends(get_db)):
    return register_service(db, user)


@router.post("/token")
def login(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db) 
):
    return login_service(form_data, db, response)

@router.post("/refresh")
def refresh_access_token(response: Response, refresh_token: str = Cookie(None), db: Session = Depends(get_db)):
    return refresh_token_service(refresh_token, db, response)

@router.get("/get_current_user", tags=["auth"])
def read_example(current_user: dict = Depends(get_current_user)):
    return {
        f"Hello, the current user is {current_user['name']} with id as {current_user['id']}, your roles are {current_user['roles']}"}


@router.get("/for_public", tags=["auth"], dependencies=[Depends(RoleChecker(["Public", "Editor", "Admin"]))])
def for_public():
    return {"Public, Editor, Admin": "Yes"}


@router.get("/for_editor", tags=["auth"], dependencies=[Depends(RoleChecker(["Editor", "Admin"]))])
def for_editor():
    return {"Editor, Admin": "Yes", "Public": "No"}

@router.get("/for_admin", tags=["auth"], dependencies=[Depends(RoleChecker(["Admin"]))])
def for_admin():
    return {"Admin": "Yes", "Editor, Public": "No"}

@router.post("/logout", tags=["auth"])
def logout(response: Response, refresh_token: str = Cookie(None),):
    return logout_service(response, refresh_token)


@router.post("/send-otp")
async def request_otp(email: str, background_tasks: BackgroundTasks):
    otp = create_otp(email)
    background_tasks.add_task(send_otp_email, email, otp)
    
    return {"message": "OTP has been sent to your email"}

@router.post("/verify-otp")
async def verify_otp(email: str, otp: str):
    is_valid = verify_otp_logic(email, otp)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid or expired OTP"
        )
    
    return {"message": "OTP verified successfully"}