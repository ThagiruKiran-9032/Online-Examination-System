from app.db.session import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = "admin@example.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                full_name="System Administrator",
                hashed_password=get_password_hash("adminpassword123"),
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"[Seed] Created default admin account: {admin_email} / adminpassword123")
        else:
            print(f"[Seed] Admin account {admin_email} already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
