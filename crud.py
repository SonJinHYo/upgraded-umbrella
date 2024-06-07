from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from .models import URL


def create_url(db: Session, url: str, short_key: str, expiry: int) -> URL:
    expiry_date = datetime.utcnow() + timedelta(seconds=expiry)
    db_url = URL(url=url, short_key=short_key, expiry=expiry_date)

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url
