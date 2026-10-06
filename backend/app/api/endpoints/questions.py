from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.models.user import User
from app.models.exam import Exam
from app.models.question import Question
from app.schemas.question import QuestionCreate, QuestionUpdate, QuestionAdminResponse

router = APIRouter()

@router.post("/exams/{exam_id}/questions", response_model=QuestionAdminResponse, status_code=status.HTTP_201_CREATED)
def create_question(
    exam_id: int,
    q_in: QuestionCreate,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question = Question(
        exam_id=exam_id,
        question_text=q_in.question_text,
        question_type=q_in.question_type,
        options=q_in.options,
        correct_answer=q_in.correct_answer,
        marks=q_in.marks
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/exams/{exam_id}/questions", response_model=List[QuestionAdminResponse])
def list_exam_questions_admin(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return db.query(Question).filter(Question.exam_id == exam_id).all()

@router.put("/questions/{question_id}", response_model=QuestionAdminResponse)
def update_question(
    question_id: int,
    q_in: QuestionUpdate,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    update_data = q_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(question, field, value)
        
    db.commit()
    db.refresh(question)
    return question

@router.delete("/questions/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(deps.get_db),
    admin_user: User = Depends(deps.get_current_admin)
) -> Any:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    db.delete(question)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
