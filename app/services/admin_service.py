from sqlalchemy.orm import Session
from app.db.models.admin_model import Admin
from app.core.security import hash_password
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


def create_admin(db: Session, data):
    try:
        # check if email already exists
        existing_admin = db.query(Admin).filter(Admin.email == data.email).first()
        if existing_admin:
            raise HTTPException(
                status_code=400,
                detail="Admin with this email already exists"
            )

        admin = Admin(
            name=data.name,
            email=data.email,
            password=hash_password(data.password),
            role=data.role
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        return {"message": "Admin created successfully", "data": admin}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Admin creation failed: {str(e)}"
        )


def get_all(db: Session):
    try:
        admins = db.query(Admin).all()
        return admins
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch admins")


def get_by_id(db: Session, id: str):
    admin = db.query(Admin).filter(Admin.id == id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin


def update(db: Session, id: str, data):
    try:
        admin = get_by_id(db, id)

        if data.name:
            admin.name = data.name
        if data.email:
            admin.email = data.email
        if data.role:
            admin.role = data.role
        if data.isActive is not None:
            admin.isActive = data.isActive

        db.commit()
        db.refresh(admin)

        return {"message": "Admin updated successfully", "data": admin}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Admin update failed: {str(e)}"
        )


def delete(db: Session, id: str):
    try:
        admin = get_by_id(db, id)

        db.delete(admin)
        db.commit()

        return {"message": "Admin deleted successfully"}

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Admin deletion failed: {str(e)}"
        )