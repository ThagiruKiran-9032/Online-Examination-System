import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Online Examination System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-123456789")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database Settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "1234567890")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "online_exam_db")
    
    # Priority: DATABASE_URL env var -> Postgres (psycopg2)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', '1234567890')}@{os.getenv('POSTGRES_SERVER', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'online_exam_db')}"
    )

    # SMTP Email Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Online Examination System")
    EMAILS_FROM_EMAIL: str = os.getenv(
        "EMAILS_FROM_EMAIL",
        os.getenv("SMTP_USER", "noreply@onlineexam.com"),
    )
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() in ("true", "1", "t")
    SMTP_ENABLED: bool = os.getenv("SMTP_ENABLED", "True").lower() in ("true", "1", "t")

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
    )

settings = Settings()
