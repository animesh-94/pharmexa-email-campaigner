from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./emailcamp.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 2525
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    FROM_EMAIL: str = "newsletter@example.com"
    APP_DOMAIN: str = "http://localhost:8000"
    
    SECRET_KEY: str = "local-dev-secret-key"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()
