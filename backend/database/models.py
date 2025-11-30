from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database.session import Base, PredatoryBase

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analyses = relationship("Analysis", back_populates="owner")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # The core result
    overall_risk = Column(String) # low, medium, high
    score = Column(Integer)
    summary = Column(Text)
    
    # Storing the full JSON result
    full_result = Column(JSON)

    owner = relationship("User", back_populates="analyses")

class PredatoryJournal(PredatoryBase):
    __tablename__ = "predatory_journals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    issn = Column(String, index=True, nullable=True)
    publisher = Column(String, index=True, nullable=True)
    source = Column(String) # beall, predatoryjournals, etc.
    entity_type = Column(String, default="journal") # journal, publisher
    url = Column(String, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
