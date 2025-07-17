from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.services.token_service import TokenService
from app.utils.auth import verify_token

bearer_schema = HTTPBearer()

def get_current_user(credential: HTTPAuthorizationCredentials = Depends(bearer_schema), db: Session = Depends(get_db)):
    token = credential.credentials

    if TokenService.is_token_blacklisted(token):
        raise HTTPException(
            status_code=401, 
            detail="만료된 토큰입니다.", 
            headers={"WWW-Authenticate": "Bearer"}
        )

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="인증되지 않은 사용자입니다.", 
            headers={"WWW-Authenticate": "Bearer"},
        )

    query = (
        select(User)
        .where(User.username == username)
    )
    user = db.execute(query).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="사용자를 찾을 수 없습니다.", 
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user