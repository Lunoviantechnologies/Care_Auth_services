from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import worker_service
from app.schemas.worker_schema import *

router = APIRouter(prefix="/worker", tags=["Worker"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(data: WorkerCreate, db: Session = Depends(get_db)):
    return worker_service.create_worker(db, data)


@router.post("/login")
def login(data: WorkerLogin, db: Session = Depends(get_db)):
    return worker_service.login_worker(db, data)


@router.post("/upload-profile/{worker_id}")
def upload_profile(
    worker_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    return worker_service.upload_profile_image(db, worker_id, file)


@router.post("/upload-aadhar/{worker_id}")
def upload_aadhar(
    worker_id: int,
    front: UploadFile = File(...),
    back: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return worker_service.upload_aadhar_images(db, worker_id, front, back)


@router.put("/kyc/{worker_id}")
def kyc(worker_id: int, data: KYCUpdate, db: Session = Depends(get_db)):
    return worker_service.update_kyc(db, worker_id, data)


@router.put("/bank/{worker_id}")
def bank(worker_id: int, data: BankUpdate, db: Session = Depends(get_db)):
    return worker_service.update_bank(db, worker_id, data)


@router.put("/address/{worker_id}")
def address(worker_id: int, data: AddressUpdate, db: Session = Depends(get_db)):
    return worker_service.update_address(db, worker_id, data)


@router.put("/approve/{worker_id}")
def approve(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.approve_worker(db, worker_id)


@router.put("/reject/{worker_id}")
def reject(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.reject_worker(db, worker_id)


@router.get("/list")
def list_workers(db: Session = Depends(get_db)):
    return worker_service.list_workers(db)


@router.get("/details/{worker_id}")
def worker_details(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.get_worker_details(db, worker_id)


@router.delete("/delete/{worker_id}")
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.delete_worker(db, worker_id)


@router.post("/logout/{worker_id}")
def logout(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.logout_worker(db, worker_id)


@router.put("/update-worker/{worker_id}")
def update_worker(worker_id: int, data: WorkerUpdate, db: Session = Depends(get_db)):
    return worker_service.update_worker(db, worker_id, data)


@router.get("/dashboard/{worker_id}")
def dashboard(worker_id: int, db: Session = Depends(get_db)):
    return worker_service.get_dashboard_data(db, worker_id)
