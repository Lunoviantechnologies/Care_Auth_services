from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import os
from uuid import uuid4
import asyncio

from app.db.session import AsyncSessionLocal
from app.services import customer_service
from app.schemas.customer_schema import (
    CustomerCreate,
    CustomerForgotPasswordRequest,
    CustomerVerifyOTPRequest,
    CustomerResetPasswordRequest,
)

# Create router
router = APIRouter(prefix="/api", tags=["Customer"])

# Upload directory
UPLOAD_DIR = "app/uploads/profile"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- DB DEPENDENCY ----------------
# Async DB session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ---------------- CREATE CUSTOMER ----------------
@router.post("/customer/create", status_code=status.HTTP_200_OK)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await customer_service.create_customer(db, data)


# ---------------- GET ALL CUSTOMERS ----------------
@router.get("/customer/all")
async def get_customers(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort_by: str = "id",
    order: str = "asc",
    name: str = None,
    email: str = None,
    db: AsyncSession = Depends(get_db),
):
    return await customer_service.get_all_customers(
        db, page, size, sort_by, order, name, email
    )


# ---------------- GET CUSTOMER BY ID ----------------
@router.get("/customer/get/{customer_id}")
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    return await customer_service.get_customer_by_id(db, customer_id)


# ---------------- UPDATE CUSTOMER (WITH IMAGE) ----------------
@router.put("/customer/update/{customer_id}")
async def update_customer(
    customer_id: int,
    name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    isVerified: bool = Form(None),
    profile_image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):

    image_url = None

    # Handle image upload
    if profile_image:

        # Validate file type
        if not profile_image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files allowed")

        # Generate unique filename
        file_ext = profile_image.filename.split(".")[-1]
        filename = f"{uuid4()}.{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Save file (non-blocking)
        content = await profile_image.read()
        await asyncio.to_thread(save_file, file_path, content)

        image_url = f"/uploads/profile/{filename}"

    # Call service
    return await customer_service.update_customer(
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


# Helper function for file saving
def save_file(path, content):
    with open(path, "wb") as f:
        f.write(content)


# ---------------- DELETE CUSTOMER ----------------
@router.delete("/customer/delete/{customer_id}")
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    return await customer_service.delete_customer(db, customer_id)


# ---------------- OTP ----------------
# Send OTP
@router.post("/customer/send-otp")
async def send_customer_otp(
    data: CustomerForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    return await customer_service.send_customer_otp(db, data.email)


# Verify OTP
@router.post("/customer/verify-otp")
async def verify_customer_otp(
    data: CustomerVerifyOTPRequest, db: AsyncSession = Depends(get_db)
):
    return await customer_service.verify_customer_otp(db, data.email, data.otp)


# Reset password
@router.post("/customer/reset-password")
async def reset_customer_password(
    data: CustomerResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    return await customer_service.reset_customer_password(
        db, data.email, data.otp, data.new_password, data.confirm_password
    )