import aiohttp
import asyncio
from bs4 import BeautifulSoup
from core.config import settings
from scrapers.extractors import find_emails

<<<<<<< HEAD
# Map email local-part keywords → human-readable role labels
ROLE_MAP = {
    # Executive
    "ceo":          "CEO",
    "cto":          "CTO",
    "coo":          "COO",
    "cfo":          "CFO",
    "cmo":          "CMO",
    "founder":      "Founder",
    "cofounder":    "Co-Founder",
    "co-founder":   "Co-Founder",
    "director":     "Director",
    "president":    "President",
    "vp":           "VP",
    "head":         "Head",
    "owner":        "Owner",
    # Sales & Marketing
    "sales":        "Sales",
    "marketing":    "Marketing",
    "growth":       "Growth",
    "partnerships": "Partnerships",
    "bizdev":       "Business Development",
    "business":     "Business Development",
    "media":        "Media / PR",
    "press":        "Press / PR",
    "pr":           "PR",
    "ads":          "Advertising",
    # Support & Ops
    "support":      "Customer Support",
    "help":         "Customer Support",
    "hello":        "General Contact",
    "info":         "General Contact",
    "contact":      "General Contact",
    "team":         "Team",
    "office":       "Office",
    "admin":        "Admin",
    "operations":   "Operations",
    "ops":          "Operations",
    # Engineering
    "engineering":  "Engineering",
    "dev":          "Engineering",
    "developer":    "Engineering",
    "tech":         "Technical",
    "api":          "Technical",
    # Finance & Legal
    "billing":      "Billing",
    "finance":      "Finance",
    "legal":        "Legal",
    "privacy":      "Legal / Privacy",
    "dpo":          "Data Protection Officer",
    "compliance":   "Compliance",
    "security":     "Security",
    # HR
    "hr":           "Human Resources",
    "careers":      "Recruiting",
    "jobs":         "Recruiting",
    "hiring":       "Recruiting",
    "recruit":      "Recruiting",
    # Investor relations
    "investor":     "Investor Relations",
    "ir":           "Investor Relations",
    "invest":       "Investor Relations",
}

def infer_role_from_email(email: str) -> str:
    """Infer a human-readable role from the email's local part."""
    if not email or "@" not in email:
        return "General Contact"
    local = email.split("@")[0].lower().strip()
    # Exact match first
    if local in ROLE_MAP:
        return ROLE_MAP[local]
    # Partial match (e.g. 'sales-team' or 'ceo.john' still maps to Sales / CEO)
    for keyword, role in ROLE_MAP.items():
        if keyword in local:
            return role
    return "General Contact"

def infer_name_from_email(email: str) -> str:
    """
    Try to extract a real person's name from the email local part.
    e.g. john.smith@company.com  -> 'John Smith'
         sarah_jones@company.com -> 'Sarah Jones'
         j.doe@company.com       -> 'J Doe'
    Returns None if the local part looks like a role/alias, not a person.
    """
    if not email or "@" not in email:
        return None
    local = email.split("@")[0].lower().strip()

    # If local part matches a known role keyword, it's not a person's name
    if local in ROLE_MAP:
        return None
    for keyword in ROLE_MAP:
        if local == keyword or local.startswith(keyword + ".") or local.startswith(keyword + "_"):
            return None

    # Split on common separators: dot, underscore, hyphen
    import re
    parts = re.split(r'[._\-]+', local)

    # Filter out numeric-only parts and very short fragments (likely initials or IDs)
    name_parts = [p.capitalize() for p in parts if p.isalpha() and len(p) >= 1]

    if len(name_parts) >= 2:
        # Looks like firstname.lastname style
        return " ".join(name_parts)
    elif len(name_parts) == 1 and len(name_parts[0]) > 3:
        # Single word, longer than 3 chars — could be a first name only
        return name_parts[0]

    return None

