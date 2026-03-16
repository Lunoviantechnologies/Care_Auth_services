from firebase_admin import auth
from fastapi import HTTPException


def verify_firebase_token(token: str):

    try:
        decoded_token = auth.verify_id_token(token)

        phone = decoded_token.get("phone_number")

        if not phone:
            raise HTTPException(400, "Phone number not found")

        return phone.replace("+91", "")

    except Exception:
        raise HTTPException(401, "Invalid Firebase token")