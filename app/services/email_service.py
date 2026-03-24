import smtplib
import asyncio
from email.mime.text import MIMEText
import os

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("EMAIL_PASSWORD")


def _send_email_sync(to_email: str, subject: str, body: str):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, to_email, msg.as_string())
        server.quit()

    except Exception as e:
        print("❌ Email Error:", str(e))


# ✅ ASYNC WRAPPER
async def send_email(to_email: str, subject: str, body: str):
    await asyncio.to_thread(_send_email_sync, to_email, subject, body)