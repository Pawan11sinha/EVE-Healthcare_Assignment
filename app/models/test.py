from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    
    centre_tests = relationship("CentreTest", back_populates="test", cascade="all, delete-orphan")
