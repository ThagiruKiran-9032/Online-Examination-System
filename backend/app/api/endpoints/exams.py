from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Any

from app.api import deps
from app.models.user import User
from app.models.exam import Exam
from app.models.question import Question
from app.schemas.exam import ExamCreate, ExamUpdate, ExamResponse

router = APIRouter()

def build_exam_response(exam: Exam) -> ExamResponse:
    total_q = len(exam.questions) if exam.questions else 0
    total_m = sum(q.marks for q in exam.questions) if exam.questions else 0
    return ExamResponse(
        id=exam.id,
        title=exam.title,
        description=exam.description,
        category=exam.category,
        duration_minutes=exam.duration_minutes,
        passing_marks=exam.passing_marks,
        max_attempts=exam.max_attempts,
        is_published=exam.is_published,
        created_at=exam.created_at,
        total_questions=total_q,
        total_marks=total_m
    )

@router.post("/", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam(
    exam_in: ExamCreate,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = Exam(
        title=exam_in.title,
        description=exam_in.description,
        category=exam_in.category,
        duration_minutes=exam_in.duration_minutes,
        passing_marks=exam_in.passing_marks,
        max_attempts=exam_in.max_attempts,
        is_published=False
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return build_exam_response(exam)

@router.get("/", response_model=List[ExamResponse])
def list_exams(
    category: Optional[str] = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    query = db.query(Exam)
    
    # Students only see published exams
    if current_user.role != "admin":
        query = query.filter(Exam.is_published == True)
        
    if category and category != "All":
        query = query.filter(Exam.category == category)
        
    exams = query.order_by(Exam.created_at.desc()).all()
    return [build_exam_response(e) for e in exams]

@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    if current_user.role != "admin" and not exam.is_published:
        raise HTTPException(status_code=403, detail="Exam is not published")
    return build_exam_response(exam)

@router.put("/{exam_id}", response_model=ExamResponse)
def update_exam(
    exam_id: int,
    exam_in: ExamUpdate,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    update_data = exam_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)
        
    db.commit()
    db.refresh(exam)
    return build_exam_response(exam)

@router.patch("/{exam_id}/publish", response_model=ExamResponse)
def toggle_publish(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    exam.is_published = not exam.is_published
    db.commit()
    db.refresh(exam)
    return build_exam_response(exam)

@router.delete("/{exam_id}")
def delete_exam(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    db.delete(exam)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
