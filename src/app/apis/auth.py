from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.services.auth_service import AuthService, get_auth_service
from app.services.token_service import TokenService
from app.utils.auth import get_token_expiry, verify_token


router = APIRouter()
bearer_scheme = HTTPBearer()

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

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    token_expiry = get_token_expiry(token)
    #print(token_expiry)
    #print("------------")
    TokenService.blacklist_token(token, token_expiry)

    return {"message": "로그아웃"}

@router.post(
    "/refresh",
    response_model=TokenResponse
)
def refresh_token(refresh_token: RefreshRequest, auth_service: AuthService = Depends(get_auth_service)):
    token = auth_service.refresh_access_token(refresh_token.refresh_token)

    if not token:
        raise HTTPException(
            status_code=401,
            detail="사용자 접근이 유효하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token["refresh_token"] = refresh_token.refresh_token
    return token

# TODO: 전체 로그아웃 시험 필요함
@router.post(
    "/logout-all",
)
def logout_all_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    token_expiry = get_token_expiry(token)
    TokenService.blacklist_token(token, token_expiry)

    user_id = verify_token(token).get("user_id")
    TokenService.remove_refresh_token(user_id)

    return {"message": "모든 기기로부터 로그아웃되었습니다."}