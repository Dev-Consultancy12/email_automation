import asyncio
from sqlalchemy import select
from core.database import get_db
from core.models import ScheduledSend
from tasks.email_tasks import process_email_send

async def retry_pending():
    async for db in get_db():
        result = await db.execute(select(ScheduledSend).where(ScheduledSend.status == 'pending'))
        pending = result.scalars().all()
        for p in pending:
            process_email_send.delay(str(p.id))
            print(f"Re-queued task for {p.id}")

if __name__ == "__main__":
    asyncio.run(retry_pending())
