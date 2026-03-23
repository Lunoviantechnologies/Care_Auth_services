import os
import shutil
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.db.models.worker_model import Worker
from app.core.security import hash_password, verify_password, create_access_token
import random
from datetime import datetime, timedelta
from app.db.models.otp_model import OTP
from app.core.email_service import send_email_otp
from sqlalchemy import or_, asc, desc
import os
import shutil
import uuid
import requests
import random
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc
from fastapi import HTTPException, UploadFile

from app.db.models.worker_model import Worker
from app.db.models.otp_model import OTP
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email_service import send_email_otp


BASE_URL = os.getenv("BASE_URL")

PROFILE_DIR = os.getenv("PROFILE_DIR")
AADHAR_DIR = os.getenv("AADHAR_DIR")

SUREPASS_API_KEY = os.getenv("SUREPASS_API_KEY")

# Create folders if not exist
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(AADHAR_DIR, exist_ok=True)

AADHAAR_HEADERS = {
    "Authorization": f"Bearer {SUREPASS_API_KEY}",
    "Content-Type": "application/json"
}

def get_worker_or_404(db, worker_id):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(404, "Worker not found")
    return worker


def format_worker(worker):
    return {
        "id": worker.id,
        "full_name": worker.full_name,
        "phone": worker.phone,
        "email": worker.email,
        "status": worker.status,
        "profile_image": (
            f"{BASE_URL}{worker.profile_image}" if worker.profile_image else None
        ),
    }


