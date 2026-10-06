from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False, default="mcq")  # "mcq" or "true_false"
    options = Column(JSON, nullable=False)  # List of option strings, e.g. ["Option A", "Option B", ...]
    correct_answer = Column(String, nullable=False)  # String index (e.g. "0") or answer text
    marks = Column(Integer, nullable=False, default=1)

    exam = relationship("Exam", back_populates="questions")
