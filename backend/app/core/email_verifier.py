from typing import Dict, Any
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User

def verify_email_address(email: str, db: Session = None, check_deliverability: bool = True) -> Dict[str, Any]:
    """
    Verifies an email address for:
    1. Syntax & RFC specification validity.
    2. Domain existence and mail deliverability (MX DNS check).
    3. Registration status in the local system database (if db session provided).
    """
    cleaned_email = (email or "").strip().lower()

    if not cleaned_email:
        return {
            "email": cleaned_email,
            "is_valid_syntax": False,
            "is_real_domain": False,
            "is_registered": False,
            "error_detail": "Email address cannot be empty."
        }

    # Step 1 & 2: Syntax and Domain Deliverability Check
    try:
        validated = validate_email(cleaned_email, check_deliverability=check_deliverability)
        normalized_email = validated.normalized
    except EmailNotValidError as e:
        # If deliverability fails, check if syntax is valid
        try:
            validated = validate_email(cleaned_email, check_deliverability=False)
            normalized_email = validated.normalized
            is_real_domain = False
            error_msg = str(e)
        except EmailNotValidError as syntax_err:
            return {
                "email": cleaned_email,
                "is_valid_syntax": False,
                "is_real_domain": False,
                "is_registered": False,
                "error_detail": f"Invalid email format: {syntax_err}"
            }
        return {
            "email": normalized_email,
            "is_valid_syntax": True,
            "is_real_domain": False,
            "is_registered": False,
            "error_detail": f"Domain verification failed: {error_msg}"
        }

    # Step 3: Check database registration status
    is_registered = False
    if db is not None:
        user = db.query(User).filter(func.lower(User.email) == normalized_email).first()
        is_registered = user is not None

    return {
        "email": normalized_email,
        "is_valid_syntax": True,
        "is_real_domain": True,
        "is_registered": is_registered,
        "error_detail": None
    }
