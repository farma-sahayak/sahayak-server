from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from app.models.farmer import FarmerProfileUpdate, FarmerProfileRead, FarmerProfileBase
from uuid import UUID
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import get_current_user_id

router = APIRouter()

@router.post("/")
def create_farmer_profile(
    request: FarmerProfileBase, 
    user_id: int = Depends(get_current_user_id), 
    db: Session = Depends(get_db)
    ):
    try:
        from app.services.farmer import FarmerService
        profile = FarmerService.create_farmer_profile(request, db, user_id)
        return JSONResponse(content={
            "user_id": profile.user_id,
            "farmer_id": str(profile.farmer_id),
        }, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Failed to create farmer profile: {e}"}
        )

@router.get("/{farmer_id}", response_model=FarmerProfileRead)
def get_farmer_profile(farmer_id: UUID, db: Session = Depends(get_db)):
    try:
        from app.services.farmer import FarmerService
        profile = FarmerService.get_farmer_profile(db, farmer_id)
        return JSONResponse(content=profile.dict())
    except HTTPException as e:
        raise JSONResponse(status_code=e.status_code, detail=f"failed with exception: {str(e)}")

@router.put("/{farmer_id}", response_model=FarmerProfileRead)
def update_farmer_profile(farmer_id: UUID, profile_in: FarmerProfileUpdate, db: Session = Depends(get_db)):
    try:
        from app.services.farmer import FarmerService
        profile = FarmerService.update_farmer_profile(db, farmer_id, profile_in)
        return JSONResponse(content=profile.dict())
    except HTTPException as e:
        raise JSONResponse(status_code=e.status_code, detail=f"failed with exception: {str(e)}")
    except Exception as e:
        raise JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"failed with exception: {str(e)}")