from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models.admin_model import Admin
from app.db.models.worker_model import Worker
from app.db.models.customer_model import Customer

from app.services.firebase_service import verify_firebase_token

from app.core.security import verify_password, create_access_token, create_refresh_token
from app.services.firebase_service import verify_firebase_token
from app.db.models.customer_model import Customer
from fastapi import HTTPException


# 🔐 TOKEN GENERATOR
def generate_tokens(user_id: int, role: str):
    return {
        "access_token": create_access_token(user_id, role),
        "refresh_token": create_refresh_token(user_id, role),
        "token_type": "bearer",
        "user_id": user_id,
        "role": role,
    }


# 🔐 ADMIN LOGIN
def admin_login(db: Session, email, password):
    user = db.query(Admin).filter(Admin.email == email).first()

    if not user:
        raise HTTPException(404, "Admin not found")

    if not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return generate_tokens(user.id, "admin")


# WORKER LOGIN (PASSWORD + DEVICE CHECK)
def worker_login(db: Session, phone: str, password: str, device_id: str):

    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(password, worker.password):
        raise HTTPException(400, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    # 🔹 SINGLE DEVICE LOGIN LOGIC
    if worker.device_id and worker.device_id != device_id:
        # new login from another device → replace device
        worker.device_id = device_id
    else:
        worker.device_id = device_id

    worker.is_logged_in = True

    db.commit()

    return generate_tokens(worker.id, "worker")


# 👤 CUSTOMER LOGIN
def customer_login(db: Session, email, password):
    user = db.query(Customer).filter(Customer.email == email).first()

    if not user:
        raise HTTPException(404, "Customer not found")

    if not verify_password(password, user.password):
        raise HTTPException(401, "Invalid credentials")

    return generate_tokens(user.id, "customer")


# FIREBASE LOGIN WORKER
def firebase_worker_login(db: Session, token: str, device_id: str):

    phone = verify_firebase_token(token)

    worker = db.query(Worker).filter(Worker.phone == phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    # 🔹 DEVICE CHECK
    if worker.device_id and worker.device_id != device_id:
        worker.device_id = device_id
    else:
        worker.device_id = device_id

    worker.is_logged_in = True

    db.commit()

    return generate_tokens(worker.id, "worker")

# firebase login for customer
def firebase_customer_login(db, token):

    phone = verify_firebase_token(token)

    customer = db.query(Customer).filter(Customer.phone == phone).first()

    if not customer:
        raise HTTPException(404, "Customer not found")

    return generate_tokens(customer.id, "customer")
