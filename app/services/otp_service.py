import requests
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")


# 📱 SEND OTP
def send_otp(db, phone: str):
    try:
        if not MSG91_AUTH_KEY:
            raise HTTPException(500, "MSG91_AUTH_KEY missing")

        if not MSG91_TEMPLATE_ID:
            raise HTTPException(500, "MSG91_TEMPLATE_ID missing")

        url = "https://control.msg91.com/api/v5/otp"

        payload = {
            "template_id": MSG91_TEMPLATE_ID,
            "mobile": f"91{phone}"
        }

        headers = {
            "Content-Type": "application/json",
            "authkey": MSG91_AUTH_KEY
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        print("SEND OTP RESPONSE:", data)

        if response.status_code != 200 or data.get("type") != "success":
            raise HTTPException(400, f"OTP send failed: {data}")

        return {"message": "OTP sent successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


# 🔢 VERIFY OTP
def verify_otp(phone: str, otp: str):
    try:
        url = "https://control.msg91.com/api/v5/otp/verify"

        payload = {
            "mobile": f"91{phone}",
            "otp": otp
        }

        headers = {
            "Content-Type": "application/json",
            "authkey": MSG91_AUTH_KEY
        }

        response = requests.post(url, json=payload, headers=headers)
        data = response.json()

        print("VERIFY OTP RESPONSE:", data)

        if response.status_code != 200 or data.get("type") != "success":
            raise HTTPException(400, "Invalid or expired OTP")

        return True

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))