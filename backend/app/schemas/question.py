from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class QuestionBase(BaseModel):
    question_text: str
    question_type: str = "mcq"  # "mcq" or "true_false"
    options: List[str]
    correct_answer: str
    marks: int = 1

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    marks: Optional[int] = None

class QuestionAdminResponse(QuestionBase):
    id: int
    exam_id: int

    model_config = ConfigDict(from_attributes=True)

class QuestionStudentResponse(BaseModel):
    id: int
    exam_id: int
    question_text: str
    question_type: str
    options: List[str]
    marks: int

    model_config = ConfigDict(from_attributes=True)
