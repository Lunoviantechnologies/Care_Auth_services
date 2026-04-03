import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #  IMPORTANT: point to correct .env location
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

     #  JWT
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    #  Database (REQUIRED)
    DATABASE_URL: str

    #  Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"

    #  Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "gangadariprashanth12@gmail.com"
    SMTP_PASSWORD: str = "ygkg fueo hyew vjip"
    ADMIN_EMAIL: str = "gangadariprashanth12@gmail.com"
    #  App
    APP_NAME: str = "Multi Role Auth System"
    DEBUG: bool = True

    MSG91_AUTH_KEY: str = os.getenv("MSG91_AUTH_KEY")
    MSG91_TEMPLATE_ID: str = os.getenv("MSG91_TEMPLATE_ID")
    MSG91_SENDER_ID: str = os.getenv("MSG91_SENDER_ID")



settings = Settings()
print("✅ DATABASE_URL loaded:", settings.DATABASE_URL)
