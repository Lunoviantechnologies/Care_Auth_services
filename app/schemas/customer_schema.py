from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ---------------- CREATE CUSTOMER ---------------- #

class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    address: Optional[str] = None
    city: Optional[str] = None


# ---------------- CUSTOMER LOGIN ---------------- #

class CustomerLogin(BaseModel):
    phone: str
    password: str
    device_id: str


# ---------------- UPDATE CUSTOMER ---------------- #

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    isVerified: Optional[bool] = None


# ---------------- LOCATION UPDATE ---------------- #

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


# ---------------- RESPONSE SCHEMA ---------------- #

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    address: Optional[str]
    city: Optional[str]
    isVerified: bool
    isActive: bool
    latitude: Optional[float]
    longitude: Optional[float]
    createdAt: datetime

    class Config:
        from_attributes = True