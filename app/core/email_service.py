import smtplib
from email.mime.text import MIMEText
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email_otp(email, otp):

    subject = "Password Reset OTP"
    body = f"Your OTP for password reset is: {otp}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

    server.sendmail(EMAIL_ADDRESS, email, msg.as_string())
    server.quit()
