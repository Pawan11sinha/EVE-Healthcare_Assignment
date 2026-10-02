from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.schemas.booking import BookingCreate, BookingOut
from app.services.booking import BookingService
from app.models.user import User
from app.models.booking import BookingStatus

router = APIRouter()

_booking_example = {
    "centre_id": 1,
    "test_id": 2,
    "appointment_at": "2027-01-15T10:30:00+05:30",
}


@router.post(
    "/",
    response_model=BookingOut,
    summary="Create a booking",
    responses={
        400: {"description": "Test not offered by this centre, or appointment in the past"},
        401: {"description": "Not authenticated"},
    },
    openapi_extra={"requestBody": {"content": {"application/json": {"example": _booking_example}}}},
)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Book a diagnostic test at a centre.

    - Validates the test is offered by the centre.
    - **appointment_at** must be a future timezone-aware datetime.
    - **amount** is taken from the centre's price list — never from the client.
    - Status starts as **PENDING** until payment is processed.
    """
    return BookingService.create_booking(db=db, user_id=current_user.id, booking_in=booking_in)


@router.get(
    "/",
    response_model=List[BookingOut],
    summary="List current user's bookings",
    responses={401: {"description": "Not authenticated"}},
)
def get_bookings(
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return paginated bookings for the authenticated user, optionally filtered by status."""
    return BookingService.get_bookings(db=db, user_id=current_user.id, skip=skip, limit=limit, status=status)


@router.get(
    "/{booking_id}",
    response_model=BookingOut,
    summary="Get a booking by ID",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Not found (or belongs to another user)"},
    },
)
def get_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch a single booking. Returns 404 (not 403) even when the booking
    exists but belongs to a different user, to avoid leaking existence.
    """
    return BookingService.get_booking(db=db, user_id=current_user.id, booking_id=booking_id)


@router.post(
    "/{booking_id}/cancel",
    response_model=BookingOut,
    summary="Cancel a booking",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Not found"},
        409: {"description": "Booking cannot be cancelled from its current state"},
    },
)
def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel a booking. Allowed only from **PENDING** or **CONFIRMED**.
    Returns 409 if the booking is already FAILED or CANCELLED.
    """
    return BookingService.cancel_booking(db=db, user_id=current_user.id, booking_id=booking_id)
