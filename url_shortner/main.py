from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import random
import string

from .database import SessionLocal, engine
from .schemas import *
from .crud import *
from .config import settings
from . import models


async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

app = FastAPI()


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


def generate_short_key(length: int = settings.SHORT_KEY_LENGTH) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def create_unique_short_key(db: AsyncSession, length: int = settings.SHORT_KEY_LENGTH) -> str:
    """
    키 생성 전체 경우의 수: 62(대소문자 알파벳 + 숫자 갯수) ** 키 길이

    if key 길이 = 6, 중복키 발생시 재생성 횟수 3:
        62 ** 6은 약 568억
        저장된 키가 10억개 일 때, 500 에러 발생 확률 = (10 / 568) ** 3 = 약 0.0005%
    """
    for _ in range(3):
        short_key = generate_short_key(length)

        if not await get_url_by_key(db, short_key):
            return short_key
    else:
        raise HTTPException(status_code=500, detail="generate key failed.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_database()
    yield


@app.post("/shorten", response_model=URLResponse)
async def shorten_url(url: URLRequest,  db: AsyncSession = Depends(get_db)):
    db_url: URL = await get_url_by_origin_url(db=db, origin_url=url.url)
    if db_url:
        return {"short_url": f"{settings.BASE_URL}/{db_url.short_key}"}

    short_key = generate_short_key()

    await create_url(db=db, url=url.url, short_key=short_key, expiry=url.expiry.duration)

    return {"short_url": f"{settings.BASE_URL}/{short_key}"}


@app.get("/{short_key}", response_model=OriginURLResponse)
async def redirect_url(short_key: str, db: AsyncSession = Depends(get_db)):
    db_url = await get_url_by_key(db=db, short_key=short_key)

    if db_url and db_url.expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await delete_url(db=db, short_key=short_key)
        db_url = None

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    await increment_url_stats(db=db, short_key=short_key)

    return RedirectResponse(url=db_url.url, status_code=301)


@app.get("/stats/{short_key}", response_model=ClicksResponse)
async def get_stats(short_key: str, db: AsyncSession = Depends(get_db)):
    db_url = await get_url_by_key(db=db, short_key=short_key)

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"clicks": db_url.clicks}
