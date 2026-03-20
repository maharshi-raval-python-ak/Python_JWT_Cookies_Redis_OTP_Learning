import random
from app.core.redis import redis_client

def create_otp(email: str) -> str:
    otp = str(random.randint(100000, 999999))
    redis_client.setex(name=email, time=300, value=otp) 
    
    return otp

def verify_otp_logic(email: str, user_otp: str) -> bool:
    stored_otp = redis_client.get(email)
    
    if stored_otp == user_otp:
        redis_client.delete(email)
        return True
    return False
