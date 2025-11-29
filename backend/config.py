from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

# Get the parent directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True

settings = Settings()
