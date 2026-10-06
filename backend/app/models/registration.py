from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.session import Base

class ExamRegistration(Base):
    __tablename__ = "exam_registrations"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    exam = relationship("Exam", back_populates="registrations")
    student = relationship("User", back_populates="registrations")

    __table_args__ = (
        UniqueConstraint("exam_id", "student_id", name="uq_exam_student_registration"),
    )
