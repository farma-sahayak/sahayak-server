from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.auth import AuthRequest
from app.db.session import get_db

router = APIRouter()

@router.get("/health")
async def health_check():
    """ Health check endpoint"""
    return {
        "status": "ok",
        "service": "auth"
    }
    pass

@router.post("/signup")
async def signup(request: AuthRequest, db: Session = Depends(get_db)):
    """ Signup endpoint """
    try:
        from app.services.auth import signup_user
        return signup_user(request, db)
    except ValueError as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    pass