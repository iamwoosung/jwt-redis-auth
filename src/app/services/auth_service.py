from datetime import timedelta
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.services.token_service import TokenService
from app.utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token
from app.utils.security import verify_password


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, login_data: LoginRequest):
        query = (
            select(User).
            where(User.email == login_data.email)
        )

        user = self.db.execute(query).scalar_one_or_none()

        if not user or not verify_password(login_data.password, user.password):
            return None 
        
        return user
    
    def create_user_token(self, user: User):
        token_data = {
            "username": user.username, 
            "email": user.email, 
            "user_id": user.id
        }

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = create_access_token(
            data=token_data, 
            expires_delta=access_token_expires
        )

        refresh_token = create_refresh_token(
            data=token_data
        )

        TokenService.store_refresh_token(user.id, refresh_token)

        return {
            "access_token": access_token, 
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str):
        payload = verify_password(refresh_token)
        
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        if not user_id:
            return None 
        
        is_valid = TokenService.validate_refresh_token(user_id, refresh_token)
        if not is_valid:
            return None
        
        query=(
            select(User).
            where(User.id == user_id)
        )

        user = self.db.execute(query).scalar_one_or_none()

        if not user:
            return None
        
        token_data = {
            "username": user.username, 
            "email": user.email, 
            "user_id": user.id
        }

        access_token = create_access_token(token_data)
        return {
            "access_token": access_token, 
            "token_type": "bearer",
        }
    
def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)