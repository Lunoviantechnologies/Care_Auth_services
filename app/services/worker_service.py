import os
import shutil
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, UploadFile
from app.db.models.worker_model import Worker
from app.core.security import hash_password, verify_password, create_access_token

BASE_URL = "http://localhost:8000"

PROFILE_DIR = "app/uploads/profile"
AADHAR_DIR = "app/uploads/aadhar"

os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(AADHAR_DIR, exist_ok=True)


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
        "profile_image": f"{BASE_URL}{worker.profile_image}" if worker.profile_image else None
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

    token = create_access_token({"sub": str(worker.id), "role": "worker"})

    return {
        "access_token": token,
        "worker": format_worker(worker)
    }


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
def list_workers(db):
    workers = db.query(Worker).all()
    return [format_worker(w) for w in workers]

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

   