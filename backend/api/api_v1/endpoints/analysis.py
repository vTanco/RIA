from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from backend.database.session import get_db, get_predatory_db
from backend.database.models import User, Analysis
from backend.schemas.api import AnalysisResponse
from backend.api import deps
from backend.core.config import settings
from backend.engine.pdf_processor import extract_text_from_pdf
from backend.engine.scorer import COIScorer
from backend.engine.llm_wrapper import LLMWrapper

router = APIRouter()

@router.post("/analyze/pdf", response_model=AnalysisResponse)
async def analyze_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    predatory_db: Session = Depends(get_predatory_db),
    current_user: User = Depends(deps.get_current_user)
):
    # Save temp file
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process
        text, file_hash = extract_text_from_pdf(temp_path)
        
        # Score
        scorer = COIScorer(text, db=db, predatory_db=predatory_db)
        result = scorer.compute_score()
        
        # Summarize
        llm = LLMWrapper(api_key=settings.OPENAI_API_KEY)
        summary = llm.summarize_risk(result, result["score"])
        
        # Save to DB
        db_analysis = Analysis(
            user_id=current_user.id,
            filename=file.filename,
            overall_risk=result["overall_risk"],
            score=result["score"],
            summary=summary,
            full_result=result
        )
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        return db_analysis
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/history", response_model=List[AnalysisResponse])
def get_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).offset(skip).limit(limit).all()
    return analyses

from backend.engine.predatory_updater import PredatoryJournalUpdater

@router.post("/admin/update-predatory-list")
def update_predatory_list(
    db: Session = Depends(get_db),
    predatory_db: Session = Depends(get_predatory_db),
    current_user: User = Depends(deps.get_current_user)
):
    # In a real app, check for admin role
    updater = PredatoryJournalUpdater(predatory_db)
    count = updater.update_database()
    return {"message": f"Updated {count} predatory journals"}
