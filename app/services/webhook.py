import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.webhook import WebhookEvent
from app.models.payment import Payment, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.schemas.webhook import WebhookPayload
from app.services.booking import BookingService
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class WebhookService:
    @staticmethod
    def process_webhook(db: Session, payload: WebhookPayload) -> str:
        try:
            with db.begin_nested():
                event = WebhookEvent(
                    event_id=payload.event_id,
                    payload=payload.model_dump(mode="json"),
                    result="pending"
                )
                db.add(event)
                db.flush()
        except IntegrityError:
            return "already_processed"
            
        payment = db.query(Payment).filter(
            Payment.provider_reference == payload.provider_reference
        ).with_for_update().first()
        
        if not payment:
            raise AppException(status_code=404, detail="Payment not found")
            
        if payment.amount != payload.amount:
            raise AppException(status_code=422, detail="Amount mismatch")
            
        booking = db.query(Booking).filter(
            Booking.id == payment.booking_id
        ).with_for_update().first()
        
        result = "processed"
        webhook_status = PaymentStatus.SUCCESS if payload.status == "SUCCESS" else PaymentStatus.FAILED

        if payment.status == webhook_status:
            result = "no_change"
        elif payment.status == PaymentStatus.PENDING:
            target_booking_status = BookingStatus.CONFIRMED if webhook_status == PaymentStatus.SUCCESS else BookingStatus.FAILED
            if target_booking_status in BookingService.ALLOWED_TRANSITIONS[booking.status]:
                payment.status = webhook_status
                booking.status = target_booking_status
                result = "processed"
            else:
                logger.warning(f"Invalid booking transition for event {payload.event_id}")
                result = "ignored_conflict"
        else:
            logger.warning(f"Conflicting final payment status for event {payload.event_id}")
            result = "ignored_conflict"
            
        event.result = result
        db.commit()
        return result
