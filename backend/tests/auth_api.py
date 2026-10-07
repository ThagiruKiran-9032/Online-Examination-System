import pytest
from app.models.user import User
from app.core.security import get_password_hash

def test_register_and_login_student(client):
    reg_response = client.post(
        "/api/auth/register",
        json={
            "email": "student1@gmail.com",
            "full_name": "Student One",
            "password": "password123",
            "role": "student"
        }
    )
    assert reg_response.status_code == 201, f"Register failed: {reg_response.text}"
    data = reg_response.json()
    assert data["email"] == "student1@gmail.com"
    assert data["role"] == "student"

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "student1@gmail.com",
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
    assert me_response.json()["email"] == "student1@gmail.com"

def test_admin_role_protection(client):
    client.post(
        "/api/auth/register",
        json={"email": "student2@gmail.com", "full_name": "Student Two", "password": "pass"}
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "student2@gmail.com", "password": "pass"}
    )
    token = login_resp.json()["access_token"]

    resp = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403

def test_admin_student_management(client, db_session):
    admin = User(
        email="admin@gmail.com",
        full_name="System Admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@gmail.com", "password": "admin123"}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    token = login_resp.json()["access_token"]

    create_resp = client.post(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"},
        json={"email": "newstudent@gmail.com", "full_name": "New Student", "password": "pass"}
    )
    assert create_resp.status_code == 201

    list_resp = client.get(
        "/api/students/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_resp.status_code == 200
    students_list = list_resp.json()
    assert len(students_list) == 1
    assert students_list[0]["email"] == "newstudent@gmail.com"

def test_student_update_personal_details_cannot_edit_email(client):
    reg_response = client.post(
        "/api/auth/register",
        json={
            "email": "editable_student@gmail.com",
            "full_name": "Original Name",
            "password": "oldpassword123",
            "role": "student"
        }
    )
    assert reg_response.status_code == 201

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "editable_student@gmail.com", "password": "oldpassword123"}
    )
    token = login_resp.json()["access_token"]

    # Student updates profile details: full_name, phone, department, password
    update_resp = client.put(
        "/api/students/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Updated Name",
            "phone": "+1234567890",
            "department": "Computer Science",
            "password": "newpassword123",
            "email": "hacked_email@gmail.com"  # attempt to hack email change
        }
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["full_name"] == "Updated Name"
    assert data["phone"] == "+1234567890"
    assert data["department"] == "Computer Science"
    # Verify email is NOT changed!
    assert data["email"] == "editable_student@gmail.com"

    # Verify student can login with new password
    login_new_pass = client.post(
        "/api/auth/login",
        json={"email": "editable_student@gmail.com", "password": "newpassword123"}
    )
    assert login_new_pass.status_code == 200

def test_admin_update_student_details(client, db_session):
    admin = User(
        email="admin_update@gmail.com",
        full_name="Admin User",
        hashed_password=get_password_hash("adminpass"),
        role="admin",
        is_active=True
    )
    student = User(
        email="target_student@gmail.com",
        full_name="Target Student",
        hashed_password=get_password_hash("pass"),
        role="student",
        is_active=True
    )
    db_session.add(admin)
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin_update@gmail.com", "password": "adminpass"}
    )
    token = login_resp.json()["access_token"]

    update_resp = client.put(
        f"/api/students/{student.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Admin Updated Student Name",
            "phone": "+9876543210",
            "department": "Mathematics"
        }
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["full_name"] == "Admin Updated Student Name"
    assert data["phone"] == "+9876543210"
    assert data["department"] == "Mathematics"
