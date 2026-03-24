from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.admin_model import Admin
from app.db.models.otp_model import OTP
from app.core.security import hash_password
from app.core.email_service import send_email_otp
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import random


# CREATE ADMIN
async def create_admin(db: AsyncSession, data):
    try:
        result = await db.execute(
            select(Admin).where(Admin.email == data.email)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin already exists")

        admin = Admin(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            role=data.role
        )

        db.add(admin)
        await db.commit()
        await db.refresh(admin)

        return {"message": "Admin created successfully", "data": admin}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# GET ALL ADMINS
async def get_all(db: AsyncSession):
    try:
        result = await db.execute(select(Admin))
        return result.scalars().all()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch admins")


# GET ADMIN BY ID
async def get_by_id(db: AsyncSession, id: str):
    result = await db.execute(
        select(Admin).where(Admin.id == id)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin


# UPDATE ADMIN
async def update(db: AsyncSession, id: str, data):
    try:
        admin = await get_by_id(db, id)

        if data.name:
            admin.name = data.name

        if data.email:
            admin.email = data.email

        if data.role:
            admin.role = data.role

        if data.isActive is not None:
            admin.isActive = data.isActive

        await db.commit()
        await db.refresh(admin)

        return {"message": "Admin updated successfully", "data": admin}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# DELETE ADMIN
async def delete(db: AsyncSession, id: str):
    try:
        admin = await get_by_id(db, id)

        await db.delete(admin)
        await db.commit()

        return {"message": "Admin deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# SEND OTP
async def send_otp(db: AsyncSession, email: str):

    result = await db.execute(
        select(Admin).where(Admin.email == email)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    otp_code = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(otp_record)
    await db.commit()

    # ⚠️ Make sure this function is async OR run in background
    await send_email_otp(email, otp_code)

    return {"message": "OTP sent successfully"}


# VERIFY OTP
async def verify_otp(db: AsyncSession, email: str, otp: str):

    result = await db.execute(
        select(OTP)
        .where(OTP.email == email, OTP.otp == otp)
        .order_by(OTP.id.desc())
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified successfully"}


# RESET PASSWORD
async def reset_password(
    db: AsyncSession,
    email: str,
    otp: str,
    new_password: str,
    confirm_password: str
):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    result = await db.execute(
        select(OTP)
        .where(OTP.email == email, OTP.otp == otp)
        .order_by(OTP.id.desc())
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    result = await db.execute(
        select(Admin).where(Admin.email == email)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.password = hash_password(new_password)

    await db.commit()

    return {"message": "Password reset successfully"}