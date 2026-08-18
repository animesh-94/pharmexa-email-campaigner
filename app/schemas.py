from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import CampaignStatus, SuppressionReason, SendingStatus

class SubscriberBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tags: Optional[List[str]] = None
    
class SubscriberCreate(SubscriberBase):
    pass

class SubscriberResponse(SubscriberBase):
    id: str
    is_active: bool
    bounce_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    title: str
    subject: str
    sender_name: Optional[str] = None
    sender_email: Optional[EmailStr] = None
    preview_text: Optional[str] = None
    mjml_content: Optional[str] = None
    target_tags: Optional[List[str]] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    sender_name: Optional[str] = None
    sender_email: Optional[EmailStr] = None
    preview_text: Optional[str] = None
    mjml_content: Optional[str] = None
    target_tags: Optional[List[str]] = None

class CampaignResponse(CampaignBase):
    id: str
    status: CampaignStatus
    html_compiled: Optional[str] = None
    plain_text: Optional[str] = None
    total_recipients: int
    sent_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedSubscribers(BaseModel):
    total: int
    page: int
    size: int
    items: List[SubscriberResponse]
