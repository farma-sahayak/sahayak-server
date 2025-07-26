# File: app/schemas/farmer_profile.py
from typing import List, Optional
from pydantic import BaseModel, UUID4


class FarmerProfileBase(BaseModel):
    name: str
    district: str
    state: str
    preferred_language: str
    primary_crops: Optional[List[str]] = None


class FarmerProfileCreate(FarmerProfileBase):
    user_id: UUID4


class FarmerProfileUpdate(BaseModel):
    name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    preferred_language: Optional[str] = None
    primary_crops: Optional[List[str]] = None


class FarmerProfileRead(FarmerProfileBase):
    farmer_id: UUID4
    user_id: UUID4

    class Config:
        from_attributes = True
