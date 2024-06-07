from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_URL: str = "http://localhost:8000"
    SHORT_KEY_LENGTH: int = 6


settings = Settings()
