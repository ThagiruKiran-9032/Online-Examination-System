from datetime import datetime
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.question import QuestionStudentResponse

class StartAttemptResponse(BaseModel):
    attempt_id: int
    exam_id: int
    exam_title: str
    category: str
    duration_minutes: int
    start_time: datetime
    questions: List[QuestionStudentResponse]

class RecordWarningRequest(BaseModel):
    warning_type: str = "tab_switch"

class SubmitExamRequest(BaseModel):
    answers: Dict[int, str]  # question_id -> selected_option index/string

class QuestionReview(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    options: List[str]
    selected_option: Optional[str] = None
    correct_answer: str
    is_correct: bool
    marks_awarded: float
    max_marks: int

class AttemptResultResponse(BaseModel):
    attempt_id: int
    exam_id: int
    exam_title: str
    category: str
    duration_minutes: int = 30
    score: float
    total_possible_score: float
    passing_marks: float
    passed: bool
    tab_switches: int
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    questions_review: List[QuestionReview] = []

    model_config = ConfigDict(from_attributes=True)

class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    student_name: str
    score: float
    total_possible_score: float
    passed: bool
    tab_switches: int
    submitted_at: datetime
