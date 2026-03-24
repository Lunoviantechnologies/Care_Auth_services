from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.worker_schema import *
from app.services import worker_service

from app.schemas.worker_schema import (
    WorkerForgotPasswordRequest,
    WorkerVerifyOTPRequest,
    WorkerResetPasswordRequest   
)

# Create router with prefix and tag
router = APIRouter(prefix="/api", tags=["Worker"])


# ---------------- DB DEPENDENCY ----------------
# This creates an async database session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ---------------- REGISTER ----------------
# Create a new worker account
@router.post("/worker/register")
async def register(data: WorkerCreate, db: AsyncSession = Depends(get_db)):
    return await worker_service.create_worker(db, data)


# ---------------- LOGIN ----------------
# Worker login with phone, password, and device_id
@router.post("/worker/login")
async def login(data: WorkerLogin, db: AsyncSession = Depends(get_db)):
    return await worker_service.login_worker(db, data)


# ---------------- PROFILE ----------------
# Upload worker profile image
@router.post("/worker/upload-profile/{worker_id}")
async def upload_profile(
    worker_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await worker_service.upload_profile_image(db, worker_id, file)


# ---------------- AADHAAR ----------------
# Upload Aadhaar front and back images
@router.post("/worker/upload-aadhaar/{worker_id}")
async def upload_aadhaar(
    worker_id: int,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    return await worker_service.upload_aadhar_images(db, worker_id, front, back)


# ---------------- KYC ----------------
# Update KYC details after Aadhaar upload
@router.put("/worker/kyc/{worker_id}")
async def kyc(worker_id: int, data: KYCUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_kyc(db, worker_id, data)


# ---------------- BANK ----------------
# Add or update bank details
@router.put("/worker/bank/{worker_id}")
async def bank(worker_id: int, data: BankUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_bank(db, worker_id, data)


# ---------------- ADDRESS ----------------
# Add or update address details
@router.put("/worker/address/{worker_id}")
async def address(worker_id: int, data: AddressUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_address(db, worker_id, data)


# ---------------- ADMIN ACTIONS ----------------
# Approve worker (admin only)
@router.put("/worker/approve/{worker_id}")
async def approve(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.approve_worker(db, worker_id)


# Reject worker (admin only)
@router.put("/worker/reject/{worker_id}")
async def reject(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.reject_worker(db, worker_id)


# ---------------- LIST WORKERS ----------------
# Get list of workers with pagination, search, sorting
@router.get("/worker/list")
async def list_workers(
    page: int = Query(1, ge=1),          # page number (min 1)
    size: int = Query(10, le=100),       # page size (max 100)
    search: str = None,                  # search by name/email/phone
    sort_by: str = "id",                 # column to sort
    sort_order: str = "desc",            # asc or desc
    db: AsyncSession = Depends(get_db),
):
    return await worker_service.list_workers(db, page, size, search, sort_by, sort_order)


# ---------------- WORKER DETAILS ----------------
# Get single worker details
@router.get("/worker/details/{worker_id}")
async def details(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.get_worker_details(db, worker_id)


# ---------------- UPDATE WORKER ----------------
# Update worker details
@router.put("/worker/update/{worker_id}")
async def update(worker_id: int, data: WorkerUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_worker(db, worker_id, data)


# ---------------- DELETE WORKER ----------------
# Delete worker account
@router.delete("/worker/delete/{worker_id}")
async def delete(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.delete_worker(db, worker_id)


# ---------------- LOGOUT ----------------
# Logout worker (invalidate session)
@router.post("/worker/logout/{worker_id}")
async def logout(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.logout_worker(db, worker_id)


# ---------------- OTP ----------------
# Send OTP to worker email for password reset
@router.post("/worker/send-otp")
async def send_otp(data: WorkerForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await worker_service.send_worker_otp(db, data.email)


# Verify OTP entered by worker
@router.post("/worker/verify-otp")
async def verify_otp(data: WorkerVerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    return await worker_service.verify_worker_otp(db, data.email, data.otp)


# Reset worker password using OTP
@router.post("/worker/reset-password")
async def reset_password(data: WorkerResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    return await worker_service.reset_worker_password(
        db, data.email, data.otp, data.new_password, data.confirm_password
    )

# @router.post("/aadhaar/generate-otp")
# def generate_otp(worker_id: int, aadhaar: str, db: Session = Depends(get_db)):
#     return generate_aadhaar_otp(db, worker_id, aadhaar)


# @router.post("/aadhaar/verify-otp")
# def verify_otp(worker_id: int, otp: str, aadhaar: str, db: Session = Depends(get_db)):
#     return verify_aadhaar_otp(db, worker_id, otp, aadhaar)
