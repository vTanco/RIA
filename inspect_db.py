from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal

db = SessionLocal()
journals = db.query(PredatoryJournal).limit(5).all()
print(f"Total records: {db.query(PredatoryJournal).count()}")
for j in journals:
    print(f"Name: {j.name}, ISSN: {j.issn}, Source: {j.source}")
db.close()
