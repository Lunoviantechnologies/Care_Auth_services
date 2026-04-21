from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.service_model import Service
from app.db.models.enums import ServiceCategoryEnum


async def seed_services(db: AsyncSession):
    services = [e.value for e in ServiceCategoryEnum]

    for service_name in services:
        result = await db.execute(select(Service).where(Service.name == service_name))
        existing = result.scalar_one_or_none()

        if not existing:
            db.add(Service(name=service_name))

    await db.commit()
