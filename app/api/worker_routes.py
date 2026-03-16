from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from app.db.session import SessionLocal
from app.services import worker_service
from app.schemas.worker_schema import *
from app.schemas.worker_schema import (
    WorkerForgotPasswordRequest,
    WorkerVerifyOTPRequest,
    WorkerResetPasswordRequest
)

router = APIRouter(prefix="/api", tags=["Worker"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/worker/register")
def register(data: WorkerCreate, db: Session = Depends(get_db)):
    return worker_service.create_worker(db, data)


@router.post("/worker/login")
def login(data: WorkerLogin, db: Session = Depends(get_db)):
    return worker_service.login_worker(db, data)


@router.post("/worker/upload-profile/{worker_id}")
def upload_profile(
    worker_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    return worker_service.upload_profile_image(db, worker_id, file)


@router.post("/worker/upload-aadhar/{worker_id}")
def upload_aadhar(
    worker_id: int,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return worker_service.upload_aadhar_images(db, worker_id, front, back)


@router.put("/worker/kyc/{worker_id}")
def kyc(worker_id: int, data: KYCUpdate, db: Session = Depends(get_db)):
    return worker_service.update_kyc(db, worker_id, data)


@router.put("/worker/bank/{worker_id}")
def bank(worker_id: int, data: BankUpdate, db: Session = Depends(get_db)):
    return worker_service.update_bank(db, worker_id, data)


@router.put("/worker/address/{worker_id}")
def address(worker_id: int, data: AddressUpdate, db: Session = Depends(get_db)):
    return worker_service.update_address(db, worker_id, data)


@router.put("/worker/approve/{worker_id}")
def approve(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.approve_worker(db, worker_id)


@router.put("/worker/reject/{worker_id}")
def reject(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.reject_worker(db, worker_id)


@router.get("/worker/list")
def list_workers(
    page: int = Query(1, ge=1),
    size: int = Query(10, le=100),
    search: str = Query(None),
    sort_by: str = Query("id"),
    sort_order: str = Query("desc"),
    db: Session = Depends(get_db)
):
    return worker_service.list_workers(
        db,
        page,
        size,
        search,
        sort_by,
        sort_order
    )


@router.get("/worker/details/{worker_id}")
def worker_details(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.get_worker_details(db, worker_id)


@router.delete("/worker/delete/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.delete_worker(db, worker_id)


@router.post("/worker/logout/{worker_id}")
def logout(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.logout_worker(db, worker_id)


@router.put("/worker/update/{worker_id}")
def update_worker(worker_id: int, data: WorkerUpdate, db: Session = Depends(get_db)):
    return worker_service.update_worker(db, worker_id, data)


@router.get("/dashboard/{worker_id}")
def dashboard(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.get_dashboard_data(db, worker_id)

@router.post("/worker/send-otp")
def send_worker_otp(data: WorkerForgotPasswordRequest, db: Session = Depends(get_db)):
    return worker_service.send_worker_otp(db, data.email)

@router.post("/worker/verify-otp")
def verify_worker_otp(data: WorkerVerifyOTPRequest, db: Session = Depends(get_db)):
    return worker_service.verify_worker_otp(db, data.email, data.otp)

@router.post("/worker/reset-password")
def reset_worker_password(data: WorkerResetPasswordRequest, db: Session = Depends(get_db)):
    return worker_service.reset_worker_password(
        db,
        data.email,
        data.otp,
        data.new_password,
        data.confirm_password
    )
