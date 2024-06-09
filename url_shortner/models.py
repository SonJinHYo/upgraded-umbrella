from datetime import datetime

from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(String(1024), unique=True)
    short_key: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    expiry: Mapped[datetime] = mapped_column(DateTime)
    clicks: Mapped[int] = mapped_column(Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "short_key": self.short_key,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "clicks": self.clicks
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data["id"],
            url=data["url"],
            short_key=data["short_key"],
            expiry=datetime.fromisoformat(data["expiry"]) if data["expiry"] else None,
            clicks=data["clicks"]
        )
