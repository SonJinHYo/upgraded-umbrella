from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from .models import URL


def create_url(db: Session, url: str, short_key: str, expiry: int) -> URL:
    expiry_date = datetime.now(timezone.utc) + timedelta(seconds=expiry)
    db_url = URL(url=url, short_key=short_key, expiry=expiry_date)

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url


def get_url_by_origin_url(db: Session, origin_url: str) -> URL:
    return db.query(URL).filter(URL.url == origin_url).first()


def get_url_by_key(db: Session, short_key: str) -> URL:
    return db.query(URL).filter(URL.short_key == short_key).first()


def increment_url_stats(db: Session, short_key: str) -> None:
    db_url = get_url_by_key(db=db, short_key=short_key)
    if db_url:
        db_url.clicks += 1
        db.commit()


def delete_url(db: Session, short_key: str) -> None:
    db_url = get_url_by_key(db=db, short_key=short_key)
    if db_url:
        db.delete(db_url)
        db.commit()
