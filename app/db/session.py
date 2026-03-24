from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


# ---------------- DATABASE URL ----------------
# ⚠️ MUST be async driver
# Example: postgresql+asyncpg://user:password@localhost/db
DATABASE_URL = settings.DATABASE_URL


# ---------------- ENGINE ----------------
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
)


# ---------------- SESSION ----------------
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# ---------------- BASE ----------------
Base = declarative_base()


# ---------------- DB DEPENDENCY ----------------
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
