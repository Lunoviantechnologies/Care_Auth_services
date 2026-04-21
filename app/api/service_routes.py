from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.service_model import Service

router = APIRouter(prefix="/api/services", tags=["Services"])


@router.get("/")
async def get_services(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service))
    services = result.scalars().all()

    return [{"id": s.id, "name": s.name} for s in services]


@router.get("/{service_id}")
async def get_service_by_id(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return {"id": service.id, "name": service.name}
