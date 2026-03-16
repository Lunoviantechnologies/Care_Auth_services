from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import admin_service
from app.schemas.admin_schema import AdminCreate, AdminUpdate

from app.schemas.admin_schema import (
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
)

router = APIRouter(prefix="/api", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/admin/create")
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    return admin_service.create_admin(db, data)


@router.get("/admin/all")
def get_all_admins(db: Session = Depends(get_db)):
    return admin_service.get_all(db)


@router.get("/admin/get/{id}")
def get_admin(id: str, db: Session = Depends(get_db)):
    return admin_service.get_by_id(db, id)


@router.put("/admin/update/{id}")
def update_admin(id: str, data: AdminUpdate, db: Session = Depends(get_db)):
    return admin_service.update(db, id, data)


@router.delete("/admin/delete/{id}")
def delete_admin(id: str, db: Session = Depends(get_db)):
    return admin_service.delete(db, id)


@router.post("/admin/send-otp")
def send_admin_otp(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return admin_service.send_otp(db, data.email)

@router.post("/admin/verify-otp")
def verify_admin_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return admin_service.verify_otp(db, data.email, data.otp)

@router.post("/admin/reset-password")
def reset_admin_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    return admin_service.reset_password(
        db,
        data.email,
        data.otp,
        data.new_password,
        data.confirm_password
    )

