from pydantic import BaseModel, field_validator
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from typing import Optional
from app.models.booking import BookingStatus

class BookingCreate(BaseModel):
    centre_id: int
    test_id: int
    appointment_at: datetime
    
    @field_validator('appointment_at')
    @classmethod
    def check_future(cls, v: datetime) -> datetime:
        if v.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise ValueError('appointment_at must be in the future')
        return v

class BookingOut(BaseModel):
    id: UUID
    user_id: UUID
    centre_test_id: int
    appointment_at: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
