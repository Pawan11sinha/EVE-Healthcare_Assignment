from pydantic import BaseModel
from typing import Optional

class DiagnosticTestBase(BaseModel):
    name: str
    description: Optional[str] = None

class DiagnosticTestCreate(DiagnosticTestBase):
    pass

class DiagnosticTestOut(DiagnosticTestBase):
    id: int
    
    model_config = {"from_attributes": True}
