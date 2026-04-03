import httpx
from app.core.config import settings

BASE_URL = "https://control.msg91.com/api/v5/otp"


# SEND OTP
async def send_otp(mobile: str):
    url = f"{BASE_URL}?authkey={settings.MSG91_AUTH_KEY}"

    payload = {
        "template_id": settings.MSG91_TEMPLATE_ID,
        "mobile": mobile,
        "sender": settings.MSG91_SENDER_ID,
    }

    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)

    return response.json()


# VERIFY OTP
async def verify_otp(mobile: str, otp: str):
    url = (
        f"{BASE_URL}/verify?authkey={settings.MSG91_AUTH_KEY}&mobile={mobile}&otp={otp}"
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    return response.json()
