from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

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
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role="student",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

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
