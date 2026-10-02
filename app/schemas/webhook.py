from pydantic import BaseModel
from decimal import Decimal
from typing import Literal

class WebhookPayload(BaseModel):
    event_id: str
    provider_reference: str
    status: Literal["SUCCESS", "FAILED"]
    amount: Decimal

class WebhookResponse(BaseModel):
    status: str
    result: str = ""
