"""
Quick test: run the web crawler + email extractor against a single domain.
Usage: python test_scrape_url.py
"""
import asyncio
from services.enrichment import crawl_domain_for_emails, find_contacts

DOMAIN = "www.google.com"

async def main():
    print(f"\n{'='*50}")
    print(f" Testing domain: {DOMAIN}")
    print(f"{'='*50}\n")

    print("--- Step 1: Raw website crawl ---")
    scraped = await crawl_domain_for_emails(DOMAIN)
    if scraped:
        print(f"Found {len(scraped)} email(s) from crawl:")
        for c in scraped:
            print(f"  email={c.get('value') or c.get('email')}  role={c.get('position')}")
    else:
        print("  No emails found via web crawl.")

    print("\n--- Step 2: Full find_contacts() (crawl + Hunter if configured) ---")
    contacts = await find_contacts(DOMAIN)
    if contacts:
        print(f"Total contacts returned: {len(contacts)}")
        for c in contacts:
            email = c.get('value') or c.get('email')
            name  = f"{c.get('first_name','')} {c.get('last_name','')}".strip() or "Unknown"
            role  = c.get('position') or "—"
            print(f"  [{name}]  {email}  ({role})")
    else:
        print("  No contacts found at all.")

    print(f"\n{'='*50}\n")

if __name__ == "__main__":
    asyncio.run(main())
