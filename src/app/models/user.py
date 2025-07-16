from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String,unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    create_at = Column(DateTime(timezone=True), server_default=func.now())

    posts = relationship("Post", back_populates="author")