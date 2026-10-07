from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
from app.api.router import api_router
from app.models import *  # Ensure all models are registered

from sqlalchemy import inspect, text

# Create database tables automatically
Base.metadata.create_all(bind=engine)

# Auto-migrate DB schema for added columns if DB already exists
try:
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("users")]
        with engine.connect() as conn:
            if "phone" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR"))
                print("[DB Migration] Added 'phone' column to 'users' table")
            if "department" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR"))
                print("[DB Migration] Added 'department' column to 'users' table")
            if "reset_token" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token VARCHAR"))
                print("[DB Migration] Added 'reset_token' column to 'users' table")
            if "reset_token_expires" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN reset_token_expires TIMESTAMP"))
                print("[DB Migration] Added 'reset_token_expires' column to 'users' table")
            conn.commit()
except Exception as e:
    print(f"[DB Migration Warning] {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Online Examination System API is running"}
