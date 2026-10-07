from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.core.security import get_password_hash
from app.core.email import send_welcome_email
from app.core.email_verifier import verify_email_address
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdateMe, UserUpdateAdmin

from sqlalchemy import func

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def list_students(
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    return db.query(User).filter(User.role == "student").all()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_student_by_admin(
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    clean_email = user_in.email.strip().lower()
    v_res = verify_email_address(clean_email, db=db, check_deliverability=True)
    if not v_res["is_valid_syntax"]:
        raise HTTPException(status_code=400, detail=f"Invalid email format: {v_res['error_detail']}")
    if not v_res["is_real_domain"]:
        raise HTTPException(status_code=400, detail="Invalid email domain. The domain does not exist or cannot receive mail.")
    if v_res["is_registered"]:
        raise HTTPException(status_code=400, detail="Email already registered in the system")
    
    user = User(
        email=clean_email,
        full_name=user_in.full_name.strip(),
        hashed_password=get_password_hash(user_in.password),
        role="student",
        phone=user_in.phone,
        department=user_in.department,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    background_tasks.add_task(send_welcome_email, user.email, user.full_name)
    return user

@router.put("/me", response_model=UserResponse)
def update_own_profile(
    user_in: UserUpdateMe,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    # Students can update personal details (full_name, phone, department, password) NOT email
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name.strip()
    if user_in.phone is not None:
        current_user.phone = user_in.phone.strip() if user_in.phone else None
    if user_in.department is not None:
        current_user.department = user_in.department.strip() if user_in.department else None
    if user_in.password:
        current_user.hashed_password = get_password_hash(user_in.password)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/{student_id}", response_model=UserResponse)
def update_student_by_admin(
    student_id: int,
    user_in: UserUpdateAdmin,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if user_in.email:
        clean_email = user_in.email.strip().lower()
        if clean_email != student.email.lower():
            existing = db.query(User).filter(func.lower(User.email) == clean_email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")
            student.email = clean_email

    if user_in.full_name is not None:
        student.full_name = user_in.full_name
    if user_in.phone is not None:
        student.phone = user_in.phone
    if user_in.department is not None:
        student.department = user_in.department
    if user_in.is_active is not None:
        student.is_active = user_in.is_active
    if user_in.password:
        student.hashed_password = get_password_hash(user_in.password)

    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    student = db.query(User).filter(User.id == student_id, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
