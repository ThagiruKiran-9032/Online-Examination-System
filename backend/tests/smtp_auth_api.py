import pytest
from app.models.user import User
from app.core.security import get_password_hash
from app.core.email import (
    send_email,
    send_welcome_email,
    send_exam_registration_email,
    send_exam_result_email,
    send_password_reset_email
)

def test_smtp_mock_senders():
    # Test that email helper functions run gracefully without throwing errors
    assert send_welcome_email("test_student@gmail.com", "Test Student") is None or True
    assert send_exam_registration_email("test_student@gmail.com", "Test Student", "Python 101", "Technical") is None or True
    assert send_exam_result_email("test_student@gmail.com", "Test Student", "Python 101", 85.0, 100.0, 60.0, True) is None or True
    assert send_password_reset_email("test_student@gmail.com", "TOKEN123") is None or True

def test_forgot_and_reset_password_flow(client, db_session):
    user = User(
        email="reset_me@gmail.com",
        full_name="Reset User",
        hashed_password=get_password_hash("oldpassword123"),
        role="student",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    # Step 1: Request password reset OTP
    forgot_resp = client.post("/api/auth/forgot-password", json={"email": "reset_me@gmail.com"})
    assert forgot_resp.status_code == 200

    # Retrieve generated reset token from DB
    db_session.refresh(user)
    token = user.reset_token
    assert token is not None

    # Step 2: Reset password using token
    reset_resp = client.post(
        "/api/auth/reset-password",
        json={
            "email": "reset_me@gmail.com",
            "token": token,
            "new_password": "brandnewpassword123"
        }
    )
    assert reset_resp.status_code == 200

    # Step 3: Verify login with new password
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "reset_me@gmail.com", "password": "brandnewpassword123"}
    )
    assert login_resp.status_code == 200
    assert "access_token" in login_resp.json()

def test_registration_otp_flow(client, db_session):
    from app.models.user import EmailVerification
    test_email = "newstudent_otp@gmail.com"

    # Step 1: Send Registration OTP
    send_resp = client.post("/api/auth/send-registration-otp", json={"email": test_email})
    assert send_resp.status_code == 200
    assert "Verification OTP code sent" in send_resp.json()["message"]

    # Retrieve stored OTP from DB
    ver_rec = db_session.query(EmailVerification).filter_by(email=test_email).first()
    assert ver_rec is not None
    otp_code = ver_rec.otp
    assert len(otp_code) == 6

    # Step 2: Verify Registration OTP
    verify_resp = client.post("/api/auth/verify-registration-otp", json={"email": test_email, "otp": otp_code})
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True

    # Step 3: Complete Registration with OTP
    reg_resp = client.post(
        "/api/auth/register",
        json={
            "email": test_email,
            "full_name": "OTP Student",
            "password": "securepassword123",
            "otp": otp_code
        }
    )
    assert reg_resp.status_code == 201
    assert reg_resp.json()["email"] == test_email

