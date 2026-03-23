import os, shutil, uuid, random, requests
from datetime import datetime, timedelta
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import or_, asc, desc

from app.db.models.worker_model import Worker, WorkerStatusEnum
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

# ---------------- COMMON ---------------- #

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
        "status": worker.status.value,
        "profile_image": worker.profile_image,
    }


# ---------------- REGISTER ---------------- #

def create_worker(db, data):
    if db.query(Worker).filter(Worker.phone == data.phone).first():
        raise HTTPException(400, "Phone already exists")

    if data.email and db.query(Worker).filter(Worker.email == data.email).first():
        raise HTTPException(400, "Email already exists")

    worker = Worker(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password)
    )

    db.add(worker)
    db.commit()

    return {"message": "Registered successfully"}


# ---------------- LOGIN ---------------- #

def login_worker(db, data):
    worker = db.query(Worker).filter(Worker.phone == data.phone).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(data.password, worker.password):
        raise HTTPException(400, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    worker.device_id = data.device_id
    worker.is_logged_in = True
    db.commit()

    token = create_access_token({"sub": str(worker.id)}, "worker")

    return {"access_token": token, "worker": format_worker(worker)}


# ---------------- PROFILE ---------------- #

def upload_profile_image(db, worker_id, file: UploadFile):
    worker = get_worker_or_404(db, worker_id)

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(PROFILE_DIR, filename)

    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    worker.profile_image = path
    db.commit()

    return {"url": path}


# ---------------- AADHAAR ---------------- #

def upload_aadhar_images(db, worker_id, front, back):
    worker = get_worker_or_404(db, worker_id)

    f1 = f"{uuid.uuid4()}_{front.filename}"
    f2 = f"{uuid.uuid4()}_{back.filename}"

    with open(os.path.join(AADHAR_DIR, f1), "wb") as f:
        shutil.copyfileobj(front.file, f)

    with open(os.path.join(AADHAR_DIR, f2), "wb") as f:
        shutil.copyfileobj(back.file, f)

    worker.aadhaar_front = f1
    worker.aadhaar_back = f2
    db.commit()

    return {"message": "Aadhaar uploaded"}


def update_kyc(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    if not worker.aadhaar_front:
        raise HTTPException(400, "Upload Aadhaar first")

    worker.aadhaar_number = data.aadhaar_number[-4:]
    worker.is_kyc_verified = True

    db.commit()
    return {"message": "KYC completed"}


# ---------------- BANK ---------------- #

def update_bank(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    worker.account_holder_name = data.account_holder_name
    worker.account_number = data.account_number
    worker.ifsc_code = data.ifsc_code
    worker.bank_name = data.bank_name
    worker.is_bank_verified = True

    db.commit()
    return {"message": "Bank added"}


# ---------------- ADDRESS ---------------- #

def update_address(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    worker.address = data.address
    worker.city = data.city
    worker.state = data.state
    worker.pincode = data.pincode
    worker.is_address_verified = True

    db.commit()
    return {"message": "Address added"}


# ---------------- ADMIN ---------------- #

def approve_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)

    if not worker.is_kyc_verified:
        raise HTTPException(400, "Complete KYC first")

    worker.is_admin_approved = True
    worker.status = WorkerStatusEnum.APPROVED

    db.commit()
    return {"message": "Approved"}


def reject_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)

    worker.status = WorkerStatusEnum.REJECTED
    db.commit()

    return {"message": "Rejected"}


# ---------------- LIST ---------------- #

def list_workers(db, page=1, size=10, search=None, sort_by="id", sort_order="desc"):

    query = db.query(Worker)

    if search:
        query = query.filter(
            or_(
                Worker.full_name.ilike(f"%{search}%"),
                Worker.email.ilike(f"%{search}%"),
                Worker.phone.ilike(f"%{search}%"),
            )
        )

    sort_column = getattr(Worker, sort_by, Worker.id)

    query = query.order_by(asc(sort_column) if sort_order == "asc" else desc(sort_column))

    total = query.count()

    workers = query.offset((page - 1) * size).limit(size).all()

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": [format_worker(w) for w in workers],
    }


# ---------------- DETAILS ---------------- #

def get_worker_details(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    return format_worker(worker)


# ---------------- UPDATE ---------------- #

def update_worker(db, worker_id, data):
    worker = get_worker_or_404(db, worker_id)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(worker, key, value)

    db.commit()
    return {"message": "Updated"}


# ---------------- DELETE ---------------- #

def delete_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    db.delete(worker)
    db.commit()
    return {"message": "Deleted"}


# ---------------- LOGOUT ---------------- #

def logout_worker(db, worker_id):
    worker = get_worker_or_404(db, worker_id)
    worker.is_logged_in = False
    db.commit()
    return {"message": "Logged out"}


# ---------------- OTP ---------------- #

def send_worker_otp(db, email):
    worker = db.query(Worker).filter(Worker.email == email).first()

    if not worker:
        raise HTTPException(404, "Worker not found")

    otp = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )

    db.add(otp_record)
    db.commit()

    send_email_otp(email, otp)

    return {"message": "OTP sent"}


def verify_worker_otp(db, email, otp):
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


def reset_worker_password(db, email, otp, new_password, confirm_password):

    if new_password != confirm_password:
        raise HTTPException(400, "Passwords mismatch")

    verify_worker_otp(db, email, otp)

    worker = db.query(Worker).filter(Worker.email == email).first()

    worker.password = hash_password(new_password)
    db.commit()

    return {"message": "Password reset successful"}


# ================= AADHAAR OTP ================= #

# def generate_aadhaar_otp(db: Session, worker_id: int, aadhaar: str):
#     worker = get_worker_or_404(db, worker_id)

#     if len(aadhaar) != 12 or not aadhaar.isdigit():
#         raise HTTPException(400, "Invalid Aadhaar")

#     response = requests.post(
#         "https://api.surepass.io/api/v1/aadhaar-v2/generate-otp",
#         json={"id_number": aadhaar},
#         headers=AADHAAR_HEADERS,
#         timeout=10
#     )

#     data = response.json()

#     if response.status_code != 200:
#         raise HTTPException(400, data)

#     worker.aadhaar_client_id = data["data"]["client_id"]
#     db.commit()

#     return {"message": "OTP sent"}


# def verify_aadhaar_otp(db: Session, worker_id: int, otp: str, aadhaar: str):
#     worker = get_worker_or_404(db, worker_id)

#     if not worker.aadhaar_client_id:
#         raise HTTPException(400, "Generate OTP first")

#     response = requests.post(
#         "https://api.surepass.io/api/v1/aadhaar-v2/submit-otp",
#         json={
#             "client_id": worker.aadhaar_client_id,
#             "otp": otp
#         },
#         headers=AADHAAR_HEADERS,
#         timeout=10
#     )

#     data = response.json()

#     if response.status_code != 200:
#         raise HTTPException(400, data)

#     worker.aadhar_number = aadhaar[-4:]
#     worker.is_kyc_verified = True
#     worker.aadhaar_client_id = None

#     db.commit()

#     return {"message": "Aadhaar verified"}

