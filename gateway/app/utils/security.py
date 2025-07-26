import jwt
from fastapi import HTTPException
from passlib.context import CryptContext
import datetime
from app.core.config import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_mpin(mpin: int) -> str:
    return pwd_context.hash(str(mpin))

def verify_mpin(plain_mpin: int, hashed: str) -> bool:
    return pwd_context.verify(str(plain_mpin), hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=float(config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"expire": expire.isoformat()})
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=float(config.JWT_REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"expire": expire.isoformat()})
    return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")