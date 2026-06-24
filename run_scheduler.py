import asyncio
import datetime
from sqlalchemy import select
from core.database import get_db
from core.models import Contact, EmailStatus, Template, ScheduledSend
from tasks.email_tasks import process_email_send

async def schedule_emails():
    print("Starting Scheduler...")
    async for db in get_db():
        # 1. Ensure we have a template
        result = await db.execute(select(Template))
        template = result.scalars().first()
        
        if not template:
            print("Creating default email template...")
            template = Template(
                name="Default Cold Outreach",
                subject="Quick question for {{name}}",
                body_text="Hi {{name}},\n\nI saw what you are building and I think we can help you scale.\n\nBest,\nAntigravity Team"
            )
            db.add(template)
            await db.flush() # get ID
            
        # 2. Find valid contacts without a scheduled send
        result = await db.execute(
            select(Contact).join(EmailStatus).where(EmailStatus.status == 'valid')
        )
        contacts = result.scalars().all()
        
        scheduled_count = 0
        for contact in contacts:
            # Check if already scheduled
            check = await db.execute(select(ScheduledSend).where(ScheduledSend.contact_id == contact.id))
            if check.scalars().first():
                continue
                
            # Schedule it
            sched = ScheduledSend(
                contact_id=contact.id,
                template_id=template.id,
                scheduled_for=datetime.datetime.utcnow(),
                status='pending'
            )
            db.add(sched)
            await db.commit() # commit to generate ID
            
            # Trigger Celery Task immediately
            print(f"Queuing email for {contact.name} ({contact.email}) to Celery...")
            process_email_send.delay(str(sched.id))
            scheduled_count += 1
            
        print(f"Done. Scheduled {scheduled_count} emails.")

if __name__ == "__main__":
    asyncio.run(schedule_emails())
