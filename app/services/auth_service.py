from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models.admin_model import Admin
from app.db.models.worker_model import Worker
from app.db.models.customer_model import Customer

from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token
)

from app.services.otp_service import verify_otp


# 🔐 TOKEN GENERATOR
def generate_tokens(user_id: int, role: str):
    return {
        "access_token": create_access_token(user_id, role),
        "refresh_token": create_refresh_token(user_id, role),
        "token_type": "bearer",
        "user_id": user_id,
        "role": role
    }


# 🔐 ADMIN LOGIN
def admin_login(db: Session, email, password):
    user = db.query(Admin).filter(Admin.email == email).first()

    if not user:
        raise HTTPException(404, "Admin not found")

    if not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return generate_tokens(user.id, "admin")


# 👷 WORKER LOGIN (PASSWORD)
def worker_login(db: Session, phone: str, password: str):
    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(password, worker.password):
        raise HTTPException(400, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    return generate_tokens(worker.id, "worker")


# 👤 CUSTOMER LOGIN
def customer_login(db: Session, email, password):
    user = db.query(Customer).filter(Customer.email == email).first()

    if not user:
        raise HTTPException(404, "Customer not found")

    if not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return generate_tokens(user.id, "customer")


# 🔢 OTP LOGIN (WORKER)
def otp_login(db: Session, phone: str, otp: str):

    # ✅ VERIFY OTP
    verify_otp(phone, otp)

    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    worker.phone_verified = True
    db.commit()

    return generate_tokens(worker.id, "worker")
