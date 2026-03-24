from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal

from app.schemas.settings_schema import (
    NotificationSettings,
    PrivacySettings,
    SecuritySettings,
    PreferenceSettings,
)

from app.services.settings_service import (
    get_or_create_settings,
    update_notifications,
    update_privacy,
    update_security,
    update_preferences,
)

# Create router
router = APIRouter(prefix="/api/settings", tags=["Settings"])


# ---------------- DB DEPENDENCY ----------------
# Async DB session
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db


# ================= 🔔 NOTIFICATIONS =================


# Get notification settings
@router.get("/notifications/{user_id}")
async def get_notifications(user_id: int, db: AsyncSession = Depends(get_db)):

    settings = await get_or_create_settings(db, user_id)

    return {
        "email_notifications": settings.email_notifications,
        "sms_alerts": settings.sms_alerts,
        "whatsapp_updates": settings.whatsapp_updates,
        "booking_updates": settings.booking_updates,
        "session_reminders": settings.session_reminders,
        "offers_promotions": settings.offers_promotions,
        "newsletter": settings.newsletter,
    }


# Update notification settings
@router.put("/notifications/{user_id}")
async def update_notifications_api(
    user_id: int, data: NotificationSettings, db: AsyncSession = Depends(get_db)
):
    await update_notifications(db, user_id, data)

    return {"message": "Notifications updated successfully"}


# ================= 🔐 PRIVACY =================


# Get privacy settings
@router.get("/privacy/{user_id}")
async def get_privacy(user_id: int, db: AsyncSession = Depends(get_db)):

    settings = await get_or_create_settings(db, user_id)

    return {
        "share_activity_data": settings.share_activity_data,
        "location_access": settings.location_access,
        "analytics_diagnostics": settings.analytics_diagnostics,
        "third_party_sharing": settings.third_party_sharing,
    }


# Update privacy settings
@router.put("/privacy/{user_id}")
async def update_privacy_api(
    user_id: int, data: PrivacySettings, db: AsyncSession = Depends(get_db)
):
    await update_privacy(db, user_id, data)

    return {"message": "Privacy updated successfully"}


# ================= 🔒 SECURITY =================


# Get security settings
@router.get("/security/{user_id}")
async def get_security(user_id: int, db: AsyncSession = Depends(get_db)):

    settings = await get_or_create_settings(db, user_id)

    return {
        "two_factor_auth": settings.two_factor_auth,
        "login_alerts": settings.login_alerts,
        "biometric_login": settings.biometric_login,
    }


# Update security settings
@router.put("/security/{user_id}")
async def update_security_api(
    user_id: int, data: SecuritySettings, db: AsyncSession = Depends(get_db)
):
    await update_security(db, user_id, data)

    return {"message": "Security updated successfully"}


# ================= ⚙️ PREFERENCES =================


# Get user preferences
@router.get("/preferences/{user_id}")
async def get_preferences(user_id: int, db: AsyncSession = Depends(get_db)):

    settings = await get_or_create_settings(db, user_id)

    return {
        "language": settings.language,
        "currency": settings.currency,
        "timezone": settings.timezone,
        "auto_fill_booking": settings.auto_fill_booking,
        "save_default_address": settings.save_default_address,
    }


# Update user preferences
@router.put("/preferences/{user_id}")
async def update_preferences_api(
    user_id: int, data: PreferenceSettings, db: AsyncSession = Depends(get_db)
):
    await update_preferences(db, user_id, data)

    return {"message": "Preferences updated successfully"}
