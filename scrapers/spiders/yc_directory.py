import aiohttp
from sqlalchemy import select
from core.database import get_db
from core.models import Company

async def scrape_yc_directory(max_companies=5):
    print(f"Starting Hacker News (YC) scrape for {max_companies} companies...")
    
    async with aiohttp.ClientSession() as session:
        # Fetch latest Show HN stories
        async with session.get('https://hacker-news.firebaseio.com/v0/showstories.json') as resp:
            story_ids = await resp.json()
            
        added = 0
        async for db in get_db():
            for story_id in story_ids:
                if added >= max_companies:
                    break
                    
                # Fetch story details
                async with session.get(f'https://hacker-news.firebaseio.com/v0/item/{story_id}.json') as item_resp:
                    item = await item_resp.json()
                    
                    if not item or 'url' not in item:
                        continue
                        
                    url = item['url']
                    title = item.get('title', 'Unknown HN Startup')
                    
                    # Extract domain
                    domain = url.split("//")[-1].split("/")[0].replace("www.", "")
                    
                    # Store in DB
                    result = await db.execute(select(Company).where(Company.domain == domain))
                    company = result.scalar_one_or_none()
                    
                    if company is None:
                        company = Company(domain=domain, name=title, source='hacker_news')
                        db.add(company)
                        await db.commit()
                        print(f"Added from HN (YC): {title} ({domain})")
                        added += 1
                    else:
                        print(f"Already exists: {domain}")
