import pytest
from app.models.user import User
from app.core.security import get_password_hash

def test_full_exam_runner_attempt_auto_grading_and_leaderboard(client, db_session):
    # 1. Setup Admin and Create Published Exam
    admin = User(email="admin@gmail.com", full_name="Admin User", hashed_password=get_password_hash("pass"), role="admin", is_active=True)
    db_session.add(admin)
    db_session.commit()

    admin_login = client.post("/api/auth/login", json={"email": "admin@gmail.com", "password": "pass"})
    admin_token = admin_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    create_exam_resp = client.post("/api/exams/", headers=headers_admin, json={
        "title": "Logic Reasoning Master",
        "category": "Logic & Reasoning",
        "duration_minutes": 10,
        "passing_marks": 2,
        "max_attempts": 1
    })
    exam_id = create_exam_resp.json()["id"]

    # Add 2 questions (marks 1 each)
    q1_resp = client.post(f"/api/exams/{exam_id}/questions", headers=headers_admin, json={
        "question_text": "If ALL A are B, and ALL B are C, are ALL A C?",
        "question_type": "true_false",
        "options": ["True", "False"],
        "correct_answer": "0",  # True
        "marks": 1
    })
    q1_id = q1_resp.json()["id"]

    q2_resp = client.post(f"/api/exams/{exam_id}/questions", headers=headers_admin, json={
        "question_text": "Complete series: 5, 10, 15, 20, ?",
        "question_type": "mcq",
        "options": ["22", "25", "30", "35"],
        "correct_answer": "1",  # "25"
        "marks": 1
    })
    q2_id = q2_resp.json()["id"]

    # Publish exam
    client.patch(f"/api/exams/{exam_id}/publish", headers=headers_admin)

    # 2. Register & Attempt Student 1
    client.post("/api/auth/register", json={"email": "alice@gmail.com", "full_name": "Alice Smith", "password": "pass"})
    alice_login = client.post("/api/auth/login", json={"email": "alice@gmail.com", "password": "pass"})
    alice_token = alice_login.json()["access_token"]
    headers_alice = {"Authorization": f"Bearer {alice_token}"}

    # Register Alice
    reg_alice = client.post(f"/api/exams/{exam_id}/register", headers=headers_alice)
    assert reg_alice.status_code == 201

    # Start Attempt Alice
    start_alice = client.post(f"/api/exams/{exam_id}/start-attempt", headers=headers_alice)
    assert start_alice.status_code == 201
    attempt_alice_id = start_alice.json()["attempt_id"]

    # Record Tab Switch Warning
    warn_resp = client.post(f"/api/attempts/{attempt_alice_id}/record-warning", headers=headers_alice, json={"warning_type": "tab_switch"})
    assert warn_resp.json()["tab_switches"] == 1

    # Submit Alice (q1 correct, q2 wrong) -> Score 1/2 -> Fail (passing=2)
    sub_alice = client.post(f"/api/attempts/{attempt_alice_id}/submit", headers=headers_alice, json={
        "answers": {str(q1_id): "0", str(q2_id): "0"}  # q2 choice 0 is wrong
    })
    assert sub_alice.status_code == 200
    res_alice = sub_alice.json()
    assert res_alice["score"] == 1.0
    assert res_alice["passed"] is False
    assert res_alice["tab_switches"] == 1

    # 3. Register & Attempt Student 2 (Bob)
    client.post("/api/auth/register", json={"email": "bob@gmail.com", "full_name": "Bob Jones", "password": "pass"})
    bob_login = client.post("/api/auth/login", json={"email": "bob@gmail.com", "password": "pass"})
    bob_token = bob_login.json()["access_token"]
    headers_bob = {"Authorization": f"Bearer {bob_token}"}

    client.post(f"/api/exams/{exam_id}/register", headers=headers_bob)
    start_bob = client.post(f"/api/exams/{exam_id}/start-attempt", headers=headers_bob)
    attempt_bob_id = start_bob.json()["attempt_id"]

    # Submit Bob (q1 correct, q2 correct) -> Score 2/2 -> Pass
    sub_bob = client.post(f"/api/attempts/{attempt_bob_id}/submit", headers=headers_bob, json={
        "answers": {str(q1_id): "0", str(q2_id): "1"}
    })
    assert sub_bob.json()["score"] == 2.0
    assert sub_bob.json()["passed"] is True

    # 4. Check Leaderboard
    leaderboard_resp = client.get(f"/api/exams/{exam_id}/leaderboard", headers=headers_alice)
    assert leaderboard_resp.status_code == 200
    lb = leaderboard_resp.json()
    assert len(lb) == 2
    # Rank 1: Bob (score 2.0)
    assert lb[0]["student_name"] == "Bob Jones"
    assert lb[0]["score"] == 2.0
    assert lb[0]["rank"] == 1
    # Rank 2: Alice (score 1.0)
    assert lb[1]["student_name"] == "Alice Smith"
    assert lb[1]["score"] == 1.0
    assert lb[1]["rank"] == 2
