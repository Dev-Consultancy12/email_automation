import aiohttp
import asyncio
from bs4 import BeautifulSoup
from core.config import settings
from scrapers.extractors import find_emails

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
        contacts.append({
            "first_name": "Unknown",
            "last_name": "",
            "value": email,
            "position": "General",
            "linkedin": None
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
