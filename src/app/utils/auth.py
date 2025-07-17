
from datetime import datetime, timedelta
import time
from typing import Optional
from jose import jwt, JWTError


SECRET_KEY = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    user_id = data["user_id"]
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    refresh_payload = {
        "user_id": user_id, 
        "exp": expire, 
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
def get_token_expiry(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = payload.get("exp")

        if exp:
            remaining = exp - time.time()
            return max(int(remaining), 1)
    except:
        pass
    return ACCESS_TOKEN_EXPIRE_MINUTES * 60