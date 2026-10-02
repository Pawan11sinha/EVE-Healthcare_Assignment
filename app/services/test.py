from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.models.test import DiagnosticTest
from app.schemas.test import DiagnosticTestCreate
from app.core.exceptions import AppException

class TestService:
    @staticmethod
    def create_test(db: Session, test_in: DiagnosticTestCreate) -> DiagnosticTest:
        test = DiagnosticTest(**test_in.model_dump())
        db.add(test)
        try:
            db.commit()
            db.refresh(test)
            return test
        except IntegrityError:
            db.rollback()
            raise AppException(status_code=409, detail="Test with this name already exists", code="TEST_EXISTS")

    @staticmethod
    def get_tests(db: Session, skip: int = 0, limit: int = 100) -> List[DiagnosticTest]:
        return db.query(DiagnosticTest).offset(skip).limit(limit).all()
