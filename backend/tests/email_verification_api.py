import pytest
from app.models.user import User
from app.core.security import get_password_hash

def test_verify_email_endpoint_valid_and_unregistered(client):
    response = client.post(
        "/api/auth/verify-email",
        json={"email": "realuser@gmail.com", "check_domain": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_syntax"] is True
    assert data["is_real_domain"] is True
    assert data["is_registered"] is False

def test_verify_email_endpoint_invalid_syntax(client):
    response = client.post(
        "/api/auth/verify-email",
        json={"email": "invalid-email-syntax", "check_domain": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_syntax"] is False
    assert data["is_registered"] is False

def test_verify_email_endpoint_fake_domain(client):
    response = client.post(
        "/api/auth/verify-email",
        json={"email": "user@thisisafakedomainthatdoesnotexist12345.com", "check_domain": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_syntax"] is True
    assert data["is_real_domain"] is False

def test_verify_email_endpoint_already_registered(client, db_session):
    user = User(
        email="existing_user@gmail.com",
        full_name="Existing User",
        hashed_password=get_password_hash("pass123"),
        role="student",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/verify-email",
        json={"email": "existing_user@gmail.com", "check_domain": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid_syntax"] is True
    assert data["is_registered"] is True
