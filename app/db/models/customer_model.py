from sqlalchemy import Column, String, Boolean, DateTime, Integer
from app.db.session import Base
from datetime import datetime


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    device_id = Column(String, nullable=True)
    isVerified = Column(Boolean, default=False)
    isActive = Column(Boolean, default=True)   # ✅ added (recommended)
    createdAt = Column(DateTime, default=datetime.utcnow)