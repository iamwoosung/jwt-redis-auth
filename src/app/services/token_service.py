from app.core.redis_config import redis_client

TOKEN_BLACKLIST_PREFIX = "blacklist:"
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