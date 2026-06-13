import aiohttp
import feedparser
from bs4 import BeautifulSoup
from sqlalchemy import select
from core.database import get_db
from core.models import Company

async def scrape_product_hunt(max_companies=5):
    print(f"Starting Product Hunt scrape for {max_companies} products...")
    added_domains = []
    
    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.producthunt.com/feed') as resp:
            feed_data = await resp.text()
            
        feed = feedparser.parse(feed_data)
        
        added = 0
        async for db in get_db():
            for entry in feed.entries:
                if added >= max_companies:
                    break
                    
                title = entry.title
                
                html_content = entry.content[0].value
                soup = BeautifulSoup(html_content, 'html.parser')
                links = soup.find_all('a')
                outbound_link = None
                for link in links:
                    if link.text == "Link":
                        outbound_link = link['href']
                        break
                        
                if not outbound_link:
                    continue
                    
                # Resolve the redirect
                try:
                    async with session.get(outbound_link, allow_redirects=True, timeout=10) as dest_resp:
                        final_url = str(dest_resp.url)
                        domain = final_url.split("//")[-1].split("/")[0].replace("www.", "")
                        
                        # Store in DB
                        result = await db.execute(select(Company).where(Company.domain == domain))
                        company = result.scalar_one_or_none()
                        
                        if company is None:
                            company = Company(domain=domain, name=title, source='product_hunt')
                            db.add(company)
                            await db.commit()
                            print(f"Added from PH: {title} ({domain})")
                            added_domains.append(domain)
                            added += 1
                        else:
                            print(f"Already exists: {domain}")
                except Exception as e:
                    print(f"Skipping {title} - redirect failed: {e}")

    return added_domains
