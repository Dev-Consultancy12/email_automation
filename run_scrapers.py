import argparse
import asyncio
from scrapers.spiders.yc_directory import scrape_yc_directory
from scrapers.spiders.product_hunt import scrape_product_hunt

async def main():
    parser = argparse.ArgumentParser(description="Run Antigravity Scrapers")
    parser.add_argument('--source', type=str, choices=['yc', 'ph', 'both'], default='both', help='Which source to scrape')
    parser.add_argument('--limit', type=int, default=5, help='Max companies to scrape per source')
    
    args = parser.parse_args()
    
    if args.source in ['yc', 'both']:
        print("=== Running YC Directory Scraper ===")
        await scrape_yc_directory(max_companies=args.limit)
        print("====================================\n")
        
    if args.source in ['ph', 'both']:
        print("=== Running Product Hunt Scraper ===")
        await scrape_product_hunt(max_companies=args.limit)
        print("====================================\n")

if __name__ == "__main__":
    asyncio.run(main())
