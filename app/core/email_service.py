import smtplib
from email.mime.text import MIMEText
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email_otp(email, otp):

    subject = "Password Reset Verification Code"

    body = f"""
Dear User,

We received a request to reset the password for your account.

Your One-Time Password (OTP) for password reset is:

OTP: {otp}

This OTP is valid for a limited time. Please do not share this code with anyone for security reasons.

If you did not request a password reset, please ignore this email or contact our support team immediately.

Best Regards,  
Support Team  
Baby_Care team
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    server.quit()
