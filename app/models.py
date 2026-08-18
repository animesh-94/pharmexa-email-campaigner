import uuid
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class CampaignStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SuppressionReason(str, enum.Enum):
    HARD_BOUNCE = "HARD_BOUNCE"
    COMPLAINT = "COMPLAINT"
    MANUAL_UNSUBSCRIBE = "MANUAL_UNSUBSCRIBE"

class SendingStatus(str, enum.Enum):
    SENT = "SENT"
    BOUNCED = "BOUNCED"
    FAILED = "FAILED"
    COMPLAINED = "COMPLAINED"

class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    bounce_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    preview_text = Column(String, nullable=True)
    sender_name = Column(String, nullable=True)
    sender_email = Column(String, nullable=True)
    mjml_content = Column(Text, nullable=True)
    html_compiled = Column(Text, nullable=True)
    plain_text = Column(Text, nullable=True)
    status = Column(SQLEnum(CampaignStatus), default=CampaignStatus.DRAFT)
    target_tags = Column(JSON, nullable=True)
    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SuppressionList(Base):
    __tablename__ = "suppression_list"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    reason = Column(SQLEnum(SuppressionReason), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SendingLog(Base):
    __tablename__ = "sending_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), index=True)
    subscriber_id = Column(String(36), ForeignKey("subscribers.id"), index=True)
    status = Column(SQLEnum(SendingStatus), nullable=False)
    message_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
