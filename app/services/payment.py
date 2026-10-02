import random
import uuid
from sqlalchemy.orm import Session
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.payment import PaymentCreate
from app.services.booking import BookingService
from app.core.exceptions import AppException
from uuid import UUID

class PaymentService:
    @staticmethod
    def process_payment(db: Session, user_id: UUID, payment_in: PaymentCreate) -> tuple[Payment, BookingStatus]:
        try:
            val = UUID(str(payment_in.booking_id))
        except ValueError:
            raise AppException(status_code=404, detail="Booking not found", code="BOOKING_NOT_FOUND")

        # 1. Lock the booking row
        booking = db.query(Booking).filter(
            Booking.id == payment_in.booking_id
        ).with_for_update().first()
        
        # 2. Check existence and ownership
        if not booking or booking.user_id != user_id:
            db.rollback()
            raise AppException(status_code=404, detail="Booking not found", code="BOOKING_NOT_FOUND")
            
        # 3. Check status
        if booking.status != BookingStatus.PENDING:
            db.rollback()
            raise AppException(status_code=409, detail=f"Booking is in {booking.status} state, cannot be paid", code="INVALID_BOOKING_STATE")
            
        # Simulate payment outcome
        if payment_in.force_outcome:
            outcome = PaymentStatus.SUCCESS if payment_in.force_outcome == "SUCCESS" else PaymentStatus.FAILED
        else:
            outcome = PaymentStatus.SUCCESS if random.random() < 0.8 else PaymentStatus.FAILED
            
        # Create payment record
        provider_ref = f"SIM-{uuid.uuid4().hex[:12].upper()}"
        payment = Payment(
            booking_id=booking.id,
            user_id=user_id,
            amount=booking.amount,
            status=outcome,
            provider_reference=provider_ref
        )
        db.add(payment)
        
        # Determine target booking status
        new_booking_status = BookingStatus.CONFIRMED if outcome == PaymentStatus.SUCCESS else BookingStatus.FAILED
        
        # Ensure transition is allowed
        if new_booking_status not in BookingService.ALLOWED_TRANSITIONS[booking.status]:
            db.rollback()
            raise AppException(status_code=409, detail="Invalid state transition", code="INVALID_STATE_TRANSITION")
            
        # Assumption: A failed payment sets the booking to FAILED (terminal). 
        # The user cannot retry payment for this booking, they must create a new one.
        booking.status = new_booking_status
        
        db.commit()
        db.refresh(payment)
        db.refresh(booking)
        
        return payment, booking.status

    @staticmethod
    def get_payment(db: Session, user_id: UUID, payment_id: UUID) -> Payment:
        try:
            val = UUID(str(payment_id))
        except ValueError:
            raise AppException(status_code=404, detail="Payment not found", code="PAYMENT_NOT_FOUND")

        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment or payment.user_id != user_id:
            raise AppException(status_code=404, detail="Payment not found", code="PAYMENT_NOT_FOUND")
            
        return payment
