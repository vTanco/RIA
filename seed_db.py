from backend.database.session import SessionLocal
from backend.database.models import PredatoryJournal
from datetime import datetime

db = SessionLocal()

sample_journals = [
    {
        "name": "International Journal of Advanced Research",
        "issn": "2320-5407",
        "publisher": "IJAR",
        "source": "Beall's List",
        "url": "http://www.journalijar.com/"
    },
    {
        "name": "Journal of Science and Technology",
        "issn": "2049-7318",
        "publisher": "Scientific Research Publishing",
        "source": "PredatoryJournals.org",
        "url": "http://www.jst.org.in/"
    },
    {
        "name": "Global Journal of Management and Business Research",
        "issn": "0975-5853",
        "publisher": "Global Journals Inc.",
        "source": "Beall's List",
        "url": "https://globaljournals.org/"
    },
    {
        "name": "Asian Journal of Biomedical and Pharmaceutical Sciences",
        "issn": "2249-622X",
        "publisher": "Allied Academies",
        "source": "PredatoryJournals.org",
        "url": "https://www.jbiopharm.com/"
    },
    {
        "name": "International Journal of Current Research",
        "issn": "0975-833X",
        "publisher": "IJCR",
        "source": "Beall's List",
        "url": "http://www.journalcra.com/"
    }
]

for data in sample_journals:
    exists = db.query(PredatoryJournal).filter_by(name=data["name"]).first()
    if not exists:
        journal = PredatoryJournal(**data)
        db.add(journal)

db.commit()
print(f"Seeded {len(sample_journals)} journals.")
db.close()
