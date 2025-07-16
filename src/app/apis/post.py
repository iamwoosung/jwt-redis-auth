from typing import List
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.post import PostCreate, PostResponse, PostUpdate
from app.services.post_service import PostService, get_post_service


router = APIRouter()

# 게시글 생성
@router.post(
        "/posts", 
        response_model=PostResponse, 
        summary="새 게시글 생성", 
        description="새로운 게시글을 생성합니다."
        )
def create_post(
    post: PostCreate, 
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user)
    ):
    create_post = post_service.create_post(post, current_user)
    return create_post

@router.get(
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
@router.get(
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
@router.put(
        "/posts/{post_id}", 
        response_model=PostResponse, 
        summary="게시글 수정", 
        description="게시글 정보를 수정합니다."
        )
def update_post(
    post_id: int, 
    post_update: PostUpdate, 
    post_service: PostService = Depends(get_post_service),
    current_user: User = Depends(get_current_user)
    ):
    post = post_service.update_post(post_id, post_update, current_user)

    if post is None:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    return post

# 게시글 삭제
@router.delete(
        "/posts/{post_id}", 
        response_model=dict,
        summary="게시글 삭제", 
        description="게시글을 삭제합니다."
        )
def delete_post(
    post_id:int, 
    post_service: PostService = Depends(get_post_service), 
    current_user: User = Depends(get_current_user)
    ): 
    post = post_service.delete_post(post_id, current_user)
    if post is False:
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.") 
    return {"message": "게시글이 성공적으로 삭제되었습니다."}