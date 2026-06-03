from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Agent Management System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-it-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    DATABASE_URL: str = "mysql+aiomysql://product:product123@192.168.6.10:37061/agent_management?charset=utf8mb4"

    class Config:
        case_sensitive = True

settings = Settings()
