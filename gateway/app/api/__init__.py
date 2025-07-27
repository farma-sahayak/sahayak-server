from fastapi import APIRouter
from .routers.auth import router as auth_router
from .routers.farmer import router as farmer_router
from .routers.prices import router as price_router
from .routers.crop_disease import router as crop_disease_router

api_router = APIRouter()

# include auth router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(farmer_router, prefix="/farmer", tags=['farmer'])
# include prices router
api_router.include_router(price_router, prefix="/prices", tags=["prices"])
# include crop disease router
api_router.include_router(crop_disease_router, prefix="/crop-disease", tags=["crop-disease"])

