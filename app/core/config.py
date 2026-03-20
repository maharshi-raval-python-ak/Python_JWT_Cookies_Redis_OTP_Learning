from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType, NameEmail
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()
from pydantic import SecretStr

class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL : str
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES : int
    REFRESH_TOKEN_EXPIRE_MINUTES : int
    ENCRYPTION_ALGO : str
    
    model_config = SettingsConfigDict(env_file=".env")
    
settings = Settings(**{})


conf = ConnectionConfig(
    MAIL_USERNAME="maharshi.raval@armakuni.com",
    MAIL_PASSWORD=SecretStr("jjvkxkihuycqpzcd"),
    MAIL_FROM="maharshi.raval@armakuni.com", 
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

async def send_otp_email(email: str, otp: str):
    recipient = NameEmail(name="User", email=email) 

    message = MessageSchema(
        subject="Your Verification Code",
        recipients=[recipient],
        body=f"Your OTP is <b>{otp}</b>. It expires in 5 minutes.",
        subtype=MessageType.html 
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)