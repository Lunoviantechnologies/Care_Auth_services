from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from app.db.session import SessionLocal
from app.services import customer_service
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
    CustomerResetPasswordRequest,
)

router = APIRouter(prefix="/api", tags=["Customer"])

UPLOAD_DIR = "app/uploads/profile"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE CUSTOMER
@router.post("/customer/create", status_code=status.HTTP_200_OK)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


# GET ALL
# GET ALL (FIXED)
@router.get("/all")
def get_customers(
    page: int = Query(1, ge=1),  # ✅ FIXED
    size: int = Query(10, ge=1),
    sort_by: str = "id",
    order: str = "asc",
    name: str = None,
    email: str = None,
    db: Session = Depends(get_db),
):
    return customer_service.get_all_customers(
        db, page, size, sort_by, order, name, email
    )


# GET BY ID
@router.get("/get/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.get_customer_by_id(db, customer_id)


# UPDATE
#  UPDATE CUSTOMER (WITH IMAGE)
@router.put("/update/{customer_id}")
async def update_customer(
    customer_id: int,
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    isVerified: bool = Form(None),
    profile_image: UploadFile = File(None),
    db: Session = Depends(get_db),
):

    image_url = None

    #  Handle image upload
    if profile_image:
        if not profile_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files allowed")

        file_ext = profile_image.filename.split(".")[-1]
        filename = f"{uuid4()}.{file_ext}"

        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await profile_image.read())

        image_url = f"/uploads/profile/{filename}"

    #  Send all data to service
    return customer_service.update_customer(
        db=db,
        customer_id=customer_id,
        name=name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        isVerified=isVerified,
        profile_image=image_url,
    )


# DELETE
@router.delete("/delete/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.delete_customer(db, customer_id)


@router.post("/customer/send-otp")
def send_customer_otp(
    data: CustomerForgotPasswordRequest, db: Session = Depends(get_db)
):
    return customer_service.send_customer_otp(db, data.email)


@router.post("/customer/verify-otp")
def verify_customer_otp(data: CustomerVerifyOTPRequest, db: Session = Depends(get_db)):
    return customer_service.verify_customer_otp(db, data.email, data.otp)


@router.post("/customer/reset-password")
def reset_customer_password(
    data: CustomerResetPasswordRequest, db: Session = Depends(get_db)
):

    return customer_service.reset_customer_password(
        db, data.email, data.otp, data.new_password, data.confirm_password
    )
