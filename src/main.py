from typing import List
from fastapi import Depends, FastAPI, HTTPException
from app.apis import auth, user
from app.database import Base, engine
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from app.services.post_service import get_post_service, PostService

app = FastAPI(
    title="FastAPI NCP Mailing Service",
    description="게시판, NCP 메일 발송 기능 제공 서비스", 
    version="1.0.0",
    # 스웨거 URL
    docs_url="/docs", 
    redoc_url="/redoc"
)

app.include_router(user.router, tags=["user"])
app.include_router(auth.router, tags=["auth"])

@app.get("/")
def health_check():
    return {"status": "ok"}

@app.get("/ping")
async def ping_db():
    try:
        with engine.connect() as conn:
            return {"status": "connected"}
    except Exception as e:
        return {"status":"error", "message": str(e)}
    
@app.on_event("startup")
def init_db():
    Base.metadata.create_all(bind=engine)

# 게시글 생성
@app.post(
        "/posts", 
        response_model=PostResponse, 
        summary="새 게시글 생성", 
        description="새로운 게시글을 생성합니다."
        )
def create_post(post: PostCreate, post_service: PostService = Depends(get_post_service)):
    create_post = post_service.create_post(post)
    return create_post

@app.get(
        "/posts/", 
        response_model=List[PostResponse],
        summary="게시글 리스트 조회", 
        description="게시글 리스트를 조회합니다.", 
        responses={
            404: {
                "description": "게시글 조회 실패", 
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "게시글을 찾을 수 없습니다."
                        }
                    }
                }
            }
        }
)
def get_posts(post_service: PostService = Depends(get_post_service)):
    posts = post_service.get_posts()

    if posts is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return posts


# 게시글 상세 조회
@app.get(
        "/posts/{post_id}", 
        response_model=PostResponse, 
        summary="게시글 상세 조회", 
        description="게시글 상세 정보를 조회합니다."
        )
def get_post(post_id: int, post_service: PostService = Depends(get_post_service)):
    post = post_service.get_post(post_id)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return post


# 게시글 수정
@app.put(
        "/posts/{post_id}", 
        response_model=PostResponse, 
        summary="게시글 수정", 
        description="게시글 정보를 수정합니다."
        )
def update_post(post_id: int, post_update: PostUpdate, post_service: PostService = Depends(get_post_service)):
    post = post_service.update_post(post_id, post_update)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return post

# 게시글 삭제
@app.delete(
        "/posts/{post_id}", 
        response_model=dict,
        summary="게시글 삭제", 
        description="게시글을 삭제합니다."
        )
def delete_post(post_id:int, post_service: PostService = Depends(get_post_service)): 
    post = post_service.delete_post(post_id)
    if post is False:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.") 
    return {"message": "게시글이 성공적으로 삭제되었습니다."}