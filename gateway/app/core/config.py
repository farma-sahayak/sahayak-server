import os
from dotenv import load_dotenv

# load .env file
load_dotenv()


class Config:
    """Base configuration class."""
    
    # General settings
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "localhost")

config = Config()