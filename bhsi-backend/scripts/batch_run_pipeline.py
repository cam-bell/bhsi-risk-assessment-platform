import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import requests
from app.db.session import SessionLocal
from app.crud.company import company as CRUDCompany

API_URL = "http://localhost:8000/api/v1/companies/unified-analysis"  # Adjust as needed

def main():
    db = SessionLocal()
    companies = CRUDCompany.get_multi(db, skip=0, limit=1000)
    for company in companies:
        payload = {
            "name": company.name,
            "vat": company.vat,
            # Add any other required fields for your endpoint
        }
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            print(f"Processed: {company.name}")
        else:
            print(f"Failed: {company.name} ({response.status_code}) - {response.text}")
    db.close()

if __name__ == "__main__":
    main()
