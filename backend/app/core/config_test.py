from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Management System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "test-secret-key-for-testing"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    class Config:
        case_sensitive = True

settings = Settings()