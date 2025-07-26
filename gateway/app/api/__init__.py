from fastapi import APIRouter
from .routers.auth import router as auth_router
from .routers.farmer import router as farmer_router

api_router = APIRouter()

# include auth router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(farmer_router, prefix="/farmer", tags=['farmer'])
