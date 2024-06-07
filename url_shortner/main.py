from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import string

from .database import SessionLocal, engine
from .schemas import URLCreate, URLResponse
from .crud import create_url, get_url_by_key
from .config import settings
from . import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_short_key(length=settings.SHORT_KEY_LENGTH):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def create_unique_short_key(db: Session, length=settings.SHORT_KEY_LENGTH):
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
        raise HTTPException(status_code=500, detail="키 생성에 실패했습니다.")


@app.post("/shorten", response_model=URLResponse)
def shorten_url(url: URLCreate, db: Session = Depends(get_db)):
    short_key = generate_short_key()

    create_url(db=db, url=url.url, short_key=short_key, expiry=url.expiry)

    return {"short_url": f"{settings.BASE_URL}/{short_key}"}
