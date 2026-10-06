from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.models.user import User
from app.models.exam import Exam
from app.models.registration import ExamRegistration
from app.schemas.registration import RegistrationResponse

router = APIRouter()

@router.post("/exams/{exam_id}/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_for_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam or not exam.is_published:
        raise HTTPException(status_code=404, detail="Exam not available for registration")
    
    existing = db.query(ExamRegistration).filter(
        ExamRegistration.exam_id == exam_id,
        ExamRegistration.student_id == student_user.id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="You are already registered for this exam")
    
    reg = ExamRegistration(exam_id=exam_id, student_id=student_user.id)
    db.add(reg)
    db.commit()
    db.refresh(reg)
    
    return RegistrationResponse(
        id=reg.id,
        exam_id=reg.exam_id,
        student_id=reg.student_id,
        exam_title=exam.title,
        category=exam.category,
        registered_at=reg.registered_at
    )

@router.get("/students/me/registrations", response_model=List[RegistrationResponse])
def my_registrations(
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    regs = db.query(ExamRegistration).filter(ExamRegistration.student_id == student_user.id).all()
    res = []
    for r in regs:
        res.append(RegistrationResponse(
            id=r.id,
            exam_id=r.exam_id,
            student_id=r.student_id,
            exam_title=r.exam.title,
            category=r.exam.category,
            registered_at=r.registered_at
        ))
    return res
