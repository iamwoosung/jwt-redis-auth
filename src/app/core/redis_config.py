from fastapi import FastAPI
import redis
import redis.exceptions

# 환경변수 처리 안함
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None

redis_client = redis.Redis(
    host = REDIS_HOST, 
    port=REDIS_PORT, 
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True
)

def init_redis(app: FastAPI):
    @app.on_event("startup")
    async def startup_redis_client():
        try:
            redis_client.ping()
            print("Redis connection completed")
        except redis.exceptions.ConnectionError:
            print("Failed to connect to Redis")

    @app.on_event("shutdown")
    async def shutdown_redis_client():
        redis_client.close()
        print("Redis connection closed")