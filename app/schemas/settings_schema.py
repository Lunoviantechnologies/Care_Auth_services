from pydantic import BaseModel


# 🔔 Notifications
class NotificationSettings(BaseModel):
    email_notifications: bool
    sms_alerts: bool
    whatsapp_updates: bool
    booking_updates: bool
    session_reminders: bool
    offers_promotions: bool
    newsletter: bool


# 🔐 Privacy
class PrivacySettings(BaseModel):
    share_activity_data: bool
    location_access: bool
    analytics_diagnostics: bool
    third_party_sharing: bool


# 🔒 Security
class SecuritySettings(BaseModel):
    two_factor_auth: bool
    login_alerts: bool
    biometric_login: bool


# ⚙️ Preferences
class PreferenceSettings(BaseModel):
    language: str
    currency: str
    timezone: str
    auto_fill_booking: bool
    save_default_address: bool