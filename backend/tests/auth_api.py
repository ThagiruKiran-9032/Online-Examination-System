import pytest
from app.models.user import User
from app.core.security import get_password_hash

def test_register_and_login_student(client):
    reg_response = client.post(
        "/api/auth/register",
        json={
            "email": "student1@example.com",
            "full_name": "Student One",
            "password": "password123",
            "role": "student"
        }
    )
    assert reg_response.status_code == 201, f"Register failed: {reg_response.text}"
    data = reg_response.json()
    assert data["email"] == "student1@example.com"
    assert data["role"] == "student"

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "student1@example.com",
            "password": "password123"
        }
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token_data = login_response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "student1@example.com"

def test_admin_role_protection(client):
    client.post(
        "/api/auth/register",
        json={"email": "student2@example.com", "full_name": "Student Two", "password": "pass"}
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "student2@example.com", "password": "pass"}
    )
    token = login_resp.json()["access_token"]

    resp = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403

def test_admin_student_management(client, db_session):
    admin = User(
        email="admin@example.com",
        full_name="System Admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin123"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]

    create_resp = client.post(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "newstudent@example.com", "full_name": "New Student", "password": "pass"}
    )
    assert create_resp.status_code == 201

    list_resp = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == 200
    students_list = list_resp.json()
    assert len(students_list) == 1
    assert students_list[0]["email"] == "newstudent@example.com"
