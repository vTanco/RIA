from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char in "!@#$%^&*(),.?\":{}|<>" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Analysis
class AnalysisBase(BaseModel):
    filename: str
    overall_risk: str
    score: int
    summary: str
    full_result: Dict[str, Any]

class AnalysisCreate(AnalysisBase):
    pass

class AnalysisResponse(AnalysisBase):
    id: int
    upload_date: datetime
    
    class Config:
        from_attributes = True

class AnalysisRequestURL(BaseModel):
    url: str
