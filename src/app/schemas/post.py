from datetime import datetime
from pydantic import BaseModel 

class PostCreate(BaseModel):
    title: str
    author: str
    content: str

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    create_at: datetime

    class Config:
        from_attributes = True