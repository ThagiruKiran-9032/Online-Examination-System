from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from app.api import deps
from app.models.user import User
from app.models.exam import Exam
from app.models.attempt import ExamAttempt
from app.schemas.attempt import AttemptResultResponse, LeaderboardEntry
from app.api.endpoints.attempts import get_attempt_result_response

router = APIRouter()

@router.get("/attempts/{attempt_id}/result", response_model=AttemptResultResponse)
def get_attempt_result(
    attempt_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    attempt = db.query(ExamAttempt).filter(ExamAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    if current_user.role != "admin" and attempt.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    return get_attempt_result_response(attempt, db)

@router.get("/exams/{exam_id}/leaderboard", response_model=List[LeaderboardEntry])
def get_exam_leaderboard(
    exam_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.exam_id == exam_id,
        ExamAttempt.status.in_(["completed", "time_expired"])
    ).order_by(ExamAttempt.score.desc(), ExamAttempt.end_time.asc()).all()
    
    leaderboard = []
    current_rank = 1
    for idx, att in enumerate(attempts):
        # Tie handling: if score equals previous score, keep same rank
        if idx > 0 and att.score == attempts[idx - 1].score:
            rank = leaderboard[-1].rank
        else:
            rank = idx + 1
            
        leaderboard.append(LeaderboardEntry(
            rank=rank,
            student_id=att.student_id,
            student_name=att.student.full_name,
            score=att.score,
            total_possible_score=att.total_possible_score,
            passed=att.passed,
            tab_switches=att.tab_switches,
            submitted_at=att.end_time or att.start_time
        ))
        
    return leaderboard

@router.get("/students/me/results", response_model=List[AttemptResultResponse])
def get_my_results(
    db: Session = Depends(deps.get_db),
    student_user: User = Depends(deps.get_current_student)
) -> Any:
    attempts = db.query(ExamAttempt).filter(
        ExamAttempt.student_id == student_user.id,
        ExamAttempt.status.in_(["completed", "time_expired"])
    ).order_by(ExamAttempt.created_at.desc()).all()
    
    return [get_attempt_result_response(a, db) for a in attempts]
