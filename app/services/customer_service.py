from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.customer_model import Customer
from app.core.security import hash_password
from datetime import datetime


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
def get_all_customers(db: Session):
    customers = db.query(Customer).all()
    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")
    return customers


# GET CUSTOMER BY ID
def get_customer_by_id(db: Session, customer_id: str):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return customer


# UPDATE CUSTOMER
def update_customer(db: Session, customer_id: str, data):
    customer = get_customer_by_id(db, customer_id)

    try:
        if data.name is not None:
            customer.name = data.name

        if data.email is not None:
            customer.email = data.email

        if data.phone is not None:
            customer.phone = data.phone

        if data.address is not None:
            customer.address = data.address

        if data.city is not None:
            customer.city = data.city

        if data.isVerified is not None:
            customer.isVerified = data.isVerified

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