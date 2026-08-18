from celery import Celery
from app.config import settings
from app.database import SessionLocal
from app.models import Campaign, Subscriber, CampaignStatus, SuppressionList, SendingLog, SendingStatus
from app.services.email import send_campaign_email

celery_app = Celery(
    "emailcamp_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, rate_limit='10/s')
def send_single_email_task(self, to_email: str, subject: str, mjml_content: str, subscriber_id: str, campaign_id: str, first_name: str):
    """
    Sends a single email. Rate limited.
    """
    db = SessionLocal()
    try:
        result = send_campaign_email(
            to_email=to_email,
            subject=subject,
            mjml_content=mjml_content,
            subscriber_id=subscriber_id,
            campaign_id=campaign_id,
            first_name=first_name
        )
        
        # Log Success
        log = SendingLog(
            campaign_id=campaign_id,
            subscriber_id=subscriber_id,
            status=SendingStatus.SENT,
            message_id=result.get("message_id")
        )
        db.add(log)
        
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign:
            campaign.sent_count += 1
            
        db.commit()
        return {"status": "sent", "email": to_email}
    except Exception as e:
        print(f"Failed to send to {to_email}: {e}")
        # Log Failure
        log = SendingLog(
            campaign_id=campaign_id,
            subscriber_id=subscriber_id,
            status=SendingStatus.FAILED,
            error_message=str(e)
        )
        db.add(log)
        db.commit()
        return {"status": "failed", "email": to_email, "error": str(e)}
    finally:
        db.close()

@celery_app.task
def process_campaign_dispatch(campaign_id: str):
    """
    Fetches active subscribers matching target_tags, excluding SuppressionList, 
    and queues individual tasks to send the campaign.
    """
    db = SessionLocal()
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign or campaign.status != CampaignStatus.QUEUED:
            return

        campaign.status = CampaignStatus.SENDING
        db.commit()

        # Query all active subscribers
        query = db.query(Subscriber).filter(Subscriber.is_active == True)
        
        # If target tags are provided, we could filter here (simplified as in-memory or jsonb query)
        # For cross-DB compat (SQLite doesn't easily do jsonb contains), we filter active.
        all_subs = query.all()

        # Get all suppressed emails
        suppressed = {s.email for s in db.query(SuppressionList.email).all()}

        # Filter manually for JSON array if needed, and exclude suppressed
        target_tags = campaign.target_tags or []
        target_tags_set = set(target_tags)
        
        recipients = []
        for sub in all_subs:
            if sub.email in suppressed:
                continue
            
            # If campaign has tags, check if subscriber has overlapping tags
            sub_tags_set = set(sub.tags or [])
            if target_tags_set and not target_tags_set.intersection(sub_tags_set):
                continue
                
            recipients.append(sub)

        campaign.total_recipients = len(recipients)
        db.commit()

        for sub in recipients:
            send_single_email_task.delay(
                to_email=sub.email,
                subject=campaign.subject,
                mjml_content=campaign.mjml_content,
                subscriber_id=sub.id,
                campaign_id=campaign.id,
                first_name=sub.first_name
            )

        campaign.status = CampaignStatus.COMPLETED
        db.commit()
    finally:
        db.close()
