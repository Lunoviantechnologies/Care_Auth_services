from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
from app.utils.redis_client import redis_client

security = HTTPBearer()

def get_current_user(token=Depends(security)):
    if redis_client.get(f"blacklist:{token.credentials}"):
        raise HTTPException(401, "Token blacklisted")

    payload = jwt.decode(token.credentials, "supersecret", algorithms=["HS256"])
    return payload