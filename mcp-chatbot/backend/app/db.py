import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pymongo import MongoClient


# Configuration via environment variables
# DB_BACKEND: "sql" or "mongo"
DB_BACKEND = os.getenv("DB_BACKEND", "sql").lower()

# SQL config
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL",
    # Example: postgresql+psycopg2://user:password@localhost:5432/dbname
    "sqlite:///./orders.db",
)

# Mongo config
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "mcp_chatbot")


# SQLAlchemy session factory (only initialized if DB_BACKEND == 'sql')
engine = None
SessionLocal: Optional[sessionmaker] = None

if DB_BACKEND == "sql":
    connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    if DB_BACKEND != "sql":
        raise RuntimeError("get_db() called but DB_BACKEND is not 'sql'")
    db: Session = SessionLocal()  # type: ignore[call-arg]
    try:
        yield db
    finally:
        db.close()


# Mongo client (only initialized if DB_BACKEND == 'mongo')
mongo_client: Optional[MongoClient] = None
mongo_db = None

if DB_BACKEND == "mongo":
    mongo_client = MongoClient(MONGO_URI)
    mongo_db = mongo_client[MONGO_DB_NAME]


def get_mongo():
    if DB_BACKEND != "mongo":
        raise RuntimeError("get_mongo() called but DB_BACKEND is not 'mongo'")
    return mongo_db


def init_sql_models(create_all: bool = True) -> None:
    """Initialize SQL models and optionally create tables."""
    if DB_BACKEND != "sql":
        return
    if not create_all:
        return
    # Local import to avoid circulars
    from .models import Base  # noqa: WPS433

    Base.metadata.create_all(bind=engine)


