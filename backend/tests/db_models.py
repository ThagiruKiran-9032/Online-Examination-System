import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models import User, Exam, Question, ExamRegistration, ExamAttempt, AttemptAnswer
from app.core.security import get_password_hash, verify_password, create_access_token

@pytest.fixture
def db_session():
    # Use SQLite in memory for ultra-fast model testing
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_user_creation_and_security(db_session):
    hashed_pwd = get_password_hash("secret123")
    assert verify_password("secret123", hashed_pwd) is True
    assert verify_password("wrong", hashed_pwd) is False

    user = User(email="testadmin@example.com", full_name="Test Admin", hashed_password=hashed_pwd, role="admin")
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(email="testadmin@example.com").first()
    assert fetched is not None
    assert fetched.role == "admin"

    token = create_access_token(subject=user.id, role=user.role)
    assert token is not None

def test_exam_and_question_relationships(db_session):
    exam = Exam(
        title="Logic & Reasoning Challenge",
        description="Test your logical skills",
        category="Logic & Reasoning",
        duration_minutes=15,
        passing_marks=2,
        max_attempts=1,
        is_published=True
    )
    db_session.add(exam)
    db_session.commit()

    q1 = Question(
        exam_id=exam.id,
        question_text="What comes next in sequence: 2, 4, 8, 16, ...?",
        question_type="mcq",
        options=["20", "24", "32", "64"],
        correct_answer="2",  # index 2 -> 32
        marks=1
    )
    q2 = Question(
        exam_id=exam.id,
        question_text="Is 17 a prime number?",
        question_type="true_false",
        options=["True", "False"],
        correct_answer="0",  # True
        marks=1
    )
    db_session.add_all([q1, q2])
    db_session.commit()

    fetched_exam = db_session.query(Exam).filter_by(id=exam.id).first()
    assert len(fetched_exam.questions) == 2
    assert fetched_exam.category == "Logic & Reasoning"

def test_registration_and_attempt_flow(db_session):
    student = User(email="student1@example.com", full_name="Student One", hashed_password="hashed_pwd", role="student")
    exam = Exam(title="English Proficiency", category="English", duration_minutes=10)
    db_session.add_all([student, exam])
    db_session.commit()

    # Registration
    reg = ExamRegistration(exam_id=exam.id, student_id=student.id)
    db_session.add(reg)
    db_session.commit()

    assert db_session.query(ExamRegistration).count() == 1

    # Attempt
    attempt = ExamAttempt(exam_id=exam.id, student_id=student.id, status="in_progress")
    db_session.add(attempt)
    db_session.commit()

    answer = AttemptAnswer(attempt_id=attempt.id, question_id=1, selected_option="0", is_correct=True, marks_awarded=1.0)
    db_session.add(answer)
    db_session.commit()

    fetched_attempt = db_session.query(ExamAttempt).filter_by(id=attempt.id).first()
    assert len(fetched_attempt.answers) == 1
    assert fetched_attempt.answers[0].is_correct is True
