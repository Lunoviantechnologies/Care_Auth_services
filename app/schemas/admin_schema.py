from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# 🔹 Create Admin
class AdminCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # SUPER_ADMIN / SUB_ADMIN


# 🔹 Update Admin
class AdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


# 🔹 Response Schema
class AdminResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    isActive: bool
    createdAt: datetime
    device_id: Optional[str] = None   # ✅ added (matches model)

    class Config:
        from_attributes = True

        # 🔹 Forgot Password - Send OTP
class ForgotPasswordRequest(BaseModel):
    email: EmailStr


# 🔹 Verify OTP
class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


# 🔹 Reset Password
class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str
    confirm_password: str