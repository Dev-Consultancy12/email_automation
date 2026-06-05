from fastapi import APIRouter, Request, Depends
import datetime
from sqlalchemy import select
from core.database import get_db
from core.models import OutreachLog, Contact, EmailStatus

router = APIRouter()

@router.post("/sendgrid")
async def sendgrid_webhook(request: Request, db=Depends(get_db)):
    """
    Receive webhook events from SendGrid.
    """
    events = await request.json()
    
    # SendGrid sends an array of events
    if not isinstance(events, list):
        events = [events]
        
    for event in events:
        email = event.get("email")
        event_type = event.get("event")
        
        result = await db.execute(select(Contact).where(Contact.email == email))
        contact = result.scalar_one_or_none()
        
        if not contact:
            continue
            
        if event_type in ('open', 'click', 'delivered'):
            log_result = await db.execute(
                select(OutreachLog)
                .where(OutreachLog.contact_id == contact.id)
                .order_by(OutreachLog.sent_at.desc())
            )
            outreach = log_result.scalars().first()
            
            if outreach:
                now = datetime.datetime.utcnow()
                if event_type == 'open' and not outreach.opened_at:
                    outreach.opened_at = now
                elif event_type == 'click' and not outreach.clicked_at:
                    outreach.clicked_at = now
                elif event_type == 'delivered' and not outreach.delivered_at:
                    outreach.delivered_at = now
                    
        elif event_type == 'bounce':
            status_result = await db.execute(
                select(EmailStatus).where(EmailStatus.contact_id == contact.id)
            )
            email_status = status_result.scalars().first()
            if email_status:
                email_status.status = 'invalid'
                email_status.bounce_reason = event.get("reason", "Hard bounce via webhook")
                
    await db.commit()
    return {"status": "ok"}
