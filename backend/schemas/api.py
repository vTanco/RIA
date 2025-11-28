from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# Auth
class UserCreate(BaseModel):
    email: EmailStr
    password: str

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
