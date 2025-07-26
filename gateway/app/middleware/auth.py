from fastapi import Header, HTTPException, status
from app.utils.security import decode_token
from typing import Optional

def get_current_user_id(authorization: Optional[str] = Header(...)) -> dict:
    try:
        access_token = get_access_token(authorization=authorization)
        payload = decode_token(access_token)

        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

        return payload['user_id']
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"auth failed with exception: {e}")
    pass

def get_access_token(authorization: Optional[str] = Header(...)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token format")
        
        token = authorization[7:]

        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")
        
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"auth failed with exception: {e}")