from sqlalchemy import Column, String, ForeignKey, ARRAY, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..models.base import Base
import uuid

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    farmer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.index"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    district = Column(String(50), nullable=False)
    state = Column(String(50), nullable=False)
    preferred_language = Column(String(20), nullable=False)
    primary_crop = Column(ARRAY(String), nullable=True)

    # relationship back to the User model
    user = relationship("User", back_populates="farmer_profile")
    pass