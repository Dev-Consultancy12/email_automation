import asyncio
import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.celery_app import celery_app
from core.config import settings
from core.models import ScheduledSend, OutreachLog, Contact, Template
from services.email import send_email

async def _process_email_send(send_id: str):
    # Create an isolated engine for this event loop to avoid InterfaceError across Celery tasks
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(ScheduledSend, Contact, Template)
                .join(Contact)
                .join(Template)
                .where(ScheduledSend.id == send_id)
            )
            row = result.first()
            if not row:
                print(f"Task aborted: No scheduled send found with id {send_id}")
                return
                
            sched_send, contact, template = row
            
            # Dispatch
            # Simple template replacement
            subject = template.subject.replace("{{name}}", contact.name)
            body_text = template.body_text.replace("{{name}}", contact.name)
            
            print(f"Dispatching email to {contact.email}...")
            resp = await send_email(contact.email, subject, body_text)
            
            if resp['status'] == 'success':
                sched_send.status = 'sent'
                
                # Create outreach log
                log = OutreachLog(
                    contact_id=contact.id,
                    template_id=template.id,
                    sent_at=datetime.datetime.utcnow()
                )
                db.add(log)
                await db.commit()
                print(f"Successfully processed schedule {send_id}")
            else:
                sched_send.status = 'failed'
                await db.commit()
                print(f"Failed to process schedule {send_id}")
    finally:
        await engine.dispose()

@celery_app.task
def process_email_send(send_id: str):
    """Celery task to dispatch an email."""
    print(f"Executing task process_email_send for id: {send_id}")
    asyncio.run(_process_email_send(send_id))
