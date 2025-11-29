from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from pathlib import Path

# Get the parent directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DATABASE_URL: str
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Application Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = str(ENV_FILE)
        case_sensitive = True
    
    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"

# Validate settings on import
try:
    settings = Settings()
except Exception as e:
    print(f"❌ Configuration Error: {e}")
    print("Please ensure all required environment variables are set in .env file")
    raise