# 🔹 REGISTER
def create_worker(db, data):
    if db.query(Worker).filter(Worker.phone == data.phone).first():
        raise HTTPException(400, "Phone already exists")

    worker = Worker(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return {"message": "Registered successfully"}


# 🔹 LOGIN (ADMIN APPROVAL CHECK)
def login_worker(db, data):
    worker = db.query(Worker).filter(Worker.phone == data.phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(data.password, worker.password):
        raise HTTPException(400, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    token = create_access_token({"sub": str(worker.id)}, "worker")

    return {"access_token": token, "worker": format_worker(worker)}


# 🔹 PROFILE UPLOAD
def upload_profile_image(db, worker_id, file):
    worker = get_worker_or_404(db, worker_id)

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(PROFILE_DIR, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    worker.profile_image = f"/uploads/profile/{filename}"
    db.commit()

    return {"url": f"{BASE_URL}{worker.profile_image}"}


# 🔹 AADHAAR UPLOAD
def upload_aadhar_images(db, worker_id, front, back):
    worker = get_worker_or_404(db, worker_id)

    f1 = f"{uuid.uuid4()}_{front.filename}"
    f2 = f"{uuid.uuid4()}_{back.filename}"

    p1 = os.path.join(AADHAR_DIR, f1)
    p2 = os.path.join(AADHAR_DIR, f2)

    with open(p1, "wb") as f:
        shutil.copyfileobj(front.file, f)

    with open(p2, "wb") as f:
        shutil.copyfileobj(back.file, f)

    worker.aadhar_front = f"/uploads/aadhar/{f1}"
    worker.aadhar_back = f"/uploads/aadhar/{f2}"

    db.commit()

    return {"message": "Uploaded"}


# 🔹 KYC
def update_kyc(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    if not worker.aadhar_front:
        raise HTTPException(400, "Upload Aadhaar first")

    worker.aadhar_number = data.aadhar_number[-4:]
    worker.is_kyc_verified = True

    db.commit()

    return {"message": "KYC done"}


# 🔹 BANK
def update_bank(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    worker.account_holder_name = data.account_holder_name
    worker.account_number = data.account_number
    worker.ifsc_code = data.ifsc_code
    worker.bank_name = data.bank_name
    worker.is_bank_verified = True

    db.commit()

    return {"message": "Bank added"}


# 🔹 ADDRESS
def update_address(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    worker.address = data.address
    worker.city = data.city
    worker.state = data.state
    worker.pincode = data.pincode
    worker.is_address_verified = True

    db.commit()

    return {"message": "Address added"}


# 🔹 APPROVE
def approve_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)

    if not worker.is_kyc_verified:
        raise HTTPException(400, "Complete KYC first")

    worker.is_admin_approved = True
    worker.status = "active"

    db.commit()

    return {"message": "Approved"}


# 🔹 REJECT
def reject_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)

    worker.is_admin_approved = False
    worker.status = "rejected"

    db.commit()

    return {"message": "Rejected"}


# 🔹 LIST
def list_workers(
    db: Session,
    page: 0,
    size: 10,
    search: str = None,
    sort_by: str = "id",
    sort_order: str = "desc",
):

    query = db.query(Worker)

    # 🔹 FILTER (Search)
    if search:
        query = query.filter(
            or_(
                Worker.full_name.ilike(f"%{search}%"),
                Worker.email.ilike(f"%{search}%"),
                Worker.phone.ilike(f"%{search}%"),
            )
        )

    # 🔹 SORTING
    sort_column = getattr(Worker, sort_by, Worker.id)

    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    # 🔹 TOTAL COUNT
    total = query.count()

    # 🔹 PAGINATION
    workers = query.offset((page - 1) * size).limit(size).all()

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": [format_worker(w) for w in workers],
    }


# 🔹 DETAILS
def get_worker_details(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    return format_worker(worker)


# 🔹 DELETE
def delete_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted"}


# 🔹 LOGOUT
def logout_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    worker.is_logged_in = False
    db.commit()
    return {"message": "Logged out"}


# 🔹 UPDATE WORKER
def update_worker(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(worker, key, value)

    db.commit()
    return {"message": "Worker updated"}

    # 🔹 UPDATE DEVICE ID


def update_device_id(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)
    worker.device_id = data.device_id
    db.commit()
    return {"message": "Device ID updated"}


# 🔹 SEND OTP
def send_worker_otp(db: Session, email: str):

    worker = db.query(Worker).filter(Worker.email == email).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    otp_code = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email, otp=otp_code, expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(otp_record)
    db.commit()

    send_email_otp(email, otp_code)

    return {"message": "OTP sent to email"}


# 🔹 VERIFY OTP
def verify_worker_otp(db: Session, email: str, otp: str):

    otp_record = (
        db.query(OTP)
        .filter(OTP.email == email, OTP.otp == otp)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(400, "Invalid OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    return {"message": "OTP verified"}


# 🔹 RESET PASSWORD
def reset_worker_password(
    db: Session, email: str, otp: str, new_password: str, confirm_password: str
):

    if new_password != confirm_password:
        raise HTTPException(400, "Passwords do not match")

    otp_record = (
        db.query(OTP)
        .filter(OTP.email == email, OTP.otp == otp)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(400, "Invalid OTP")

    worker = db.query(Worker).filter(Worker.email == email).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    worker.password = hash_password(new_password)

    db.commit()

    return {"message": "Password reset successful"}


# ================= AADHAAR OTP ================= #

def generate_aadhaar_otp(db: Session, worker_id: int, aadhaar: str):
    worker = get_worker_or_404(db, worker_id)

    if len(aadhaar) != 12 or not aadhaar.isdigit():
        raise HTTPException(400, "Invalid Aadhaar")

    response = requests.post(
        "https://api.surepass.io/api/v1/aadhaar-v2/generate-otp",
        json={"id_number": aadhaar},
        headers=AADHAAR_HEADERS,
        timeout=10
    )

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(400, data)

    worker.aadhaar_client_id = data["data"]["client_id"]
    db.commit()

    return {"message": "OTP sent"}


def verify_aadhaar_otp(db: Session, worker_id: int, otp: str, aadhaar: str):
    worker = get_worker_or_404(db, worker_id)

    if not worker.aadhaar_client_id:
        raise HTTPException(400, "Generate OTP first")

    response = requests.post(
        "https://api.surepass.io/api/v1/aadhaar-v2/submit-otp",
        json={
            "client_id": worker.aadhaar_client_id,
            "otp": otp
        },
        headers=AADHAAR_HEADERS,
        timeout=10
    )

    data = response.json()

    if response.status_code != 200:
        raise HTTPException(400, data)

    worker.aadhar_number = aadhaar[-4:]
    worker.is_kyc_verified = True
    worker.aadhaar_client_id = None

    db.commit()

    return {"message": "Aadhaar verified"}

