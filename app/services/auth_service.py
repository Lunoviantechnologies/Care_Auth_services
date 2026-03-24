from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
async def admin_login(db: AsyncSession, email: str, password: str):

    result = await db.execute(
        select(Admin).where(Admin.email == email)
    )
    admin = result.scalar_one_or_none()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if not verify_password(password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return generate_tokens(admin.id, "admin")


# ---------------- WORKER LOGIN ----------------
async def worker_login(db: AsyncSession, phone: str, password: str, device_id: str):

    result = await db.execute(
        select(Worker).where(Worker.phone == phone)
    )
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    if not verify_password(password, worker.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(status_code=403, detail="Wait for admin approval")

    # SINGLE DEVICE LOGIN
    worker.device_id = device_id
    worker.is_logged_in = True

    await db.commit()

    return generate_tokens(worker.id, "worker")


# ---------------- CUSTOMER LOGIN ----------------
async def customer_login(db: AsyncSession, phone: str, password: str):

    result = await db.execute(
        select(Customer).where(Customer.phone == phone)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer with this phone number not found"
        )

    if not verify_password(password, customer.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    if not customer.isActive:
        raise HTTPException(
            status_code=403,
            detail="Customer account is inactive"
        )

    return generate_tokens(customer.id, "customer")


# ---------------- WORKER FIREBASE LOGIN ----------------
async def firebase_worker_login(db: AsyncSession, token: str, device_id: str):

    # ⚠️ If this function is sync, keep as is
    phone = verify_firebase_token(token)

    result = await db.execute(
        select(Worker).where(Worker.phone == phone)
    )
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    if not worker.is_admin_approved:
        raise HTTPException(status_code=403, detail="Wait for admin approval")

    worker.device_id = device_id
    worker.is_logged_in = True

    await db.commit()

    return generate_tokens(worker.id, "worker")


# ---------------- CUSTOMER FIREBASE LOGIN ----------------
async def firebase_customer_login(db: AsyncSession, token: str):

    phone = verify_firebase_token(token)

    result = await db.execute(
        select(Customer).where(Customer.phone == phone)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return generate_tokens(customer.id, "customer")