from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

from app.services.auth_service import (
    admin_login,
    firebase_worker_login,
    firebase_customer_login,
    worker_login,
    customer_login
  
)
router = APIRouter(prefix="/auth")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#  ADMIN LOGIN
@router.post("/admin/login")
def login_admin(data: dict, db: Session = Depends(get_db)):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(400, "Email and password required")

    return {"data": admin_login(db, data["email"], data["password"])}


#  WORKER LOGIN (PASSWORD)
@router.post("/worker/login")
def login_worker(data: dict, db: Session = Depends(get_db)):
    if not data.get("phone") or not data.get("password"):
        raise HTTPException(400, "Phone and password required")

    return {"data": worker_login(db, data["phone"], data["password"])}


#  CUSTOMER LOGIN
@router.post("/customer/login")
def login_customer(data: dict, db: Session = Depends(get_db)):
    if not data.get("email") or not data.get("password"):
        raise HTTPException(400, "Email and password required")

    return {"data": customer_login(db, data["email"], data["password"])}



#firebase login for worker
@router.post("/worker/firebase-login")
def worker_login(data: dict, db: Session = Depends(get_db)):

    if not data.get("token"):
        raise HTTPException(400, "Firebase token required")

    return {"data": firebase_worker_login(db, data["token"])}

#firebase login for customer
@router.post("/customer/firebase-login")
def customer_login(data: dict, db: Session = Depends(get_db)):

    if not data.get("token"):
        raise HTTPException(400, "Firebase token required")

    return {"data": firebase_customer_login(db, data["token"])}