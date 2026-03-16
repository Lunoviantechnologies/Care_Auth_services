from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.db.session import get_db
from app.services import customer_service
from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerUpdate,
    CustomerForgotPasswordRequest,
    CustomerVerifyOTPRequest,
    CustomerResetPasswordRequest
)

router = APIRouter(prefix="/api", tags=["Customer"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE CUSTOMER
@router.post("/customer/create", status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


# GET ALL
@router.get("/all")
def get_customers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort_by: str = "id",
    order: str = "asc",
    name: str = None,
    email: str = None,
    db: Session = Depends(get_db)
):

    return customer_service.get_all_customers(
        db,
        page,
        size,
        sort_by,
        order,
        name,
        email
    )


# GET BY ID
@router.get("/get/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.get_customer_by_id(db, customer_id)


# UPDATE
@router.put("/update/{customer_id}")
def update_customer(
    customer_id: str, data: CustomerUpdate, db: Session = Depends(get_db)
):
    return customer_service.update_customer(db, customer_id, data)


# DELETE
@router.delete("/delete/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.delete_customer(db, customer_id)

@router.post("/customer/send-otp")
def send_customer_otp(data: CustomerForgotPasswordRequest, db: Session = Depends(get_db)):
    return customer_service.send_customer_otp(db, data.email)

@router.post("/customer/verify-otp")
def verify_customer_otp(data: CustomerVerifyOTPRequest, db: Session = Depends(get_db)):
    return customer_service.verify_customer_otp(db, data.email, data.otp)

@router.post("/customer/reset-password")
def reset_customer_password(data: CustomerResetPasswordRequest, db: Session = Depends(get_db)):

    return customer_service.reset_customer_password(
        db,
        data.email,
        data.otp,
        data.new_password,
        data.confirm_password
    )
