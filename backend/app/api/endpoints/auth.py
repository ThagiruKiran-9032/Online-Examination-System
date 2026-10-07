from datetime import datetime, timedelta, timezone
import secrets
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.email import send_welcome_email, send_password_reset_email, send_registration_otp_email
from app.core.email_verifier import verify_email_address
from app.models.user import User, EmailVerification
from app.schemas.user import (
    UserCreate, 
    UserResponse, 
    UserUpdateMe, 
    LoginRequest, 
    Token, 
    ForgotPasswordRequest, 
    ResetPasswordRequest,
    VerifyEmailRequest,
    VerifyEmailResponse,
    SendRegistrationOtpRequest,
    VerifyRegistrationOtpRequest
)

from sqlalchemy import func

router = APIRouter()

@router.post("/verify-email", response_model=VerifyEmailResponse)
def verify_email_endpoint(
    req: VerifyEmailRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    result = verify_email_address(req.email, db=db, check_deliverability=req.check_domain)
    return VerifyEmailResponse(**result)

@router.post("/send-registration-otp")
def send_registration_otp(
    req: SendRegistrationOtpRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> Any:
    clean_email = req.email.strip().lower()
    
    # Full deliverability & registration check
    v_res = verify_email_address(clean_email, db=db, check_deliverability=True)
    if not v_res["is_valid_syntax"]:
        raise HTTPException(status_code=400, detail=f"Invalid email format: {v_res['error_detail']}")
    if not v_res["is_real_domain"]:
        raise HTTPException(status_code=400, detail="Invalid email domain. The domain does not exist or cannot receive mail.")
    if v_res["is_registered"]:
        raise HTTPException(status_code=400, detail="A user with this email address is already registered.")

    # Generate 6-digit numeric OTP
    otp = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Upsert into EmailVerification table
    existing = db.query(EmailVerification).filter(func.lower(EmailVerification.email) == clean_email).first()
    if existing:
        existing.otp = otp
        existing.expires_at = expires_at
    else:
        record = EmailVerification(email=clean_email, otp=otp, expires_at=expires_at)
        db.add(record)
    
    db.commit()

    # Send OTP email via SMTP
    background_tasks.add_task(send_registration_otp_email, clean_email, otp)
    return {"message": f"Verification OTP code sent to {clean_email}"}

@router.post("/verify-registration-otp")
def verify_registration_otp(
    req: VerifyRegistrationOtpRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    clean_email = req.email.strip().lower()
    record = db.query(EmailVerification).filter(func.lower(EmailVerification.email) == clean_email).first()

    if not record or record.otp != req.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP verification code")

    now = datetime.now(timezone.utc)
    if record.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Verification code has expired. Please request a new one.")

    return {"verified": True, "message": "Email verified successfully"}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_student(
    user_in: UserCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(deps.get_db)
) -> Any:
    clean_email = user_in.email.strip().lower()
    
    # Run full verification (syntax, deliverability, registration)
    v_res = verify_email_address(clean_email, db=db, check_deliverability=True)
    if not v_res["is_valid_syntax"]:
        raise HTTPException(status_code=400, detail=f"Invalid email syntax: {v_res['error_detail']}")
    if not v_res["is_real_domain"]:
        raise HTTPException(status_code=400, detail=f"Invalid email domain. The domain does not exist or cannot receive mail.")
    if v_res["is_registered"]:
        raise HTTPException(status_code=400, detail="A user with this email address is already registered.")

    # Require OTP verification code if provided or enforced
    if user_in.otp:
        record = db.query(EmailVerification).filter(func.lower(EmailVerification.email) == clean_email).first()
        if not record or record.otp != user_in.otp.strip():
            raise HTTPException(status_code=400, detail="Invalid email verification code")
        now = datetime.now(timezone.utc)
        if record.expires_at.replace(tzinfo=timezone.utc) < now:
            raise HTTPException(status_code=400, detail="Verification code has expired")
        db.delete(record)

    # Force student role on public registration unless specified otherwise
    role = user_in.role if user_in.role in ["admin", "student"] else "student"
    
    user = User(
        email=clean_email,
        full_name=user_in.full_name.strip(),
        hashed_password=get_password_hash(user_in.password),
        role=role,
        phone=user_in.phone,
        department=user_in.department,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Trigger background welcome email via SMTP
    background_tasks.add_task(send_welcome_email, user.email, user.full_name)
    return user

@router.post("/login", response_model=Token)
def login_json(login_data: LoginRequest, db: Session = Depends(deps.get_db)) -> Any:
    clean_email = login_data.email.strip().lower()

    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    # Enforce strict deliverability check for student accounts only (Admin accounts exempt)
    if user.role != "admin":
        v_res = verify_email_address(clean_email, check_deliverability=True)
        if not v_res["is_valid_syntax"] or not v_res["is_real_domain"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email address '{login_data.email}' is invalid or does not belong to a real email domain."
            )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/token", response_model=Token)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(deps.get_db)) -> Any:
    clean_email = form_data.username.strip().lower()

    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user account")

    # Enforce strict deliverability check for student accounts only (Admin accounts exempt)
    if user.role != "admin":
        v_res = verify_email_address(clean_email, check_deliverability=True)
        if not v_res["is_valid_syntax"] or not v_res["is_real_domain"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email address '{form_data.username}' is invalid or does not belong to a real email domain."
            )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/forgot-password")
def forgot_password(
    req: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db)
) -> Any:
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    
    # Always return success message to prevent user enumeration
    if user:
        reset_token = secrets.token_hex(3).upper()  # 6-character OTP token
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        user.reset_token = reset_token
        user.reset_token_expires = expires_at
        db.commit()
        
        background_tasks.add_task(send_password_reset_email, user.email, reset_token)
        
    return {"message": "If an account with that email exists, password reset instructions have been sent."}

@router.post("/reset-password")
def reset_password(
    req: ResetPasswordRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    clean_email = req.email.strip().lower()
    user = db.query(User).filter(func.lower(User.email) == clean_email).first()
    
    if not user or not user.reset_token or user.reset_token != req.token.strip().upper():
        raise HTTPException(status_code=400, detail="Invalid verification token or email")
        
    now = datetime.now(timezone.utc)
    if user.reset_token_expires and user.reset_token_expires.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(status_code=400, detail="Password reset token has expired")
        
    user.hashed_password = get_password_hash(req.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password reset successfully. You can now log in with your new password."}

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(deps.get_current_user)) -> Any:
    return current_user

@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_in: UserUpdateMe,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Users can update personal details (full_name, phone, department, password). Email is immutable for self-update.
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.department is not None:
        current_user.department = user_in.department
    if user_in.password:
        current_user.hashed_password = get_password_hash(user_in.password)

    db.commit()
    db.refresh(current_user)
    return current_user
