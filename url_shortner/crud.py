from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .models import URL


async def create_url(db: AsyncSession, url: str, short_key: str, expiry: int) -> URL:
    expiry_date = datetime.now(timezone.utc) + timedelta(seconds=expiry)
    db_url = URL(url=url, short_key=short_key, expiry=expiry_date)

    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)

    return db_url


async def get_url_by_origin_url(db: AsyncSession, origin_url: str) -> URL:
    result = await db.execute(select(URL).filter(URL.url == origin_url))
    return result.scalars().first()


async def get_url_by_key(db: AsyncSession, short_key: str) -> URL:
    result = await db.execute(select(URL).filter(URL.short_key == short_key))
    return result.scalars().first()


async def increment_url_stats(db: AsyncSession, short_key: str) -> None:
    db_url = await get_url_by_key(db=db, short_key=short_key)
    if db_url:
        db_url.clicks += 1
        await db.commit()


async def delete_url(db: AsyncSession, short_key: str) -> None:
    db_url = await get_url_by_key(db=db, short_key=short_key)
    if db_url:
        await db.delete(db_url)
        await db.commit()
