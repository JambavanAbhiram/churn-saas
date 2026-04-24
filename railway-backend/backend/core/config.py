import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ChurnSaaS"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "changeme-in-production-32chars!!")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql+asyncpg://churn:churn@db:5432/churndb")
    MODEL_DIR: str = os.environ.get("MODEL_DIR", "/app/models")
    TRAIN_DATA: str = os.environ.get("TRAIN_DATA", "/app/data/churn.csv")
    STORAGE_DIR: str = os.environ.get("STORAGE_DIR", "/app/storage")

    # S3 (optional)
    USE_S3: bool = False
    AWS_BUCKET: str = ""
    AWS_REGION: str = "us-east-1"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
