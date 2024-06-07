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
