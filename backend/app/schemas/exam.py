from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

VALID_CATEGORIES = ["Numeric", "Logic & Reasoning", "English", "General Knowledge", "Technical"]

class ExamBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "General Knowledge"
    duration_minutes: int = 30
    passing_marks: int = 1
    max_attempts: int = 1

class ExamCreate(ExamBase):
    pass

class ExamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    passing_marks: Optional[int] = None
    max_attempts: Optional[int] = None
    is_published: Optional[bool] = None

class ExamResponse(ExamBase):
    id: int
    is_published: bool
    created_at: datetime
    total_questions: int = 0
    total_marks: int = 0

    model_config = ConfigDict(from_attributes=True)
