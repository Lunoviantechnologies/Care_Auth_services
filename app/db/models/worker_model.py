from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, Float
from app.db.session import Base
from datetime import datetime
import enum


# Worker Status Enum
class WorkerStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


# Worker Type Enum
class WorkerType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"


# Vehicle Type Enum
class VehicleType(enum.Enum):
    BIKE = "bike"
    SCOOTER = "scooter"
    AUTO = "auto"
    CAR = "car"
    VAN = "van"
    NONE = "none"


# Worker Availability Enum
class WorkerAvailability(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


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

    # Worker Status
    status = Column(Enum(WorkerStatus), default=WorkerStatus.PENDING)

    # Worker Type
    worker_type = Column(Enum(WorkerType), nullable=True)

    # Vehicle Type
    vehicle_type = Column(Enum(VehicleType), nullable=True)

    # Worker Availability
    availability = Column(Enum(WorkerAvailability), default=WorkerAvailability.OFFLINE)

    # Employment Type (Normal Field)
    employment_type = Column(String, nullable=True)

    # Service Category (simple field)
    service_category = Column(String, nullable=True)

    # Rating
    rating = Column(Float, default=0.0)

    # Live Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # Device Login Fields
    device_id = Column(String, nullable=True)
    is_logged_in = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)