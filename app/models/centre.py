from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    city = Column(String, index=True, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    centre_tests = relationship("CentreTest", back_populates="centre", cascade="all, delete-orphan")
