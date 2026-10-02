from sqlalchemy import Column, Integer, ForeignKey, Numeric, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.base import Base

class CentreTest(Base):
    __tablename__ = "centre_tests"
    
    id = Column(Integer, primary_key=True, index=True)
    centre_id = Column(Integer, ForeignKey("diagnostic_centres.id"), nullable=False)
    test_id = Column(Integer, ForeignKey("diagnostic_tests.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    
    __table_args__ = (
        UniqueConstraint('centre_id', 'test_id', name='uq_centre_test'),
        CheckConstraint('price > 0', name='chk_price_positive')
    )
    
    centre = relationship("DiagnosticCentre", back_populates="centre_tests")
    test = relationship("DiagnosticTest", back_populates="centre_tests")
