from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: Optional[str] = "student"
    phone: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str
    otp: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdateMe(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None

class UserUpdateAdmin(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str

class VerifyEmailRequest(BaseModel):
    email: str
    check_domain: Optional[bool] = True

class VerifyEmailResponse(BaseModel):
    email: str
    is_valid_syntax: bool
    is_real_domain: bool
    is_registered: bool
    error_detail: Optional[str] = None

class SendRegistrationOtpRequest(BaseModel):
    email: EmailStr

class VerifyRegistrationOtpRequest(BaseModel):
    email: EmailStr
    otp: str
