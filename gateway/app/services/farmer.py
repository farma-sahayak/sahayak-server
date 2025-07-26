# File: app/services/farmer_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app.db.models.farmer import FarmerProfile
from app.models.farmer import FarmerProfileBase, FarmerProfileUpdate
from app.db.models.user import User

class FarmerService:
    @staticmethod
    def create_farmer_profile(request: FarmerProfileBase, db: Session, user_id: int) -> FarmerProfile:
        try:
            # Check for existing profile for the user
            existing = db.query(User).filter_by(index=user_id).first()
            if not existing:
                raise ValueError(f"User with id {user_id} does not exist")
            
            # cehck for existing farmer profile
            existing_profile = db.query(FarmerProfile).filter_by(user_id=user_id).first()
            if existing_profile:
                raise ValueError(f"Farmer profile already exists for user id {user_id}")

            profile = FarmerProfile(
                farmer_id=uuid.uuid4(),
                user_id=user_id,
                name=request.name,
                district=request.district,
                state=request.state,
                preferred_language=request.preferred_language,
                primary_crop= [] if request.primary_crops is None else request.primary_crops
            )

            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
        except Exception as e:
            raise ValueError(f"Failed to create farmer profile: {str(e)}")

    @staticmethod
    def update_farmer_profile(db: Session, farmer_id: uuid.UUID, profile_in: FarmerProfileUpdate) -> FarmerProfile:
        try:
            profile = db.query(FarmerProfile).filter(FarmerProfile.farmer_id == farmer_id).first()
            if not profile:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Farmer profile not found"
                )

            for key, value in profile_in.dict(exclude_unset=True).items():
                setattr(profile, key, value)

            db.commit()
            db.refresh(profile)
            return profile
        except Exception as ex:
            raise ValueError(f"failed to update farmer profile with {ex}")

    @staticmethod
    def get_farmer_profile(db: Session, farmer_id: uuid.UUID, user_id: int) -> FarmerProfile:
        try:
            profile = db.query(FarmerProfile).filter(FarmerProfile.farmer_id == farmer_id).first()
            if not profile:
                raise ValueError("no matching profile found")
            return profile
        except Exception as ex:
            raise ValueError(f"failed to fetch farmer profile with: {ex}")
