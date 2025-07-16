from fastapi import FastAPI
from app.apis import auth, user, post
from app.database import Base, engine

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
app.include_router(post.router, tags=["post"])


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

