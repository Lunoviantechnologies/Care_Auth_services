from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# ✅ Create engine
engine = create_engine(settings.DATABASE_URL)

# ✅ Create session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ✅ THIS LINE IS MANDATORY (YOU ARE MISSING THIS)
Base = declarative_base()