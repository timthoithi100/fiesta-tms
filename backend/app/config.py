from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Fiesta Training Management System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 10
    
    # Redis
    redis_url: str
    redis_session_db: int = 1
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: str = "http://localhost:8000"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Password Policy
    min_password_length: int = 8
    require_special_char: bool = True
    require_uppercase: bool = True
    require_digit: bool = True
    
    # Session
    session_cookie_name: str = "fiesta_session"
    session_max_age: int = 3600
    
    # File Upload
    max_upload_size: int = 5242880  # 5MB
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@fiesta.edu"
    
    # Sentry
    sentry_dsn: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()