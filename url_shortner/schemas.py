from enum import Enum

from pydantic import BaseModel


class ExpirationDate(str, Enum):
    ONE_H = "1 hour"
    THREE_H = "3 hour"
    TWELVE_H = "12 hour"
    ONE_D = "1 day"
    THREE_D = "3 days"
    SEVEN_D = "7 days"
    THIRTY_D = "30 days"

    @property
    def duration(self) -> int:
        time, unit = self.value.split()

        if unit[0] == "h":
            return int(time) * 3600
        elif unit[0] == "d":
            return int(time) * 24 * 3600
        else:
            raise ValueError("Bad Request: expiry value.")


class URLRequest(BaseModel):
    url: str
    expiry: ExpirationDate


class URLResponse(BaseModel):
    short_url: str


class ClicksResponse(BaseModel):
    clicks: int


class OriginURLResponse(BaseModel):
    origin_url: str
