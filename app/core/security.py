import os
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

# 🔐 CONFIG
SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# 🔐 PASSWORD
def hash_password(password: str) -> str:
    return pwd.hash(password[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd.verify(plain_password[:72], hashed_password)


# 🔐 CREATE ACCESS TOKEN
def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None):
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "user_id": user_id,
        "role": role,
        "type": "access",   # ✅ important
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 🔄 CREATE REFRESH TOKEN
def create_refresh_token(user_id: int, role: str):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user_id,
        "role": role,
        "type": "refresh",   # ✅ important
        "exp": expire
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 🔍 VERIFY TOKEN
def verify_token(token: str, expected_type: str = "access"):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("user_id")
        role = payload.get("role")
        token_type = payload.get("type")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # ✅ check token type
        if token_type != expected_type:
            raise HTTPException(status_code=401, detail="Invalid token type")

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# 👤 CURRENT USER
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token, expected_type="access")


# 🔐 ROLE BASED ACCESS
def admin_required(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def worker_required(user=Depends(get_current_user)):
    if user["role"] != "worker":
        raise HTTPException(status_code=403, detail="Worker access required")
    return user


def customer_required(user=Depends(get_current_user)):
    if user["role"] != "customer":
        raise HTTPException(status_code=403, detail="Customer access required")
    return user