from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Campaign Intelligence Platform"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "hackathon-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    DATABASE_URL: str = "sqlite+aiosqlite:///./campaign_platform.db"
    REDIS_URL: str = "redis://localhost:6379"

    model_config = {"env_file": ".env"}


settings = Settings()
