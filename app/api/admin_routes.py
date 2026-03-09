from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import admin_service
from app.schemas.admin_schema import AdminCreate, AdminUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/admin")
def create_admin(data: AdminCreate, db: Session = Depends(get_db)):
    return admin_service.create_admin(db, data)


@router.get("/")
def get_all_admins(db: Session = Depends(get_db)):
    return admin_service.get_all(db)


@router.get("/{id}")
def get_admin(id: str, db: Session = Depends(get_db)):
    return admin_service.get_by_id(db, id)


@router.put("/{id}")
def update_admin(id: str, data: AdminUpdate, db: Session = Depends(get_db)):
    return admin_service.update(db, id, data)


@router.delete("/{id}")
def delete_admin(id: str, db: Session = Depends(get_db)):
    return admin_service.delete(db, id)