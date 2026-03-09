import random
from app.utils.redis_client import redis_client

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(key: str):
    otp = generate_otp()
    redis_client.setex(f"otp:{key}", 300, otp)
    print(f"OTP for {key}: {otp}")

def verify_otp(key: str, otp: str):
    return redis_client.get(f"otp:{key}") == otp