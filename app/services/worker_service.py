import os, shutil, uuid, random, asyncio
from datetime import datetime, timedelta

from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, asc, desc

from app.db.models.worker_model import Worker, WorkerStatusEnum
from app.db.models.otp_model import OTP
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email_service import send_email_otp


BASE_URL = os.getenv("BASE_URL")
PROFILE_DIR = os.getenv("PROFILE_DIR")
AADHAR_DIR = os.getenv("AADHAR_DIR")

os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(AADHAR_DIR, exist_ok=True)


# ---------------- COMMON ---------------- #


async def get_worker_or_404(db: AsyncSession, worker_id: int):
    result = await db.execute(select(Worker).where(Worker.id == worker_id))
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

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


async def create_worker(db: AsyncSession, data):

    result = await db.execute(select(Worker).where(Worker.phone == data.phone))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Phone already exists")

    if data.email:
        result = await db.execute(select(Worker).where(Worker.email == data.email))
        if result.scalar_one_or_none():
            raise HTTPException(400, "Email already exists")

    worker = Worker(
        full_name=data.full_name,
        phone=data.phone,
        email=data.email,
        password=hash_password(data.password),
    )

    db.add(worker)
    await db.commit()

    return {"message": "Registered successfully"}


# ---------------- LOGIN ---------------- #


async def login_worker(db: AsyncSession, data):

    result = await db.execute(select(Worker).where(Worker.phone == data.phone))
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(404, "Worker not found")

    if not verify_password(data.password, worker.password):
        raise HTTPException(400, "Invalid credentials")

    if not worker.is_admin_approved:
        raise HTTPException(403, "Wait for admin approval")

    worker.device_id = data.device_id
    worker.is_logged_in = True

    await db.commit()

    token = create_access_token({"sub": str(worker.id)}, "worker")

    return {"access_token": token, "worker": format_worker(worker)}


# ---------------- PROFILE ---------------- #


async def upload_profile_image(db: AsyncSession, worker_id: int, file: UploadFile):

    worker = await get_worker_or_404(db, worker_id)

    filename = f"{uuid.uuid4()}_{file.filename}"
    path = os.path.join(PROFILE_DIR, filename)

    # file write (sync → thread)
    await asyncio.to_thread(_save_file, file, path)

    worker.profile_image = path
    await db.commit()

    return {"url": path}


def _save_file(file, path):
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)


# ---------------- AADHAAR ---------------- #


async def upload_aadhar_images(db: AsyncSession, worker_id: int, front, back):

    worker = await get_worker_or_404(db, worker_id)

    f1 = f"{uuid.uuid4()}_{front.filename}"
    f2 = f"{uuid.uuid4()}_{back.filename}"

    await asyncio.to_thread(_save_file, front, os.path.join(AADHAR_DIR, f1))
    await asyncio.to_thread(_save_file, back, os.path.join(AADHAR_DIR, f2))

    worker.aadhaar_front = f1
    worker.aadhaar_back = f2

    await db.commit()

    return {"message": "Aadhaar uploaded"}


async def update_kyc(db: AsyncSession, worker_id: int, data):

    worker = await get_worker_or_404(db, worker_id)

    if not worker.aadhaar_front:
        raise HTTPException(400, "Upload Aadhaar first")

    worker.aadhaar_number = data.aadhaar_number[-4:]
    worker.is_kyc_verified = True

    await db.commit()

    return {"message": "KYC completed"}


# ---------------- BANK ---------------- #


async def update_bank(db: AsyncSession, worker_id: int, data):

    worker = await get_worker_or_404(db, worker_id)

    worker.account_holder_name = data.account_holder_name
    worker.account_number = data.account_number
    worker.ifsc_code = data.ifsc_code
    worker.bank_name = data.bank_name
    worker.is_bank_verified = True

    await db.commit()

    return {"message": "Bank added"}


# ---------------- ADDRESS ---------------- #


