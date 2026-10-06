import pytest
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_token(client, db_session):
    admin = User(
        email="admin@test.com",
        full_name="Admin",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "adminpass"})
    return resp.json()["access_token"]

def create_student_token(client):
    client.post("/api/auth/register", json={
        "email": "student@test.com",
        "full_name": "Student",
        "password": "studentpass",
        "role": "student"
    })
    login_resp = client.post("/api/auth/login", json={"email": "student@test.com", "password": "studentpass"})
    return login_resp.json()["access_token"]

def test_exam_and_question_crud_flow(client, db_session):
    admin_token = create_admin_token(client, db_session)
    student_token = create_student_token(client)
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    headers_student = {"Authorization": f"Bearer {student_token}"}

    # 1. Create Exam
    create_exam_resp = client.post("/api/exams/", headers=headers_admin, json={
        "title": "Numeric Ability Test 1",
        "description": "Math & Speed calculation test",
        "category": "Numeric",
        "duration_minutes": 20,
        "passing_marks": 2,
        "max_attempts": 1
    })
    assert create_exam_resp.status_code == 201
    exam_data = create_exam_resp.json()
    assert exam_data["category"] == "Numeric"
    assert exam_data["is_published"] is False
    exam_id = exam_data["id"]

    # Student cannot see draft exam
    list_student_1 = client.get("/api/exams/", headers=headers_student)
    assert len(list_student_1.json()) == 0

    # 2. Add Questions
    q1_resp = client.post(f"/api/exams/{exam_id}/questions", headers=headers_admin, json={
        "question_text": "What is 15 * 12?",
        "question_type": "mcq",
        "options": ["160", "180", "190", "200"],
        "correct_answer": "1",  # "180"
        "marks": 1
    })
    assert q1_resp.status_code == 201

    q2_resp = client.post(f"/api/exams/{exam_id}/questions", headers=headers_admin, json={
        "question_text": "Is 101 a prime number?",
        "question_type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "0",  # True
        "marks": 1
    })
    assert q2_resp.status_code == 201

    # 3. Publish Exam
    pub_resp = client.patch(f"/api/exams/{exam_id}/publish", headers=headers_admin)
    assert pub_resp.status_code == 200
    assert pub_resp.json()["is_published"] is True

    # 4. Student listing & category filtering
    list_student_2 = client.get("/api/exams/", headers=headers_student)
    assert len(list_student_2.json()) == 1

    list_filtered_numeric = client.get("/api/exams/?category=Numeric", headers=headers_student)
    assert len(list_filtered_numeric.json()) == 1

    list_filtered_english = client.get("/api/exams/?category=English", headers=headers_student)
    assert len(list_filtered_english.json()) == 0
