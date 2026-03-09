from pydantic import BaseModel


class WorkerCreate(BaseModel):
    full_name: str
    phone: str
    email: str | None = None
    password: str


class WorkerLogin(BaseModel):
    phone: str
    password: str


class WorkerUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None


class KYCUpdate(BaseModel):
    aadhar_number: str


class BankUpdate(BaseModel):
    account_holder_name: str
    account_number: str
    ifsc_code: str
    bank_name: str


class AddressUpdate(BaseModel):
    address: str
    city: str
    state: str
    pincode: str