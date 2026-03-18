from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models.admin_model import Admin
from app.db.models.worker_model import Worker
from app.db.models.customer_model import Customer

from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.firebase_service import verify_firebase_token


# ---------------- TOKEN GENERATOR ----------------
def generate_tokens(user_id: int, role: str):
    return {
        "access_token": create_access_token(user_id, role),
        "refresh_token": create_refresh_token(user_id, role),
        "token_type": "bearer",
        "user_id": user_id,
        "role": role,
    }


# ---------------- ADMIN LOGIN ----------------
def admin_login(db: Session, email: str, password: str):

    admin = db.query(Admin).filter(Admin.email == email).first()

    if not admin:
        raise HTTPException(404, "Admin not found")

    if not verify_password(password, admin.password):
        raise HTTPException(401, "Invalid credentials")

    return generate_tokens(admin.id, "admin")


# ---------------- WORKER LOGIN ----------------
def worker_login(db: Session, phone: str, password: str, device_id: str):

    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(password, worker.password):
        raise HTTPException(401, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    # SINGLE DEVICE LOGIN
    worker.device_id = device_id
    worker.is_logged_in = True

    db.commit()

    return generate_tokens(worker.id, "worker")


# ---------------- CUSTOMER LOGIN ----------------
# CUSTOMER LOGIN SERVICE
def customer_login(db: Session, phone: str, password: str):

    customer = db.query(Customer).filter(Customer.phone == phone).first()

    # Customer not found
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer with this phone number not found"
        )

    # Password check
    if not verify_password(password, customer.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    # Inactive account
    if not customer.isActive:
        raise HTTPException(
            status_code=403,
            detail="Customer account is inactive"
        )

    return generate_tokens(customer.id, "customer")


# ---------------- WORKER FIREBASE LOGIN ----------------
def firebase_worker_login(db: Session, token: str, device_id: str):

    phone = verify_firebase_token(token)

    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    worker.device_id = device_id
    worker.is_logged_in = True

    db.commit()

    return generate_tokens(worker.id, "worker")


# ---------------- CUSTOMER FIREBASE LOGIN ----------------
def firebase_customer_login(db: Session, token: str):

    phone = verify_firebase_token(token)

    customer = db.query(Customer).filter(Customer.phone == phone).first()

    if not customer:
        raise HTTPException(404, "Customer not found")

    return generate_tokens(customer.id, "customer")
