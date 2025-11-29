from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal

db = SessionLocal()
count = db.query(PredatoryJournal).count()
print(f"Total Predatory Journals: {count}")
db.close()
