from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from decimal import Decimal
from app.schemas.test import DiagnosticTestOut

class DiagnosticCentreBase(BaseModel):
    name: str
    city: str
    address: str

class DiagnosticCentreCreate(DiagnosticCentreBase):
    pass

class DiagnosticCentreOut(DiagnosticCentreBase):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class CentreTestAdd(BaseModel):
    test_id: int
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)

class CentreTestOut(BaseModel):
    id: int
    centre_id: int
    test_id: int
    price: Decimal
    test: DiagnosticTestOut
    
    model_config = {"from_attributes": True}

class DiagnosticCentreDetail(DiagnosticCentreOut):
    centre_tests: List[CentreTestOut] = []
