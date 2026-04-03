from fastapi import APIRouter, HTTPException
from app.schemas.otp_schema import SendOTPRequest, VerifyOTPRequest
from app.services.msg91_service import send_otp, verify_otp

router = APIRouter(prefix="/otp", tags=["OTP"])


# SEND OTP
@router.post("/send")
async def send_otp_api(data: SendOTPRequest):
    result = await send_otp(data.mobile)

    if result.get("type") == "success":
        return {"message": "OTP sent successfully", "details": result}

    raise HTTPException(status_code=400, detail=result)


# VERIFY OTP
@router.post("/verify")
async def verify_otp_api(data: VerifyOTPRequest):
    result = await verify_otp(data.mobile, data.otp)

    if result.get("type") == "success":
        return {"message": "OTP verified successfully", "details": result}

    raise HTTPException(status_code=400, detail=result)
