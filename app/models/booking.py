import enum
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Numeric, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    centre_test_id = Column(Integer, ForeignKey("centre_tests.id"), nullable=False)
    appointment_at = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User")
    centre_test = relationship("CentreTest")
