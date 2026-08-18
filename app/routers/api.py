from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Subscriber, Campaign, CampaignStatus, SuppressionList, SuppressionReason
from app.schemas import SubscriberResponse, CampaignResponse, CampaignCreate, SubscriberCreate
from app.services.csv_parser import process_subscriber_csv
from app.services.security import verify_unsubscribe_token
from app.worker import process_campaign_dispatch, send_single_email_task
import json
import requests

router = APIRouter()

@router.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "ok"}

# --- Subscribers ---

@router.post("/subscribers/upload")
async def upload_subscribers(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Must be a CSV file")
    
    content = await file.read()
    try:
        decoded = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
        
    inserted, skipped = process_subscriber_csv(db, decoded)
    return {"message": "Upload complete", "inserted": inserted, "skipped": skipped}

@router.get("/subscribers", response_model=list[SubscriberResponse])
def list_subscribers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Subscriber).offset(skip).limit(limit).all()


# --- Campaigns ---

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_subscribers = db.query(func.count(Subscriber.id)).scalar()
    active_subscribers = db.query(func.count(Subscriber.id)).filter(Subscriber.is_active == True).scalar()
    total_campaigns = db.query(func.count(Campaign.id)).scalar()
    sent_emails = db.query(func.sum(Campaign.sent_count)).scalar() or 0
    bounced_emails = db.query(func.count(SuppressionList.id)).filter(SuppressionList.reason == SuppressionReason.HARD_BOUNCE).scalar()
    
    return {
        "total_subscribers": total_subscribers,
        "active_subscribers": active_subscribers,
        "total_campaigns": total_campaigns,
        "sent_emails": sent_emails,
        "bounced_emails": bounced_emails
    }

@router.get("/campaigns", response_model=list[CampaignResponse])
def list_campaigns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Campaign).order_by(Campaign.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/campaigns", response_model=CampaignResponse)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    db_campaign = Campaign(**campaign.model_dump())
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

@router.post("/campaigns/{campaign_id}/test")
def test_campaign(campaign_id: str, test_email: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
        
    # Trigger single email dispatch for test
    send_single_email_task.delay(
        to_email=test_email,
        subject=f"[TEST] {campaign.subject}",
        mjml_content=campaign.mjml_content,
        subscriber_id="test-id",
        campaign_id=campaign_id,
        first_name="Test"
    )
    return {"message": f"Test email queued for {test_email}"}

@router.post("/campaigns/{campaign_id}/launch")
def launch_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status in [CampaignStatus.QUEUED, CampaignStatus.SENDING]:
        raise HTTPException(status_code=400, detail="Campaign is already queued or sending")

    campaign.status = CampaignStatus.QUEUED
    db.commit()
    
    # Trigger Celery task
    process_campaign_dispatch.delay(campaign_id)
    
    return {"message": "Campaign queued for sending"}


# --- Unsubscribe Handling ---

@router.get("/unsubscribe")
def unsubscribe_get(sub_id: str, camp_id: str, token: str, db: Session = Depends(get_db)):
    """One-click unsubscribe GET fallback, though POST is preferred."""
    if not verify_unsubscribe_token(sub_id, camp_id, token):
        raise HTTPException(status_code=403, detail="Invalid token")
        
    sub = db.query(Subscriber).filter(Subscriber.id == sub_id).first()
    if sub and sub.is_active:
        sub.is_active = False
        # Log suppression
        log = SuppressionList(email=sub.email, reason=SuppressionReason.MANUAL_UNSUBSCRIBE)
        db.add(log)
        db.commit()
        
    return {"message": "You have been successfully unsubscribed."}

@router.post("/unsubscribe")
def unsubscribe_post(sub_id: str = Form(...), camp_id: str = Form(...), token: str = Form(...), db: Session = Depends(get_db)):
    """RFC 8058 One-Click POST handler."""
    if not verify_unsubscribe_token(sub_id, camp_id, token):
        raise HTTPException(status_code=403, detail="Invalid token")
        
    sub = db.query(Subscriber).filter(Subscriber.id == sub_id).first()
    if sub and sub.is_active:
        sub.is_active = False
        log = SuppressionList(email=sub.email, reason=SuppressionReason.MANUAL_UNSUBSCRIBE)
        db.add(log)
        db.commit()
        
    return {"message": "Unsubscribed successfully"}

# --- Webhooks (MTA) ---

@router.post("/webhooks/mta")
async def mta_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Handles self-hosted MTA (Postal/Stalwart) notifications for Bounce and Complaint events.
    """
    body = await request.body()
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Assuming a generic standard payload: {"event": "Bounce", "email": "test@bounced.com"}
    event_type = payload.get("event")
    email_addr = payload.get("email")
    
    if event_type == "Bounce" and email_addr:
        sub = db.query(Subscriber).filter(Subscriber.email == email_addr).first()
        if sub:
            sub.is_active = False
            sub.bounce_count += 1
            db.add(SuppressionList(email=email_addr, reason=SuppressionReason.HARD_BOUNCE))
        db.commit()
        
    elif event_type == "Complaint" and email_addr:
        sub = db.query(Subscriber).filter(Subscriber.email == email_addr).first()
        if sub:
            sub.is_active = False
            db.add(SuppressionList(email=email_addr, reason=SuppressionReason.COMPLAINT))
        db.commit()

    return {"status": "processed"}
