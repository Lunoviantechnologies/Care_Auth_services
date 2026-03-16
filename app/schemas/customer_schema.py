from pydantic import BaseModel, EmailStr
from typing import Optional


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    address: Optional[str]
    city: Optional[str]


class CustomerUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    isVerified: Optional[bool]

    # FORGOT PASSWORD REQUEST


class CustomerForgotPasswordRequest(BaseModel):
    email: EmailStr


# VERIFY OTP
class CustomerVerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


# RESET PASSWORD
class CustomerResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str
