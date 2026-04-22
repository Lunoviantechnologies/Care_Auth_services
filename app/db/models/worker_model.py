from sqlalchemy import Column, String, Boolean, DateTime, Integer, Enum, Float
from app.db.session import Base
from datetime import datetime
import enum


# ---------------- ENUMS ---------------- #


class WorkerStatusEnum(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


# ---------------- SERVICE CATEGORY ENUM ---------------- #


class ServiceCategoryEnum(enum.Enum):
    BABY_CARE = "baby_care"
    PET_CARE = "pet_care"
    ELDER_CARE = "elder_care"
    PREGNANCY_CARE = "pregnancy_care"
    KITCHEN_CARE = "kitchen_care"


class WorkerTypeEnum(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"


class VehicleTypeEnum(enum.Enum):
    BIKE = "bike"
    SCOOTER = "scooter"
    AUTO = "auto"
    CAR = "car"
    VAN = "van"
    NONE = "none"


class WorkerAvailabilityEnum(enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


# ---------------- WORKER MODEL ---------------- #


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # -------- BASIC DETAILS -------- #
    full_name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)

    phone_verified = Column(Boolean, default=False)

    profile_image = Column(String, nullable=True)

    # -------- AADHAAR (KYC) -------- #
    aadhaar_number = Column(String, nullable=True)  # store last 4 digits only
    aadhaar_front = Column(String, nullable=True)
    aadhaar_back = Column(String, nullable=True)
    aadhaar_client_id = Column(String, nullable=True)

    is_kyc_verified = Column(Boolean, default=False)

    # -------- BANK -------- #
    account_holder_name = Column(String, nullable=True)
    account_number = Column(String, nullable=True)
    ifsc_code = Column(String, nullable=True)
    bank_name = Column(String, nullable=True)

    is_bank_verified = Column(Boolean, default=False)

    # -------- ADDRESS -------- #
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)

    is_address_verified = Column(Boolean, default=False)

    # -------- ADMIN -------- #
    is_admin_approved = Column(Boolean, default=False)

    # -------- STATUS -------- #
    status = Column(Enum(WorkerStatusEnum), default=WorkerStatusEnum.PENDING)

    # -------- WORK DETAILS -------- #
    worker_type = Column(Enum(WorkerTypeEnum), nullable=True)
    vehicle_type = Column(Enum(VehicleTypeEnum), nullable=True)
    availability = Column(
        Enum(WorkerAvailabilityEnum), default=WorkerAvailabilityEnum.OFFLINE
    )

    employment_type = Column(String, nullable=True)
    service_category = Column(Enum(ServiceCategoryEnum), nullable=True)

    rating = Column(Float, default=0.0)

    # -------- LOCATION -------- #
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # -------- DEVICE -------- #
    device_id = Column(String, nullable=True)
    is_logged_in = Column(Boolean, default=False)

    # -------- TIMESTAMP -------- #
    created_at = Column(DateTime, default=datetime.utcnow)

    is_banned = Column(Boolean, default=False)


banned_until = Column(DateTime, nullable=True)
