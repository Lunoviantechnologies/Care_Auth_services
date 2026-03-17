from pydantic import BaseModel, EmailStr
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


# ---------------- CREATE WORKER ---------------- #

class WorkerCreate(BaseModel):
    full_name: str
    phone: str
    email: Optional[EmailStr] = None
    password: str
    worker_type: Optional[WorkerType] = None
    vehicle_type: Optional[VehicleType] = None
    employment_type: Optional[str] = None
    service_category: Optional[str] = None


# ---------------- LOGIN ---------------- #

class WorkerLogin(BaseModel):
    phone: str
    password: str
    device_id: str


# ---------------- UPDATE PROFILE ---------------- #

class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    profile_image: Optional[str] = None
    worker_type: Optional[WorkerType] = None
    vehicle_type: Optional[VehicleType] = None
    employment_type: Optional[str] = None
    service_category: Optional[str] = None


# ---------------- KYC UPDATE ---------------- #

class KYCUpdate(BaseModel):
    aadhar_number: str
    aadhar_front: Optional[str] = None
    aadhar_back: Optional[str] = None


# ---------------- BANK UPDATE ---------------- #

class BankUpdate(BaseModel):
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str


# ---------------- ADDRESS UPDATE ---------------- #

class AddressUpdate(BaseModel):
    address: str
    city: str
    state: str
    pincode: str


# ---------------- LOCATION UPDATE ---------------- #

class WorkerLocationUpdate(BaseModel):
    latitude: float
    longitude: float


# ---------------- AVAILABILITY UPDATE ---------------- #

class WorkerAvailabilityUpdate(BaseModel):
    availability: WorkerAvailability


# ---------------- FORGOT PASSWORD ---------------- #

class WorkerForgotPasswordRequest(BaseModel):
    email: EmailStr


# ---------------- VERIFY OTP ---------------- #

class WorkerVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


# ---------------- RESET PASSWORD ---------------- #

class WorkerResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


# ---------------- RESPONSE SCHEMA ---------------- #

class WorkerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[EmailStr]
    status: WorkerStatus
    worker_type: Optional[WorkerType]
    vehicle_type: Optional[VehicleType]
    availability: WorkerAvailability
    rating: float
    latitude: Optional[float]
    longitude: Optional[float]

    class Config:
        from_attributes = True