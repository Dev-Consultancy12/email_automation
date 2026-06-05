import aiohttp
from core.config import settings

async def send_email(to_email: str, subject: str, body_text: str):
    """
    Dispatch an email via SendGrid.
    """
    api_key = settings.SENDGRID_API_KEY
    
    # Mock behavior if the API key is missing or set to the default placeholder
    if not api_key or api_key == 'your_sendgrid_key':
        print(f"\n[Mock] SendGrid API: Simulating email send to {to_email}")
        print(f"       Subject: {subject}")
        print(f"       Body: {body_text.replace(chr(10), ' | ')}") # one-line summary
        return {"status": "success", "message_id": "mock-message-id"}
        
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "personalizations": [
            {
                "to": [{"email": to_email}],
                "subject": subject
            }
        ],
        "from": {"email": "hello@antigravity.local"},
        "content": [
            {
                "type": "text/plain",
                "value": body_text
            }
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status not in (200, 202):
                print(f"Error sending email: {resp.status} - {await resp.text()}")
                return {"status": "error"}
                
            return {"status": "success", "message_id": resp.headers.get("X-Message-Id", "unknown")}
