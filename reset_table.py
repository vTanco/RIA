from backend.database.session import engine
from backend.database.models import Base, PredatoryJournal

# Drop the table to force recreation with new schema
PredatoryJournal.__table__.drop(engine)
print("Dropped predatory_journals table.")

# Recreate it
Base.metadata.create_all(bind=engine)
print("Recreated tables.")
