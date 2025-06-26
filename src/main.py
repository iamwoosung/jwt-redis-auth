from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from app.database import Base, engine, get_db
from app.models.post import Post
from app.schemas.post import PostResponse, PostCreate, PostUpdate
from sqlalchemy.orm import Session

app = FastAPI(
    title="FastAPI NCP Mailing Service",
    description="게시판, NCP 메일 발송 기능 제공 서비스", 
    version="1.0.0",
    # 스웨거 URL
    docs_url="/docs", 
    redoc_url="/redoc"
)

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
def create_post(post: PostCreate, db: Session=Depends(get_db)):
    created_post = Post(**post.model_dump())
    db.commit()
    db.refresh(created_post)

    return created_post

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
def get_posts(db: Session=Depends(get_db)):
    query = (
        select(Post). 
        order_by(Post.create_at.desc())
    )
    posts = db.execute(query).scalar().all()

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
def get_post(post_id: int, db: Session=Depends(get_db)):
    query = (
        select(Post). 
        where(Post.id==post_id)
    )
    post = db.execute(query).scalar_one_or_none()

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
def update_post(post_id: int, post_update: PostUpdate, db: Session=Depends(get_db)):
    query = (
        select(Post).
        where(Post.id==post_id)
    )
    post = db.execute(query).scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    update_dict = {
            key: value
            for key, value in post_update.model_dump().items()
            if value is not None   
        }
    
    for key, value in update_dict.items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)
    return post

# 게시글 삭제
@app.delete(
        "/posts/{post_id}", 
        response_model=dict,
        summary="게시글 삭제", 
        description="게시글을 삭제합니다."
        )
def delete_post(post_id: int, db:Session=Depends(get_db)):
    query = (
        select(Post). 
        where(Post.id==post_id)
    )
    post = db.execute(query).scalar_one_or_none()
