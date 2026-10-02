from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_db, get_current_user
from app.schemas.centre import (
    DiagnosticCentreCreate, DiagnosticCentreOut,
    DiagnosticCentreDetail, CentreTestAdd, CentreTestOut,
)
from app.services.centre import CentreService
from app.models.user import User

router = APIRouter()


@router.post(
    "/",
    response_model=DiagnosticCentreOut,
    summary="Create a diagnostic centre",
    responses={401: {"description": "Not authenticated"}},
)
def create_centre(
    centre_in: DiagnosticCentreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new diagnostic centre (auth required)."""
    return CentreService.create_centre(db=db, centre_in=centre_in)


@router.get(
    "/",
    response_model=List[DiagnosticCentreOut],
    summary="List diagnostic centres",
)
def get_centres(
    city: Optional[str] = Query(None, description="Filter by city name"),
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(100, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db),
):
    """List all diagnostic centres with optional city filter and pagination."""
    return CentreService.get_centres(db=db, skip=skip, limit=limit, city=city)


@router.get(
    "/{centre_id}",
    response_model=DiagnosticCentreDetail,
    summary="Get a centre with its offered tests",
    responses={404: {"description": "Centre not found"}},
)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    """Return full details for a centre including all tests and prices."""
    return CentreService.get_centre_detail(db=db, centre_id=centre_id)


@router.post(
    "/{centre_id}/tests",
    response_model=CentreTestOut,
    summary="Add a test to a centre",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Centre or test not found"},
        409: {"description": "Test already offered by this centre"},
        422: {"description": "Price must be greater than 0"},
    },
)
def add_test_to_centre(
    centre_id: int,
    test_in: CentreTestAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Associate a diagnostic test with a centre at a given price (auth required)."""
    return CentreService.add_test_to_centre(db=db, centre_id=centre_id, test_in=test_in)


@router.get(
    "/{centre_id}/tests",
    response_model=List[CentreTestOut],
    summary="List tests offered by a centre",
    responses={404: {"description": "Centre not found"}},
)
def get_centre_tests(centre_id: int, db: Session = Depends(get_db)):
    """Return all tests offered at the given centre with their prices."""
    return CentreService.get_centre_tests(db=db, centre_id=centre_id)
