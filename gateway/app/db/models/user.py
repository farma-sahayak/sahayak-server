from sqlalchemy import Column, Integer, String

from ..models.base import Base

class User(Base):
    """ User model for the sahayak ai application """
    __tablename__ = "users"

    index = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(14), unique=True, index=True, nullable=False)
    mpin_hash = Column(String, nullable=False)
    pass