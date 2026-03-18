from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.schemas.customer_schema import CustomerLogin
from app.services.auth_service import customer_login

from app.services.auth_service import (
    admin_login,
    worker_login,
    customer_login,
    firebase_worker_login,
    firebase_customer_login
)

router = APIRouter(prefix="/auth")


# DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- ADMIN LOGIN ----------------
@router.post("/admin/login")
def login_admin(data: dict, db: Session = Depends(get_db)):

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(400, "Email and password required")

    return {"data": admin_login(db, email, password)}


# ---------------- WORKER LOGIN ----------------
@router.post("/worker/login")
def login_worker_api(data: dict, db: Session = Depends(get_db)):

    phone = data.get("phone")
    password = data.get("password")
    device_id = data.get("device_id")

    if not phone or not password:
        raise HTTPException(400, "Phone and password required")

    if not device_id:
        raise HTTPException(400, "device_id required")

    return {
        "data": worker_login(
            db,
            phone,
            password,
            device_id
        )
    }


# ---------------- CUSTOMER LOGIN ----------------

@router.post("/customer/login")
def login_customer_api(data: CustomerLogin, db: Session = Depends(get_db)):

    if not data.phone:
        raise HTTPException(status_code=400, detail="Phone number required")

    if not data.password:
        raise HTTPException(status_code=400, detail="Password required")

    return {
        "data": customer_login(
            db,
            data.phone,
            data.password
        )
    }

# ---------------- WORKER FIREBASE LOGIN ----------------
@router.post("/worker/firebase-login")
def worker_firebase_login_api(data: dict, db: Session = Depends(get_db)):

    token = data.get("token")
    device_id = data.get("device_id")

    if not token:
        raise HTTPException(400, "Firebase token required")

    if not device_id:
        raise HTTPException(400, "device_id required")

    return {
        "data": firebase_worker_login(
            db,
            token,
            device_id
        )
    }


# ---------------- CUSTOMER FIREBASE LOGIN ----------------
@router.post("/customer/firebase-login")
def customer_firebase_login_api(data: dict, db: Session = Depends(get_db)):

    token = data.get("token")

    if not token:
        raise HTTPException(400, "Firebase token required")

    return {
        "data": firebase_customer_login(
            db,
            token
        )
    }