import asyncio
import aiohttp
from sqlalchemy import select
from core.database import get_db
from core.models import Contact, OutreachLog

async def test_webhook():
    # 1. Grab an email from the database to simulate
    async for db in get_db():
        result = await db.execute(select(Contact))
        contact = result.scalars().first()
        break
        
    if not contact:
        print("No contacts to test with.")
        return
        
    email_to_test = contact.email
    print(f"Testing webhook for email: {email_to_test}")
    
    # 2. Simulate the SendGrid payload
    payload = [
        {
            "email": email_to_test,
            "event": "open",
            "sg_event_id": "mock_event_id_12345"
        }
    ]
    
    # 3. Send the HTTP POST request to our FastAPI app
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("http://127.0.0.1:8000/webhooks/sendgrid", json=payload) as resp:
                print(f"Webhook responded with status: {resp.status}")
                print(await resp.text())
    except Exception as e:
        print(f"Error calling webhook: {e}. Make sure FastAPI is running (uvicorn main:app --reload)")
        return
        
    # 4. Verify in DB
    print("\nVerifying database update...")
    async for db in get_db():
        log_result = await db.execute(
            select(OutreachLog).where(OutreachLog.contact_id == contact.id).order_by(OutreachLog.sent_at.desc())
        )
        outreach = log_result.scalars().first()
        if outreach and outreach.opened_at:
            print(f"SUCCESS! opened_at was recorded as {outreach.opened_at}")
        else:
            print("FAILED. opened_at was not recorded.")
        break

if __name__ == "__main__":
    asyncio.run(test_webhook())
