from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router

# Create FastAPI app
app = FastAPI(
    title="Sahayak Gateway",
    description="API Gateway for Sahayak AI - Voice-First Farming Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    # lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(api_router, prefix="/api", tags=["api"])

__all__ = ["app"]