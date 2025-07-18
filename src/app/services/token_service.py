from datetime import timedelta
from app.core.redis_config import redis_client

TOKEN_BLACKLIST_PREFIX = "blacklist:"
REFRESH_TOKEN_PREFIX = "refresh:"
DEFAULT_TOKEN_EXPIRY = 60 * 30

class TokenService:
    @classmethod
    def blacklist_token(cls, token:str, expires_in: int=DEFAULT_TOKEN_EXPIRY):
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        redis_client.set(key, "1", ex=expires_in)

        return True
    
    @classmethod
    def is_token_blacklisted(cls, token:str) -> bool:
        key = f"{TOKEN_BLACKLIST_PREFIX}{token}"
        return redis_client.exists(key) == 1
    
    @classmethod
    def store_refresh_token(cls, user_id:int, refresh_token:str):
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"

        with redis_client.pipeline() as pipe:
            pipe.sadd(user_key, refresh_token)
            expire_seconds = int(timedelta(days=REFRESH_TOKEN_PREFIX + 1).total_seconds())
            pipe.expire(user_key, expire_seconds)
            pipe.execute()
        return True
    
    @classmethod
    def validate_refresh_token(cls, user_id:int, refresh_token:str) -> bool:
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        return redis_client.sismember(user_key, refresh_token)
    
    @classmethod
    def remove_refresh_token(cls, user_id:int, refresh_token:str = None):
        user_key = f"{REFRESH_TOKEN_PREFIX}{user_id}"
        
        if refresh_token:
            redis_client.srem(user_key, refresh_token)
        else:
            redis_client.delete(user_key)
        return True