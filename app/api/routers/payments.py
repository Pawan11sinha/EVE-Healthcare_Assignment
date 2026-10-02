from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentResponse
from app.services.payment import PaymentService
from app.models.user import User
from app.api.deps_webhook import verify_signature
from app.schemas.webhook import WebhookPayload, WebhookResponse
from app.services.webhook import WebhookService

router = APIRouter()

_payment_example = {"booking_id": "550e8400-e29b-41d4-a716-446655440000", "force_outcome": "SUCCESS"}
_webhook_example = {
    "event_id": "evt_abc123",
    "provider_reference": "SIM-ABC123DEF",
    "status": "SUCCESS",
    "amount": "1000.00",
}


@router.post(
    "/",
    response_model=PaymentResponse,
    summary="Initiate a payment for a booking",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Booking not found"},
        409: {"description": "Booking is not in PENDING state"},
    },
    openapi_extra={"requestBody": {"content": {"application/json": {"example": _payment_example}}}},
)
def create_payment(
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Simulate a payment for a PENDING booking.

    - **force_outcome**: optional `"SUCCESS"` or `"FAILED"` for deterministic testing.
      Without it, the simulator uses an 80% success rate.
    - Amount is always taken from the booking, never from the client.
    - On SUCCESS the booking moves to CONFIRMED; on FAILED it moves to FAILED (terminal).
    - A SELECT FOR UPDATE lock prevents concurrent double-payment.
    """
    payment, booking_status = PaymentService.process_payment(db=db, user_id=current_user.id, payment_in=payment_in)
    return PaymentResponse(payment=payment, booking_status=booking_status)


@router.get(
    "/{payment_id}",
    response_model=PaymentOut,
    summary="Get a payment by ID",
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Not found (or belongs to another user)"},
    },
)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch a payment record. Returns 404 for other users' payments."""
    return PaymentService.get_payment(db=db, user_id=current_user.id, payment_id=payment_id)


@router.post(
    "/webhook/",
    response_model=WebhookResponse,
    summary="Receive a payment-provider webhook callback",
    dependencies=[Depends(verify_signature)],
    responses={
        401: {"description": "Missing or invalid HMAC-SHA256 signature"},
        404: {"description": "Unknown provider_reference"},
        422: {"description": "Amount mismatch or malformed payload"},
    },
    openapi_extra={"requestBody": {"content": {"application/json": {"example": _webhook_example}}}},
)
def handle_webhook(
    payload: WebhookPayload,
    db: Session = Depends(get_db),
):
    """
    Idempotent signed payment-provider callback.

    **Security**: the raw request body must be HMAC-SHA256 signed with
    `WEBHOOK_SECRET` and the hex digest sent in the `X-Signature` header.
    No JWT is required — the signature is the authentication.

    **Idempotency**: the `event_id` is inserted into `webhook_events` inside a
    savepoint. A unique-violation means the event was already processed; in that
    case the handler returns 200 `already_processed` without touching any data.

    **State rules**:
    - Payment `PENDING`: apply outcome, update booking via allowed transitions.
    - Payment already in same state: no-op (`no_change`).
    - Conflicting final state or invalid booking transition: log warning,
      return 200 `ignored_conflict` so the provider stops retrying.
    """
    result = WebhookService.process_webhook(db, payload)
    status_str = "already_processed" if result == "already_processed" else "processed"
    return WebhookResponse(status=status_str, result=result if result != "already_processed" else "")
