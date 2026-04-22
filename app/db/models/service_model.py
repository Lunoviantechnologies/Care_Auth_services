from sqlalchemy import Column, Integer, String
from app.db.session import Base  # ⚠️ use your existing Base
#from app.db.base import Base
from app.db.session import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
 