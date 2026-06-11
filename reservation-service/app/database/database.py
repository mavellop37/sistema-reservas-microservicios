import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _build_database_url() -> str:
    # 1. Si existe DATABASE_URL (inyectada por Render), la usamos directamente
    if url := os.getenv("DATABASE_URL"):
        # Corregir el formato antiguo de Heroku/Render si es necesario
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    # 2. Si activamos SQLite para pruebas locales
    if os.getenv("USE_SQLITE", "").lower() in ("1", "true", "yes"):
        return "sqlite:///./auth.db"

    # 3. Construcción estándar para local/desarrollo seguro
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "secret")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME", "postgres")

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


DATABASE_URL = _build_database_url()

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
