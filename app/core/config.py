from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ✅ IMPORTANT: point to correct .env location
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore"
    )

    # 🔐 JWT
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 🗄️ Database (REQUIRED)
    DATABASE_URL: str

    # 🔴 Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379"

    # 📧 Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_password"

    # 🌍 App
    APP_NAME: str = "Multi Role Auth System"
    DEBUG: bool = True
    
settings = Settings()
print("✅ DATABASE_URL loaded:", settings.DATABASE_URL)