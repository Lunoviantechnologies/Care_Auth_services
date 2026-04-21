from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db.session import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer)
    worker_id = Column(Integer)
    booking_id = Column(Integer, nullable=True)

    title = Column(String)
    description = Column(String)

    status = Column(String, default="pending")
    # pending | resolved | rejected | banned

    admin_action = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
