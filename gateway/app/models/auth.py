import re
from pydantic import BaseModel, field_validator, Field

class AuthRequest(BaseModel):
    phone_number: str = Field(..., alias="phoneNumber")
    mpin: int = Field(..., ge=100000, le=999999) # 6 digit int

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        phone_pattern = r'^\+91-\d{10}$'
        if not re.match(phone_pattern, v):
            raise ValueError('Invalid phone number format')
        return v.replace(" ", "").replace("-", "")

class AuthResponse(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    refresh_token: str = Field(..., alias="refreshToken")
    pass