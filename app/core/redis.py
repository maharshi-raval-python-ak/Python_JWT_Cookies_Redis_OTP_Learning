import redis
from app.core.config import settings

redis_client = redis.Redis(
    host="localhost", 
    port=6379, 
    db=0, 
    decode_responses=True
)
