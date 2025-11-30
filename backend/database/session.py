from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Predatory Database Setup
predatory_engine = create_engine(
    settings.PREDATORY_DATABASE_URI, connect_args={"check_same_thread": False}
)
PredatorySessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=predatory_engine)

PredatoryBase = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_predatory_db():
    db = PredatorySessionLocal()
    try:
        yield db
    finally:
        db.close()
