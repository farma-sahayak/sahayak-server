from sqlalchemy.orm import Session
from app.models.auth import AuthRequest, AuthResponse
from app.db.models.user import User
from app.utils.security import hash_mpin, create_access_token, create_refresh_token, decode_token
from app.middleware.auth import get_current_user_id

def signup_user(payload: AuthRequest, db: Session):
    """ sign up user and upon sucess, return pair of access and refresh tokens """
    # check for existing user
    existing_user = db.query(User).filter_by(phone_number=payload.phone_number).first()
    if existing_user:
        raise ValueError(f"user already exists with {payload.phone_number}")
    
    # hash mpin to save
    user = User(phone_number=payload.phone_number, mpin_hash=hash_mpin(payload.mpin))

    # add to db
    db.add(user)
    db.commit() # commit the write
    db.refresh(user)

    payload = {"user_id" : user.index}

    return AuthResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload)
    )

def login_user(payload: AuthRequest, db: Session) -> AuthResponse:
    # check for existing user, if user is not present, send user doesn't exist error
    existing_user = db.query(User).filter_by(phone_number=payload.phone_number).first()
    if not existing_user:
        # user doesn't exist, return bad request, ask to log in
        raise ValueError(f"user doesn't exist with {payload.phone_number}")
    
    # else user exists, issue access and refresh token
    payload = {
        'user_id': existing_user.index
    }
    return AuthResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload)
    )

def logout_user(refresh_token: str, current_user_id: int, db: Session):
    try:
        # invalidate refresh token
        # check for existing user
        existing_user = db.query(User).filter_by(index=current_user_id).first()
        if not existing_user:
            raise ValueError(f"user id doesn't exist: {current_user_id}")
        return True
    except Exception as ex:
        print(f"logout user failed with exception: {ex}")
        return False

def refresh_token(refresh_token: str, db: Session):
    """
    refresh the access and refresh token pair if the refresh token is valid
    """
    try:
        payload = decode_token(refresh_token)
        # get the user id from the payload
        user_id = payload['user_id']
        # get user from the user id
        existing_user = db.query(User).filter_by(index=user_id).first()
        if not existing_user:
            # user doesn't exist
            raise ValueError(f"user doesn't exist with {payload.phone_number}")
        
        payload = {"user_id": existing_user.index}

        return AuthResponse(
            access_token=create_access_token(payload),
            refresh_token=create_refresh_token(payload)
        )
    except Exception as ex:
        raise ValueError(f"refresh token validation failed with {ex}")
    pass

def validate_token(access_token: str, db: Session):
    try:
        user_id = get_current_user_id(authorization=access_token)
        # check if user exists
        existing_user = db.query(User).filter_by(index=user_id).first()
        if not existing_user:
            return False
        return False
    except Exception as e:
        print(f"failed with exception {e}")
        return False
