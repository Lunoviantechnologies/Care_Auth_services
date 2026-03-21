from sqlalchemy.orm import Session
from app.db.models.admin_model import Admin
from app.db.models.otp_model import OTP
from app.core.security import hash_password
from app.core.email_service import send_email_otp
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
import random


# CREATE ADMIN
def create_admin(db: Session, data):
    try:
        existing_admin = db.query(Admin).filter(Admin.email == data.email).first()

        if existing_admin:
            raise HTTPException(status_code=400, detail="Admin with this email already exists")

        admin = Admin(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            role=data.role
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return {"message": "Admin created successfully", "data": admin}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Admin creation failed: {str(e)}")


# GET ALL ADMINS
def get_all(db: Session):
    try:
        return db.query(Admin).all()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch admins")


# GET ADMIN BY ID
def get_by_id(db: Session, id: str):
    admin = db.query(Admin).filter(Admin.id == id).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin


# UPDATE ADMIN
def update(db: Session, id: str, data):
    try:
        admin = get_by_id(db, id)

        if data.name:
            admin.name = data.name

        if data.email:
            admin.email = data.email

        if data.role:
            admin.role = data.role

        if data.isActive is not None:
            admin.isActive = data.isActive

        db.commit()
        db.refresh(admin)

        return {"message": "Admin updated successfully", "data": admin}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Admin update failed: {str(e)}")


# DELETE ADMIN
def delete(db: Session, id: str):
    try:
        admin = get_by_id(db, id)

        db.delete(admin)
        db.commit()

        return {"message": "Admin deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Admin deletion failed: {str(e)}")




# SEND OTP
def send_otp(db: Session, email: str):

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    otp_code = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(otp_record)
    db.commit()

    # send email
    send_email_otp(email, otp_code)

    return {"message": "OTP sent to email"}


# VERIFY OTP
def verify_otp(db: Session, email: str, otp: str):

    otp_record = db.query(OTP).filter(
        OTP.email == email,
        OTP.otp == otp
    ).order_by(OTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    return {"message": "OTP verified successfully"}


# RESET PASSWORD
def reset_password(db: Session, email: str, otp: str, new_password: str, confirm_password: str):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    otp_record = db.query(OTP).filter(
        OTP.email == email,
        OTP.otp == otp
    ).order_by(OTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.password = hash_password(new_password)

    db.commit()

    return {"message": "Password reset successfully"}