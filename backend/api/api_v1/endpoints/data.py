from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.session import get_db
from backend.database.models import PredatoryJournal
from fastapi.responses import StreamingResponse
import csv
import io

router = APIRouter()

@router.get("/download/predatory-journals")
def download_predatory_journals(db: Session = Depends(get_db)):
    journals = db.query(PredatoryJournal).all()
    
    output = io.StringIO()
    # Use semicolon delimiter which is often safer for Excel in some locales, 
    # but comma is standard. Let's stick to comma but ensure BOM is handled if we were writing bytes.
    # Since we are using StreamingResponse with text/csv, we can't easily prepend BOM to StringIO.
    # We need to yield bytes.
    
    def iter_csv():
        # Yield BOM for Excel
        yield u'\ufeff'.encode('utf-8')
        
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        
        # Header
        writer.writerow(['Name', 'ISSN', 'Publisher', 'Source', 'URL', 'Last Updated'])
        yield csv_file.getvalue().encode('utf-8')
        csv_file.seek(0)
        csv_file.truncate(0)
        
        # Data
        for j in journals:
            writer.writerow([
                j.name,
                j.issn,
                j.publisher,
                j.source,
                j.url,
                str(j.last_updated)
            ])
            yield csv_file.getvalue().encode('utf-8')
            csv_file.seek(0)
            csv_file.truncate(0)

    response = StreamingResponse(
        iter_csv(),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=predatory_journals.csv"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response

@router.get("/predatory-journals")
def get_predatory_journals(
    skip: int = 0, 
    limit: int = 50, 
    search: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(PredatoryJournal)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (PredatoryJournal.name.ilike(search_filter)) | 
            (PredatoryJournal.publisher.ilike(search_filter)) |
            (PredatoryJournal.issn.ilike(search_filter))
        )
    
    total = query.count()
    journals = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "items": journals,
        "skip": skip,
        "limit": limit
    }
