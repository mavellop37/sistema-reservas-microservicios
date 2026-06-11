import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _build_database_url() -> str:
    if url := os.getenv("DATABASE_URL"):
        return url

    if os.getenv("USE_SQLITE", "").lower() in ("1", "true", "yes"):
        return "sqlite:///./auth.db"

    user = os.getenv("DB_USER", "marorigenet_reserva_user")
    password = os.getenv("DB_PASSWORD", "vPw{M+e~ow]0")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "reservadb")

    return f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{name}"


DATABASE_URL = _build_database_url()

# Algunos hosts (cPanel, Heroku) entregan postgres:// en lugar de postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