async def update_address(db: AsyncSession, worker_id: int, data):

    worker = await get_worker_or_404(db, worker_id)

    worker.address = data.address
    worker.city = data.city
    worker.state = data.state
    worker.pincode = data.pincode
    worker.is_address_verified = True

    await db.commit()

    return {"message": "Address added"}


# ---------------- ADMIN ---------------- #


async def approve_worker(db: AsyncSession, worker_id: int):

    worker = await get_worker_or_404(db, worker_id)

    if not worker.is_kyc_verified:
        raise HTTPException(400, "Complete KYC first")

    worker.is_admin_approved = True
    worker.status = WorkerStatusEnum.APPROVED

    await db.commit()

    return {"message": "Approved"}


async def reject_worker(db: AsyncSession, worker_id: int):

    worker = await get_worker_or_404(db, worker_id)

    worker.status = WorkerStatusEnum.REJECTED

    await db.commit()

    return {"message": "Rejected"}


# ---------------- LIST ---------------- #


async def list_workers(
    db: AsyncSession, page=1, size=10, search=None, sort_by="id", sort_order="desc"
):

    query = select(Worker)

    if search:
        query = query.where(
            or_(
                Worker.full_name.ilike(f"%{search}%"),
                Worker.email.ilike(f"%{search}%"),
                Worker.phone.ilike(f"%{search}%"),
            )
        )

    sort_column = getattr(Worker, sort_by, Worker.id)
    query = query.order_by(
        asc(sort_column) if sort_order == "asc" else desc(sort_column)
    )

    result = await db.execute(query)
    workers = result.scalars().all()

    total = len(workers)

    start = (page - 1) * size
    end = start + size

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": [format_worker(w) for w in workers[start:end]],
    }


# ---------------- DETAILS ---------------- #


def get_worker_by_id(worker_id: int, db):
    return db.query(Worker).filter(Worker.id == worker_id).first()


# ---------------- UPDATE ---------------- #


async def update_worker(db: AsyncSession, worker_id: int, data):

    worker = await get_worker_or_404(db, worker_id)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(worker, key, value)

    await db.commit()

    return {"message": "Updated"}


# ---------------- DELETE ---------------- #


async def delete_worker(db: AsyncSession, worker_id: int):

    worker = await get_worker_or_404(db, worker_id)

    await db.delete(worker)
    await db.commit()

    return {"message": "Deleted"}


# ---------------- LOGOUT ---------------- #


async def logout_worker(db: AsyncSession, worker_id: int):

    worker = await get_worker_or_404(db, worker_id)

    worker.is_logged_in = False

    await db.commit()

    return {"message": "Logged out"}


# ---------------- OTP ---------------- #


async def send_worker_otp(db: AsyncSession, email: str):

    result = await db.execute(select(Worker).where(Worker.email == email))
    worker = result.scalar_one_or_none()

    if not worker:
        raise HTTPException(404, "Worker not found")

    otp = str(random.randint(100000, 999999))

    otp_record = OTP(
        email=email,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5),
    )

    db.add(otp_record)
    await db.commit()

    await asyncio.to_thread(send_email_otp, email, otp)

    return {"message": "OTP sent"}


async def verify_worker_otp(db: AsyncSession, email: str, otp: str):

    result = await db.execute(
        select(OTP).where(OTP.email == email, OTP.otp == otp).order_by(OTP.id.desc())
    )
    otp_record = result.scalar_one_or_none()

    if not otp_record:
        raise HTTPException(400, "Invalid OTP")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(400, "OTP expired")

    return {"message": "OTP verified"}


async def reset_worker_password(
    db: AsyncSession, email: str, otp: str, new_password: str, confirm_password: str
):

    if new_password != confirm_password:
        raise HTTPException(400, "Passwords mismatch")

    await verify_worker_otp(db, email, otp)

    result = await db.execute(select(Worker).where(Worker.email == email))
    worker = result.scalar_one_or_none()

    worker.password = hash_password(new_password)

    await db.commit()

    return {"message": "Password reset successful"}


async def get_worker_by_id(worker_id: int, db):
    result = await db.execute(select(Worker).where(Worker.id == worker_id))
    return result.scalar_one_or_none()
