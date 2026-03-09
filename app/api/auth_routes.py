from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.services.auth_service import (
    admin_login,
    worker_login,
    customer_login,
    otp_login
)

from app.services.otp_service import send_otp

router = APIRouter(prefix="/auth")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 ADMIN LOGIN
@router.post("/admin/login")
def login_admin(data: dict, db: Session = Depends(get_db)):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(400, "Email and password required")

    return {"data": admin_login(db, data["email"], data["password"])}


# 👷 WORKER LOGIN (PASSWORD)
@router.post("/worker/login")
def login_worker(data: dict, db: Session = Depends(get_db)):
    if not data.get("phone") or not data.get("password"):
        raise HTTPException(400, "Phone and password required")

    return {"data": worker_login(db, data["phone"], data["password"])}


# 👤 CUSTOMER LOGIN
@router.post("/customer/login")
def login_customer(data: dict, db: Session = Depends(get_db)):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(400, "Email and password required")

    return {"data": customer_login(db, data["email"], data["password"])}


# 📱 SEND OTP
@router.post("/worker/send-otp")
def send_worker_otp(data: dict, db: Session = Depends(get_db)):
    if not data.get("phone"):
        raise HTTPException(400, "Phone is required")

    return send_otp(db, data["phone"])


# 📱 LOGIN WITH OTP
@router.post("/worker/login-otp")
def worker_login_otp(data: dict, db: Session = Depends(get_db)):
    if not data.get("phone") or not data.get("otp"):
        raise HTTPException(400, "Phone and OTP required")

    return {"data": otp_login(db, data["phone"], data["otp"])}


