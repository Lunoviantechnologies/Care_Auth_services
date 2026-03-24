from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.settings_model import UserSettings


# 🔥 GET OR CREATE SETTINGS
async def get_or_create_settings(db: AsyncSession, user_id: int):

    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user_id)
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return settings


# 🔔 NOTIFICATIONS
async def update_notifications(db: AsyncSession, user_id: int, data):

    settings = await get_or_create_settings(db, user_id)

    for key, value in data.dict().items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings


# 🔐 PRIVACY
async def update_privacy(db: AsyncSession, user_id: int, data):

    settings = await get_or_create_settings(db, user_id)

    for key, value in data.dict().items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings


# 🔒 SECURITY
async def update_security(db: AsyncSession, user_id: int, data):

    settings = await get_or_create_settings(db, user_id)

    for key, value in data.dict().items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings


# ⚙️ PREFERENCES
async def update_preferences(db: AsyncSession, user_id: int, data):

    settings = await get_or_create_settings(db, user_id)

    for key, value in data.dict().items():
        setattr(settings, key, value)

    await db.commit()
    await db.refresh(settings)

    return settings