from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.schemas.worker_schema import *
from app.services import worker_service
from app.services.worker_service import get_worker_by_id  # ✅ FIX
from app.db.models.worker_model import ServiceCategoryEnum
from app.schemas.worker_schema import (
    WorkerForgotPasswordRequest,
    WorkerVerifyOTPRequest,
    WorkerResetPasswordRequest,
)

router = APIRouter(prefix="/api", tags=["Worker"])


# ---------------- DB DEPENDENCY ----------------
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ---------------- REGISTER ----------------
@router.post("/worker/register")
async def register(data: WorkerCreate, db: AsyncSession = Depends(get_db)):
    return await worker_service.create_worker(db, data)


# ---------------- LOGIN ----------------
@router.post("/worker/login")
async def login(data: WorkerLogin, db: AsyncSession = Depends(get_db)):
    return await worker_service.login_worker(db, data)


# ---------------- PROFILE ----------------
@router.post("/worker/upload-profile/{worker_id}")
async def upload_profile(
    worker_id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    return await worker_service.upload_profile_image(db, worker_id, file)


# ---------------- AADHAAR ----------------
@router.post("/worker/upload-aadhaar/{worker_id}")
async def upload_aadhaar(
    worker_id: int,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    return await worker_service.upload_aadhar_images(db, worker_id, front, back)


# ---------------- KYC ----------------
@router.put("/worker/kyc/{worker_id}")
async def kyc(worker_id: int, data: KYCUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_kyc(db, worker_id, data)


# ---------------- BANK ----------------
@router.put("/worker/bank/{worker_id}")
async def bank(worker_id: int, data: BankUpdate, db: AsyncSession = Depends(get_db)):
    return await worker_service.update_bank(db, worker_id, data)


# ---------------- ADDRESS ----------------
@router.put("/worker/address/{worker_id}")
async def address(
    worker_id: int, data: AddressUpdate, db: AsyncSession = Depends(get_db)
):
    return await worker_service.update_address(db, worker_id, data)


# ---------------- ADMIN ----------------
@router.put("/worker/approve/{worker_id}")
async def approve(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.approve_worker(db, worker_id)


@router.put("/worker/reject/{worker_id}")
async def reject(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.reject_worker(db, worker_id)


# ---------------- LIST ----------------
@router.get("/worker/list")
async def list_workers(
    page: int = Query(1, ge=1),
    size: int = Query(10, le=100),
    search: str = None,
    sort_by: str = "id",
    sort_order: str = "desc",
    service_category: str = None,   # ✅ changed to string
    db: AsyncSession = Depends(get_db),
):
    return await worker_service.list_workers(
        db,
        page,
        size,
        search,
        sort_by,
        sort_order,
        service_category,
    )


# ---------------- GET WORKER (FIXED) ----------------
@router.get("/worker/{worker_id}")
async def get_worker(worker_id: int, db: AsyncSession = Depends(get_db)):

    worker = await get_worker_by_id(worker_id, db)  # ✅ await

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    return {
        "id": worker.id,
        "full_name": worker.full_name,
        "phone": worker.phone,
        "gender": worker.gender,
        "age": worker.age,
        "status": worker.status.value if worker.status else None,
        "availability": worker.availability.value if worker.availability else None,
        "rating": worker.rating,
    }


# ---------------- UPDATE ----------------
@router.put("/worker/update/{worker_id}")
async def update(
    worker_id: int, data: WorkerUpdate, db: AsyncSession = Depends(get_db)
):
    return await worker_service.update_worker(db, worker_id, data)


# ---------------- DELETE ----------------
@router.delete("/worker/delete/{worker_id}")
async def delete(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.delete_worker(db, worker_id)


# ---------------- LOGOUT ----------------
@router.post("/worker/logout/{worker_id}")
async def logout(worker_id: int, db: AsyncSession = Depends(get_db)):
    return await worker_service.logout_worker(db, worker_id)


# ---------------- OTP ----------------
@router.post("/worker/send-otp")
async def send_otp(
    data: WorkerForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    return await worker_service.send_worker_otp(db, data.email)


@router.post("/worker/verify-otp")
async def verify_otp(data: WorkerVerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    return await worker_service.verify_worker_otp(db, data.email, data.otp)


@router.post("/worker/reset-password")
async def reset_password(
    data: WorkerResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    return await worker_service.reset_worker_password(
        db, data.email, data.otp, data.new_password, data.confirm_password
    )


# ---------------- VALIDATE (FIXED) ----------------
@router.get("/worker/validate/{worker_id}")
async def validate_worker(worker_id: int, db: AsyncSession = Depends(get_db)):

    worker = await get_worker_by_id(worker_id, db)

    if not worker:
        return {"valid": False, "message": "Worker not found"}

    if worker.status.value != "approved":
        return {"valid": False, "message": "Not approved"}

    if worker.availability.value != "online":
        return {"valid": False, "message": "Offline"}

    return {"valid": True}
