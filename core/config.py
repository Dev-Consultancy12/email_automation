from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    
    # Task Queue
    REDIS_URL: str
    
    # External APIs
    HUNTER_API_KEY: str
    ZEROBOUNCE_API_KEY: str
    SENDGRID_API_KEY: str
    SENDGRID_WEBHOOK_SECRET: str
    
    # Application Settings
    ENVIRONMENT: str = "development"
    MAX_EMAILS_PER_DAY: int = 50

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
