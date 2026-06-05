import aiohttp
from core.config import settings

async def find_contacts(domain: str):
    """
    Search for contacts at a given domain using Hunter.io.
    Returns a list of dicts with contact details.
    """
    api_key = settings.HUNTER_API_KEY
    
    # Mock behavior if the API key is missing or set to the default placeholder
    if not api_key or api_key == 'your_hunter_key':
        print(f"[Mock] Hunter API: Using mock data for {domain}.")
        return [
            {
                "first_name": "Jane",
                "last_name": "Doe",
                "value": f"jane.doe@{domain}",
                "position": "CEO",
                "linkedin": f"https://linkedin.com/in/janedoe-{domain.replace('.', '-')}"
            },
            {
                "first_name": "John",
                "last_name": "Smith",
                "value": f"john.smith@{domain}",
                "position": "Head of Engineering",
                "linkedin": None
            }
        ]

    url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Error fetching from Hunter: {resp.status}")
                return []
            
            data = await resp.json()
            contacts = data.get("data", {}).get("emails", [])
            return contacts
