from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.complaint_schema import *
from app.services.complaint_service import *

router = APIRouter(prefix="/api/complaints", tags=["Complaints"])

# TEMP USER
DUMMY_USER_ID = 1


# ================= CREATE =================
@router.post("/create")
async def create(
    data: ComplaintCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_complaint(data, DUMMY_USER_ID, db)


# ================= GET ALL =================
@router.get("/all")
async def get_all(
    page: int = 1,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    return await list_complaints(db, page, size)


# ================= GET BY ID =================
@router.get("/{complaint_id}")
async def get_one(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
):
    complaint = await get_complaint_by_id(complaint_id, db)

    if not complaint:
        raise HTTPException(404, "Complaint not found")

    return complaint


# ================= ADMIN ACTION =================
@router.post("/action/{complaint_id}")
async def action(
    complaint_id: int,
    data: ComplaintAction,
    db: AsyncSession = Depends(get_db),
):
    complaint, msg = await take_action(complaint_id, data.action, db)

    if not complaint:
        raise HTTPException(400, msg)

    return {"message": msg}


# ================= DELETE =================
@router.delete("/{complaint_id}")
async def delete(
    complaint_id: int,
    db: AsyncSession = Depends(get_db),
):
    success = await delete_complaint(complaint_id, db)

    if not success:
        raise HTTPException(404, "Complaint not found")

    return {"message": "Deleted successfully"}
