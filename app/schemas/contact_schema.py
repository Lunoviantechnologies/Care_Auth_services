from pydantic import BaseModel, EmailStr
from typing import Optional

class ContactCreate(BaseModel):
    full_name: str
    phone_number: str
    email: Optional[EmailStr] = None
    city: str
    service_required: str
    message: Optional[str] = None