import json
import random
import string

from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from .database import SessionLocal, engine, REDIS_URL
from .schemas import *
from .crud import *
from .config import settings
from . import models


###############     DataBase     ###############

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


class RedisDriver:
    def __init__(self):
        self.redis_url = REDIS_URL
        self.redis_client = aioredis.from_url(self.redis_url)

    async def set_url(self, key: str, url: URL, ttl=60) -> None:
        url_dict = url.to_dict()
        ttl = min(ttl, get_remain_expiry_to_sec(url.expiry))
        await self.set(key=key, val=json.dumps(url_dict), ttl=ttl)

    async def get_url(self, key: str) -> URL:
        url_data = await self.get(key=key)

        if url_data is None:
            return None

        url_dict = json.loads(url_data)

        return URL.from_dict(url_dict)

    async def set(self, key, val, ttl=60):
        await self.redis_client.set(key, val)
        if ttl:
            await self.redis_client.expire(key, ttl)

    async def get(self, key):
        return await self.redis_client.get(key)

    async def delete(self, key):
        await self.redis_client.delete(key)


async def get_url_cache_or_db(short_key: str, redis_instance: RedisDriver, db: AsyncSession) -> URL | None:
    url: URL = await redis_instance.get_url(key=short_key)

    if url is None:
        url = await get_url_by_key(db=db, short_key=short_key)

    return url


###############     support func     ###############

def generate_short_key(length: int = settings.SHORT_KEY_LENGTH) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def create_unique_short_key(db: AsyncSession, length: int = settings.SHORT_KEY_LENGTH) -> str:
    """
    키 생성 전체 경우의 수: 62(대소문자 알파벳 + 숫자 갯수) ** 키 길이

    if key 길이 = 6, 중복키 발생시 재생성 횟수 3:
        62 ** 6은 약 568억
        저장된 키가 10억개 일 때, None 반환 발생 확률 = (10 / 568) ** 3 = 약 0.0005%
    """
    for _ in range(3):
        short_key = generate_short_key(length)

        if not await get_url_by_key(db=db, short_key=short_key):
            return short_key
    else:
        return None


def get_remain_expiry_to_sec(expiry: datetime) -> float:
    return (expiry.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds()
