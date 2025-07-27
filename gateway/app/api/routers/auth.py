from fastapi import APIRouter, Depends, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models.auth import AuthRequest
from app.db.session import get_db
from app.models.auth import RefreshTokenRequest
from app.middleware.auth import get_current_user_id, get_access_token

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
        auth_response = signup_user(request, db)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=auth_response.dict()
        )
    except ValueError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": f"signup failed with exception: {e}"
            }
        )
    
@router.post('/login')
async def login(request: AuthRequest, db: Session = Depends(get_db)):
    """ Log in endpoint """
    try:
        from gateway.app.services.auth import login_user
        return login_user(request, db)
    except ValueError as ex:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "message": f"log in failed with exception: {ex}"
        })
    
@router.post("/logout")
async def logout(request: RefreshTokenRequest, current_user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    """
    remove token pairs from cache
    refresh token comes in body, access token comes in header
    """
    try:
        from gateway.app.services.auth import logout_user
        if logout_user(request.refresh_token, current_user_id, db):
            return Response(status_code=status.HTTP_200_OK)
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "failed to logout"
            }
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": f"failed to logout with exception: {ex}"
            }
        )
    pass

# refresh token -> issues a new pair of tokens
@router.post("/token/refresh")
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """ Refresh token pairs from the refreshToken """
    try:
        from gateway.app.services.auth import refresh_token
        return refresh_token(request.refresh_token, db=db)
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": f"refresh token failed with exception: {ex}"
            }
        )

# validate token -> check if the accessToken is valid or not
@router.get("/validate-token")
async def validate_token(access_token: str = Depends(get_access_token), db: Session = Depends(get_db)):
    """
    Validates access token
    """
    try:
        from app.services.auth import validate_token
        if validate_token(access_token, db):
            return Response(status_code=status.HTTP_200_OK)
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)
    
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": f"invalid token {ex}"
            }
        )
    pass