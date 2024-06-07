from datetime import datetime, timezone

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import random
import string

from .database import SessionLocal, engine
from .schemas import *
from .crud import *
from .config import settings
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_key(length: int = settings.SHORT_KEY_LENGTH) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_unique_short_key(db: Session, length: int = settings.SHORT_KEY_LENGTH) -> str:
    """
    키 생성 전체 경우의 수: 62(대소문자 알파벳 + 숫자 갯수) ** 키 길이

    if key 길이 = 6:
        62 ** 6은 약 568억
        100만개의 키를 생성할 때 중복이 발생할 확률 = 약 0.0015%
    """
    for _ in range(3):
        short_key = generate_short_key(length)

        if not get_url_by_key(db, short_key):
            return short_key
    else:
        raise HTTPException(status_code=500, detail="generate key failed.")


@app.post("/shorten", response_model=URLResponse)
def shorten_url(url: URLRequest,  db: Session = Depends(get_db)):
    db_url: URL = get_url_by_origin_url(db=db, origin_url=url.url)
    if db_url:
        return {"short_url": f"{settings.BASE_URL}/{db_url.short_key}"}

    short_key = generate_short_key()

    create_url(db=db, url=url.url, short_key=short_key, expiry=url.expiry.duration)

    return {"short_url": f"{settings.BASE_URL}/{short_key}"}


@app.get("/{short_key}", response_model=OriginURLResponse)
def redirect_url(short_key: str, db: Session = Depends(get_db)):
    db_url = get_url_by_key(db=db, short_key=short_key)

    if db_url and db_url.expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        delete_success = delete_url(db=db, short_key=short_key)
        if delete_success:
            db_url = None
        else:
            raise HTTPException(status_code=500, detail="Server Error")
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found")

    increment_url_stats(db=db, short_key=short_key)

    return RedirectResponse(url=db_url.url, status_code=301)
