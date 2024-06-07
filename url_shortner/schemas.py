from pydantic import BaseModel


class URLCreate(BaseModel):
    url: str
    expiry: int


class URLResponse(BaseModel):
    short_url: str
