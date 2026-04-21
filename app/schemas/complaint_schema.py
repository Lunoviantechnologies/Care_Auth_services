from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ComplaintCreate(BaseModel):
    worker_id: int
    booking_id: Optional[int] = None
    title: str
    description: str


class ComplaintAction(BaseModel):
    action: str  # resolve | reject | ban


class ComplaintResponse(BaseModel):
    id: int
    customer_id: int
    worker_id: int
    title: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
