from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from enum import Enum


# ---------------- ENUMS ---------------- #


class WorkerStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class WorkerType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"


class VehicleType(str, Enum):
    BIKE = "bike"
    SCOOTER = "scooter"
    AUTO = "auto"
    CAR = "car"
    VAN = "van"
    NONE = "none"


class WorkerAvailability(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"


# ---------------- CREATE ---------------- #


class WorkerCreate(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str

    worker_type: Optional[WorkerType] = None
    vehicle_type: Optional[VehicleType] = None
    employment_type: Optional[str] = None
    service_category: Optional[str] = None

    @field_validator("phone")
    def validate_phone(cls, v):
        if len(v) != 10 or not v.isdigit():
            raise ValueError("Phone must be 10 digits")
        return v


# ---------------- LOGIN ---------------- #


class WorkerLogin(BaseModel):
    phone: str
    password: str
    device_id: str


# ---------------- UPDATE ---------------- #


class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    worker_type: Optional[WorkerType] = None
    vehicle_type: Optional[VehicleType] = None
    employment_type: Optional[str] = None
    service_category: Optional[str] = None


# ---------------- KYC ---------------- #


class KYCUpdate(BaseModel):
    aadhaar_number: str

    @field_validator("aadhaar_number")
    def validate_aadhaar(cls, v):
        if len(v) != 12 or not v.isdigit():
            raise ValueError("Aadhaar must be 12 digits")
        return v


# ---------------- BANK ---------------- #


class BankUpdate(BaseModel):
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str


# ---------------- ADDRESS ---------------- #


class AddressUpdate(BaseModel):
    address: str
    city: str
    state: str
    pincode: str


# ---------------- LOCATION ---------------- #


class WorkerLocationUpdate(BaseModel):
    latitude: float
    longitude: float


# ---------------- AVAILABILITY ---------------- #


class WorkerAvailabilityUpdate(BaseModel):
    availability: WorkerAvailability


# ---------------- FORGOT PASSWORD ---------------- #


class WorkerForgotPasswordRequest(BaseModel):
    email: EmailStr


class WorkerVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class WorkerResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


# ---------------- RESPONSE ---------------- #


class WorkerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[EmailStr]

    profile_image: Optional[str]
    status: WorkerStatus

    worker_type: Optional[WorkerType]
    vehicle_type: Optional[VehicleType]
    availability: WorkerAvailability

    employment_type: Optional[str]
    service_category: Optional[str]

    rating: float

    latitude: Optional[float]
    longitude: Optional[float]

    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    address: Optional[str]

    is_admin_approved: bool
    is_kyc_verified: bool
    is_bank_verified: bool

    created_at: datetime

    class Config:
        from_attributes = True
