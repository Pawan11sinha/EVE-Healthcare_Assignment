import sys
import os
from decimal import Decimal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest
from app.models.centre_test import CentreTest

def seed():
    db = SessionLocal()
    try:
        tests_data = [
            {"name": "Complete Blood Count", "description": "Overall health check"},
            {"name": "Lipid Panel", "description": "Cholesterol check"},
            {"name": "Thyroid Profile", "description": "T3, T4, TSH"},
            {"name": "Liver Function Test", "description": "LFT"},
            {"name": "Vitamin D", "description": "Vit D3 levels"},
        ]
        
        tests = []
        for t_data in tests_data:
            t = db.query(DiagnosticTest).filter_by(name=t_data["name"]).first()
            if not t:
                t = DiagnosticTest(**t_data)
                db.add(t)
                db.flush()
            tests.append(t)
        db.commit()

        centres_data = [
            {"name": "Apollo Diagnostics", "city": "Mumbai", "address": "Andheri West"},
            {"name": "Dr Lal PathLabs", "city": "Delhi", "address": "Connaught Place"},
            {"name": "Thyrocare", "city": "Bangalore", "address": "Koramangala"},
        ]
        
        centres = []
        for c_data in centres_data:
            c = db.query(DiagnosticCentre).filter_by(name=c_data["name"]).first()
            if not c:
                c = DiagnosticCentre(**c_data)
                db.add(c)
                db.flush()
            centres.append(c)
        db.commit()

        links_data = [
            (centres[0], tests[0], Decimal("500.00")),
            (centres[0], tests[1], Decimal("800.00")),
            (centres[1], tests[2], Decimal("600.00")),
            (centres[2], tests[3], Decimal("1200.00")),
            (centres[2], tests[4], Decimal("1500.00")),
        ]
        
        for centre, test, price in links_data:
            ct = db.query(CentreTest).filter_by(centre_id=centre.id, test_id=test.id).first()
            if not ct:
                ct = CentreTest(centre_id=centre.id, test_id=test.id, price=price)
                db.add(ct)
        db.commit()
        
        print("Seed successful")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
