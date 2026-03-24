import os
import random
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.customer_model import Customer
from app.db.models.otp_model import OTP
from app.core.security import hash_password
from app.core.email_service import send_email_otp


PROFILE_DIR = "app/uploads/profile"
os.makedirs(PROFILE_DIR, exist_ok=True)


# ---------------- CREATE CUSTOMER ----------------
async def create_customer(db: AsyncSession, data):

    # Check email
    result = await db.execute(
        select(Customer).where(Customer.email == data.email)
    )
    existing_email = result.scalar_one_or_none()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check phone
    result = await db.execute(
        select(Customer).where(Customer.phone == data.phone)
    )
    existing_phone = result.scalar_one_or_none()

    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")

    try:
        customer = Customer(
            name=data.name,
            email=data.email,
            phone=data.phone,
            password=hash_password(data.password),
            address=data.address,
            city=data.city,
            createdAt=datetime.utcnow()
        )

        db.add(customer)
        await db.commit()
        await db.refresh(customer)

        return customer

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- GET ALL CUSTOMERS ----------------
async def get_all_customers(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
    sort_by: str = "id",
    order: str = "asc",
    name: str = None,
    email: str = None
):

    query = select(Customer)

    # Filtering
    if name:
        query = query.where(Customer.name.ilike(f"%{name}%"))

    if email:
        query = query.where(Customer.email.ilike(f"%{email}%"))

    # Sorting
    if hasattr(Customer, sort_by):
        column = getattr(Customer, sort_by)
        query = query.order_by(column.desc() if order == "desc" else column.asc())

    # Execute
    result = await db.execute(query)
    customers = result.scalars().all()

    total = len(customers)

    # Pagination (manual slicing)
    start = (page - 1) * size
    end = start + size
    paginated = customers[start:end]

    if not paginated:
        raise HTTPException(status_code=404, detail="No customers found")

    return {
        "total_records": total,
        "page": page,
        "size": size,
        "data": paginated
    }


# ---------------- GET CUSTOMER BY ID ----------------
async def get_customer_by_id(db: AsyncSession, customer_id: int):

    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


# ---------------- UPDATE CUSTOMER ----------------
async def update_customer(
    db: AsyncSession,
    customer_id: int,
    name=None,
    email=None,
    phone=None,
    address=None,
    city=None,
    isVerified=None,
    profile_image=None
):
    customer = await get_customer_by_id(db, customer_id)

    try:
        if name is not None:
            customer.name = name

        if email is not None:
            customer.email = email

        if phone is not None:
            customer.phone = phone

        if address is not None:
            customer.address = address

        if city is not None:
            customer.city = city

        if isVerified is not None:
            customer.isVerified = isVerified

        if profile_image is not None:
            customer.profile_image = profile_image

        await db.commit()
        await db.refresh(customer)

        return customer

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- DELETE CUSTOMER ----------------
async def delete_customer(db: AsyncSession, customer_id: int):

    customer = await get_customer_by_id(db, customer_id)

    try:
        await db.delete(customer)
        await db.commit()

        return {"message": "Customer deleted successfully"}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- SEND OTP ----------------
async def send_customer_otp(db: AsyncSession, email: str):

    result = await db.execute(
        select(Customer).where(Customer.email == email)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    otp_code = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(otp_record)
    await db.commit()

    # If email function is sync → wrap it
    import asyncio
    await asyncio.to_thread(send_email_otp, email, otp_code)

    return {"message": "OTP sent to email"}


# ---------------- VERIFY OTP ----------------
async def verify_customer_otp(db: AsyncSession, email: str, otp: str):

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


# ---------------- RESET PASSWORD ----------------
async def reset_customer_password(
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
        select(Customer).where(Customer.email == email)
    )
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.password = hash_password(new_password)

    await db.commit()

    return {"message": "Customer password reset successfully"}