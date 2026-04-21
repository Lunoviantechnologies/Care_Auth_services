from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from app.db.models.complaint import Complaint
from app.db.models.worker_model import Worker


# ================= CREATE =================
async def create_complaint(data, customer_id, db: AsyncSession):
    complaint = Complaint(
        customer_id=customer_id,
        worker_id=data.worker_id,
        booking_id=data.booking_id,
        title=data.title,
        description=data.description,
    )

    db.add(complaint)
    await db.commit()
    await db.refresh(complaint)

    return complaint


# ================= GET ALL =================
async def list_complaints(
    db: AsyncSession,
    page: int = 1,
    size: int = 10,
):
    query = select(Complaint)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    data = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "data": data,
    }


# ================= GET BY ID =================
async def get_complaint_by_id(complaint_id: int, db: AsyncSession):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    return result.scalar_one_or_none()


# ================= ADMIN ACTION =================
async def take_action(complaint_id: int, action: str, db: AsyncSession):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()

    if not complaint:
        return None, "Complaint not found"

    worker_result = await db.execute(
        select(Worker).where(Worker.id == complaint.worker_id)
    )
    worker = worker_result.scalar_one_or_none()

    if action == "resolve":
        complaint.status = "resolved"

    elif action == "reject":
        complaint.status = "rejected"

    elif action == "ban":
        complaint.status = "banned"

        if worker:
            worker.is_banned = True
            worker.banned_until = datetime.utcnow() + timedelta(days=30)

    else:
        return None, "Invalid action"

    complaint.admin_action = action

    await db.commit()

    return complaint, f"{action} applied"


# ================= DELETE =================
async def delete_complaint(complaint_id: int, db: AsyncSession):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()

    if not complaint:
        return False

    await db.delete(complaint)
    await db.commit()

    return True
