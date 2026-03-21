from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ---------------- BASE ---------------- #


class CustomerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    address: Optional[str] = None
    city: Optional[str] = None
    profile_image: Optional[str] = None


# ---------------- CREATE ---------------- #


class CustomerCreate(CustomerBase):
    password: str = Field(..., min_length=6)


# ---------------- LOGIN ---------------- #


class CustomerLogin(BaseModel):
    phone: str
    password: str


# ---------------- UPDATE ---------------- #


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    profile_image: Optional[str] = None
    isVerified: Optional[bool] = None


# ---------------- LOCATION ---------------- #


class CustomerLocationUpdate(BaseModel):
    latitude: float
    longitude: float


# ---------------- FORGOT PASSWORD ---------------- #


class CustomerForgotPasswordRequest(BaseModel):
    email: EmailStr


# ---------------- VERIFY OTP ---------------- #


class CustomerVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


# ---------------- RESET PASSWORD ---------------- #


class CustomerResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str


# ---------------- RESPONSE ---------------- #


class CustomerResponse(CustomerBase):
    id: int
    isVerified: bool
    isActive: bool
    latitude: Optional[float]
    longitude: Optional[float]
    createdAt: datetime

    class Config:
        from_attributes = True
