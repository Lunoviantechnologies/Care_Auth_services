from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.customer_schema import CustomerLogin

from app.services.auth_service import (
    admin_login,
    worker_login,
    customer_login,
    firebase_worker_login,
    firebase_customer_login
)

router = APIRouter(prefix="/api")


# ---------------- DB SESSION ----------------
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ---------------- ADMIN LOGIN ----------------
@router.post("/admin/login")
async def login_admin(data: dict, db: AsyncSession = Depends(get_db)):

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    return {
        "data": await admin_login(db, email, password)
    }


# ---------------- WORKER LOGIN ----------------
@router.post("/worker/login")
async def login_worker_api(data: dict, db: AsyncSession = Depends(get_db)):

    phone = data.get("phone")
    password = data.get("password")
    device_id = data.get("device_id")

    if not phone or not password:
        raise HTTPException(status_code=400, detail="Phone and password required")

    if not device_id:
        raise HTTPException(status_code=400, detail="device_id required")

    return {
        "data": await worker_login(
            db,
            phone,
            password,
            device_id
        )
    }


# ---------------- CUSTOMER LOGIN ----------------
@router.post("/customer/login")
async def login_customer_api(data: CustomerLogin, db: AsyncSession = Depends(get_db)):

    if not data.phone:
        raise HTTPException(status_code=400, detail="Phone number required")

    if not data.password:
        raise HTTPException(status_code=400, detail="Password required")

    return {
        "data": await customer_login(
            db,
            data.phone,
            data.password
        )
    }


# ---------------- WORKER FIREBASE LOGIN ----------------
@router.post("/worker/firebase-login")
async def worker_firebase_login_api(data: dict, db: AsyncSession = Depends(get_db)):

    token = data.get("token")
    device_id = data.get("device_id")

    if not token:
        raise HTTPException(status_code=400, detail="Firebase token required")

    if not device_id:
        raise HTTPException(status_code=400, detail="device_id required")

    return {
        "data": await firebase_worker_login(
            db,
            token,
            device_id
        )
    }


# ---------------- CUSTOMER FIREBASE LOGIN ----------------
@router.post("/customer/firebase-login")
async def customer_firebase_login_api(data: dict, db: AsyncSession = Depends(get_db)):

    token = data.get("token")

    if not token:
        raise HTTPException(status_code=400, detail="Firebase token required")

    return {
        "data": await firebase_customer_login(
            db,
            token
        )
    }