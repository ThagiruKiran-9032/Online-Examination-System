from urllib.parse import urlparse
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

def ensure_database_exists(db_url: str):
    try:
        # Normalize URL to get connection details
        clean_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
        parsed = urlparse(clean_url)
        db_name = parsed.path.lstrip('/')
        
        if not db_name or db_name == 'postgres':
            return
            
        user = parsed.username or 'postgres'
        password = parsed.password or ''
        host = parsed.hostname or 'localhost'
        port = parsed.port or 5432
        
        # Connect to default 'postgres' maintenance database
        conn = psycopg2.connect(
            user=user, 
            password=password, 
            host=host, 
            port=port, 
            dbname='postgres'
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s;", (db_name,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f'CREATE DATABASE "{db_name}";')
            print(f"[PostgreSQL] Successfully created database: '{db_name}'")
        else:
            print(f"[PostgreSQL] Database '{db_name}' is ready.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PostgreSQL] Notice during database auto-creation: {e}")

def get_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        
    ensure_database_exists(db_url)
    print(f"[Database] Connecting to PostgreSQL at {db_url.split('@')[-1] if '@' in db_url else db_url}")
    return create_engine(db_url, pool_pre_ping=True)

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
