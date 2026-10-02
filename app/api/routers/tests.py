from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_db, get_current_user
from app.schemas.test import DiagnosticTestCreate, DiagnosticTestOut
from app.services.test import TestService
from app.models.user import User

router = APIRouter()


@router.post(
    "/",
    response_model=DiagnosticTestOut,
    summary="Create a diagnostic test",
    responses={
        401: {"description": "Not authenticated"},
        409: {"description": "Test name already exists"},
    },
)
def create_test(
    test_in: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new named diagnostic test (auth required)."""
    return TestService.create_test(db=db, test_in=test_in)


@router.get(
    "/",
    response_model=List[DiagnosticTestOut],
    summary="List diagnostic tests",
)
def get_tests(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """Return all diagnostic tests with pagination."""
    return TestService.get_tests(db=db, skip=skip, limit=limit)
