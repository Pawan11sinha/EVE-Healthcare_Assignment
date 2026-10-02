from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from typing import Optional, Literal
from app.models.payment import PaymentStatus
from app.models.booking import BookingStatus

class PaymentCreate(BaseModel):
    booking_id: UUID
    force_outcome: Optional[Literal["SUCCESS", "FAILED"]] = None

class PaymentOut(BaseModel):
    id: UUID
    booking_id: UUID
    user_id: UUID
    amount: Decimal
    status: PaymentStatus
    provider_reference: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

class PaymentResponse(BaseModel):
    payment: PaymentOut
    booking_status: BookingStatus
