import uuid
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.base import Base

class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String, unique=True, index=True, nullable=False)
    payload = Column(JSONB, nullable=False)
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    result = Column(String, nullable=False)
