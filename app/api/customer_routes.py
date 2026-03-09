from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import customer_service
from app.schemas.customer_schema import CustomerCreate, CustomerUpdate

router = APIRouter(prefix="/customer", tags=["Customer"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# CREATE CUSTOMER
@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


# GET ALL
@router.get("/all")
def get_customers(db: Session = Depends(get_db)):
    return customer_service.get_all_customers(db)


# GET BY ID
@router.get("/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.get_customer_by_id(db, customer_id)


# UPDATE
@router.put("/{customer_id}")
def update_customer(customer_id: str, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_service.update_customer(db, customer_id, data)


# DELETE
@router.delete("/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    return customer_service.delete_customer(db, customer_id)