=======
>>>>>>> 0afe74a5532695c5acf969057c8e84c186b53c27
async def crawl_domain_for_emails(domain: str) -> list[dict]:
    """Crawl a domain's homepage and contact pages to find emails."""
    print(f"[Scraper] Crawling {domain} for emails...")
    urls_to_visit = [f"https://{domain}", f"http://{domain}"]
    visited = set()
    found_emails = set()
    
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for base_url in urls_to_visit:
            if base_url in visited:
                continue
            visited.add(base_url)
            
            try:
                async with session.get(base_url, ssl=False) as resp:
                    if resp.status != 200:
                        continue
                    html = await resp.text()
                    found_emails.update(find_emails(html))
                    
                    # Look for contact/about pages
                    soup = BeautifulSoup(html, "html.parser")
                    sub_pages = []
                    for a in soup.find_all("a", href=True):
                        href = a["href"].lower()
                        if any(keyword in href for keyword in ['contact', 'about', 'team']):
                            if href.startswith('/'):
                                sub_pages.append(f"{base_url.rstrip('/')}{href}")
                            elif href.startswith('http'):
                                if domain in href:
                                    sub_pages.append(href)
                    
                    # Visit up to 3 sub-pages concurrently
                    sub_pages = list(set(sub_pages))[:3]
                    for sub_url in sub_pages:
                        if sub_url not in visited:
                            visited.add(sub_url)
                            try:
                                async with session.get(sub_url, ssl=False) as sub_resp:
                                    if sub_resp.status == 200:
                                        sub_html = await sub_resp.text()
                                        found_emails.update(find_emails(sub_html))
                            except Exception:
                                pass
                    break # Stop if we successfully loaded the domain (https or http)
            except Exception as e:
                pass
                
    contacts = []
    for email in found_emails:
<<<<<<< HEAD
        role = infer_role_from_email(email)
        name = infer_name_from_email(email)
        first_name = name.split()[0] if name else "Unknown"
        last_name  = " ".join(name.split()[1:]) if name and len(name.split()) > 1 else ""
        contacts.append({
            "first_name": first_name,
            "last_name":  last_name,
            "value":      email,
            "position":   role,
            "linkedin":   None
=======
        contacts.append({
            "first_name": "Unknown",
            "last_name": "",
            "value": email,
            "position": "General",
            "linkedin": None
>>>>>>> 0afe74a5532695c5acf969057c8e84c186b53c27
        })
    if contacts:
        print(f"[Scraper] Found {len(contacts)} emails on {domain}.")
    return contacts

async def find_contacts(domain: str):
    """
    Search for contacts at a given domain using web scraping and Hunter.io.
    Returns a list of dicts with contact details.
    """
    api_key = settings.HUNTER_API_KEY
    contacts = []
    
    # 1. Scrape the actual website first
    scraped_contacts = await crawl_domain_for_emails(domain)
    contacts.extend(scraped_contacts)
    
<<<<<<< HEAD
    # 2. Hunter.io (if API key is configured)
    if not api_key or api_key == 'your_hunter_key':
        print(f"[Info] No Hunter API key configured — using web-scraped contacts only for {domain}.")
=======
    # 2. Hunter.io / Mock fallback
    if not api_key or api_key == 'your_hunter_key':
        print(f"[Mock] Hunter API: Using mock data for {domain}.")
        contacts.extend([
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
        ])
>>>>>>> 0afe74a5532695c5acf969057c8e84c186b53c27
    else:
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        hunter_contacts = data.get("data", {}).get("emails", [])
                        contacts.extend(hunter_contacts)
                    else:
                        print(f"Error fetching from Hunter: {resp.status}")
        except Exception as e:
            print(f"Hunter API Exception: {e}")
            
    # Deduplicate by email
    unique_contacts = {}
    for c in contacts:
        email = c.get("value")
        if email and email not in unique_contacts:
            unique_contacts[email] = c
            
    return list(unique_contacts.values())
