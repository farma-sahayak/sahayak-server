from sqlalchemy.orm import Session
from app.models.auth import AuthRequest, AuthResponse
from app.db.models.user import User
from app.utils.security import hash_mpin, create_access_token, create_refresh_token

def signup_user(payload: AuthRequest, db: Session):
    """ sign up user and upon sucess, return pair of access and refresh tokens """
    # check for existing user
    existing_user = db.query(User).filter_by(phone_number=payload.phone_number).first()
    if (existing_user):
        raise ValueError(f"user already exists with {payload.phone_number}")
    
    # hash mpin to save
    user = User(phone_number=payload.phone_number, mpin_hash=hash_mpin(payload.mpin))

    # add to db
    db.add(user)
    db.commit() # commit the write
    db.refresh(user)

    payload = {"sub" : user.phone_number}

    return AuthResponse(
        accessToken=create_access_token(payload),
        refreshToken=create_refresh_token(payload)
    )