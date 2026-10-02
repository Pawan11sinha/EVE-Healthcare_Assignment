from sqlalchemy.orm import Session
from app.models.booking import Booking, BookingStatus
from app.models.centre_test import CentreTest
from app.schemas.booking import BookingCreate
from app.core.exceptions import AppException
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

class BookingService:
    ALLOWED_TRANSITIONS = {
        BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.FAILED, BookingStatus.CANCELLED},
        BookingStatus.CONFIRMED: {BookingStatus.CANCELLED},
        BookingStatus.FAILED: set(),
        BookingStatus.CANCELLED: set(),
    }

    @staticmethod
    def create_booking(db: Session, user_id: UUID, booking_in: BookingCreate) -> Booking:
        centre_test = db.query(CentreTest).filter(
            CentreTest.centre_id == booking_in.centre_id,
            CentreTest.test_id == booking_in.test_id
        ).first()
        
        if not centre_test:
            raise AppException(status_code=400, detail="Test not offered by this centre", code="INVALID_CENTRE_TEST")
        
        if booking_in.appointment_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise AppException(status_code=400, detail="Appointment must be in the future", code="INVALID_APPOINTMENT_DATE")
            
        booking = Booking(
            user_id=user_id,
            centre_test_id=centre_test.id,
            appointment_at=booking_in.appointment_at,
            amount=centre_test.price,
            status=BookingStatus.PENDING
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def get_bookings(db: Session, user_id: UUID, skip: int = 0, limit: int = 100, status: Optional[BookingStatus] = None) -> List[Booking]:
        query = db.query(Booking).filter(Booking.user_id == user_id)
        if status:
            query = query.filter(Booking.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_booking(db: Session, user_id: UUID, booking_id: UUID) -> Booking:
        try:
            val = UUID(str(booking_id))
        except ValueError:
            raise AppException(status_code=404, detail="Booking not found", code="BOOKING_NOT_FOUND")

        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking or booking.user_id != user_id:
            raise AppException(status_code=404, detail="Booking not found", code="BOOKING_NOT_FOUND")
        return booking

    @staticmethod
    def cancel_booking(db: Session, user_id: UUID, booking_id: UUID) -> Booking:
        booking = BookingService.get_booking(db, user_id, booking_id)
        
        if BookingStatus.CANCELLED not in BookingService.ALLOWED_TRANSITIONS[booking.status]:
            raise AppException(status_code=409, detail=f"Cannot transition from {booking.status} to CANCELLED", code="INVALID_STATE_TRANSITION")
            
        booking.status = BookingStatus.CANCELLED
        db.commit()
        db.refresh(booking)
        return booking
