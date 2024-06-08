import redis.asyncio as aioredis
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

MYSQL_USER = os.getenv("MYSQL_ROOT_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")

SQLALCHEMY_DATABASE_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


###############     Redis     ###############

class RedisDriver:
    def __init__(self):
        REDIS_HOST = os.getenv("REDIS_HOST")
        REDIS_PORT = os.getenv("REDIS_PORT")

        self.redis_url = f'redis://{REDIS_HOST}:{REDIS_PORT}'
        self.redis_client = aioredis.from_url(self.redis_url)

    async def set(self, key, val, ttl=60):
        await self.redis_client.set(key, val)
        if ttl:
            await self.redis_client.expire(key, ttl)

    async def get(self, key):
        return await self.redis_client.get(key)

    async def delete(self, key):
        await self.redis_client.delete(key)
