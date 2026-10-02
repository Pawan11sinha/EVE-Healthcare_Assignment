from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.centre import DiagnosticCentre
from app.models.test import DiagnosticTest
from app.models.centre_test import CentreTest
from app.schemas.centre import DiagnosticCentreCreate, CentreTestAdd
from app.core.exceptions import AppException

class CentreService:
    @staticmethod
    def create_centre(db: Session, centre_in: DiagnosticCentreCreate) -> DiagnosticCentre:
        centre = DiagnosticCentre(**centre_in.model_dump())
        db.add(centre)
        db.commit()
        db.refresh(centre)
        return centre

    @staticmethod
    def get_centres(db: Session, skip: int = 0, limit: int = 100, city: Optional[str] = None) -> List[DiagnosticCentre]:
        query = db.query(DiagnosticCentre)
        if city:
            query = query.filter(DiagnosticCentre.city == city)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_centre_detail(db: Session, centre_id: int) -> DiagnosticCentre:
        centre = db.query(DiagnosticCentre).options(
            joinedload(DiagnosticCentre.centre_tests).joinedload(CentreTest.test)
        ).filter(DiagnosticCentre.id == centre_id).first()
        if not centre:
            raise AppException(status_code=404, detail="Centre not found", code="CENTRE_NOT_FOUND")
        return centre

    @staticmethod
    def add_test_to_centre(db: Session, centre_id: int, test_in: CentreTestAdd) -> CentreTest:
        centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
        if not centre:
            raise AppException(status_code=404, detail="Centre not found", code="CENTRE_NOT_FOUND")
            
        test = db.query(DiagnosticTest).filter(DiagnosticTest.id == test_in.test_id).first()
        if not test:
            raise AppException(status_code=404, detail="Test not found", code="TEST_NOT_FOUND")
            
        try:
            centre_test = CentreTest(
                centre_id=centre_id,
                test_id=test_in.test_id,
                price=test_in.price
            )
            db.add(centre_test)
            db.commit()
            db.refresh(centre_test)
            
            return db.query(CentreTest).options(joinedload(CentreTest.test)).filter(CentreTest.id == centre_test.id).first()
        except IntegrityError:
            db.rollback()
            raise AppException(status_code=409, detail="Test already added to this centre", code="CENTRE_TEST_EXISTS")

    @staticmethod
    def get_centre_tests(db: Session, centre_id: int) -> List[CentreTest]:
        centre = db.query(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id).first()
        if not centre:
            raise AppException(status_code=404, detail="Centre not found", code="CENTRE_NOT_FOUND")
            
        return db.query(CentreTest).options(joinedload(CentreTest.test)).filter(CentreTest.centre_id == centre_id).all()
