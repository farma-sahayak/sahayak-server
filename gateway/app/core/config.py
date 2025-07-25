import os
from dotenv import load_dotenv

# load .env file
load_dotenv()

class Config:
    """Base configuration class."""
    
    # db
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://sahayak_gw_user:sahayak_gw_pass@sahayak-db:5432/sahayak_gw_db")

    # General settings
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "localhost")

    # security
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sahayak-server-jwt-secret")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7")


config = Config()