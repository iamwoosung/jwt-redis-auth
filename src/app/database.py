from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

# engine 생성
# check_same_thread=False는 SQLite의 동시 설정을 비활성화
# SQLite는 단일 스레드이지만 FastAPI는 비동기이기 때문에 동시 접근이 적합 
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 트렌젝션 수동 관리를 위한 설정 비활성화
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close