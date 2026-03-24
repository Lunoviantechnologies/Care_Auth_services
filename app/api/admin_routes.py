from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.services import admin_service
from app.schemas.admin_schema import AdminCreate, AdminUpdate

from app.schemas.admin_schema import (
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/api", tags=["Admin"])


# ---------------- DB DEPENDENCY ----------------
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ---------------- CREATE ADMIN ----------------
@router.post("/admin/create")
async def create_admin(data: AdminCreate, db: AsyncSession = Depends(get_db)):
    return await admin_service.create_admin(db, data)


# ---------------- GET ALL ----------------
@router.get("/admin/all")
async def get_all_admins(db: AsyncSession = Depends(get_db)):
    return await admin_service.get_all(db)


# ---------------- GET BY ID ----------------
@router.get("/admin/get/{id}")
async def get_admin(id: str, db: AsyncSession = Depends(get_db)):
    return await admin_service.get_by_id(db, id)


# ---------------- UPDATE ----------------
@router.put("/admin/update/{id}")
async def update_admin(id: str, data: AdminUpdate, db: AsyncSession = Depends(get_db)):
    return await admin_service.update(db, id, data)


# ---------------- DELETE ----------------
@router.delete("/admin/delete/{id}")
async def delete_admin(id: str, db: AsyncSession = Depends(get_db)):
    return await admin_service.delete(db, id)


# ---------------- SEND OTP ----------------
@router.post("/admin/send-otp")
async def send_admin_otp(data: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await admin_service.send_otp(db, data.email)


# ---------------- VERIFY OTP ----------------
@router.post("/admin/verify-otp")
async def verify_admin_otp(data: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    return await admin_service.verify_otp(db, data.email, data.otp)


# ---------------- RESET PASSWORD ----------------
@router.post("/admin/reset-password")
async def reset_admin_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await admin_service.reset_password(
        db,
        data.email,
        data.otp,
        data.new_password,
        data.confirm_password
    )