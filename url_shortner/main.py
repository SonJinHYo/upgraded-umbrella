from .config import settings
from .crud import *
from .schemas import *
from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from . import utils

app = FastAPI()


redis_instance = utils.RedisDriver()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await utils.create_database()
    yield


@app.post("/shorten", response_model=URLResponse)
async def shorten_url(url: URLRequest,  db: AsyncSession = Depends(utils.get_db)):
    db_url: URL = await get_url_by_origin_url(db=db, origin_url=url.url)
    if db_url:
        return {"short_url": f"{settings.BASE_URL}/{db_url.short_key}"}

    short_key: str | None = utils.generate_short_key()

    if short_key is None:
        raise HTTPException(status_code=500, detail="generate key failed.")

    await create_url(db=db, url=url.url, short_key=short_key, expiry=url.expiry.duration)

    return {"short_url": f"{settings.BASE_URL}/{short_key}"}


@app.get("/{short_key}", response_model=OriginURLResponse)
async def redirect_url(short_key: str, db: AsyncSession = Depends(utils.get_db)):
    db_url: URL | None = await redis_instance.get(short_key)

    if db_url is None:
        db_url: URL | None = await get_url_by_key(db=db, short_key=short_key)
        redis_instance.set(key=short_key, val=db_url)

    if db_url and db_url.expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await delete_url(db=db, short_key=short_key)
        await redis_instance.delete(key=short_key)
        db_url = None

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    await increment_url_stats(db=db, short_key=short_key)

    return RedirectResponse(url=db_url.url, status_code=301)


@app.get("/stats/{short_key}", response_model=ClicksResponse)
async def get_stats(short_key: str, db: AsyncSession = Depends(utils.get_db)):
    db_url: URL | None = await redis_instance.get(short_key)

    if db_url is None:
        db_url: URL | None = await get_url_by_key(db=db, short_key=short_key)
        redis_instance.set(key=short_key, val=db_url)

    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"clicks": db_url.clicks}
