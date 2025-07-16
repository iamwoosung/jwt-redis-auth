from sqlalchemy import select

from fastapi import Depends, HTTPException
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.post import Post
from app.schemas.post import PostCreate

class PostService:
    def __init__(self, db: Session):
        self.db = db

    """
    게시글 생성
    """
    def create_post(self, post: PostCreate, user: User):


        created_post = Post(**post.model_dump())
        
        author_id = user.id
        created_post.author_id = author_id
        
        self.db.add(created_post)
        self.db.commit()
        self.db.refresh(created_post)

        return created_post
    

    """
    전체 게시글 조회
    """
    def get_posts(self):
        query = (
            select(Post). 
            order_by(Post.create_at.desc())
        )
        posts = self.db.execute(query).scalars().all()

        return posts
    
    """
    특정 게시글 조회
    """
    def get_post(self, post_id: int):
        
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        return post
    
    """
    게시글 수정
    작성자만 수정 가능
    """
    def update_post(self, post_id: int, post_update: PostUpdate, user: User):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return None
        
        if post.author_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="접근 권한이 없습니다."
            )
        
        update_dict = {
            key: value
            for key, value in post_update.model_dump().items()
            if value is not None
        }

        for key, value in update_dict.items():
            setattr(post, key, value)

        self.db.commit()
        self.db.refresh(post)

        return post
    
    """
    게시글 삭제
    작성자만 삭제 가능
    """
    def delete_post(self, post_id: int, user: User):
        query = (
            select(Post).
            where(Post.id == post_id)
        )
        post = self.db.execute(query).scalar_one_or_none()

        if post is None:
            return False
        
        if post.author_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="접근 권한이 없습니다."
            )
        
        self.db.delete(post)
        self.db.commit()

        return True

def get_post_service(db: Session = Depends(get_db)):
    return PostService(db)