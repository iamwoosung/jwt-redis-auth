from fastapi import APIRouter, Depends, HTTPException

from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService, get_auth_service


router = APIRouter()

@router.post("/login", 
            response_model=TokenResponse,
            summary="로그인", 
            description="사용자 로그인 후 JWT 토큰을 발급합니다.", 
            responses={
                 409: {
                     "description": "인증 실패", 
                     "content": {
                         "application/json": {
                             "example": {
                                 "detail": "인증 실패"
                             }
                         }
                     }
                 }
             }
)
def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    user = auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="인증 실패", 
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token_data = auth_service.create_user_token(user)
    return token_data