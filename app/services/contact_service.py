from app.utils.email_utils import send_email
from app.schemas.contact_schema import ContactCreate
from app.core.config import settings
from datetime import datetime


def send_contact_notification(data: ContactCreate):

    subject = f"New Contact Request - {data.full_name}"

    body = f"""
Hello Admin,

You have received a new contact request.

Name         : {data.full_name}
Phone        : {data.phone_number}
Email        : {data.email or "Not Provided"}
City         : {data.city}
Service      : {data.service_required}

Message:
{data.message or "No message"}

Date:
{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    # ✅ send to admin
    send_email(to_email=settings.ADMIN_EMAIL, subject=subject, body=body)

    # ✅ AUTO REPLY (inside function)
    if data.email and data.email.strip():
        try:
            user_subject = "We Received Your Request"

            user_body = f"""
Dear {data.full_name},

Thank you for contacting us!

We have received your request regarding:
"{data.service_required}"

Our team will contact you soon.

Best Regards,
Support Team
"""

            send_email(to_email=data.email, subject=user_subject, body=user_body)

        except Exception as e:
            print("❌ Auto-reply failed:", e)

    return True
