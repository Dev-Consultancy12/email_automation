import argparse
import asyncio
from scrapers.spiders.yc_directory import scrape_yc_directory
from scrapers.spiders.product_hunt import scrape_product_hunt
from scrapers.email_scraper import scrape_company, save_to_database

async def process_added_domains(domains):
    if not domains:
        return
    print(f"\n--- Initiating Email Scraping for {len(domains)} new companies ---")
    for domain in domains:
        website = f"https://{domain}"
        print(f"Deep scraping emails for: {website}")
        emails = await asyncio.to_thread(scrape_company, website)
        if emails:
            print(f"Found {len(emails)} emails for {website}. Saving...")
            await save_to_database(website, emails)
        else:
            print(f"No emails found for {website}.")
    print("--- Email Scraping Complete ---\n")

async def main():
    parser = argparse.ArgumentParser(description="Run Antigravity Scrapers")
    parser.add_argument('--source', type=str, choices=['yc', 'ph', 'both'], default='both', help='Which source to scrape')
    parser.add_argument('--limit', type=int, default=5, help='Max companies to scrape per source')
    
    args = parser.parse_args()
    
    if args.source in ['yc', 'both']:
        print("=== Running YC Directory Scraper ===")
        added_domains_yc = await scrape_yc_directory(max_companies=args.limit)
        print("====================================\n")
        await process_added_domains(added_domains_yc)
        
    if args.source in ['ph', 'both']:
        print("=== Running Product Hunt Scraper ===")
        added_domains_ph = await scrape_product_hunt(max_companies=args.limit)
        print("====================================\n")
        await process_added_domains(added_domains_ph)

if __name__ == "__main__":
    asyncio.run(main())
