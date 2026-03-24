from sqlalchemy import Column, Integer, Boolean, String
from app.db.session import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False)

    # 🔔 Notifications
    email_notifications = Column(Boolean, default=True)
    sms_alerts = Column(Boolean, default=True)
    whatsapp_updates = Column(Boolean, default=False)
    booking_updates = Column(Boolean, default=True)
    session_reminders = Column(Boolean, default=True)
    offers_promotions = Column(Boolean, default=False)
    newsletter = Column(Boolean, default=False)

    # 🔐 Privacy
    share_activity_data = Column(Boolean, default=False)
    location_access = Column(Boolean, default=True)
    analytics_diagnostics = Column(Boolean, default=True)
    third_party_sharing = Column(Boolean, default=False)

    # 🔒 Security
    two_factor_auth = Column(Boolean, default=False)
    login_alerts = Column(Boolean, default=True)
    biometric_login = Column(Boolean, default=False)

    # ⚙️ Preferences
    language = Column(String, default="English,hindi,telugu,kannada,marathi,bengali,tamil,urdu,gujarati,odia,punjabi,assamese,maithili")
    currency = Column(String, default="INR")
    timezone = Column(String, default="Asia/Kolkata")
    auto_fill_booking = Column(Boolean, default=False)
    save_default_address = Column(Boolean, default=True)