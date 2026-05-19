from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "ComplianceSync"
    VERSION: str = "1.0.0-beta"
    DESCRIPTION: str = "Real-Time Corporate Compliance Dashboard for Bangladesh"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://compliance:compliance@localhost:5432/compliancesync"
    SYNC_DATABASE_URL: str = "postgresql://compliance:compliance@localhost:5432/compliancesync"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "compliancesync-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB

    # Cloudflare R2 / S3 Storage Settings
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_STORAGE_BUCKET_NAME: str = ""
    AWS_S3_ENDPOINT_URL: str = ""
    AWS_S3_CUSTOM_DOMAIN: str = ""

    # Email/SMS (placeholder for integrations)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # Compliance Rules
    DEFAULT_FISCAL_YEAR_END: str = "06-30"
    PENALTY_DAILY_FINE: float = 500.0  # BDT per day for late filing

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()