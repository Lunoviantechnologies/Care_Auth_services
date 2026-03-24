import asyncio
from firebase_admin import auth
from fastapi import HTTPException


async def verify_firebase_token(token: str):

    try:
        # run blocking Firebase call in separate thread
        decoded_token = await asyncio.to_thread(auth.verify_id_token, token)

        phone = decoded_token.get("phone_number")

        if not phone:
            raise HTTPException(status_code=400, detail="Phone number not found")

        return phone.replace("+91", "")

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")