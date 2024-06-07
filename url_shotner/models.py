from datetime import datetime

from sqlalchemy.orm import Mapped

from .database import Base

from sqlalchemy import Column, Integer, String, DateTime
from .database import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    url: Mapped[str] = Column(String, index=True)
    short_key: Mapped[str] = Column(String, unique=True, index=True)
    expiry: Mapped[datetime] = Column(DateTime, nullable=True)
    clicks: Mapped[int] = Column(Integer, default=0)
