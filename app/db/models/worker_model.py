from sqlalchemy import Column, String, Boolean, DateTime, Integer
from app.db.session import Base
from datetime import datetime


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=True)
    phone_verified = Column(Boolean, default=False)
    profile_image = Column(String, nullable=True)
    aadhar_number = Column(String, nullable=True)
    aadhar_front = Column(String, nullable=True)
    aadhar_back = Column(String, nullable=True)
    is_kyc_verified = Column(Boolean, default=False)

    account_holder_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)
    is_bank_verified = Column(Boolean, default=False)

    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    is_address_verified = Column(Boolean, default=False)

    is_admin_approved = Column(Boolean, default=False)
    status = Column(String, default="pending")

    created_at = Column(DateTime, default=datetime.utcnow)