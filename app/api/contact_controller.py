from fastapi import APIRouter, HTTPException
from app.schemas.contact_schema import ContactCreate
from app.services.contact_service import send_contact_notification

router = APIRouter(prefix="/api", tags=["Contact"])


# ---------------- SUBMIT CONTACT ----------------
# Sends email notification when user submits contact form
@router.post("/contact")
async def submit_contact(data: ContactCreate):
    try:
        # Call async service
        await send_contact_notification(data)

        return {"message": "Success"}

    except Exception as e:
        # Proper error handling (avoid exposing raw error in production)
        raise HTTPException(
            status_code=500,
            detail="Failed to process contact request"
        )