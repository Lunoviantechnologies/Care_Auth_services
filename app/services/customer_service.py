import os
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.customer_model import Customer
from app.core.security import hash_password
from datetime import datetime
import random
from datetime import datetime, timedelta
from app.db.models.otp_model import OTP
from app.core.email_service import send_email_otp
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.customer_model import Customer

PROFILE_DIR = "app/uploads/profile"
os.makedirs(PROFILE_DIR, exist_ok=True)

# CREATE CUSTOMER
def create_customer(db: Session, data):

    # Check email already exists
    existing_email = db.query(Customer).filter(Customer.email == data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Check phone already exists
    existing_phone = db.query(Customer).filter(Customer.phone == data.phone).first()
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
        db.commit()
        db.refresh(customer)

        return customer

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))



# GET ALL CUSTOMERS
def get_all_customers(
    db: Session,
    page: int = 0,
    size: int = 10,
    sort_by: str = "id",
    order: str = "asc",
    name: str = None,
    email: str = None
):

    query = db.query(Customer)

    # 🔎 Filtering
    if name:
        query = query.filter(Customer.name.ilike(f"%{name}%"))

    if email:
        query = query.filter(Customer.email.ilike(f"%{email}%"))

    # 🔃 Sorting
    if hasattr(Customer, sort_by):
        column = getattr(Customer, sort_by)

        if order == "desc":
            query = query.order_by(column.desc())
        else:
            query = query.order_by(column.asc())

    # 📄 Pagination
    total = query.count()

    customers = query.offset((page - 1) * size).limit(size).all()

    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")

    return {
        "total_records": total,
        "page": page,
        "size": size,
        "data": customers
    }


# GET CUSTOMER BY ID
def get_customer_by_id(db: Session, customer_id: str):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


def update_customer(
    db: Session,
    customer_id: int,
    name=None,
    email=None,
    phone=None,
    address=None,
    city=None,
    isVerified=None,
    profile_image=None
):
    customer = get_customer_by_id(db, customer_id)

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

        # ✅ IMAGE UPDATE
        if profile_image is not None:
            customer.profile_image = profile_image

        db.commit()
        db.refresh(customer)

        return customer

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# DELETE CUSTOMER
def delete_customer(db: Session, customer_id: str):
    customer = get_customer_by_id(db, customer_id)

    try:
        db.delete(customer)
        db.commit()
        return {"message": "Customer deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    # SEND OTP FOR CUSTOMER
def send_customer_otp(db: Session, email: str):

    customer = db.query(Customer).filter(Customer.email == email).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    otp_code = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp_code,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(otp_record)
    db.commit()

    send_email_otp(email, otp_code)

    return {"message": "OTP sent to email"}

# VERIFY OTP
def verify_customer_otp(db: Session, email: str, otp: str):

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
def reset_customer_password(db: Session, email: str, otp: str, new_password: str, confirm_password: str):

    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    otp_record = db.query(OTP).filter(
        OTP.email == email,
        OTP.otp == otp
    ).order_by(OTP.id.desc()).first()

    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    customer = db.query(Customer).filter(Customer.email == email).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    customer.password = hash_password(new_password)

    db.commit()

    return {"message": "Customer password reset successfully"}