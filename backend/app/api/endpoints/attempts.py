from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Any

from app.api import deps
from app.core.email import send_exam_result_email
from app.models.user import User
from app.models.exam import Exam
from app.models.question import Question
from app.models.registration import ExamRegistration
from app.models.attempt import ExamAttempt, AttemptAnswer
from app.schemas.question import QuestionStudentResponse
from app.schemas.attempt import (
    StartAttemptResponse, 
    RecordWarningRequest, 
    SubmitExamRequest, 
    AttemptResultResponse, 
    QuestionReview
)

router = APIRouter()

@router.post("/exams/{exam_id}/start-attempt", response_model=StartAttemptResponse, status_code=status.HTTP_201_CREATED)
def start_exam_attempt(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam or not exam.is_published:
        raise HTTPException(status_code=404, detail="Exam not available")
    
    # Check registration
    reg = db.query(ExamRegistration).filter(
        ExamRegistration.exam_id == exam_id,
        ExamRegistration.student_id == student_user.id
    ).first()
    if not reg:
        raise HTTPException(status_code=403, detail="You must register for this exam before attempting it.")
    
    # Check max attempt limit
    completed_attempts = db.query(ExamAttempt).filter(
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.student_id == student_user.id
    ).count()
    if completed_attempts >= exam.max_attempts:
        raise HTTPException(
            status_code=400, 
            detail=f"Maximum allowed attempts ({exam.max_attempts}) reached for this exam."
        )
    
    # Check active attempt
    active = db.query(ExamAttempt).filter(
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.student_id == student_user.id,
        ExamAttempt.status == "in_progress"
    ).first()
    if active:
        # Resume active attempt
        attempt = active
    else:
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=student_user.id,
            start_time=datetime.now(timezone.utc),
            status="in_progress",
            tab_switches=0
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    
    questions = db.query(Question).filter(Question.exam_id == exam_id).all()
    student_questions = [
        QuestionStudentResponse(
            id=q.id,
            exam_id=q.exam_id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            marks=q.marks
        ) for q in questions
    ]
    
    return StartAttemptResponse(
        attempt_id=attempt.id,
        exam_id=exam.id,
        exam_title=exam.title,
        category=exam.category,
        duration_minutes=exam.duration_minutes,
        start_time=attempt.start_time,
        questions=student_questions
    )

@router.post("/attempts/{attempt_id}/record-warning")
def record_warning(
    attempt_id: int,
    payload: RecordWarningRequest,
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.student_id == student_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != "in_progress":
        raise HTTPException(status_code=400, detail="Attempt is not active")
    
    attempt.tab_switches += 1
    db.commit()
    return {"tab_switches": attempt.tab_switches}

@router.post("/attempts/{attempt_id}/submit", response_model=AttemptResultResponse)
def submit_exam_attempt(
    attempt_id: int,
    payload: SubmitExamRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    attempt = db.query(ExamAttempt).filter(
        ExamAttempt.id == attempt_id,
        ExamAttempt.student_id == student_user.id
    ).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != "in_progress":
        # Return result if already submitted
        return get_attempt_result_response(attempt, db)
    
    now = datetime.now(timezone.utc)
    exam = attempt.exam
    
    # Timer validation
    elapsed_seconds = (now.replace(tzinfo=None) - attempt.start_time.replace(tzinfo=None)).total_seconds()
    max_allowed_seconds = (exam.duration_minutes * 60) + 60  # 1 min grace buffer for latency
    is_time_expired = elapsed_seconds > max_allowed_seconds
    
    questions = db.query(Question).filter(Question.exam_id == exam.id).all()
    
    total_score = 0.0
    total_possible = sum(q.marks for q in questions)
    answers_map = payload.answers  # question_id -> selected_option
    
    # Delete prior answers if any retry
    db.query(AttemptAnswer).filter(AttemptAnswer.attempt_id == attempt.id).delete()
    
    reviews = []
    for q in questions:
        selected_opt = answers_map.get(q.id) or answers_map.get(str(q.id))
        is_corr = False
        marks_awarded = 0.0
        
        if selected_opt is not None and str(selected_opt).strip() == str(q.correct_answer).strip():
            is_corr = True
            marks_awarded = float(q.marks)
            total_score += marks_awarded
            
        attempt_ans = AttemptAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=str(selected_opt) if selected_opt is not None else None,
            is_correct=is_corr,
            marks_awarded=marks_awarded
        )
        db.add(attempt_ans)
        
        reviews.append(QuestionReview(
            question_id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            selected_option=str(selected_opt) if selected_opt is not None else None,
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            marks_awarded=marks_awarded,
            max_marks=q.marks
        ))
        
    passed = total_score >= exam.passing_marks
    attempt.end_time = now
    attempt.score = total_score
    attempt.total_possible_score = total_possible
    attempt.passed = passed
    attempt.status = "time_expired" if is_time_expired else "completed"
    
    db.commit()
    db.refresh(attempt)
    
    background_tasks.add_task(
        send_exam_result_email,
        student_user.email,
        student_user.full_name,
        exam.title,
        attempt.score,
        attempt.total_possible_score,
        exam.passing_marks,
        attempt.passed
    )
    
    return AttemptResultResponse(
        attempt_id=attempt.id,
        exam_id=exam.id,
        exam_title=exam.title,
        category=exam.category,
        duration_minutes=exam.duration_minutes,
        score=attempt.score,
        total_possible_score=attempt.total_possible_score,
        passing_marks=float(exam.passing_marks),
        passed=attempt.passed,
        tab_switches=attempt.tab_switches,
        status=attempt.status,
        start_time=attempt.start_time,
        end_time=attempt.end_time,
        questions_review=reviews
    )

def get_attempt_result_response(attempt: ExamAttempt, db: Session) -> AttemptResultResponse:
    exam = attempt.exam
    questions = db.query(Question).filter(Question.exam_id == exam.id).all()
    user_answers = {a.question_id: a for a in attempt.answers}
    
    reviews = []
    for q in questions:
        ans = user_answers.get(q.id)
        selected_opt = ans.selected_option if ans else None
        is_corr = ans.is_correct if ans else False
        marks_awarded = ans.marks_awarded if ans else 0.0
        
        reviews.append(QuestionReview(
            question_id=q.id,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            selected_option=selected_opt,
            correct_answer=q.correct_answer,
            is_correct=is_corr,
            marks_awarded=marks_awarded,
            max_marks=q.marks
        ))
        
    return AttemptResultResponse(
        attempt_id=attempt.id,
        exam_id=exam.id,
        exam_title=exam.title,
        category=exam.category,
        duration_minutes=exam.duration_minutes,
        score=attempt.score,
        total_possible_score=attempt.total_possible_score,
        passing_marks=float(exam.passing_marks),
        passed=attempt.passed,
        tab_switches=attempt.tab_switches,
        status=attempt.status,
        start_time=attempt.start_time,
        end_time=attempt.end_time,
        questions_review=reviews
    )
