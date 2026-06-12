import aiohttp
from core.config import settings

async def verify_email(email: str):
    """
    Verify an email address using ZeroBounce.
    Returns a dict with status and bounce details.
    """
    api_key = settings.ZEROBOUNCE_API_KEY
    
    # Mock behavior if the API key is missing or set to the default placeholder
    if not api_key or api_key == 'your_zerobounce_key':
        print(f"[Mock] ZeroBounce API: Using mock data for {email}.")
        return {"status": "valid", "sub_status": ""}
        
    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email={email}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Error verifying with ZeroBounce: {resp.status}")
                return {"status": "unknown", "sub_status": "api_error"}
                
            data = await resp.json()
            return {
                "status": data.get("status", "unknown"),
                "sub_status": data.get("sub_status", "")
            }
